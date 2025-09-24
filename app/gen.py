import httpx
import uuid
import json
from app.database.requests import set_key
from config import BASE_URL

BASE_URL =  BASE_URL
LOGIN_URL = BASE_URL + "login"
API_URL = BASE_URL + "panel/api/inbounds/addClient"
REALITY_PBK = "BMo9OvK7YJu4JPXIrR2TcY8u0lavNdlPvN2j8N56sBE"
REALITY_SNI = "google.com"
REALITY_SID = "18d923c6768d6144"
INBOUND_NAME = "eschalon"

async def addkey(user_id: int):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Авторизация
        login_resp = await client.post("login", json={"username": "leg01", "password": "5sdvwlh25S"})
        if login_resp.status_code != 200:
            return

        # 2. Создание клиента
        new_uuid = str(uuid.uuid4())
        client_email = f"NL_{new_uuid[:8]}"
        payload = {
            "id": 1,
            "settings": json.dumps({
                "clients": [{
                    "id": new_uuid,
                    "email": client_email,
                    "flow": "xtls-rprx-vision"
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
            await set_key(user_id, vless_link, new_uuid)


async def delkey(uuides, tg_id):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        login_resp = await client.post("login", json={"username": "leg01", "password": "5sdvwlh25S"})
        if login_resp.status_code != 200:
            return


        new_uuid = str(uuides)
        client_email = f"NL_{new_uuid[:8]}"
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

