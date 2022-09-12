from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    def calculate_total_debt(self) -> int:
        return 1000
    
    def __repr__(self) -> str:
        return f"{self.first_name} {self.last_name}"