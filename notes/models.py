from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from users.models import UserProfile


DEPARTMENT_CHOICES = UserProfile.DEPARTMENT_CHOICES
class Semester(models.Model):
    department = models.CharField(max_length = 100 , choices = DEPARTMENT_CHOICES)
    semester_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ['department','semester_number']
        ordering = ['semester_number']

    def __str__(self):
        return f"{self.department} - Semester {self.semester_number}"
    
class Subject(models.Model):
    semester = models.ForeignKey(Semester , on_delete=models.CASCADE , related_name = 'subjects')
    name = models.CharField(max_length = 100)

    def __str__(self):
        return f"Department {self.semester.department} - Semester {self.semester.semester_number} - {self.name}"

class StudyMaterial(models.Model):
    subject = models.ForeignKey(Subject , on_delete=models.CASCADE , related_name='materials')
    title = models.CharField(max_length = 100)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='study-material/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE , null=True , blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title        