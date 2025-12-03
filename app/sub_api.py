import base64
import logging
from fastapi import FastAPI, APIRouter
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from app.database.models import async_session, User
from app.gen import get_servers

logger = logging.getLogger("uvicorn.error")
router = APIRouter()

def to_base64_prefixed(s: str) -> str:
    """Возвращает строку вида 'base64:<base64-of-utf8>' — ascii-only."""
    b = base64.b64encode(s.encode("utf-8")).decode("ascii")
    return f"base64:{b}"

@router.get("/sub/{uuid}", response_class=PlainTextResponse)
async def sub(uuid: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.uuid == uuid))

        if not user:
            return PlainTextResponse("User not found", status_code=404)

        servers = await get_servers()

        vless_lines = []
        for srv in servers:
            if not srv.get("enabled"):
                continue

            client_label = f"NL-{uuid[:8]}"
            link = (
                f"vless://{uuid}@{srv['address']}:{srv['port']}?"
                f"type=tcp&encryption=none&security=reality&flow=xtls-rprx-vision"
                f"&pbk={srv['pbk']}&fp={srv['fp']}"
                f"&sni={srv['sni']}&sid={srv['sid']}&spx=%2F"
                f"#{client_label}"
            )
            vless_lines.append(link)

        body = "\n".join(vless_lines)
        response = PlainTextResponse(body)

        # Формируем безопасные ASCII header values
        title_utf = "OAO «beautiful VPN»"     # человекочитаемая версия (юникод)
        title_ascii_fallback = "OAO_beautiful_VPN"  # ascii fallback
        title_b64 = to_base64_prefixed(title_utf)

        descr = "Персональная подписка для клиента"  # описание (юникод)
        descr_b64 = to_base64_prefixed(descr)

        # Попробуем аккуратно установить несколько вариантов заголовков.
        # Устанавливаем в try/except чтобы не приводить к 500.
        try:
            # base64 вариант, который поддерживает v2raytun / xray clients
            response.headers["Profile-Title"] = title_b64
            response.headers["X-Profile-Title"] = title_b64

            # ascii fallback (чтобы избежать non-ascii проблем)
            response.headers["profile-title"] = title_ascii_fallback

            # описание/метаданные — тоже в base64-формате
            response.headers["Subscription-Userinfo"] = f"base64:{base64.b64encode(descr.encode('utf-8')).decode('ascii')}"
            response.headers["X-Subscription-Userinfo"] = f"description={descr_b64}"

            # Content-Disposition — чтобы в некоторых клиентах отображалось имя файла
            # Используем ascii-safe filename (цитирование ровное)
            response.headers["Content-Disposition"] = 'attachment; filename="OAO_beautiful_VPN.txt"'

        except Exception as exc:
            # Логируем проблему, но возвращаем тело, чтобы не обрывать работу подписки
            logger.exception("Cannot set subscription headers: %s", exc)

        return response

app = FastAPI()
app.include_router(router)