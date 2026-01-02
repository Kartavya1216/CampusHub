from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Q
from django.http import Http404

from users.models import UserProfile
from rooms.models import Building, Room, RoomBooking
from notes.models import Semester, Subject
from notices.models import Notice
from events.models import Event
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
    notices = Notice.objects.filter(
        is_active=True
    ).order_by('-created_at')

    return render(request, 'dashboard/student/notices.html', {
        'notices': notices
    })


@login_required
def study_material_view(request):
    profile = UserProfile.objects.get(user=request.user)
    department = profile.department

    semesters = Semester.objects.filter(department=department).order_by("semester_number")
    semester_id = request.GET.get("semester")

    if semester_id:
        try:
            selected_semester = Semester.objects.get(id=semester_id, department=department)
        except Semester.DoesNotExist:
            raise Http404

        subjects = selected_semester.subjects.all()
    else:
        subjects = None
        selected_semester = None

    return render(
        request,
        "dashboard/student/study_material.html",
        {
            "semesters": semesters,
            "subjects": subjects,
            "selected_semester": selected_semester,
        }
    )

@login_required
def events_view(request):
    profile = UserProfile.objects.get(user=request.user)
    search_query = request.GET.get('search', '').strip()

    events = Event.objects.filter(status='Approved', date__gte=date.today())

    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    visible_events = [
        event for event in events
        if not event.target_role or event.target_role == profile.role
    ]

    return render(
        request,
        'dashboard/student/event_Page.html',
        {
            'events': visible_events,
            'search_query': search_query
        }
    )

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
