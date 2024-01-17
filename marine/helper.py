from django.contrib.auth.models import User
from .models import Vente, Produit


def setup_handling(request):
    current_order = get_current_user_order(request.user.username)

    return current_order


def get_current_user_order(username):
    """
    Gets the order for the current user.
    """

    usr = User.objects.get_by_natural_key(username)
    q = Vente.objects.filter(user=usr, done=False).order_by("-last_change")
    if q.count() >= 1:
        return q[0]
    else:
        return Vente.objects.create(user=usr)


def order_item_from_product(product, order):
    """
    Creates an Order-Item from a given Product,
    to be added to an Order.
    """

    return Produit.objects.create(
        product=product,
        order=order,
        price=product.price,
        quantity=product.quantity,
        name=product.name,
    )


def product_list_from_order(order):
    """
    Returns a list of Products that appear in an Order
    """

    product_list = []
    order_item_list = Produit.objects.filter(order=order)

    for order_item in order_item_list:
        product_list.append(order_item.product)

    return product_list


# function to create a new customer/supplier
def creater(form):
    if form.is_valid():
        form.save()


# function to create a new customer/supplier
def lister(form):
    if form.is_valid():
        form.save()
