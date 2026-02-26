import httpx
import json
from fastapi import FastAPI, APIRouter, Response
from sqlalchemy import select
from app.database.models import async_session, User
from app.gen import get_servers, serch_pull, plusserverid
import base64

router = APIRouter()


async def create_key_on_server(user_uuid: str, srv: dict):
    client_email = f"NL-{user_uuid[:8]}"
    sub_id = user_uuid[:16]

    async with httpx.AsyncClient(base_url=srv["base_url"], timeout=10.0) as client:
        login_resp = await client.post("login", json={
            "username": srv["login"],
            "password": srv["password"]
        })

        if login_resp.status_code != 200:
            raise Exception(f"Login failed on {srv['name']}")

        payload = {
            "id": 1,
            "settings": json.dumps({
                "clients": [{
                    "id": user_uuid,
                    "email": client_email,
                    "flow": "xtls-rprx-vision",
                    "fingerprint": srv["fp"],
                    "shortId": srv["sid"],
                    "subId": sub_id,
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
            raise Exception(f"Failed to create client on {srv['name']}")
        else:
            await plusserverid(user_uuid, srv["id"])

def to_profile_title_b64(s: str) -> str:
    # Вернёт строку в виде "base64:<BASE64_UTF8>"
    b = s.encode("utf-8")
    return "base64:" + base64.b64encode(b).decode("ascii")


@router.get("/sub/{uuid}")
async def sub(uuid: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.uuid == uuid))

        if not user:
            return Response("User not found", status_code=404, media_type="text/plain")

        user_server_ids = set(await serch_pull(uuid))

        # 2. все сервера системы
        servers = await get_servers()

        enabled_server_ids = {
            srv["id"] for srv in servers if srv.get("enabled")
        }

        # 3. какие сервера нужно ДОБАВИТЬ пользователю
        missing_server_ids = enabled_server_ids - user_server_ids

        for srv in servers:
            if srv["id"] in missing_server_ids:
                try:
                    await create_key_on_server(uuid, srv)
                except Exception as e:
                    print(e)

            # 5. финальный список серверов для подписки
        final_server_ids = user_server_ids | enabled_server_ids

        vless_lines = []

        for srv in servers:
            if srv["id"] not in final_server_ids:
                continue

            link = (
                f"vless://{uuid}@{srv['address']}:{srv['port']}?"
                f"type=tcp"
                f"&encryption=none"
                f"&security=reality"
                f"&pbk={srv['pbk']}"
                f"&fp={srv['fp']}"
                f"&sni={srv['sni']}"
                f"&sid={srv['sid']}"
                f"&spx=%2F"
                f"&flow=xtls-rprx-vision"
                f"#eschalon-NL-{uuid[:8]}"
            )
            vless_lines.append(link)

        body = "\n".join(vless_lines)

        # НАЗВАНИЕ с кавычками — кодируем в base64 UTF-8 и ставим в profile-title
        profile_title_value = to_profile_title_b64('eschalon «VPN»')
        headers = {
            # важное: значение ASCII (base64:...), имя заголовка в нижнем регистре OK
            "profile-title": profile_title_value,
            # описание можно передать как простой ASCII заголовок
            "profile-desc": "Change_location_if_not_working",
            "Content-Type": "text/plain; charset=utf-8",
            # опционально: статистика
        }

        return Response(content=body, media_type="text/plain", headers=headers)

app = FastAPI()
app.include_router(router)