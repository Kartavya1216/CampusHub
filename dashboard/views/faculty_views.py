from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date , timezone , datetime , timedelta
from django.db.models import Q
from django.http import Http404

from users.models import UserProfile
from rooms.models import Building, Room, RoomBooking
from notes.models import Semester, Subject , StudyMaterial
from notices.models import Notice , UserNoticeStatus
from events.models import Event , EventRegistration
from events.forms import EventForm
from .auth_views import redirect_to_dashboard

@login_required
def faculty_dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Faculty':
        return redirect(redirect_to_dashboard(request.user))

    return render(request, 'dashboard/faculty/dashboard.html',{'profile':profile})

@login_required
def faculty_room_booking_select_building(request):
    buildings = Building.objects.all()
    building_id = request.GET.get("building")

    floors = None
    selected_building = None

    if building_id:
        selected_building = Building.objects.get(id=building_id)
        floors = selected_building.floors.order_by('-floor_number')

    return render(
        request,
        "dashboard/faculty/faculty_select_building.html",
        {
            "buildings": buildings,
            "floors": floors,
            "selected_building": selected_building,
        }
    )

def faculty_room_booking_submit(request):
    if request.method !="POST":
        return render('faculty_roomBook')
    selected_rooms_raw = request.POST.get("selected_rooms", "")
    selected_rooms = selected_rooms_raw.split(",") if selected_rooms_raw else []

    date1 = request.POST.get('date')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')
    reason = request.POST.get('reason')

    if len(selected_rooms)==0 :
        messages.error(request,'Please select atleast one room')
        return redirect('faculty_roomBook')
    if not date1 or not start_time or not end_time or not reason:
        messages.error(request,'Please all the required fields')
        return redirect('faculty_roomBook')    
    booking_date = datetime.strptime(date1, "%Y-%m-%d").date()
    if booking_date < date.today():
        messages.error(request, "Booking date cannot be in the past.")
        return redirect('faculty_roomBook')
    for room_id in selected_rooms:
        room = Room.objects.get(id=room_id)

        conflict = RoomBooking.objects.filter(
            room=room,
            date=date1,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if conflict:
            messages.error(request, f"Room {room.room_number} is already booked for that time.")
            return redirect("faculty_room_booking")

    for room_id in selected_rooms:
        room = Room.objects.get(id=room_id)

        RoomBooking.objects.create(
            room=room,
            registered_by=request.user,
            date=date1,
            start_time=start_time,
            end_time=end_time,
            reason=reason,
            status="Pending"
        )

    messages.success(request, "Booking request submitted successfully!")
    return redirect("faculty_dashboard") 


@login_required
def faculty_room_booking_history(request):
    bookings = RoomBooking.objects.filter(
        registered_by=request.user
    ).order_by('-date', '-start_time')

    return render(
        request,
        'dashboard/faculty/faculty_room_booking_history.html',
        {'bookings': bookings}
    )
@login_required
def faculty_cancel_room_booking(request, booking_id):
    booking = get_object_or_404(
        RoomBooking,
        id=booking_id,
        registered_by=request.user,
        status='Pending'
    )

    booking.delete()
    messages.success(request, "Booking request cancelled successfully.")
    return redirect('faculty_room_booking_history')

@login_required
def faculty_events_view(request):
    profile = UserProfile.objects.get(user=request.user)

    search_query = request.GET.get('search', '').strip()

    events = Event.objects.filter(
        status='Approved',
        date__gte=date.today()
    )

    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    visible_events = [
        event for event in events
        if not event.target_role or event.target_role == profile.role
    ]
    registered_event_ids = set(
        EventRegistration.objects.filter(
            user=request.user
        ).values_list('event_id', flat=True)
    )

    context = {
        'events': visible_events,
        'search_query': search_query,
        'registered_event_ids': registered_event_ids,
    }

    return render(request, 'dashboard/faculty/faculty_event_Page.html', context)
@login_required
def faculty_add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.status = 'Pending'
            event.save()
            messages.success(request, 'Event request submitted. Awaiting approval.')
            return redirect('faculty_events')
    else:
        form = EventForm()

    return render(request, 'dashboard/faculty/faculty_add_event.html', {'form': form})

@login_required
def faculty_register_event(request , event_id):
    event = get_object_or_404(Event , id=event_id)
    if event.status != "Approved":
        messages.error(request , 'This event is not approved yet')
        return redirect('faculty_events')
    if event.date < date.today():
        messages.error(request , 'You cannot register for past events')
        return redirect('faculty_events')
    already_registered = EventRegistration.objects.filter(
        event=event,
        user=request.user
    )
    if already_registered:
        messages.warning(request,'You are already registered for this event')
        return redirect('faculty_events')
    else:
        EventRegistration.objects.create(
            event=event,
            user=request.user
        )
        messages.success(request,'You are successfully registered for this event.')
        return redirect('faculty_events')
    
@login_required
def faculty_unregister_event(request,event_id):
    event = get_object_or_404(Event , id=event_id)
    registration = EventRegistration.objects.filter(
        event=event,
        user=request.user
    ).first()

    if not registration:
        messages.error(request, "You are not registered for this event.")
        return redirect('faculty_events')

    if event.date < date.today():
        messages.error(request, "You cannot unregister from past events.")
        return redirect('faculty_events')

    registration.delete()
    messages.success(request, "You have been unregistered from the event.")
    return redirect('faculty_events')

@login_required
def faculty_notices_view(request):
    all_notices = Notice.objects.filter(is_active=True).filter(
                    Q(expires_at__isnull=True) |
                    Q(expires_at__gte=datetime.now())).order_by('-created_at')

    for notice in all_notices:
        UserNoticeStatus.objects.get_or_create(
            user=request.user,
            notice=notice
        )

    hidden_notice_ids = UserNoticeStatus.objects.filter(
        user=request.user,
        cleared=True
    ).values_list('notice_id', flat=True)

    statuses = UserNoticeStatus.objects.filter(
        user=request.user
    ).exclude(
        notice_id__in=hidden_notice_ids
    ).select_related('notice').order_by('-notice__created_at')

    return render(request, 'dashboard/faculty/faculty_notices.html', {
        'statuses': statuses
    })

@login_required
def faculty_mark_notice_read(request, notice_id):
    if request.method == "POST":
        status = get_object_or_404(
            UserNoticeStatus,
            user=request.user,
            notice_id=notice_id
        )
        if not status.is_read:
            status.is_read = True
            status.save()

    return redirect('faculty_notices')

@login_required
def faculty_clear_notices(request):
    if request.method == "POST":
        UserNoticeStatus.objects.filter(
            user=request.user,
            cleared=False
        ).update(cleared=True)

    return redirect('faculty_notices')

@login_required
def faculty_create_notice(request):
    profile = UserProfile.objects.get(user=request.user)

    if profile.role!='Faculty':
        return redirect(redirect_to_dashboard(request.user))

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        attachment = request.FILES.get('attachment')
        expires_at_raw = request.POST.get('expires_at')

        if not title or not content:
            messages.error(request, "Title and content are required.")
            return redirect('create_notice')

        if expires_at_raw:
            expires_at = timezone.make_aware(
                datetime.fromisoformat(expires_at_raw)
            )
            if expires_at <= timezone.now():
                messages.error(request, "Expiry must be in the future.")
                return redirect('create_notice')
        else:
            expires_at = timezone.now() + timedelta(hours=24)

        Notice.objects.create(
            title=title,
            content=content,
            attachment=attachment,
            posted_by=request.user,
            expires_at=expires_at
        )

        messages.success(request, "Notice published successfully.")
        return redirect('admin_notices' if profile.role == 'Admin' else 'notices')

    return render(request, 'dashboard/faculty/create_notice.html')

@login_required
def faculty_study_material_view(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Faculty':
        return redirect(redirect_to_dashboard(request.user))

    department = profile.department

    semesters = Semester.objects.filter(
        department=department
    ).order_by("semester_number")

    selected_semester = None
    subjects = None
    materials = None

    semester_id = request.GET.get("semester")
    subject_id = request.GET.get("subject")

    if semester_id:
        selected_semester = get_object_or_404(
            Semester,
            id=semester_id,
            department=department
        )
        subjects = selected_semester.subjects.all().order_by("name")

    if subject_id:
        subject = get_object_or_404(
            Subject,
            id=subject_id,
            semester__department=department
        )
        materials = subject.materials.all().order_by("-uploaded_at")

    return render(
        request,
        "dashboard/faculty/study_material.html",
        {
            "semesters": semesters,
            "subjects": subjects,
            "materials": materials,
            "selected_semester": selected_semester,
        }
    )


@login_required
def upload_study_material(request):
    profile = UserProfile.objects.get(user=request.user)

    if profile.role not in ['Faculty', 'Admin']:
        return redirect(redirect_to_dashboard(request.user))

    subjects = Subject.objects.all().order_by('name')

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        title = request.POST.get('title')
        description = request.POST.get('description')
        file = request.FILES.get('file')

        if not subject_id or not title or not file:
            messages.error(request, "All required fields must be filled.")
            return redirect('upload_material')

        subject = get_object_or_404(Subject, id=subject_id)

        StudyMaterial.objects.create(
            subject=subject,
            title=title,
            description=description,
            file=file,
            uploaded_by=request.user
        )

        messages.success(request, "Study material uploaded successfully.")
        return redirect('upload_material')

    return render(
        request,
        'dashboard/faculty/upload_material.html',
        {'subjects': subjects}
    )
