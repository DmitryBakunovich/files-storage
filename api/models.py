import os
from shutil import move, Error as MoveError

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    path = models.CharField(max_length=400, null=False, default=None)

    def save(self, *args, **kwargs):
        self.path = os.path.join(settings.USERFILES_DIR, self.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Folder(models.Model):
    path = models.CharField(max_length=415, null=False, unique=True)
    name = models.CharField(max_length=40, null=False, default=None)
    created = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='children',
    )
    owner = models.ForeignKey(
        'api.CustomUser',
        on_delete=models.CASCADE,
        related_name='folders',
    )

    def create_folder(self):
        try:
            os.mkdir(self.path)
        except OSError:
            pass

    def move_folder(self):
        try:
            move(
                self.path,
                self.parent.path
            )
            self.path = os.path.join(
                self.parent.path,
                self.name
            )
        except MoveError:
            pass

    def save(self, *args, **kwargs):
        if not self.pk:
            self.path = self.owner.path if not self.parent else os.path.join(
                self.parent.path,
                self.name
            )
            self.create_folder()
        else:
            self.move_folder()
        super().save(*args, **kwargs)

    def remove_folder(self):
        try:
            os.rmdir(self.path)
        except OSError:
            pass

    def delete(self, using=None, keep_parents=False):
        self.remove_folder()
        super().delete()

    def __str__(self):
        return self.path


class File(models.Model):
    name = models.CharField(max_length=40, null=False, default=None)
    folder = models.ForeignKey(
        'api.Folder',
        null=False,
        on_delete=models.CASCADE,
        related_name='files'
    )
