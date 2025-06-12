from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    avatar_color = models.CharField(max_length=7, default='#007bff')
    
    def is_admin(self):
        return self.role == 'admin'
