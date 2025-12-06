import httpx
import json
from app.database.models import async_session, Servers
from sqlalchemy import select

#REALITY_FP = "chrome"
#REALITY_SID = "6dc9a670b54255f1"
async def get_serv():
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

async def activatekey(user_uuid: str):
    servers = await get_serv()
    client_email = f"NL-{user_uuid[:8]}"

    for srv in servers:
        if not srv["enabled"]:
            continue

        # Гарантируем, что URL правильный
        base_url = srv["base_url"]
        if not base_url.startswith(("http://", "https://")):
            base_url = "http://" + base_url

        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:

            # --- 1. Логин ---
            login_resp = await client.post("login", json={
                "username": srv["login"],
                "password": srv["password"]
            })

            if login_resp.status_code != 200:
                print(f"[{srv['name']}] ❌ Ошибка авторизации: {login_resp.text}")
                continue

            # --- 2. Формируем payload ---
            payload = {
                "id": 1,
                "settings": json.dumps({
                    "clients": [{
                        "id": user_uuid,
                        "email": client_email,
                        "flow": "xtls-rprx-vision",
                        "fingerprint": srv["fp"],
                        "shortId": [srv["sid"]],
                        "enable": True
                    }]
                })
            }

            # --- 3. Запрос активации ---
            resp = await client.post(
                f"panel/api/inbounds/updateClient/{user_uuid}",
                json=payload
            )

            try:
                j = resp.json()
            except:
                print(f"[{srv['name']}] ❌ Ошибка активации {resp.status_code}: {resp.text}")
                continue

            if j.get("success"):
                print(f"[{srv['name']}] ✅ Пользователь {client_email} активирован")
            else:
                print(f"[{srv['name']}] ❌ Ответ API: {j}")
