import httpx
import uuid
import base64
import json
from app.database.requests import set_key, cheng_state_d
from app.database.models import async_session, Servers, UserServer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config import SUB_DOMAIN
from fastapi import APIRouter

router = APIRouter()


#REALITY_PBK = "k-FhLsJOvN4lAFyVBoohK__IFCh6v6BzLn6Yo1j9Tm8"
#REALITY_SNI = "google.com"
#REALITY_SID = "6dc9a670b54255f1"
#INBOUND_NAME = "eschalon"
#REALITY_FP = "chrome"


async def get_servers():
    async with async_session() as session:
        result = await session.execute(select(Servers))
        servers = result.scalars().all()

    server_dicts = []
    for s in servers:
        server_dicts.append({
            "id": s.id,
            "name": s.name,
            "base_url": s.base_url,
            "address": s.address,
            "port": s.port,
            "pbk": s.pbk,
            "sni": s.sni,
            "sid": s.sid,
            "fp": s.fp,
            "enabled": s.enabled,
            "login": s.login,
            "password": s.password
        })

    return server_dicts

async def plusserverid(uuid, pull):
    async with async_session() as session:
        session.add(UserServer(uuid=uuid, server=pull))
        await session.commit()


async def serch_pull(uuid):
    async with async_session() as session:
        result = await session.execute(
            select(UserServer.server)
            .where(UserServer.user_uuid == uuid)
        )

        servers = result.scalars().all()
    return servers


async def addkey(user_id):
    # Один UUID для всех серверов
    user_uuid = str(uuid.uuid4())
    client_email = f"NL-{user_uuid[:8]}"
    sub_id = str(uuid.uuid4())[:16]  # 🔥 ОДИН subId для всех серверов

    servers = await get_servers()


    for srv in servers:
        if not srv["enabled"]:
            continue

        async with httpx.AsyncClient(base_url=srv["base_url"], timeout=10.0) as client:

            # Логин
            login_resp = await client.post("login", json={
                "username": srv["login"],
                "password": srv["password"]
            })

            if login_resp.status_code != 200:
                print(f"Ошибка логина {srv['name']}")
                continue

            payload = {
                "id": 1,
                "settings": json.dumps({
                    "clients": [{
                        "id": user_uuid,
                        "email": client_email,
                        "flow": "xtls-rprx-vision",
                        "fingerprint": srv["fp"],
                        "shortId": srv["sid"],
                        "subId": sub_id,     # один на все
                        "enable": True
                    }]
                }),
                "streamSettings": json.dumps({
                    "network": "tcp",
                    "security": "reality",
                    "realitySettings": {
                        "publicKey": srv["pbk"],
                        "fingerprint": srv["fp"],
                        "serverNames": [srv["sni"], f"www.{srv['sni']}"],
                        "shortIds": [srv["sid"]],
                        "spiderX": "/"
                    }
                })
            }

            resp = await client.post("panel/api/inbounds/addClient", json=payload)

            if resp.status_code != 200:
                print(f"Ошибка клиента на {srv['name']}: {resp.text}")
                continue
            else:
                await plusserverid(user_uuid, srv["id"])

    # Каким должен быть домен подписки? → задаётся в config.SUB_DOMAIN
    subscription_url = f"https://{SUB_DOMAIN}/sub/{user_uuid}"

    await set_key(user_id, subscription_url, user_uuid)

async def delkey(user_uuid: str):

    servers = await get_servers()
    final_server_ids = set(await serch_pull(user_uuid))
    client_email = f"NL-{user_uuid[:8]}"

    for srv in servers:
        if srv["id"] not in final_server_ids:
            continue
        async with httpx.AsyncClient(base_url=srv["base_url"], timeout=10.0) as client:

            # 1️⃣ Логин в панель
            login_resp = await client.post("login", json={
                "username": srv["login"],
                "password": srv["password"]
            })

            if login_resp.status_code != 200:
                print(f"[{srv['name']}] ❌ Ошибка логина")
                continue

            # 2️⃣ Формируем payload
            payload = {
                "id": 1,
                "settings": json.dumps({
                    "clients": [{
                        "id": user_uuid,
                        "email": client_email,
                        "flow": "xtls-rprx-vision",
                        "fingerprint": srv["fp"],
                        "shortId": srv["sid"],
                        "enable": False
                    }]
                })
            }

            # 3️⃣ Отправляем правильный запрос
            resp = await client.post(f"panel/api/inbounds/updateClient/{user_uuid}", json=payload)

            try:
                resp_json = resp.json()
            except Exception:
                print(f"Ошибка {resp.status_code}: {resp.text}")

            if resp_json.get("success"):
                print(f"Пользователь {client_email} отключён")
            else:
                print(f"Ошибка API: {resp_json}")
    await cheng_state_d(user_uuid)


