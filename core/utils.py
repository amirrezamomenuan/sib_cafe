from datetime import date

from django.conf import settings
from redis import Redis, RedisError, ConnectionError
from django.db.models import Model, Count, Sum

def _get_queryset(klass):
    if hasattr(klass, '_default_manager'):
        return klass._default_manager.all()
    return klass

def get_object_or_404_rest(klass, **kwargs):
    queryset = _get_queryset(klass)
    if not hasattr(queryset, 'get'):
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(**kwargs)
    except queryset.model.DoesNotExist:
        return None


class RedisClient:
    def __init__(self) -> None:
        try:
            if settings.REDIS_URL:
                self.redis_client = Redis.from_url(
                    url=settings.REDIS_URL,
                    decode_responses=True
                )
            else:
                self.redis_client = Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True
                )
        except RedisError:
           return

    @staticmethod
    def format_key(id, date:date) -> str:
        return f'{id}:{date.strftime("%Y/%m/%d")}'
    

class LeaderBoardRedisClient(RedisClient):
    total_rate_key = f"{settings.REDIS_PREFIX}:total"
    rate_counter_key = f'{settings.REDIS_PREFIX}:counter'
    rate_set_key = f"{settings.REDIS_PREFIX}:rate"

    def __init__(self) -> None:
        super().__init__()



    def update_food_order_count(self, food_item_id: int, order_date:date, canceling_order:bool = False):
        update_value = -1 if canceling_order else 1
        try:
            return self.redis_client.incrby(name=self.format_key(food_item_id, order_date), amount=update_value)
        except Exception as e:
            return None
    
    def get_food_order_count(self, food_item_id: int, order_date: date):
        try:
            return self.redis_client.get(name=self.format_key(food_item_id, order_date))
        except Exception as e:
            return None
    
    def set_food_order_count(self, food_item_id: int, order_date: date, value: int):
        try:
            return self.redis_client.set(name=self.format_key(food_item_id, order_date), value=value)
        except Exception as e:
            return None

    def insert_rate(self, food_id:int, rate:int) -> bool:
        try:
            self.redis_client.zincrby(name= self.total_rate_key, amount=rate, value=food_id)
            self.redis_client.zincrby(name=self.rate_counter_key, amount=1, value=food_id)
            return True
        except:
            return False
    
    def bulk_insert_rate(self, rate_totals:dict, rate_counts:dict):
        try:
            self.redis_client.zadd(name=self.total_rate_key, mapping=rate_totals)
            self.redis_client.zadd(name=self.rate_counter_key, mapping=rate_counts)
            return True
        except:
            return False
    
    # TODO : its very inefficient change after internet access
    def upgrade_leader_board(self, food_model:Model):
        try:
            # shold have used "self.redis_client.zmscore" to decrease redis_connections but my redis_version does not support it 
            # and i dont have internet access to upgrade it
            rate_counts = self.redis_client.zrange(name=self.rate_counter_key, start=0, end=-1, withscores=True)
            food_item_total_values = []
            for r in rate_counts:
                food_item_total_values.append(self.redis_client.zscore(name=self.total_rate_key, value=r[0]))
            items = {}
            for i in range(len(rate_counts)):
                items[rate_counts[i][0]] = food_item_total_values[i] / rate_counts[i][1]
            self.redis_client.zadd(self.rate_set_key, items)

        except RedisError:
            #log error

            rates = food_model.objects.annotate(rate_count = Count('food_rates'), rate_total = Sum('food_rates__rate')).values('id', 'rate_count', 'rate_total')
            rate_totals = {}
            rate_counts = {}
            rate_results = {}
            for rate in rates:
                if rate['rate_total'] and rate['rate_count']:
                    rate_totals[str(rate['id'])] = rate['rate_total']
                    rate_counts[str(rate['id'])] = rate['rate_count']
                    rate_results[str(rate['id'])] = rate['rate_total'] / rate['rate_count']

            self.bulk_insert_rate(rate_totals, rate_counts)
            self.redis_client.zadd(self.rate_set_key, rate_results)

    def get_leaderboard(self) -> dict:
        results = self.redis_client.zrevrangebyscore(name=self.rate_set_key, min=0, max=10, withscores=True)
        dict_result = {}
        for r in results:
            # should have replaced with formating but i dont remember the exact syntax
            dict_result[r[0]] = float(str(r[1]).split('.')[0] + '.' +str(r[1]).split('.')[1][:2])
        return dict_result
    
    def get_leaderboard_lazy(self, food_model:Model) -> dict:
        rates = food_model.objects.annotate(rate_count = Count('food_rates'), rate_total = Sum('food_rates__rate')).values('id', 'rate_count', 'rate_total')
        rate_results = {}
        for rate in rates:
            if rate['rate_total'] and rate['rate_count']:
                rate_results[str(rate['id'])] = rate['rate_total'] / rate['rate_count']
        
        return rate_results
