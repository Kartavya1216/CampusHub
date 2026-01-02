from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Maintenance(models.Model):
    STATUS = [
        ('Pending','Pending'),
        ('Approved','Approved'),
        ('Rejected','Rejected')
    ]
    created_by = models.ForeignKey(User , on_delete=models.CASCADE)
    cateogry = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20 , choices=STATUS , default='Pending')
    assigned_to = models.ForeignKey(User , on_delete=models.SET_NULL ,related_name='assigned_staff' ,  null=True , blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)