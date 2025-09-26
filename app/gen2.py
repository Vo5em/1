import httpx
import json
from config import BASE_URL

REALITY_FP = "chrome"
REALITY_SID = "6dc9a670b54255f1"

async def activatekey(user_uuid: str):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1️⃣ Авторизация
        login_resp = await client.post("login", data={"username": "leg01", "password": "5sdvwlh25S"})
        if login_resp.status_code != 200:
            print("Ошибка авторизации:", login_resp.text)
            return False

        client_email = f"NL-{user_uuid[:8]}"

        # 2️⃣ Формируем payload
        payload = {
            "id": 1,
            "settings": json.dumps({
                "clients": [{
                    "id": user_uuid,
                    "email": client_email,
                    "flow": "xtls-rprx-vision",
                    "fingerprint": REALITY_FP,
                    "shortId": REALITY_SID,
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
            return False
