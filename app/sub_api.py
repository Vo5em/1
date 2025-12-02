from fastapi import FastAPI, APIRouter
import base64

router = APIRouter()

@router.get("/sub/{code}")
async def sub(code: str):
    """
    Возвращает раскодированные ключи по base64 кодовой строке.
    """
    # Добавляем padding для Base64
    padded = code + "=" * (-len(code) % 4)

    try:
        decoded = base64.urlsafe_b64decode(padded.encode()).decode()
        return decoded
    except:
        return "Invalid subscription code"

app = FastAPI()
app.include_router(router)