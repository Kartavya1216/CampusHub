from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date
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
def student_dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Student':
        return redirect(redirect_to_dashboard(request.user))

    return render(request, 'dashboard/student/dashboard.html')

@login_required
def room_booking_select_building(request):
    buildings = Building.objects.all()
    building_id = request.GET.get("building")

    floors = None
    selected_building = None

    if building_id:
        selected_building = Building.objects.get(id=building_id)
        floors = selected_building.floors.order_by('-floor_number')

    return render(
        request,
        "dashboard/student/select_building.html",
        {
            "buildings": buildings,
            "floors": floors,
            "selected_building": selected_building,
        }
    )

def room_booking_submit(request):
    if request.method !="POST":
        return render('roomBook')
    selected_rooms_raw = request.POST.get("selected_rooms", "")
    selected_rooms = selected_rooms_raw.split(",") if selected_rooms_raw else []

    date1 = request.POST.get('date')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')
    reason = request.POST.get('reason')

    if len(selected_rooms)==0 :
        messages.error(request,'Please select atleast one room')
        return redirect('roomBook')
    if not date1 or not start_time or not end_time or not reason:
        messages.error(request,'Please all the required fields')
        return redirect('roomBook')    
    if date1 < str(date.today()):
        messages.error(request,'Booking date cannot be date that is gone. ')
        return redirect('roomBook')
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
            return redirect("room_booking")

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
    return redirect("dashboard") 

@login_required
def notices_view(request):
    hidden_notice_ids = UserNoticeStatus.objects.filter(user=request.user ,cleared=True).values_list('notice_id',flat=True)
    notices = Notice.objects.filter(
        is_active=True
    ).exclude(id__in=hidden_notice_ids).order_by('-created_at')

    return render(request, 'dashboard/student/notices.html', {
        'notices': notices
    })


@login_required
def study_material_view(request):
    profile = UserProfile.objects.get(user=request.user)
    department = profile.department

    semesters = Semester.objects.filter(department=department).order_by("semester_number")

    selected_semester = None
    subjects = None
    semester_id = request.GET.get("semester")

    if semester_id:
        try:
            selected_semester = Semester.objects.get(id=semester_id, department=department)
        except Semester.DoesNotExist:
            raise Http404("Semester not found for your department.")

        subjects = selected_semester.subjects.all().order_by("name")

    selected_subject = None
    materials = None
    subject_id = request.GET.get("subject")

    if subject_id:
        try:
            selected_subject = Subject.objects.get(id=subject_id, semester__department=department)
        except Subject.DoesNotExist:
            raise Http404("Subject not found for your department.")

        materials = selected_subject.materials.all().order_by("-id")

    context = {
        "department": department,
        "semesters": semesters,
        "selected_semester": selected_semester,
        "subjects": subjects,
        "selected_subject": selected_subject,
        "materials": materials,
    }
    return render(request, "dashboard/student/study_material.html", context)
@login_required
def subject_materials_view(request, subject_id):
    profile = UserProfile.objects.get(user=request.user)

    subject = get_object_or_404(
        Subject,
        id=subject_id,
        semester__department=profile.department
    )

    materials = subject.materials.all().order_by('-id')

    return render(
        request,
        'dashboard/student/subject_materials.html',
        {
            'subject': subject,
            'materials': materials
        }
    )


@login_required
def events_view(request):
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

    return render(request, 'dashboard/student/event_Page.html', context)
@login_required
def add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.status = 'Pending'
            event.save()
            messages.success(request, 'Event request submitted. Awaiting approval.')
            return redirect('events')
    else:
        form = EventForm()

    return render(request, 'dashboard/student/add_event.html', {'form': form})

@login_required
def register_event(request , event_id):
    event = get_object_or_404(Event , id=event_id)
    if event.status != "Approved":
        messages.error(request , 'This event is not approved yet')
        return redirect('events')
    if event.date < date.today():
        messages.error(request , 'You cannot register for past events')
        return redirect('events')
    already_registered = EventRegistration.objects.filter(
        event=event,
        user=request.user
    )
    if already_registered:
        messages.warning(request,'You are already registered for this event')
        return redirect('events')
    else:
        EventRegistration.objects.create(
            event=event,
            user=request.user
        )
        messages.success(request,'You are successfully registered for this event.')
        return redirect('events')
    
@login_required
def unregister_event(request,event_id):
    event = get_object_or_404(Event , id=event_id)
    registration = EventRegistration.objects.filter(
        event=event,
        user=request.user
    ).first()

    if not registration:
        messages.error(request, "You are not registered for this event.")
        return redirect('events')

    if event.date < date.today():
        messages.error(request, "You cannot unregister from past events.")
        return redirect('events')

    registration.delete()
    messages.success(request, "You have been unregistered from the event.")
    return redirect('events')    

@login_required
def clear_student_notices(request):
    if request.method == 'POST':
        notices = Notice.objects.filter(is_active=True)
        for notice in notices:
            UserNoticeStatus.objects.get_or_create(user=request.user , notice=notice , defaults={'cleared':True})

        messages.success(request , 'Your Inbox has been cleared')

    return redirect('notices')        