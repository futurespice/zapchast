from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .utils import standardize_phone_number, is_valid_phone_number


class CustomUser(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
        blank=True,
        null=True
    )

    USER_TYPE_CHOICES = (
        (1, 'client'),
        (2, 'seller'),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1)

    phone = models.CharField(
        _("Номер телефона"),
        max_length=13,
        unique=True
    )
    is_phone_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    reset_password_token = models.CharField(max_length=6, blank=True, null=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.phone

    def clean(self):
        try:
            self.phone = standardize_phone_number(self.phone)
        except ValueError:
            raise ValidationError({'phone': 'Invalid phone number format'})

        if not is_valid_phone_number(self.phone):
            raise ValidationError({'phone': 'Invalid phone number'})

    def save(self, *args, **kwargs):
        self.clean()
        creating = not self.pk
        super().save(*args, **kwargs)

        if creating:
            if self.user_type == 1:
                group_name = 'Клиент'
            elif self.user_type == 2:
                group_name = 'Продавец'
            else:
                return

            group, created = Group.objects.get_or_create(name=group_name)
            self.groups.add(group)