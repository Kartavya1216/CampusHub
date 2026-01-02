from django.contrib import admin
from .models import Semester , Subject , StudyMaterial
# Register your models here.
class SubjectInline(admin.TabularInline):
    model = Subject
    extra = 1

class StudyMaterialInline(admin.TabularInline):
    model = StudyMaterial
    extra = 1

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('department','semester_number')
    list_filter = ('department',)
    inlines = [SubjectInline]

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name','semester')
    list_filter = ('semester',)
    inlines = [StudyMaterialInline]

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title','subject')
    list_filter = ('subject',)
