from django.db import models


# Create your models here.
class Order(models.Model):
    # Add your model here
    order_number = models.CharField(max_length=100, unique=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_number