from django.contrib import admin
from .models import Building , Floor , Room , RoomBooking
# Register your models here.
class FloorInline(admin.TabularInline):
    model = Floor
    extra = 1

class RoomInline(admin.TabularInline):
    model = Room
    extra = 1 

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [FloorInline]

@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ('building','floor_number','floor_name')
    inlines = [RoomInline]

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number','floor','type','capacity')
    list_filter = ('floor__building','floor__floor_number','type')

@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
        list_display = ('room','registered_by','date','start_time','end_time','status')
        list_filter = ('status','date','room__floor__building')               