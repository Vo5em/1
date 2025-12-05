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
            return Response(
                "User not found",
                status_code=404,
                media_type="text/plain"
            )

        servers = await get_servers()
        vless_lines = []

        for srv in servers:
            if not srv["enabled"]:
                continue

            link = (
                f"vless://{uuid}@{srv['address']}:{srv['port']}?"
                f"type=tcp"
                f"&encryption=none"
                f"&security=reality"
                f"&pbk={srv['pbk']}"
                f"&fp={srv['fp']}"
                f"&sni={srv['sni']}"
                f"&sid={srv['sid']}"
                f"&spx=%2F"
                f"&flow=xtls-rprx-vision"
                f"#eschalon-NL-{uuid[:8]}"
            )

            vless_lines.append(link)

        # <<< Вот эти две строки — секретный формат V2RayTun >>>
        meta = (
            "#!name: eschalon «VPN»\n"
            "#!desc: Change_location_if_not_working\n"
        )

        body = meta + "\n".join(vless_lines)

        return Response(
            content=body,
            media_type="text/plain; charset=utf-8"
        )

app = FastAPI()
app.include_router(router)