from fastapi import FastAPI, APIRouter
from fastapi.responses import PlainTextResponse
from app.database.models import async_session, User
from sqlalchemy import select
from app.gen import get_servers

router = APIRouter()

@router.get("/sub/{uuid}", response_class=PlainTextResponse)
async def sub(uuid: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.uuid == uuid))

        if not user:
            return PlainTextResponse("User not found", status_code=404)

        servers = await get_servers()

        vless_lines = []

        # ---------- 🔥 Добавляем название и описание в PlainText ----------
        vless_lines.append("OAO «beautiful VPN»")
        vless_lines.append("Добро пожаловать! Вот ваша VPN-подписка:")
        vless_lines.append("")  # пустая строка

        # ---------- 🔥 VLESS ссылки ----------
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

        # ---------- 🔥 Возвращаем ровно строку ----------
        return "\n".join(vless_lines)


app = FastAPI()
app.include_router(router)