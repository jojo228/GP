from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import deletion
from django.http.response import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    DeleteView,
)

from marine.sale.models import Sale


class SaleDeleteView(LoginRequiredMixin, DeleteView):
    model = Sale
    success_url = reverse_lazy("list_sale")
    template_name = "marine/sale/sale_confirm_delete.html"

    def delete(self, *args, **kwargs):
        try:
            return super(SaleDeleteView, self).delete(*args, **kwargs)
        except deletion.ProtectedError:
            return HttpResponse("oops")
