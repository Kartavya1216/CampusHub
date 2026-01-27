from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import UserProfile
from django.contrib.auth.models import User
from .auth_views import redirect_to_dashboard
from django.contrib import messages
from rooms.models import RoomBooking , Floor , Room , Building
from notices.models import Notice
from events.models import Event
from notes.models import Semester , Subject
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
def admin_campus_setup(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))
    if profile.is_campus_setup_completed:
        return redirect('admin_dashboard')    
    return render(request, 'dashboard/admin/campus_setup/start.html')

@login_required
def admin_setup_buildings(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))

    buildings = Building.objects.all()

    if request.method == "POST":
        name = request.POST.get('name')
        if name:
            Building.objects.create(name=name)
            messages.success(request, "Building added successfully.")

    return render(
        request,
        'dashboard/admin/campus_setup/buildings.html',
        {'buildings': buildings}
    )

@login_required
def admin_setup_floors(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))

    buildings = Building.objects.all()
    floors = Floor.objects.select_related('building').order_by('building', 'floor_number')

    if request.method == "POST":
        building_id = request.POST.get('building')
        floor_number = request.POST.get('floor_number')
        floor_name = request.POST.get('floor_name')

        if building_id and floor_number:
            Floor.objects.create(
                building_id=building_id,
                floor_number=floor_number,
                floor_name=floor_name
            )
            messages.success(request, "Floor added successfully.")
            return redirect('admin_setup_floors')

    return render(
        request,
        'dashboard/admin/campus_setup/floors.html',
        {
            'buildings': buildings,
            'floors': floors
        }
    )

@login_required
def admin_setup_rooms(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))

    buildings = Building.objects.all()
    floors = Floor.objects.select_related('building')
    rooms = Room.objects.select_related('floor__building').order_by(
        'floor__building__name',
        'floor__floor_number',
        'room_number'
    )

    if request.method == "POST":
        floor_id = request.POST.get('floor')
        room_number = request.POST.get('room_number')
        room_type = request.POST.get('type')
        capacity = request.POST.get('capacity')

        if floor_id and room_number and room_type and capacity:
            try:
                Room.objects.create(
                    floor_id=floor_id,
                    room_number=room_number,
                    type=room_type,
                    capacity=capacity
                )
                messages.success(request, "Room added successfully.")
            except:
                messages.error(request, "Room already exists on this floor.")

        return redirect('admin_setup_rooms')

    return render(
        request,
        'dashboard/admin/campus_setup/rooms.html',
        {
            'buildings': buildings,
            'floors': floors,
            'rooms': rooms
        }
    )
@login_required
def admin_setup_academics(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))

    departments = UserProfile.DEPARTMENT_CHOICES
    semesters = Semester.objects.all().order_by('department', 'semester_number')

    if request.method == "POST":
        department = request.POST.get('department')
        total_semesters = int(request.POST.get('total_semesters', 0))

        for i in range(1, total_semesters + 1):
            Semester.objects.get_or_create(
                department=department,
                semester_number=i
            )

        messages.success(
            request,
            f"{total_semesters} semesters created for {department}."
        )
        return redirect('admin_setup_academics')

    return render(
        request,
        'dashboard/admin/campus_setup/academics.html',
        {
            'departments': departments,
            'semesters': semesters
        }
    )
@login_required
def admin_setup_subjects(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))

    semesters = Semester.objects.order_by('department', 'semester_number')
    subjects = Subject.objects.select_related('semester').order_by('semester__semester_number')

    if request.method == "POST":
        semester_id = request.POST.get('semester')
        subject_name = request.POST.get('name')

        if not semester_id or not subject_name:
            messages.error(request, "All fields are required.")
            return redirect('admin_setup_subjects')

        Subject.objects.create(
            semester_id=semester_id,
            name=subject_name
        )

        messages.success(request, "Subject added successfully.")
        return redirect('admin_setup_subjects')

    return render(
        request,
        'dashboard/admin/campus_setup/subjects.html',
        {
            'semesters': semesters,
            'subjects': subjects
        }
    )
@login_required
def complete_campus_setup(request):
    profile = UserProfile.objects.get(user=request.user)

    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))

    profile.is_campus_setup_completed = True
    profile.save()

    messages.success(request, "Campus setup completed successfully.")
    return redirect('admin_dashboard')


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
def admin_events_view(request):
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
def admin_add_event(request):
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
            return redirect('admin_events')
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
        expires_at_input = request.POST.get('expires_at')

        if not title or not content:
            messages.error(request, 'Title and content are required.')
            return redirect('create_notice')

        now = timezone.now()

        expires_at = now + timedelta(hours=24)

        if expires_at_input:
            try:
                expires_at = timezone.make_aware(
                    timezone.datetime.fromisoformat(expires_at_input)
                )
            except ValueError:
                messages.error(request, 'Invalid expiry date format.')
                return redirect('create_notice')

            if expires_at <= now:
                messages.error(
                    request,
                    'Expiry date must be later than the current time.'
                )
                return redirect('create_notice')

        Notice.objects.create(
            title=title,
            content=content,
            attachment=attachment,
            posted_by=request.user,
            expires_at=expires_at
        )

        messages.success(request, 'Notice published successfully.')
        return redirect('admin_notices')

    return render(request, 'dashboard/admin/create_notice.html')
