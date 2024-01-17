import datetime

import pandas as pd
from django.db.models import F
from marine.employee.models import Employee

from marine.product.models import Product, Warehouse
from marine.sale.billing.model import Billing
from marine.shop.models import Shop, Sold, Store

database = "db.sqlite3"


# for returning ip address
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# load data from database and convert into dataframe for pandas manipulation
def objects_to_df(model, fields=None, exclude=None, date_cols=None, **kwargs):
    """
    Return a pandas dataframe containing the records in a model
    ``fields`` is an optional list of field names. If provided, return only the
    named.
    ``exclude`` is an optional list of field names. If provided, exclude the
    named from the returned dict, even if they are listed in the ``fields``
    argument.
    ``date_cols`` chart.js doesn't currently handle dates very well so these
    columns need to be converted to a string. Pass in the strftime string
    that would work best as the first value followed by the column names.
    ex:  ['%Y-%month', 'dat_col1', 'date_col2']
    ``kwargs`` can be include to limit the model query to specific records
    """

    if not fields:
        fields = [field.name for field in model._meta.get_fields()]

    if exclude:
        fields = [field for field in fields if field not in exclude]
    records = model.objects.filter(**kwargs).values_list(*fields)
    df = pd.DataFrame(list(records), columns=fields)

    if date_cols:
        strftime = date_cols.pop(0)
        for date_col in date_cols:
            df[date_col] = df[date_col].apply(lambda x: x.strftime(strftime))

    return df


# load the PRODUCTs Data from excel into the db


# headers of the table
headers = [
    "designation",
    "prix_vente",
    "stock_alerte_magazin",
    "quantite_en_stock_magazin",
]


def product_loading(file):
    data_df = pd.detail_excel(file, sheet_name=0).fillna(0)
    data_df = data_df[headers]
    for _, row in data_df.iterrows():
        # check if a product exist
        product, _ = Product.objects.get_or_create(
            designation=row.designation,
        )
        product.unit_price = row.prix_vente

        # create or link warehouse information to product
        try:
            product.marine_warehouse_related.quantity = row.quantite_en_stock_magazin
            product.marine_warehouse_related.quantity_alert = row.stock_alerte_magazin
        except Warehouse.DoesNotExist:
            warehouse = Warehouse(
                product=product,
                quantity=row.quantite_en_stock_magazin,
                quantity_alert=row.stock_alerte_magazin,
            )
            warehouse.save()

        # link store and warehouse to product
        product.marine_warehouse_related.quantity_initial = (
            product.marine_warehouse_related.quantity
        )
        product.marine_warehouse_related.save()

        product.save()

        # loop the shops
        for shop in Shop.objects.all():
            # get or create a store instance
            Store.objects.get_or_create(product=product, shop=shop)
            # get or create a sold instance
            Sold.objects.get_or_create(product=product, shop=shop)
        msga = '<span style="color: green;">Chargement réussi</span>'
    return msga


def store_alert_function(shop):
    alert = False
    # retrieve shop
    products_under_alert = Product.objects.filter(
        marine_stores__quantity__lt=F("marine_stores__quantity_alert"),
        marine_stores__shop=shop,
    )
    if products_under_alert:
        alert = True
    return alert


def warehouse_alert_function():
    alert = False
    # retrieve shop
    products_under_alert = Product.objects.filter(
        marine_warehouses__quantity__lt=F("marine_warehouses__quantity_alert"),
    )
    if products_under_alert:
        alert = True
    return alert


def bill_alert_function():
    alert = False
    todays_date = datetime.date.today()
    # retrieve shop
    bills_under_alert = Billing.objects.filter(
        next_payment_date=todays_date,
    )
    if bills_under_alert:
        alert = True
    return alert


def salary_alert_function():
    alert = False
    todays_date = datetime.date.today().day
    employee_salary_date = Employee.objects.filter(salary_payment_date__day=todays_date)

    if employee_salary_date:
        alert = True
    return alert
