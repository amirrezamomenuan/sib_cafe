from __future__ import absolute_import, unicode_literals

from celery import shared_task

@shared_task
def update_food_rates_periodically():
    print('task is runnnnnnnnnnning\a')
    # could not implement because some python3.redis library commands, were unknown for my redisdb : zmscore, ...