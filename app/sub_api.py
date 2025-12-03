from fastapi import FastAPI, APIRouter, Response
from sqlalchemy import select
from app.database.models import async_session, User
from app.gen import get_servers
from urllib.parse import quote

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
            # Добавляем имя и описание прямо в фрагмент ссылки
            name = "OAO_beautiful_VPN"
            desc = "Change_location_if_not_working"
            fragment = quote(f"{client_email} | {name} | {desc}")

            link = (
                f"vless://{uuid}@{srv['address']}:{srv['port']}?"
                f"type=tcp&encryption=none&security=reality&flow=xtls-rprx-vision"
                f"&pbk={srv['pbk']}&fp={srv['fp']}"
                f"&sni={srv['sni']}&sid={srv['sid']}&spx=%2F"
                f"#{fragment}"
            )

            vless_lines.append(link)

        return Response("\n".join(vless_lines), media_type="text/plain")

app = FastAPI()
app.include_router(router)