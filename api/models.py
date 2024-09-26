from django.db import models
from datetime import date
from django.contrib.auth.models import User


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This model won't create a database table


class Restaurant(TimestampedModel):
    name = models.CharField(max_length = 100)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Menu(TimestampedModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    items = models.TextField()

    class Meta:
        unique_together = ('restaurant', 'date')
        permissions = [
            ('get_current_day_menu', 'Can get menus of current day'),
            ('upload_menu', 'Can upload menu'),
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.date}'


class Employee(TimestampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100)
    position = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Vote(TimestampedModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    points = models.IntegerField() # 1-3

    class Meta:
        unique_together = ('employee', 'menu')
        permissions = [
            ('cast_vote', 'Can cast vote to menu for the current day'),
            ('get_my_vote', 'Can get the menu voted for the current day by the employee'),
            ('get_all_votes_results', 'Can get all menus voted by employees for the current day')
        ]
    def __str__(self):
        return f'{self.employee.user.username} voted for {self.menu.restaurant.name}'

