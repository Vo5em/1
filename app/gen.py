import httpx
import asyncio
import uuid
import json
from app.database.requests import set_key
from app.notification import notify_end
from config import BASE_URL

BASE_URL =  BASE_URL
LOGIN_URL = BASE_URL + "login"
API_URL = BASE_URL + "panel/inbound/addClient"
REALITY_PBK = "wV19LWOWi6RmSJne51QbGL8A8MjalDgbNlMnQUO9C0g"
REALITY_SNI = "yahoo.com"
REALITY_SID = "1de065d8"
INBOUND_NAME = "leg"

async def addkey(user_id: int):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Авторизация
        login_resp = await client.post("login", json={"username": "leg01", "password": "5sdvwlh25S"})
        if login_resp.status_code != 200:
            return

        # 2. Создание клиента
        new_uuid = str(uuid.uuid4())
        client_email = f"user_{new_uuid[:8]}example.com"
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

        resp = await client.post("panel/inbound/addClient", json=payload)

        if resp.status_code == 200:
            vless_link = (
                f"vless://{new_uuid}@set.kabinetboos.ru:443?"
                f"type=tcp&security=reality&"
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
        client_email = f"user_{new_uuid[:8]}example.com"
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

        resp = await client.post(f"panel/inbound/updateClient/{new_uuid}", json=payload)

        if resp.status_code == 200:
            return

