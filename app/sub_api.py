from fastapi import FastAPI, APIRouter
from fastapi.responses import PlainTextResponse
import base64

router = APIRouter()

@router.get("/sub/{code}", response_class=PlainTextResponse)
async def sub(code: str):
    # Добавляем padding
    padded = code + "=" * (-len(code) % 4)

    try:
        decoded = base64.urlsafe_b64decode(padded.encode()).decode()
        return PlainTextResponse(decoded)
    except:
        return PlainTextResponse("Invalid subscription code")

app = FastAPI()
app.include_router(router)