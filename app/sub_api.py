from fastapi import FastAPI, APIRouter, Response
from sqlalchemy import select
from app.database.models import async_session, User
from app.gen import get_servers
from typing import List
from pydantic import BaseModel
import json

router = APIRouter()

# Модель для одного сервера
class ServerItem(BaseModel):
    name: str        # Название сервера
    link: str      # Ссылка VLESS

# Модель подписки
class Subscription(BaseModel):
    subscription_name: str
    subscription_desc: str
    servers: List[ServerItem]

@router.get("/sub/{uuid}")
async def sub(uuid: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.uuid == uuid))
        if not user:
            return Response(json.dumps({"error": "User not found"}),
                            status_code=404,
                            media_type="application/json")

        servers = await get_servers()
        server_list = []

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
            server_list.append(ServerItem(
                name=f"{srv['address']} ({srv['port']})",  # Можно кастомизировать
                link=link,
                 # Здесь можно вставлять реальный трафик пользователя
            ))

        subscription_data = Subscription(
            subscription_name="OAO_beautiful_VPN",
            subscription_desc="Change_location_if_not_working",
            servers=server_list
        )

        return Response(
            content=subscription_data.json(ensure_ascii=False, indent=2),
            media_type="application/json"
        )

app = FastAPI()
app.include_router(router)