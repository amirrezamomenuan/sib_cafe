from django.db import models
from django.contrib.auth.models import User as parrent_user

class User(parrent_user):
    def calculate_total_debt(self) -> int:
        return 1000