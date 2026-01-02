from django.shortcuts import render , redirect
from django.contrib import messages
from .forms import RegistrationForm
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from users.models import UserProfile
from rooms.models import Building, Floor, Room, RoomBooking
from notes.models import Semester , Subject , StudyMaterial
from notices.models import Notice
from events.models import Event , EventRegistration
from datetime import  date
from django.http import Http404
from django.db.models import Q
from events.forms import EventForm

def landingPage(request):
    return render(request , 'dashboard/landingPage.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request,'Account Created Successfully...Redirecting to login page')
            return redirect('login')
        else:
            pass  
    else:
        form = RegistrationForm()
    return render(request,'dashboard/authentication/registration.html',{'form':form})          

def login_def(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            messages.error(request,'No user found for this email')
            return render(request,'dashboard/authentication/login.html')
        user = authenticate(request, username=user_obj.username , password=password)    
        if user is not None:
            login(request,user)
            messages.success(request,'login Successful...Redirecting to Dashboard')
            dashboard_url = redirect_to_dashboard(user)
            return redirect(dashboard_url)
        else:
            messages.error(request,'Incorrect Password')
    return render(request,'dashboard/authentication/login.html')

def redirect_to_dashboard(user):
    profile = UserProfile.objects.get(user=user)

    if profile.role == 'Admin':
        return 'admin_dashboard'
    elif profile.role == 'Faculty':
        return 'faculty_dashboard'
    elif profile.role == 'Staff':
        return 'staff_dashboard'
    else:
        return 'student_dashboard'


@login_required
def student_dashboard(request):
    return render(request, 'dashboard/student/dashboard.html')

@login_required
def faculty_dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Faculty':
        return redirect(redirect_to_dashboard(request.user))

    return render(request, 'dashboard/faculty/dashboard.html')


@login_required
def staff_dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Staff':
        return redirect(redirect_to_dashboard(request.user))

    return render(request, 'dashboard/staff/dashboard.html')


@login_required
def admin_dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'Admin':
        return redirect(redirect_to_dashboard(request.user))

    return render(request, 'dashboard/admin/dashboard.html')


def room_booking_select_building(request):
    buildings = Building.objects.all()
    building_id = request.GET.get("building")

    floors = None
    selected_building = None

    if building_id:
        selected_building = Building.objects.get(id=building_id)
        floors = selected_building.floors.order_by('-floor_number')

    context = {
        "buildings": buildings,
        "floors": floors,
        "selected_building": selected_building,
    }

    return render(request, "dashboard/student/select_building.html", context) 

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
def notices_view(request):
    notices = Notice.objects.filter(
        is_active=True
    ).order_by('-created_at')

    return render(request, 'dashboard/student/notices.html', {
        'notices': notices
    })



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

  
    visible_events = []

    for event in events:
        if event.target_role and event.target_role != profile.role:
            continue

        visible_events.append(event)

    context = {
        'events': visible_events,
        'search_query': search_query
    }

    return render(request, 'dashboard/student/event_Page.html', context)

@login_required
def add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST , request.FILES)
        if form.is_valid():
            event = form.save(commit = False)
            event.created_by = request.user
            event.status = 'Pending'
            event.save()
            messages.success(request,'Event request submitted successfully. Awaiting approval.')
            return redirect('events')
    else:
        form = EventForm()

    return render(request, 'dashboard/student/add_event.html', {'form': form})    

def logout_def(request):
    logout(request)
    messages.success(request,'logout successfull')
    return redirect('landingPage')