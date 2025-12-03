import base64
from fastapi import FastAPI, APIRouter
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from app.database.models import async_session, User
from app.gen import get_servers

router = APIRouter()

def to_base64_prefixed(s: str) -> str:
    # v2raytun/doc examples use prefix "base64:" followed by base64 of UTF-8
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
            if not srv["enabled"]:
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

        # Название подписки (v2raytun and similar accept raw or base64:)
        profile_title = "OAO beautiful VPN"        # ascii-safe fallback
        profile_title_utf = "OAO «beautiful VPN»"  # human-friendly (unicode)
        response.headers["Profile-Title"] = to_base64_prefixed(profile_title_utf)
        # Дополнительный header с кратким описанием (варианты названий у разных клиентов)
        response.headers["Subscription-Userinfo"] = "description=Персональная подписка;owner=OAO"
        # Content-Disposition полезен для имени скачиваемого файла
        response.headers["Content-Disposition"] = 'attachment; filename="OAO_beautiful_VPN.txt"'

        return response

app = FastAPI()
app.include_router(router)