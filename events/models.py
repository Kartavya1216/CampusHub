from email.policy import default
from random import choice
from django.db import models
from  django.contrib.auth.models import User
from users.models import UserProfile
# Create your models here.
class Event(models.Model):
    STATUS_CHOICES = [
        ('Pending','Pending'),
        ('Approved','Approved'),
        ('Rejected','Rejected')
    ]
    ROLE_CHOICES = UserProfile.ROLE_CHOICES
    DEPARTMENT_CHOICES = UserProfile.DEPARTMENT_CHOICES
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_by = models.ForeignKey(User , on_delete=models.CASCADE)
    department = models.CharField(max_length=100 , choices=DEPARTMENT_CHOICES , null=True , blank=True)
    target_role = models.CharField(max_length=20 , choices=ROLE_CHOICES , null=True , blank=True)
    semester = models.CharField(max_length=20 , null=True , blank=True)
    is_public = models.BooleanField(default=True)
    poster = models.FileField(upload_to='events/', blank=True , null=True)
    status = models.CharField(max_length = 20 , choices = STATUS_CHOICES , default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

class EventRegistration(models.Model):
    event = models.ForeignKey(Event , on_delete=models.CASCADE)
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)    

    class Meta:
        unique_together = ['event','user']    