from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Faculty', 'Faculty'),
        ('Student', 'Student'),
        ('Staff', 'Staff'),
    ]

    DEPARTMENT_CHOICES = [
        ('Computer Science', 'Computer Science'),
        ('Information Technology', 'Information Technology'),
        ('Electronics', 'Electronics'),
        ('Mechanical', 'Mechanical'),
        ('Civil', 'Civil'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    department = models.CharField(
        max_length=100,
        choices=DEPARTMENT_CHOICES,
        null=True,
        blank=True
    )

    semester = models.CharField(max_length=15, null=True, blank=True)
    enrollment = models.CharField(max_length=20, null=True, blank=True)

    phone = models.CharField(max_length=15 , null=True, blank=True)
    is_campus_setup_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
