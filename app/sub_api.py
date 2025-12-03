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

            remark = f"🇳🇱 NL-{uuid[:8]} TCP"

            link = (
                f"vless://{uuid}@{srv['address']}:{srv['port']}?"
                f"security=reality&type=tcp"
                f"&fp={srv['fp']}"
                f"&pbk={srv['pbk']}"
                f"&sni={srv['sni']}"
                f"&sid={srv['sid']}"
                f"&spx=%2F"
                f"#{remark}"
            )

            vless_lines.append(link)

        body = "\n".join(vless_lines)

        # ---------------------------------------
        # ✨ ЭТО ГЛАВНОЕ: Метаданные подписки
        # ---------------------------------------
        headers = {
            "profile-title": "OAO_beautiful_VPN",             # Название подписки
            "profile-desc": "Change_location_if_not_working", # Описание
            "Content-Type": "text/plain; charset=utf-8",
            # По желанию: отображение трафика
            # upload=0; download=0; total=0; expire=0
            "subscription-userinfo": "upload=0; download=0; total=0; expire=0"
        }

        return Response(content=body, media_type="text/plain", headers=headers)

app = FastAPI()
app.include_router(router)