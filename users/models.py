from django.contrib.auth.models import AbstractUser, Group
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
        message="Номер телефона должен быть введен в формате: '+999999999'. Допускается до 14 цифр."
    )
    phone = models.CharField(
        _("Номер телефона"),
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
        # Убедитесь, что номер телефона начинается с '+'
        if self.phone and not self.phone.startswith('+'):
            self.phone = '+' + self.phone

        creating = not self.pk
        super().save(*args, **kwargs)

        if creating:
            # Добавьте пользователя в соответствующую группу в зависимости от user_type
            if self.user_type == 1:
                group_name = 'Клиент'
            elif self.user_type == 2:
                group_name = 'Продавец'
            else:
                return

            group, created = Group.objects.get_or_create(name=group_name)
            self.groups.add(group)
