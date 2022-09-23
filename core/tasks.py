from __future__ import absolute_import, unicode_literals

from celery import shared_task
from core.utils import LeaderBoardRedisClient
from core.models import Food

@shared_task
def update_food_rates_periodically():
    LeaderBoardRedisClient().upgrade_leader_board(food_model=Food)
    print('task is runnnnnnnnnnning\a')
