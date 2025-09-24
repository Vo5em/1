import httpx
import uuid
import json
from app.database.requests import set_key
from config import BASE_URL

BASE_URL =  BASE_URL
LOGIN_URL = BASE_URL + "login"
API_URL = BASE_URL + "panel/api/inbounds/addClient"
REALITY_PBK = "rZK50rxskpnFkkxvGWolSGOsmjQ3GenCWeTcE0jiiEI"
REALITY_SNI = "google.com"
REALITY_SID = "52"
INBOUND_NAME = "eschalon"

'''async def addkey(user_id: int):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Авторизация
        login_resp = await client.post("login", json={"username": "leg01", "password": "5sdvwlh25S"})
        if login_resp.status_code != 200:
            return

        # 2. Создание клиента
        new_uuid = str(uuid.uuid4())
        client_email = f"NL-{new_uuid[:8]}"
        payload = {
            "id": 2,
            "settings": json.dumps({
                "clients": [{
                    "id": new_uuid,
                    "email": client_email,
                    "flow": "xtls-rprx-vision",
                            "shortId": REALITY_SID,
                            "fingerprint": "chrome"
                }]
            })
        }

        resp = await client.post("panel/api/inbounds/addClient", json=payload)

        if resp.status_code == 200:
            vless_link = (
                f"vless://{new_uuid}@eschalon.ru:443?"
                f"type=tcp&encryption=none&security=reality&"
                f"pbk={REALITY_PBK}&fp=chrome&"
                f"sni={REALITY_SNI}&sid={REALITY_SID}&spx=%2F&"
                f"flow=xtls-rprx-vision"
                f"#{INBOUND_NAME}-{client_email}"
            )
            await set_key(user_id, vless_link, new_uuid)'''


async def addkey(user_id: int):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # Авторизация
        login_resp = await client.post("login", json={"username": "leg01", "password": "5sdvwlh25S"})
        login_resp.raise_for_status()

        inbound_id = 2

        # Получаем текущий inbound
        get_resp = await client.get(f"panel/api/inbounds/get/{inbound_id}")
        get_resp.raise_for_status()
        inbound_data = get_resp.json()

        # Достаём список клиентов
        settings = json.loads(inbound_data["obj"]["settings"])
        clients = settings.get("clients", [])

        # Генерируем нового клиента
        new_uuid = str(uuid.uuid4())
        client_email = f"NL-{new_uuid[:8]}"
        short_id = new_uuid.replace("-", "")[:8]

        new_client = {
            "id": new_uuid,
            "email": client_email,
            "flow": "xtls-rprx-vision",
            "shortIds": [short_id],
            "fingerprint": "chrome"
        }

        # Добавляем нового к списку
        clients.append(new_client)

        # Отправляем обратно через addClient
        payload = {
            "id": inbound_id,
            "settings": json.dumps({"clients": clients})
        }

        resp = await client.post("panel/api/inbounds/addClient", json=payload)
        resp.raise_for_status()

        # Строим ссылку
        vless_link = (
            f"vless://{new_uuid}@eschalon.ru:443?"
            f"type=tcp&encryption=none&security=reality&"
            f"pbk={REALITY_PBK}&fp=chrome&"
            f"sni={REALITY_SNI}&sid={short_id}&spx=%2F&"
            f"flow=xtls-rprx-vision"
            f"#{INBOUND_NAME}-{client_email}"
        )
        await set_key(user_id, vless_link, new_uuid)


async def delkey(uuides, tg_id):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        login_resp = await client.post("login", json={"username": "leg01", "password": "5sdvwlh25S"})
        if login_resp.status_code != 200:
            return


        new_uuid = str(uuides)
        client_email = f"NL-{new_uuid[:8]}"
        payload = {
            "id": 1,
            "settings": json.dumps({
                "clients": [{
                    "id": new_uuid,
                    "enable": False,
                    "email": client_email,
                    "flow": "xtls-rprx-vision"
                }]
            })
        }

        resp = await client.post(f"panel/api/inbounds/updateClient/{new_uuid}", json=payload)

        if resp.status_code == 200:
            return

