from django.db import models
from django.contrib.auth.models import User

class Building(models.Model):
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name

class Floor(models.Model):
    building = models.ForeignKey(Building , on_delete=models.CASCADE , related_name='floors')
    floor_number = models.PositiveIntegerField()
    floor_name = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['building', 'floor_number']

    def __str__(self):
        label = self.floor_name or f'Floor {self.floor_number}'
        return f'{self.building.name} - {label}'

class Room(models.Model):
    ROOM_TYPE = [
        ('ClassRoom','ClassRoom'),
        ('Lab','Lab'),
        ('Conference','Conference')
    ]
    floor = models.ForeignKey(Floor , on_delete=models.CASCADE , related_name='rooms')
    room_number = models.CharField(max_length = 20)
    type = models.CharField(max_length = 20 , choices=ROOM_TYPE)
    capacity = models.IntegerField()

    class Meta:
        unique_together = ['floor','room_number']
        ordering = ['floor','room_number']

    def __str__(self):
            return f"{self.floor.building.name} | {self.floor.floor_name or 'Floor '+str(self.floor.floor_number)} | Room {self.room_number}"                


class RoomBooking(models.Model):
    STATUS = [
        ('Pending','Pending'),
        ('Approved','Approved'),
        ('Rejected','Rejected')
    ]
    room = models.ForeignKey(Room , on_delete=models.CASCADE)
    registered_by = models.ForeignKey(User , on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20,choices=STATUS , default='Pending')
    reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.room} | {self.date} | {self.registered_by.username} | {self.status}"