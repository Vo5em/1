import httpx
import json
from app.gen import get_servers

#REALITY_FP = "chrome"
#REALITY_SID = "6dc9a670b54255f1"

async def activatekey(user_uuid: str):
    servers = await get_servers()
    client_email = f"NL-{user_uuid[:8]}"
    for srv in servers:
        async with httpx.AsyncClient(base_url=srv["base_url"], timeout=10.0) as client:
            login_resp = await client.post("login", json={
                "username": srv["login"],
                "password": srv["password"]
            })
        if login_resp.status_code != 200:
            print("Ошибка авторизации:", login_resp.text)
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
                    "shortId": [srv["sid"]],
                    "enable": True
                }]
            })
        }

        # 3️⃣ Отправляем правильный запрос
        resp = await client.post(f"panel/api/inbounds/updateClient/{user_uuid}", json=payload)

        try:
            resp.json()
        except Exception:
            print(f"Ошибка {resp.status_code}: {resp.text}")
