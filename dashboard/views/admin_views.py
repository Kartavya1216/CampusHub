from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import UserProfile
from django.contrib.auth.models import User
from .auth_views import redirect_to_dashboard
from django.contrib import messages
from rooms.models import RoomBooking
from notices.models import Notice
from events.models import Event
from events.forms import EventForm
from django.utils import timezone
from datetime import timedelta, date
from django.db.models import Q


@login_required
def admin_dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))

    return render(request, 'dashboard/admin/dashboard.html')
@login_required
def manage_users(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))
    user = User.objects.select_related('userprofile').all()
    return render(request,'dashboard/admin/manage_user.html',{'users':user})

@login_required
def edit_user(request, user_id):
    admin_profile = UserProfile.objects.get(user=request.user)
    if admin_profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))

    user = get_object_or_404(User, id=user_id)
    profile = user.userprofile
    if user.id == request.user.id:
        messages.error(request, "You cannot edit your own account.")
        return redirect('manage_users')

    if request.method == 'POST':
        profile.role = request.POST.get('role')
        profile.department = request.POST.get('department') or None
        user.is_active = request.POST.get('is_active') == 'on'

        profile.save()
        user.save()

        messages.success(request, "User updated successfully.")
        return redirect('manage_users')

    context = {
        'user_obj': user,
        'roles': UserProfile.ROLE_CHOICES,
        'departments': UserProfile.DEPARTMENT_CHOICES
    }

    return render(request, 'dashboard/admin/edit_user.html', context)

@login_required
def approve_rooms(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role!='Admin':
        return redirect(redirect_to_dashboard(request.user))
    bookings = RoomBooking.objects.filter(status='Pending').order_by('date','start_time')
    return render(request,'dashboard/admin/approve_rooms.html',{'bookings':bookings})

@login_required
def handle_room_booking(request, booking_id, action):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))

    booking = get_object_or_404(RoomBooking, id=booking_id)

    if booking.status != 'Pending':
        messages.warning(request, "This request has already been processed.")
        return redirect('approve_rooms')

    if action == 'approve':
        booking.status = 'Approved'
        Notice.objects.create(
            title='Room Booking Approved',
            posted_by = request.user,
            content=(
                f"Your booking for room {booking.room} "
                f"on {booking.date} from {booking.start_time} "
                f"to {booking.end_time} has been approved."
            ),
            expires_at = timezone.now() + timedelta(hours=24)
        )
        messages.success(request, 'Room booking approved.')

    elif action == 'reject':
        booking.status = 'Rejected'
        messages.success(request, 'Room booking rejected.')

    else:
        messages.error(request, 'Invalid action.')
        return redirect('approve_rooms')

    booking.save()
    return redirect('approve_rooms')

@login_required
def approve_events(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))
    events = Event.objects.filter(status='Pending').order_by('date','start_time')
    return render(request,'dashboard/admin/approve_events.html',{'events':events})

@login_required
def handle_event_approval(request, event_id , action):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))
    event = get_object_or_404(Event , id=event_id)

    if event.status != 'Pending':
        messages.warning(request , 'This event has already been proccessed !!')
        return redirect('approve_events')
    if action == 'approve' :
        event.status = 'Approved'
        Notice.objects.create(
            title=f"New Event Approved: {event.title}",
            posted_by=request.user,
            content=(
                f"The event '{event.title}' has been approved and will take place on "
                f"{event.date} from {event.start_time} to {event.end_time}.\n\n"
                f"Description: {event.description}"
            ),
            expires_at=timezone.now() + timedelta(hours=24)
        )
        messages.success(request , 'Event Approved')
    elif action == 'reject' :
        event.status = 'Rejected'
        messages.success(request , 'Event Rejected')
    else:
        messages.error(request, 'Invalid action.')
        return redirect('approve_events')     
    event.save()
    return redirect('approve_events')
@login_required
def events_view(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))
    search_query = request.GET.get('search', '').strip()

    events = Event.objects.filter(status='Approved', date__gte=date.today())

    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )


    return render(
        request,
        'dashboard/admin/event_Page.html',
        {
            'events': events,
            'search_query': search_query
        }
    )

@login_required
def add_event(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            if profile.role == 'Admin':
                event.status = "Approved"
                messages.success(request, 'Event created and published successfully.')

            else:    
                event.status = 'Pending'
                messages.success(request, 'Event request submitted. Awaiting approval.')
            event.save()
            return redirect('events')
    else:
        form = EventForm()

    return render(request, 'dashboard/admin/add_event.html', {'form': form})

@login_required
def admin_notices(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))

    search_query = request.GET.get('search', '').strip()

    notices = Notice.objects.all()

    if search_query:
        notices = notices.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(posted_by__username__icontains=search_query)
        )

    notices = notices.order_by('-created_at')

    return render(
        request,
        'dashboard/admin/notices.html',
        {
            'notices': notices,
            'search_query': search_query
        }
    )


@login_required
def bulk_delete_notices(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))

    if request.method == 'POST':
        ids = request.POST.getlist('notice_ids')
        Notice.objects.filter(id__in=ids).delete()
        messages.success(request, 'Selected notices deleted.')

    return redirect('admin_notices')

@login_required
def create_notice(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        attachment = request.FILES.get('attachment')

        if not title or not content:
            messages.error(request, 'Title and content are required.')
            return redirect('create_notice')

        Notice.objects.create(
            title=title,
            content=content,
            attachment=attachment,
            posted_by=request.user
        )

        messages.success(request, 'Notice published successfully.')
        return redirect('admin_notices')

    return render(request, 'dashboard/admin/create_notice.html')
