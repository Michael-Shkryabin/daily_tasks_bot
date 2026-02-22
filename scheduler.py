import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from pytz import timezone as pytz_timezone
from pytz import UnknownTimeZoneError

from db import (
    get_all_users_with_timezone,
    is_digest_time_for_user,
    get_today_tasks_texts,
    get_tasks_for_reminder,
)

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def digest_job(bot):
    users = get_all_users_with_timezone()
    for u in users:
        try:
            tz = pytz_timezone(u["timezone"])
        except UnknownTimeZoneError:
            logger.warning("Неизвестная таймзона для user_id=%s: %s", u["user_id"], u["timezone"])
            continue
        now = datetime.now(tz).strftime("%H:%M")
        today = datetime.now(tz).date().isoformat()

        if not is_digest_time_for_user(u["user_id"], now):
            continue

        tasks = get_today_tasks_texts(u["user_id"], today)
        if not tasks:
            continue

        text = "📋 Задачи на сегодня:\n"
        for t in tasks:
            text += f"• {t}\n"
        try:
            await bot.send_message(u["user_id"], text)
        except Exception as e:
            logger.exception("Ошибка отправки дайджеста user_id=%s: %s", u["user_id"], e)


async def reminder_job(bot):
    """Отправляет напоминания по задачам в указанное пользователем время (в его таймзоне)."""
    users = get_all_users_with_timezone()
    for u in users:
        try:
            tz = pytz_timezone(u["timezone"])
        except UnknownTimeZoneError:
            continue
        now_str = datetime.now(tz).strftime("%H:%M")
        today_iso = datetime.now(tz).date().isoformat()
        tasks = get_tasks_for_reminder(u["user_id"], today_iso, now_str)
        for task in tasks:
            text = f"⏰ Напоминание\n\n{task['text']}\n📅 {task['task_date']} в {task['remind_time']}"
            try:
                await bot.send_message(u["user_id"], text)
            except Exception as e:
                logger.exception(
                    "Ошибка отправки напоминания user_id=%s task_id=%s: %s",
                    u["user_id"], task["id"], e
                )


def setup_scheduler(bot):
    scheduler.add_job(digest_job, "cron", minute="*", args=[bot])
    scheduler.add_job(reminder_job, "cron", minute="*", args=[bot])
    scheduler.start()


def shutdown_scheduler():
    scheduler.shutdown(wait=False)
