from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Notice(models.Model):
    status = models.CharField(
        max_length=20,
        choices=[('Pending','Pending'), ('Approved','Approved'), ('Rejected','Rejected')],
        default='Pending'
    )
    title = models.CharField(max_length=200)
    posted_by = models.ForeignKey(User , on_delete=models.CASCADE)
    content = models.TextField()
    attachment = models.FileField(upload_to='notices/', blank=True , null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class UserNoticeStatus(models.Model):
    notice = models.ForeignKey(Notice , on_delete=models.CASCADE) 
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    cleared = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together=  ['user','notice']   

    def __str__(self):
        return f"{self.user.username} - {self.notice.title} - {'Read' if self.is_read else 'Unread'}"    