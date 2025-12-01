from email.policy import default

from sqlalchemy import ForeignKey, String, BigInteger, DateTime
from sqlalchemy.orm import Mapped, Boolean, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime
from zoneinfo import ZoneInfo
from config import DATABASE_URL

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    vpnkey: Mapped[str] = mapped_column(String(250),nullable=True)
    uuid: Mapped[str] = mapped_column(String(60),nullable=True)
    daybalance: Mapped[int] = mapped_column(default=3)
    dayend = mapped_column(DateTime(timezone=True))
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    payment_method_id: Mapped[str] = mapped_column(String(100), nullable=True)
    payload: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    notify_message: Mapped[int] = mapped_column(default=0)


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(50),default="pending")
    create_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(MOSCOW_TZ))
    payment_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)

class Servers(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Имя сервера (удобный label)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    # URL панели → https://domain.com/ или https://x.x.x.x/
    base_url: Mapped[str] = mapped_column(String(120), nullable=False)
    # Адрес реального сервера (домен или IP)
    address: Mapped[str] = mapped_column(String(120), nullable=False)
    # Порт (обычно 443)
    port: Mapped[int] = mapped_column(nullable=False, default=443)
    # Reality параметры
    pbk: Mapped[str] = mapped_column(String(120), nullable=False)   # publicKey
    sni: Mapped[str] = mapped_column(String(120), nullable=False)
    sid: Mapped[str] = mapped_column(String(120), nullable=False)
    fp: Mapped[str] = mapped_column(String(60), nullable=False)     # fingerprint
    #login
    login: Mapped[str] = mapped_column(String(60), nullable=False)
    password: Mapped[str] = mapped_column(String(60), nullable=False)

    # Активен ли сервер
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)