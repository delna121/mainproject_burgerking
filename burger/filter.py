import django_filters
from .models import *
from django_filters import DateFilter


class OrderplacedFilter(django_filters.FilterSet):
    class Meta:
        model = OrderPlaced
        fields = ['user','order_number','status']
        exclude=['quantity','ordered_date','payment','delivery_boy','is_assigned']
