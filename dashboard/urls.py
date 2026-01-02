from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.landingPage , name='landingPage'),
    path('register/',views.register , name='register'),
    path('login/',views.login_def,name='login'),
    path('logout/',views.logout_def,name='logout'),
    path('dashboard/student/',views.student_dashboard ,name='student_dashboard'),
    path('dashboard/admin/',views.admin_dashboard ,name='admin_dashboard'),
    path('dashboard/faculty/',views.faculty_dashboard ,name='faculty_dashboard'),
    path('dashboard/staff/',views.staff_dashboard ,name='staff_dashboard'),
    path('dashboard/student/roomBook/',views.room_booking_select_building , name='roomBook'),
    path('dashboard/student/roomBook/submit-roomRequest/',views.room_booking_submit , name='room_booking_submit'),
    path('dashboard/student/study-material/', views.study_material_view , name='study_material'),
    path('dashboard/student/notices/', views.notices_view, name='notices'),
    path('dashboard/student/events/',views.events_view,name='events'),
    path('dashboard/student/events/add/', views.add_event, name='add_event'),
    path('dashboard/admin/users',views.manage_users , name='manage_users'),
    path('dashboard/admin/users/<int:user_id>/edit/',views.edit_user,name='edit_user'),
    path('dashboard/admin/rooms',views.approve_rooms , name='approve_rooms'),
    path('dashboard/admin/rooms/<int:booking_id>/<str:action>/',views.handle_room_booking,name='handle_room_booking'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)