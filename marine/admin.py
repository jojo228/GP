from django.contrib import admin

from marine.computer.models import Computer
from marine.customer.models import Customer
from marine.employee.models import Employee
from marine.loading.models import Loading, LoadingItem
from marine.product.models import Product, Warehouse
from marine.sale.billing.model import Billing
from marine.sale.models import Sale, SaleItem
from marine.shop.models import Shop, Sold, Store
from marine.supplier.models import Supplier
from marine.supply.models import Supply, SupplyItem

admin.site.register(Billing)
admin.site.register(Computer)
admin.site.register(Customer)
admin.site.register(Employee)
admin.site.register(Loading)
admin.site.register(LoadingItem)
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(SaleItem)
admin.site.register(Shop)
admin.site.register(Sold)
admin.site.register(Store)
admin.site.register(Supplier)
admin.site.register(Supply)
admin.site.register(SupplyItem)
admin.site.register(Warehouse)
