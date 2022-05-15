from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .manager import UserManager
from PIL import Image
from django.contrib.auth.validators import UnicodeUsernameValidator

GENDER_CHOICE = (('Male','Male'),('Female','Female'))

def upload_to(instance, filename):
    return 'owner_pics/{filename}'.format(filename=filename)

class User(AbstractUser):
    """CustomUser model."""
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },)
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]
    objects = UserManager()
    contact = models.CharField(validators = [RegexValidator(regex = r"^\+?1?\d{8,15}$")], max_length = 16)
    gender = models.CharField(choices=GENDER_CHOICE, max_length=34, default='Male')

    def __str__(self):
        return f'{self.email}'


class Photo(models.Model):
    title = models.CharField(max_length=5, default='photo')
    roi = models.ImageField(upload_to=upload_to)
    img = models.ImageField(upload_to=upload_to)

    def __str__(self):
        return f'{self.title}'


class VehicleOwner(models.Model):
    plate_number = models.CharField(max_length=20, null=False, blank=False)
    first_name = models.CharField(max_length=20, null=False, blank=False)
    last_name = models.CharField(max_length=20, null=False, blank=False)
    age = models.IntegerField()
    vehicle_model = models.CharField(max_length=20, null=False, blank=False)
    entered = models.DateTimeField(max_length=10, null=False, blank=False)
    avatar = models.ImageField(_('Image'), upload_to=upload_to, default='default.png')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()
        try:
            image = Image.open(self.avatar.path)
            if image.height > 300 or image.width > 300:
                image.thumbnail((150,150))
                image.save(self.avatar.path)   
        except:
            print("******Error in Processing images*******")
            return

    def __str__(self):
        return f'{self.plate_number}'


class ImageUpload(models.Model):
    avatar = models.ImageField(_('Image'), upload_to=upload_to, blank=True, max_length=100)