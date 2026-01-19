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
    path('dashboard/student/study_material/subject/<int:subject_id>' ,views.subject_materials_view , name="subject_materials" ),
    path('dashboard/student/notices/', views.notices_view, name='notices'),
    path('notices/read/<int:notice_id>/', views.mark_notice_read, name='mark_notice_read'),
    path('dashboard/student/notices/clear', views.clear_student_notices , name='clear_student_notices'),
    path('dashboard/student/events/',views.events_view,name='events'),
    path('dashboard/student/events/add/', views.add_event, name='add_event'),
    path('dashboard/student/events/<int:event_id>/register/',views.register_event,name='register_event'),
    path('dashboard/student/events/<int:event_id>/unregister/',views.unregister_event,name='unregister_event'),
    path('dashboard/admin/setup/', views.admin_campus_setup, name='admin_campus_setup'),
    path('dashboard/admin/setup/buildings', views.admin_setup_buildings, name='admin_setup_buildings'),
    path('dashboard/admin/setup/floors', views.admin_setup_floors, name='admin_setup_floors'),
    path('dashboard/admin/setup/rooms', views.admin_setup_rooms, name='admin_setup_rooms'),
    path('dashboard/admin/setup/academics', views.admin_setup_academics, name='admin_setup_academics'),    
    path('dashboard/admin/users',views.manage_users , name='manage_users'),
    path('dashboard/admin/users/<int:user_id>/edit/',views.edit_user,name='edit_user'),
    path('dashboard/admin/rooms',views.approve_rooms , name='approve_rooms'),
    path('dashboard/admin/rooms/<int:booking_id>/<str:action>/',views.handle_room_booking,name='handle_room_booking'),
    path('dashboard/admin/manage_events',views.approve_events , name='approve_events'),
    path('dashboard/admin/manage_events/<int:event_id>/<str:action>/',views.handle_event_approval,name='handle_event_approval'),
    path('dashboard/admin/events/',views.admin_events_view,name='admin_events'),
    path('dashboard/admin/events/add/', views.admin_add_event, name='admin_add_event'),
    path('dashboard/admin/notices/',views.admin_notices,name='admin_notices'),
    path('dashboard/admin/notices/bulk-delete/',views.bulk_delete_notices,name='bulk_delete_notices'),
    path('dashboard/admin/notices/create/',views.create_notice,name='create_notice'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)