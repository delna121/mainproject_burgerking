import django_filters
from .models import *
from django_filters import DateFilter


class OrderplacedFilter(django_filters.FilterSet):
    class Meta:
        model = OrderPlaced
        fields = '__all__'
        exclude=['quantity','ordered_date','payment','delivery_boy','is_assigned']
