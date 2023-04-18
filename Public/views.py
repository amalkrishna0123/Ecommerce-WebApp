from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import Product
from django.contrib.messages import constants as messages
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
import razorpay
from django.conf import settings
from .models import Order
from .models import OrderItem
from django.views.decorators.csrf import csrf_exempt


client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
def Index(request):
    return render(request,"index.html")

def Product1(request):
    return render(request,"product.html")

def About(request):
    return render(request,"about.html")

def Contact(request):
    return render(request,"contact.html") 

def Diamond(request):
    product = Product.objects.all()

    context = {
        "product" : product
    }
    return render(request,"diamond.html",context)

def Gold(request):
    return render(request,"gold.html")

def Silver(request):
    return render(request,"silver.html")

def MensDress(request):
    return render(request,"mensdress.html")

def WomensDress(request):
    return render(request,"womensdress.html")

def KidsDress(request):
    return render(request,"kidsdress.html")

def MensAccessories(request):
    return render(request,"mensacces.html")

def WomensAccessories(request):
    return render(request,"womensacces.html")

def KidsAccessories(request):
    return render(request,"kidsacces.html")

def Bride(request):
    return render(request,"bride.html")

def Groom(request):
    return render(request,"groom.html")

def ProductView(request,pk):
    productview = Product.objects.filter(unique_id = pk)

    context = {
        "productview" : productview
    }
    return render(request,"productview.html",context)


def SEARCH(request):
    query = request.GET.get('query')
    product = Product.objects.filter(name__icontains = query)

    context = {
        "product" : product 
    }
    return render(request,"search.html",context)


def Register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        customer = User.objects.create_user(username,email,pass1)
        customer.first_name = first_name
        customer.last_name = last_name
        customer.save()
        return redirect('Index')
    return render(request,"register.html")


def Login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username = username, password = password)
        if user is not None:
            login(request,user)
            return redirect('Index')
        else:
            return redirect('Login')

    return render(request,'login.html')

def Logout(request):
    logout(request)
    return render(request,"index.html")

#cart
@login_required(login_url="/Login")
def cart_add(request, id):
    cart = Cart(request)
    product = Product.objects.get(unique_id=id)
    cart.add(product=product)
    return redirect("Product1")


@login_required(login_url="/Login")
def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(unique_id=id)
    cart.remove(product)
    return redirect("cart_detail")


@login_required(login_url="/Login")
def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(unique_id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="/Login")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(unique_id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")


@login_required(login_url="/Login")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


@login_required(login_url="/Login")
def cart_detail(request):
    return render(request, 'cart.html')

def checkout(request):
    payment = client.order.create({
        "amount" :500,
        "currency" :"INR",
        "payment_capture" : "1"
        })
    order_id = payment['id']
    context = {
        'order_id' : order_id,
        'payment' : payment
    }
    return render(request,"checkout.html",context)


def PlaceOrder(request):
    if request.method == "POST":
        uid = request.session.get('_auth_user_id')
        user = User.objects.get(id = uid)
        cart = request.session.get('cart')
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        country = request.POST.get("country")
        address = request.POST.get("address")
        state = request.POST.get("state")
        postcode = request.POST.get("postcode")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        amount = request.POST.get("amount")

        order_id = request.POST.get('order_id')
        context = {
            'order_id' : order_id
        }
        payment = request.POST.get('payment')

        order = Order(
            user = user,
            firstname = firstname,
            lastname = lastname,
            country = country,
            address = address,
            state = state,
            postcode = postcode,
            phone = phone,
            email = email,
            payment_id = order_id,
            amount = amount
        )
        order.save()
        for i in cart:

            a = (int(cart[i]['price']))
            b = cart[i]['quantity']
            total = a* b 
            item = OrderItem(
                order = order,
                product = cart[i]['name'],
                image = cart[i]['image'],
                quantity = cart[i]['quantity'],
                price = cart[i]['price'],
                total = total
            )
            item.save()

    return render(request,"placeorder.html",context)

@csrf_exempt
def Success(request):
    if request.method == 'POST':
        a = request.POST
        order_id = ""
        for key, val in a.items():
            if key == 'razorpay_order_id':
                order_id = val
                break

        user = Order.objects.filter(payment_id = order_id).first()
        user.paid = True
        user.save()
    return render(request,'thankyou.html')

