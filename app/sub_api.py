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

        nodes = []

        for srv in servers:
            if not srv["enabled"]:
                continue

            nodes.append({
                "type": "vless",
                "tag": srv["name"],         # имя в приложении
                "server": srv["address"],
                "port": srv["port"],
                "uuid": uuid,
                "network": "tcp",
                "flow": "xtls-rprx-vision",
                "tls": {
                    "enabled": True,
                    "type": "reality",
                    "serverName": srv["sni"],
                    "publicKey": srv["pbk"],
                    "shortId": srv["sid"],
                    "fingerprint": srv["fp"],
                    "spiderX": "/"
                }
            })

        return JSONResponse({
            "version": 1,
            "title": "eschalon VPN",
            "description": "Сменил локацию? Нажми на стрелку ↗️",
            "nodes": nodes
        })


app = FastAPI()
app.include_router(router)