import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.db.models import Q
from asgiref.sync import sync_to_async

from apps.accounts.models import User


@sync_to_async
def _get_user(telegram_id: int):
    """
    ORM → fully sync context’da ishlaydi
    Lazy relationlar ham oldindan yuklanadi
    """

    return (
        User.objects
        .select_related("mahalla")  # keyinchalik ishlatilsa safe bo‘ladi
        .filter(
            Q(telegram_id=telegram_id) &
            Q(role=User.Role.OQSOQOL)
        )
        .first()
    )


async def user_status(telegram_id: int):
    """
    Async layer faqat await qiladi
    ORM bilan ishlamaydi
    """
    return await _get_user(telegram_id)