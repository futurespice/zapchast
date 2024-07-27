from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'client'),
        (2, 'seller'),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,14}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 14 digits allowed."
    )
    phone = models.CharField(
        _("Phone number"),
        validators=[phone_regex],
        max_length=17,
        unique=True
    )
    reset_password_token = models.CharField(max_length=6, blank=True, null=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username', 'email']

    def __str__(self):
        return self.phone

    def save(self, *args, **kwargs):
        # Ensure the phone number starts with a '+'
        if self.phone and not self.phone.startswith('+'):
            self.phone = '+' + self.phone
        super().save(*args, **kwargs)