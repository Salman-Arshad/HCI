from django.shortcuts import render
from .models import Product, Cart, Container, Category,singleImage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from newsletter.views import newsletter_signup_home
from django.db.models import Q
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.contrib.auth import login as auth_login
from user.models import User
# Create your views here.
import time


def get_product_count(request):
    try:
        if request.user.is_authenticated:
            mcart = Cart.objects.filter(user=request.user)
            if cart is not None:
                container = Container.objects.filter(cart=mcart[0])
                return len(container)
            return 0
        else:
            return 0
        return 0
    except:
        return 0


def category(request, cat):
    qs = Product.objects.filter(category__name=cat)
    count = len(qs)
    qsc = Category.objects.all()
    form = newsletter_signup_home(request)
    des = get_object_or_404(Category, name=cat)
    print(qsc)
    return render(request, "categories.html", {
        "qs": qs,
        "product_count": get_product_count(request),
        "qsc": qsc,
        "catName": cat,
        "des": des.description,
        "form": form,
        "count": count
    })


def homepage(request):
    qs = Product.objects.all()
    qsc = Category.objects.all()
    form = newsletter_signup_home(request)
    print("___________")
    print(request)
    return render(request, "index.html", {"form": form, "qs": qs, "product_count": get_product_count(request), "qsc": qsc})


def product(request, id):
    qsc = Category.objects.all()
    print('I am heeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrew')
    ProductObj = get_object_or_404(Product, pk=id)
    related_prods = Product.objects.filter(
        category=ProductObj.category).exclude(pk=id)[:4]
    zimages=singleImage.objects.filter(product=ProductObj)
    print(related_prods)
    print(zimages)
    return render(request, 'product.html', {"qsc": qsc, 'product': ProductObj, 'related': related_prods, "product_count": get_product_count(request),"zimages":zimages})


@login_required(login_url='/login')
def cart(request):
    qsc = Category.objects.all()
    if not request.user.is_authenticated:
        return redirect('/admin')
    else:
        mcart = Cart.objects.filter(user=request.user)
        if len(mcart) <= 0:
            return render(request, 'cart.html', {'container': None, 'cartPrice': None, "qsc": qsc, "product_count": get_product_count(request)})
        else:
            container = Container.objects.filter(cart=mcart[0])
            totalPrice = 0
            for i in container:
                totalPrice += i.product.price*i.quantity
            # print(container[0].product)
            return render(request, 'cart.html', {"qsc": qsc, 'container': container, 'cartPrice': totalPrice, "product_count": get_product_count(request)})


# @register.simple_tag()
# def multiply(qty, unit_price, *args, **kwargs):
#     # you would need to do any localization of the result here
#     return qty * unit_price

def updateCart(request):
    if request.method == 'POST':
        item_ids = request.POST.get('item_ids')
        quantity = request.POST.get('quantity')
        print(item_ids)
        print(quantity)
        for i in range(0, len(item_ids)):
            cart = Cart.objects.get(user=request.user)
            yproduct = Product.objects.get(pk=item_ids[0])
            container = Container.objects.get(product=yproduct, cart=cart)
            container.quantity = quantity[0]
            container.save()
    return HttpResponse("UPDATED")


def clearCart(request):
    mcart = get_object_or_404(Cart, user=request.user)
    Container.objects.filter(cart=mcart).delete()
    Cart.objects.filter(user=request.user).delete()
    print("clearCart")
    return HttpResponse("Sucessfully Cleared")


def addtocart(request, id, quantity):
    time.sleep(4)
    print(request.user)
    print("Asdasdsad", quantity)
    if request.user.is_authenticated:
        print("n000000")
        print(id)
        product = get_object_or_404(Product, pk=id)
        i_user = request.user
        cart, created = Cart.objects.get_or_create(user=i_user)
        container, created = Container.objects.get_or_create(
            product=product, cart=cart)
        container.product = product
        container.quantity = quantity
        container.save()
        cart.user = i_user
        cart.container.add(container)
        cart.save()
        return HttpResponse('update Cart')
    else:
        return HttpResponse('unauthenticated')


def query(request):
    query = request.GET['search']
    print(query)
    qset = Q()
    for term in query.split():
        qset |= Q(name__contains=term)
    products = Product.objects.filter(qset)
    print(products)
    return render(request, "search.html", {"search": query, "products": products, "product_count": get_product_count(request), "qsc": Category.objects.all()})


def allProducts(request):
    products = Product.objects.filter()
    return render(request, "allproducts.html", {"products": products, "product_count": get_product_count(request), "qsc": Category.objects.all(), "count": len(products)})


def login(request):
    r = False
    if "reg" in request.session:
        r = request.session["reg"]
    request.session["reg"] = False
    # if request.user.is_authenticated:
    #     return redirect("/")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(email=email, password=password)
        if(user):
            auth_login(request, user)
            if 'next' not in request.GET:
                next = '/'
            else:
                next = request.GET["next"]
            print(next)
            return redirect(next)
        else:
            return render(request, "login.html", {"alert": True})
    print(r)
    return render(request, "login.html", {"alert": False, "registered": r})


def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        pass1 = request.POST.get("password1")
        pass2 = request.POST.get("password2")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        address = request.POST.get("address")
        print(fname)
        try:
            obj = User.objects.get(email=email)
        except Exception as e:
            obj = None
            return render(request, "register.html",{error:True})
        if obj is None:
            if pass1 == pass2:
                user = User(email=email, firstName=fname,
                            lastName=lname, address=address)
                user.set_password(pass1)
                user.save()
                request.session['reg'] = True
                return redirect("/login")
            else:
                return render(request, "register.html",{"error":"Passswords donot match"})
        else:
            return render(request, "register.html",{"error":"Email address already exixts"})

    return render(request, "register.html")


def mlogout(request):
    logout(request)
    return redirect("/")


@login_required(login_url='/login')
def checkout(request):
    qsc = Category.objects.all()
    user = User.objects.get(pk=request.user.id)
    context = {
        "user": user
    }
    mcart = Cart.objects.filter(user=request.user)
    if len(mcart) <= 0:
        return render(request, 'cart.html', {'container': None, 'cartPrice': None, "qsc": qsc, "product_count": get_product_count(request)})
    else:
        container = Container.objects.filter(cart=mcart[0])
        totalPrice = 0
        for i in container:
            totalPrice += i.product.price*i.quantity
    return render(request, 'checkout.html', {"user": user, "qsc": qsc, 'container': container, 'cartPrice': totalPrice, "product_count": get_product_count(request)})

