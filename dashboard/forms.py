from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from users.models import UserProfile
from django.core.exceptions import ValidationError

ROLE_CHOICE = UserProfile.ROLE_CHOICES
DEPARTMENT_CHOICE = UserProfile.DEPARTMENT_CHOICES
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True , help_text = "Required. Enter the user email !!!")
    role = forms.ChoiceField(required=True , choices=ROLE_CHOICE)
    department = forms.ChoiceField(required=True , choices=DEPARTMENT_CHOICE)
    phone = forms.CharField(max_length=10 , required=True)

    semester = forms.CharField(required=False)
    enrollment = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('username','email','password1','password2','role','department','semester','enrollment','phone')

    def clean(self):
        cleaned_data = super().clean()
        email = self.cleaned_data.get('email') 
        role = self.cleaned_data.get('role')
        semester = self.cleaned_data.get('semester')
        enrollment = self.cleaned_data.get('enrollment')    

        if User.objects.filter(email__iexact = email).exists():
            raise ValidationError('Entered User email already exists')
        if role == 'Student':
            if not semester:
                self.add_error('semester','Semester is required for student')
            if not enrollment:
                self.add_error('enrollment','Enrollment is required for student')
        if role == 'Faculty':
            if not semester:
                self.add_error('semester','Semester is required for student')              
        return cleaned_data 

    def save(self , commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()

            role = self.cleaned_data.get('role')
            department = self.cleaned_data.get('department')
            phone = self.cleaned_data.get('phone')
            semester = self.cleaned_data.get('semester')
            enrollment = self.cleaned_data.get('enrollment')
            UserProfile.objects.create(
                user=user,
                role=role,
                department=department,
                semester=semester,
                enrollment=enrollment,
                phone=phone
            ) 
        return user          