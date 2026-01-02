from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'date',
            'start_time',
            'end_time',
            'department',
            'target_role',
            'semester',
            'poster',
        ]

        widgets = {
            'date' : forms.DateInput(attrs={'type':'date'}),
            'start_time' : forms.TimeInput(attrs={'type':'time'}),
            'end_time' : forms.TimeInput(attrs={'type':'time'})

        }