import httpx
import json
from config import BASE_URL

async def activatekey(uuides):
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
                    "enable": True,
                    "email": client_email,
                    "flow": "xtls-rprx-vision"
                }]
            })
        }

        resp = await client.post(f"panel/inbound/updateClient/{new_uuid}", json=payload)

        if resp.status_code == 200:
            return