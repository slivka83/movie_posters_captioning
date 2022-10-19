from django.db import models


# Create your models here.
class Users(models.Model):

    telegram_id = models.BigIntegerField(unique=True)
    user_name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.full_name


class UsersRequests(models.Model):
    user = models.ForeignKey('Users', on_delete=models.PROTECT)
    image = models.ImageField(upload_to='media/photo')
    response = models.CharField(max_length=1000)
    time_create = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Users request'
        verbose_name_plural = 'Users requests'
