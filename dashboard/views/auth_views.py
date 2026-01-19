from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from users.models import UserProfile
from dashboard.forms import RegistrationForm

def landingPage(request):
    return render(request, 'dashboard/landingPage.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account Created Successfully...Redirecting to login page')
            return redirect('login')
    else:
        form = RegistrationForm()

    return render(request, 'dashboard/authentication/registration.html', {'form': form})


def login_def(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            messages.error(request, 'No user found for this email')
            return render(request, 'dashboard/authentication/login.html')

        user = authenticate(request, username=user_obj.username, password=password)

        if user:
            login(request, user)
            return redirect(redirect_to_dashboard(user))

        messages.error(request, 'Incorrect Password')

    return render(request, 'dashboard/authentication/login.html')


def redirect_to_dashboard(user):
    profile = UserProfile.objects.get(user=user)

    if profile.role == 'Admin':
        if not profile.is_campus_setup_completed:
            return 'admin_campus_setup'
        return 'admin_dashboard'

    elif profile.role == 'Faculty':
        return 'faculty_dashboard'

    elif profile.role == 'Staff':
        return 'staff_dashboard'

    return 'student_dashboard'



def logout_def(request):
    logout(request)
    messages.success(request, 'Logout successful')
    return redirect('landingPage')
