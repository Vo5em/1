import httpx
import uuid
import json
from app.database.requests import set_key
from config import BASE_URL

LOGIN_URL = BASE_URL + "login"
API_URL = BASE_URL + "panel/inbound/addClient"
REALITY_PBK = "k-FhLsJOvN4lAFyVBoohK__IFCh6v6BzLn6Yo1j9Tm8"
REALITY_SNI = "google.com"
REALITY_SID = "6dc9a670b54255f1"
INBOUND_NAME = "eschalon"
REALITY_FP = "chrome"


async def addkey(user_id):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1️⃣ Авторизация
        login_resp = await client.post("login", json={"username": "leg01", "password": "5sdvwlh25S"})
        if login_resp.status_code != 200:
            print("Ошибка авторизации")
            return

        # 2️⃣ Генерация UUID и email
        new_uuid = str(uuid.uuid4())
        client_email = f"NL-{new_uuid[:8]}"
        new_subid = str(uuid.uuid4())[:16]  # subId как у панели

        # 3️⃣ Формируем payload точно по образцу панели
        payload = {
            "id": 1,
            "settings": json.dumps({
                "clients": [{
                    "id": new_uuid,
                    "email": client_email,
                    "flow": "xtls-rprx-vision",
                    "fingerprint": REALITY_FP,
                    "shortId": REALITY_SID,
                    "subId": new_subid,
                    "enable": True,
                    "expiryTime": 0,
                    "comment": "",
                    "created_at": 0,
                    "updated_at": 0
                }],
                "decryption": "none",
                "encryption": "none"
            }),
            "streamSettings": json.dumps({
                "network": "tcp",
                "security": "reality",
                "realitySettings": {
                    "publicKey": REALITY_PBK,
                    "fingerprint": REALITY_FP,
                    "serverNames": [REALITY_SNI, f"www.{REALITY_SNI}"],
                    "shortIds": [REALITY_SID],
                    "spiderX": "/"
                },
                "tcpSettings": {
                    "header": {"type": "none"},
                    "acceptProxyProtocol": False
                }
            })
        }

        # 4️⃣ Создание клиента через API
        resp = await client.post("panel/api/inbounds/addClient", json=payload)
        if resp.status_code != 200:
            print(f"Ошибка создания клиента: {resp.status_code} {resp.text}")
            return

        # 5️⃣ Формируем рабочую VLESS ссылку
        vless_link = (
            f"vless://{new_uuid}@eschalon.ru:443?"
            f"type=tcp&encryption=none&security=reality&"
            f"pbk={REALITY_PBK}&fp={REALITY_FP}&"
            f"sni={REALITY_SNI}&sid={REALITY_SID}&spx=%2F&"
            f"flow=xtls-rprx-vision"
            f"#{INBOUND_NAME}-{client_email}"
        )

        print(f"Новый ключ создан: {vless_link} бесполезная хрень которая мне нужна {new_subid}")
        await set_key(user_id, vless_link, new_uuid)

async def delkey(user_uuid: str):
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
            return False

        if resp_json.get("success"):
            print(f"Пользователь {client_email} отключён")
            return True
        else:
            print(f"Ошибка API: {resp_json}")
            return False


