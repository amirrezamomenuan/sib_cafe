from datetime import date
from django.db.models import QuerySet,Model

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


class RedisConnectionHandler:
    __total_rate_key = 'food-rate-total'
    __rate_counter_key = 'food-rate-counter'

    def __init__(self, connection) -> None:
        self.__connection = connection

    @staticmethod
    def format_key(id, date:date) -> str:
        return f'{id}:{date.strftime("%Y/%m/%d")}'
    
    def insert_rate(self, food_id:int, rate:int) -> bool:
        try:
            self.__connection.zincrby(name= self.__total_rate_key, amount=rate, value=food_id)
            self.__connection.zincrby(name=self.__rate_counter_key, amount=1, value=food_id)
            return True
        except:
            return False

    def update_food_order_count(self, food_item_id: int, order_date:date, canceling_order:bool = False):
        update_value = -1 if canceling_order else 1
        try:
            return self.__connection.incr(name=self.format_key(food_item_id, order_date), value=update_value)
        except:
            return None
    
    def get_food_order_count(self, food_item_id: int, order_date: date):
        try:
            return self.__connection.get(name=self.format_key(food_item_id, order_date))
        except:
            return None
    
    def set_food_order_count(self, food_item_id: int, order_date: date, value: int):
        try:
            return self.__connection.set(name=self.format_key(food_item_id, order_date), value=value)
        except:
            return None