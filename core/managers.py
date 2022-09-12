from datetime import date
from django.db.models import Manager, Q, QuerySet
from django.conf import settings


class PaginatorQuerySet(QuerySet):
    def get_page(self, **kwargs) -> list:
        offset = kwargs.get('offset')
        limit = kwargs.get('limit')
        offset = 0 if offset is None else int(offset[0])
        limit = limit if limit is None else int(limit[0]) + offset

        return self[offset: limit]


class FoodItemManager(Manager):

    @staticmethod
    def get_weekday() -> int:
        return (date.weekday(date.today()) + 2) % 7
    
    @staticmethod
    def proccess_sort_parameter(sort_by):
        if sort_by is not None:
            sort_by = sort_by[0]
            if sort_by in ('price', '-price', 'rate', '-rate'):
                return sort_by

    def get_queryset(self):
        return PaginatorQuerySet(self.model)

    def show_menu(self, **kwargs):
        sort_by = kwargs.get('sort_by')
        week_day = kwargs.get('weekday')
        if week_day:
            week_day = int(week_day[0])
        else:
            week_day = int(self.get_weekday())
        
        if week_day in (5, 6):
            return self.none()

        # TODO: check if food can be ordered
        query_set = self.filter(Q(weekday= week_day) | Q(weekday = -1))
        sort_by = self.proccess_sort_parameter(sort_by)
        if sort_by:
            return query_set.order_by(sort_by)
        return query_set


























class FoodManager(Manager):
    page_size = settings.FOOD_PAGE_SIZE

    def get_queryset(self):
        return PaginatorQuerySet(self.model)

    # def get_page(self, page: int):
    #     return self.all()[(page - 1) * self.page_size : page * self.page_size]


class OrderItemManager(Manager):
    def get_queryset(self):
        return PaginatorQuerySet(self.model)

    def __getattr__(self, name, *args):
        if name.startswith("_"): 
            raise AttributeError
        return getattr(self.get_queryset(), name, *args) 
    
    def get_user_orders(self, user):
        return self.filter(user = user)




# class Entry(models.Model):
#     objects = EntryManager() # don't forget this

#     is_public = models.BooleanField()
#     owner = models.ForeignKey(User)


# class EntryManager(models.Manager):
#     '''Use this class to define methods just on Entry.objects.'''
#     def get_query_set(self):
#         return EntryQuerySet(self.model)

    # def __getattr__(self, name, *args):
    #     if name.startswith("_"): 
    #         raise AttributeError
    #     return getattr(self.get_query_set(), name, *args) 

#     def get_stats(self):
#         '''A sample custom Manager method.'''
#         return { 'public_count': self.get_query_set().public().count() }


# class EntryQuerySet(models.query.QuerySet):
#     '''Use this class to define methods on queryset itself.'''
#     def public(self):
#         return self.filter(is_public=True)

#     def by(self, owner):
#         return self.filter(owner=owner)


# stats = Entry.objects.get_stats()    
# my_entries = Entry.objects.by(request.user).public()