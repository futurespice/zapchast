from django.db import models
from users.models import CustomUser

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('order_status', 'Order Status'),
        ('new_product', 'New Product'),
        ('price_drop', 'Price Drop'),
        ('general', 'General Notification'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} notification for {self.user.username}"