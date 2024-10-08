import django_filters
from django_filters import DateFilter

from marine.sale.models import Sale


class BillFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name="date", lookup_expr="gte")
    end_date = DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Sale
        fields = {}
