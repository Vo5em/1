import base64
import httpx
import asyncio
import uuid
from fastapi import FastAPI, Request
from app.database.models import async_session, User, Order
from app.notification import notify_before_end, notify_spss, notify_end, test_job
from zoneinfo import ZoneInfo
from sqlalchemy import select, update, delete, desc
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from yookassa import Payment, Configuration
from config import yookassa_shopid, yookassa_api, mybot
from app.gen2 import activatekey


MOSCOW_TZ = ZoneInfo("Europe/Moscow")
scheduler = AsyncIOScheduler(timezone=MOSCOW_TZ)

Configuration.account_id = yookassa_shopid
Configuration.secret_key = yookassa_api

app = FastAPI()


async def set_user(tg_id, ref_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            if ref_id:
                ref_check = await session.scalar(select(User).where(User.tg_id == ref_id))
                if ref_check:
                    session.add(User(tg_id=tg_id,referrer_id=ref_check.id))
                    new_daybalance = (ref_check.daybalance) + 7
                    is_day = await find_dayend(ref_id)
                    now_moscow = datetime.now(tz=MOSCOW_TZ)
                    if is_day.tzinfo is None:
                        is_day = is_day.replace(tzinfo=MOSCOW_TZ)
                    if is_day < now_moscow:
                        dayend = now_moscow + timedelta(days=new_daybalance)
                        await session.execute(update(User).where(User.tg_id == ref_id).values(dayend=dayend,
                                                                                              daybalance=0))
                    else:
                        dayend = is_day + timedelta(days=new_daybalance)
                        await session.execute(update(User).where(User.tg_id == ref_id).values(dayend=dayend,
                                                                                              daybalance=0))
                else:
                    session.add(User(tg_id=tg_id))
            else:
                session.add(User(tg_id=tg_id))
        await session.commit()


async def set_key(tg_id, vless_link, new_uuid):
    async with async_session() as session:
        result = await session.execute(select(User.daybalance).where(User.tg_id == tg_id))
        daybalance = result.scalar_one_or_none()
        now_moscow = datetime.now(tz=MOSCOW_TZ)
        dayend = now_moscow + timedelta(days=daybalance)
        dayend_naive = dayend.replace(tzinfo=None)
        await session.execute(update(User).where(User.tg_id == tg_id).values(vpnkey=vless_link,
                                                                             uuid=new_uuid,
                                                                             dayend=dayend_naive,
                                                                             daybalance=0))
        await session.commit()
        if dayend:
            try:
                scheduler.remove_job(f'before_{tg_id}')
            except Exception:
                pass

            schedule_notifications(tg_id, dayend)


async def check_end():
    print("ger")
    from app.gen import delkey
    now_moscow = datetime.now(tz=MOSCOW_TZ)
    async with async_session() as session:
        end = await session.execute(select(User.uuid, User.tg_id).where(User.dayend != None, User.dayend < now_moscow))
        results = end.all()
        if not results:
            return
        for uuid, tg_id in results:
            await delkey(uuid)
        await session.commit()


async def get_users():
    async with async_session() as session:
        result = await session.scalars(select(User.tg_id))
        return result.all()


async def get_vip():
    async with async_session() as session:
        result = await session.execute(select(User.tg_id).where(User.payload != None))
        return [row[0] for row in result.all()]


async def get_broke():
    async with async_session() as session:
        result = await session.execute(select(User.tg_id).where(User.payload == None))
        return [row[0] for row in result.all()]


async def find_key(tg_id):
    async with async_session() as session:
        key = await session.scalar(select(User.vpnkey).where(User.tg_id == tg_id))
        return key


async def find_dayend(tg_id):
    async with async_session() as session:
        day = await session.scalar(select(User.dayend).where(User.tg_id == tg_id))
    return day


async def find_tgid(id):
    async with async_session() as session:
        tg_id = await session.scalar(select(User.tg_id).where(User.id == id))
    return tg_id

async def maketake(ref_id):
    async with async_session() as session:
        result = await session.execute(
            select(Order).where(Order.user_id == ref_id, Order.status == "paid")
        )
        paid_orders = result.scalars().all()

        if ref_id and len(paid_orders) == 0:
            await takeprise(ref_id)


async def takeprise(ref_id2):
    async with async_session() as session:
         ref_check = await session.scalar(select(User).where(User.id == ref_id2))
         if ref_check:
            print("ger")
            new_daybalance = (ref_check.daybalance) + 7
            is_tgid = await find_tgid(ref_id2)
            is_day = await find_dayend(is_tgid)
            now_moscow = datetime.now(tz=MOSCOW_TZ)
            if is_day.tzinfo is None:
                is_day = is_day.replace(tzinfo=MOSCOW_TZ)
            if is_day < now_moscow:
                dayend = now_moscow + timedelta(days=new_daybalance)
                await session.execute(update(User).where(User.tg_id == is_tgid).values(dayend=dayend,
                                                                                      daybalance=0))
            else:
                dayend = is_day + timedelta(days=new_daybalance)
                await session.execute(update(User).where(User.tg_id == is_tgid).values(dayend=dayend,
                                                                                      daybalance=0))
         await session.commit()


async def find_payload(tg_id):
    async with async_session() as session:
        payload = await session.scalar(select(User.payload).where(User.tg_id == tg_id))
    return payload


async def save_message(tg_id, message_id):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()
        print("t")
        if user:
            user.message_id = message_id
            await session.commit()


async def find_message(tg_id):
    async with async_session() as session:
        message = await session.scalar(select(User.message_id).where(User.tg_id == tg_id))
    return message


async def find_paymethod_id(tg_id):
    async with async_session() as session:
        paymenthod_id = await session.scalar(select(User.payment_method_id).where
                                             (User.payment_method_id != None, User.tg_id == tg_id))
        return paymenthod_id


async def delpaymethod_id(tg_id):
    async with async_session() as session:
        paymenthod_id = await session.scalar(select(User.payment_method_id).where
                                             (User.payment_method_id != None, User.tg_id == tg_id)
                                             )
        if paymenthod_id:
            await session.execute(update(User).where(User.tg_id == tg_id).values(payment_method_id=None))
            await session.commit()


async def schedulers():
    while True:
        await check_subscriptions()
        await check_end()
        await asyncio.sleep(18)


def schedule_notifications(tg_id, dayend):
    if dayend.tzinfo is None:
        dayend = dayend.replace(tzinfo=MOSCOW_TZ)

    before = dayend - timedelta(days=1)
    now = datetime.now(tz=MOSCOW_TZ)
    scheduler.add_job(test_job, "date", run_date=datetime.now(MOSCOW_TZ) + timedelta(seconds=10))

    if before > now:
        scheduler.add_job(
            notify_before_end,
            trigger="date",
            run_date=before,
            args=[tg_id],
            id=f"before_{tg_id}",
            replace_existing=True
        )

    if dayend > now:
        scheduler.add_job(
            notify_end,
            trigger="date",
            run_date=dayend,
            args=[tg_id],
            id=f"end_{tg_id}",
            replace_existing=True
        )

def schedule_notifications2(tg_id, dayend):
    if dayend.tzinfo is None:
        dayend = dayend.replace(tzinfo=MOSCOW_TZ)

    now = datetime.now(tz=MOSCOW_TZ)

    if dayend > now:
        scheduler.add_job(
            notify_end,
            trigger="date",
            run_date=dayend,
            args=[tg_id],
            id=f"end_{tg_id}",
            replace_existing=True
        )


async def restore_notifications():
    async with async_session() as session:
        result = await session.execute(
            select(User.tg_id, User.dayend, User.payload).where(User.dayend != None)
        )
        users = result.all()
        now = datetime.now(tz=MOSCOW_TZ)

        for tg_id, dayend, payload in users:
            if payload and dayend > now:
                schedule_notifications2(tg_id, dayend)
            if dayend.tzinfo is None:
                dayend = dayend.replace(tzinfo=MOSCOW_TZ)
            if dayend > now:
                schedule_notifications(tg_id, dayend)


async def create_payment(tg_id: int, amount: float = 150.0, currency: str = "RUB") -> tuple[str, int]:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            raise ValueError("Пользователь не найден")

        if not user.payload:
            user.payload = str(uuid.uuid4())
        payload_value = user.payload

        now_naive = datetime.now().replace(tzinfo=None)
        order = Order(user_id=user.id, create_at=now_naive, status="pending")
        session.add(order)
        await session.commit()
        await session.refresh(order)  # получаем order.id
        order_id = order.id

    def _sync_create():
        return Payment.create({
            "amount": {"value": f"{amount:.2f}", "currency": currency},
            "capture": True,
            "confirmation": {"type": "redirect", "return_url": str(mybot)},
            "description": f"Оплата подписки для {tg_id}",
            "save_payment_method": True,
            "metadata": {"payload": payload_value},
        })

    payment = await asyncio.to_thread(_sync_create)
    payment_id = str(payment.id)
    payment_url = payment.confirmation.confirmation_url

    # Сохраняем payment_id в заказе
    async with async_session() as session:
        order = await session.get(Order, order_id)
        order.payment_id = payment_id
        await session.commit()

    print(f"[LOG] Created payment: {payment_id}, order_id: {order_id}")
    return payment_url


@app.post("/yookassa/webhook")
async def yookassa_webhook(request: Request):
    raw = await request.body()
    print("RAW webhook:", raw.decode())  # для отладки

    data = await request.json()
    event = data.get("event")
    obj = data.get("object", {})

    if event == "payment.succeeded":
        payload = obj.get("metadata", {}).get("payload")
        payment_method_id = obj.get("payment_method", {}).get("id")

        if payload:
            async with async_session() as session:
                result = await session.execute(select(User).where(User.payload == payload))
                user = result.scalars().first()
                if not user:
                    return {"status": "user_not_found"}

                now = datetime.now(tz=MOSCOW_TZ)
                if not user.dayend or user.dayend < now:
                    user.dayend = now + timedelta(days=30)
                else:
                    user.dayend += timedelta(days=30)

                ruuid = user.uuid
                tg_id = int(user.tg_id)
                dayend = user.dayend
                ref_id = user.referrer_id


                await activatekey(ruuid)
                try:
                    await notify_spss(tg_id)
                except Exception as e:
                    print(f"Ошибка при notify_spss: {e}")
                if ref_id is not None:
                    await maketake(ref_id)
                else:
                    print("User has no referrer, skipping takeprise")
                schedule_notifications2(tg_id,dayend)


                if payment_method_id:
                    user.payment_method_id = payment_method_id

                result = await session.execute(
                    select(Order)
                    .where(Order.user_id == user.id)
                    .order_by(Order.create_at.desc())
                )
                order = result.scalars().first()
                if order:
                    order.status = "paid"

                await session.commit()


    elif event == "payment.canceled":
        payload = obj.get("metadata", {}).get("payload")

        if payload:
            async with async_session() as session:
                result = await session.execute(
                    select(User).where(User.payload == payload)
                )
                user = result.scalars().first()
                if not user:
                    return {"status": "user_not_found"}

                result = await session.execute(
                    select(Order)
                    .where(Order.user_id == user.id)
                    .order_by(Order.create_at.desc())
                )
                order = result.scalars().first()
                if order:
                    order.status = "canceled"

                await session.commit()

    return {"status": "ok"}


async def create_auto_payment(user: User, amount: float = 150.0, currency: str = "RUB"):
    if not user.payment_method_id:
        raise ValueError("Нет сохранённого способа оплаты")

    payment = Payment.create({
        "amount": {
            "value": f"{amount:.2f}",
            "currency": currency
        },
        "capture": True,
        "payment_method_id": user.payment_method_id,  # ключ для автосписания
        "description": f"Автопродление подписки",
        "metadata": {
            "payload": user.payload
        }
    })

    return payment.id  # можем сохранить для логов


async def check_subscriptions():
    print("g")
    now = datetime.now(tz=MOSCOW_TZ)
    async with async_session() as session:
        users = await session.execute(
            select(User).where(User.dayend != None, User.dayend - timedelta(hours=1) <= now, User.dayend >= now)
        )
        for user in users.scalars().all():
            result = await session.execute(
                select(Order).where(
                    Order.user_id == user.id,
                    Order.status.in_(["pending"])
                ).order_by(Order.create_at.desc())
            )
            order = result.scalars().first()

            if order:
                continue

            await create_auto_payment(user)

        await session.commit()

@app.get("/")
async def index(request: Request):
    return {"message": "Hello"}

