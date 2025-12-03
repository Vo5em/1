from fastapi import FastAPI, APIRouter, Response
from sqlalchemy import select
from app.database.models import async_session, User
from app.gen import get_servers

router = APIRouter()

@router.get("/sub/{uuid}")
async def sub(uuid: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.uuid == uuid))
        if not user:
            return Response("User not found", status_code=404, media_type="text/plain")

        servers = await get_servers()
        vless_lines = []

        for srv in servers:
            if not srv["enabled"]:
                continue
            client_email = f"NL-{uuid[:8]}"
            link = (
                f"vless://{uuid}@{srv['address']}:{srv['port']}?"
                f"type=tcp&encryption=none&security=reality&flow=xtls-rprx-vision"
                f"&pbk={srv['pbk']}&fp={srv['fp']}"
                f"&sni={srv['sni']}&sid={srv['sid']}&spx=%2F"
                f"#{client_email}"
            )
            vless_lines.append(link)

        headers = {
            "X-Name": "OAO_beautiful_VPN",
            "X-Desc": "Change_location_if_not_working"
        }

        return Response("\n".join(vless_lines), media_type="text/plain", headers=headers)

app = FastAPI()
app.include_router(router)