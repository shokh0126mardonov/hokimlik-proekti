import os
import django
from django.db.models import Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django.setup()

from apps.accounts.models import User

from asgiref.sync import sync_to_async
from apps.accounts.models import User


@sync_to_async
def _get_user_role(telegram_id: int):
    return User.objects.filter(Q(telegram_id=telegram_id) & Q(role = User.Role.OQSOQOL)).first()
    
async def user_status(telegram_id: int) -> dict:
    return await _get_user_role(telegram_id)

