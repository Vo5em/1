from fastapi import FastAPI, APIRouter
from fastapi.responses import PlainTextResponse, JSONResponse
from app.database.models import async_session, User
from sqlalchemy import select, update, delete, desc
from app.gen import get_servers

router = APIRouter()

@router.get("/sub/{uuid}")
async def sub(uuid: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.uuid == uuid))

        if not user:
            return JSONResponse({"error": "User not found"}, status_code=404)

        servers = await get_servers()

        vless_links = []
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

            vless_links.append(link)

        return JSONResponse({
            "version": 1,
            "title": "eschalon VPN",
            "description": "Сменил локацию? Нажми на стрелку ↗️",
            "links": vless_links    # ВАЖНО — список, не строка
        })


app = FastAPI()
app.include_router(router)