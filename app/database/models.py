from email.policy import default

from sqlalchemy import ForeignKey, String, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
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


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(50),default="pending")
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=MOSCOW_TZ))
    payment_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)