from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='employee_profile')
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=120, blank=True)
    position = models.CharField(max_length=120, blank=True)
    start_date = models.DateField(null=True, blank=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='team')

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
