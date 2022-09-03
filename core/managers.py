# from calendar import weekday as _weekday
from datetime import date, timedelta
from django.db.models import Manager, Q, QuerySet
from django.conf import settings


class PaginatorQuerySet(QuerySet):
    page_size = settings.DEFAULT_PAGE_SIZE

    def get_page(self, page: int):
        return self[(page - 1) * self.page_size : page * self.page_size]


class FoodItemManager(Manager):
    page_size = settings.MENU_PAGE_SIZE

    def get_queryset(self):
        return PaginatorQuerySet(self.model)

    def show_menu(self, week_day: int):
        # TODO: update to ASYNC after adding redis to the project
        # since fitem.can_be_ordered will triger a redis call
        return self.filter(id__in = {fitem.id for fitem in self.filter(Q(weekday= week_day) | Q(weekday = -1)) if fitem.can_be_ordered})

    # def get_page(self, queryset, page: int):
    #     return queryset[(page - 1) * self.page_size : page * self.page_size]

class FoodManager(Manager):
    page_size = settings.FOOD_PAGE_SIZE

    def get_queryset(self):
        return PaginatorQuerySet(self.model)


class OrderItemManager(Manager):
    def get_queryset(self):
        return PaginatorQuerySet(self.model)

    def __getattr__(self, name, *args):
        if name.startswith("_"): 
            raise AttributeError
        return getattr(self.get_queryset(), name, *args) 
    
    def get_user_order(self, user):
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