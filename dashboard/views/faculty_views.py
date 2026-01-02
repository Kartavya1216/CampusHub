from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import UserProfile
from .auth_views import redirect_to_dashboard

@login_required
def faculty_dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Faculty':
        return redirect(redirect_to_dashboard(request.user))

    return render(request, 'dashboard/faculty/dashboard.html')
