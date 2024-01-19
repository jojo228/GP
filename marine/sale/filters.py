import django_filters
from django_filters import DateFilter
from django import forms

from marine.sale.models import Sale


class SaleFilter(django_filters.FilterSet):
    start_date = DateFilter(
        field_name="date_modified",
        lookup_expr="gte",
        label="Ventes effectuées entre le (ex: 2022-05-18)",
    )
    end_date = DateFilter(field_name="date_modified", lookup_expr="lte", label="et le")

    class Meta:
        model = Sale
        fields = (
            "added_by",
            "category",
        )

class CategorySaleFilter(django_filters.FilterSet):

    start_date = DateFilter(field_name ="sale__date_modified", lookup_expr="gte", label="Ventes effectuées entre le",widget=forms.DateInput(
            attrs={
                'type': 'date'
            }
        ))
    end_date = DateFilter(field_name ="sale__date_modified", lookup_expr="lt", label="et le", widget=forms.DateInput(
            attrs={
                'type': 'date'
            }
        ))