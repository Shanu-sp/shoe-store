from itertools import product
from multiprocessing.connection import address_type

from django.shortcuts import render,redirect,get_object_or_404
from .models import Product, OrderItem
from .models import Brand
import random
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import EmailOTP
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import logout
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Order



def home(request):
    q=request.GET.get('q')
    if q:
        products = Product.objects.filter(name__icontains=q)
    else:
        products = Product.objects.all()
    return render(request,'store/home.html',{'products':products})

def product_detail(request,pk):
    product = get_object_or_404(Product,pk=pk)
    return render(request,'store/detail.html',{'product':product})


def home(request):
    brands = Brand.objects.all()
    return render(request, 'store/home.html', {'brands': brands})

def brand_products(request, brand_id):
    brand = Brand.objects.get(id=brand_id)   # 👈 get selected brand
    products = Product.objects.filter(brand=brand)

    return render(
        request,
        'store/brand_products.html',
        {
            'products': products,
            'brand': brand   # 👈 send brand to template
        }
    )



def add_to_cart(request, pk):
    cart = request.session.get('cart', {})   # get cart or empty

    # if product already exists → increase quantity
    if str(pk) in cart:
        cart[str(pk)] += 1
    else:
        cart[str(pk)] = 1

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('home')


def cart_page(request):
    cart=request.session.get('cart',{})
    products = Product.objects.filter(id__in=cart.keys())
    return render(request,'store/cart.html',{'products':products,'cart':cart})


def place_order(request):
    request.session['cart'] = {}
    request.session.modified = True
    return render(request, 'store/order.html')


def signup(request):
    if request.method == 'POST':
        email=request.POST['email']

        # ✅ CHECK IF USER ALREADY EXISTS
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Account already exists. Please login.')
            return redirect('login')



        otp=str(random.randint(100000,999999))

        EmailOTP.objects.create(email=email,otp=otp)

        send_mail(
            'your Signup OTP',
            f'your OTP is{otp}',
            'shanusp17@gmail.com',
            [email],
        )
        request.session['signup_email']=email
        return redirect('verify_signup_otp')
    return render(request,'store/signup.html')


def verify_signup_otp(request):
    email = request.session.get('signup_email')

    if not email:
        messages.error(request, "Session expired. Please signup again.")
        return redirect('signup')

    if request.method == 'POST':
        otp = request.POST.get('otp')

        otp_obj = EmailOTP.objects.filter(email=email, otp=otp).first()

        if otp_obj:
            if otp_obj:
                # ⏱ OTP EXPIRY CHECK
                if timezone.now() - otp_obj.created_at > timedelta(minutes=5):
                    otp_obj.delete()
                    messages.error(request, "OTP expired. Please resend OTP.")
                    return redirect('verify_signup_otp')

            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(username=email, email=email)
                user.set_unusable_password()
                user.save()

            otp_obj.delete()
            del request.session['signup_email']
            messages.success(request, "Signup successful. Please login.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'store/verify_otp.html')



def login_request(request):
    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        email=request.POST['email']

        if not User.objects.filter(email=email).exists():
            return render(request,'store/login.html',{'error':'user not found'})

        otp=str(random.randint(10000,99999))
        EmailOTP.objects.create(email=email,otp=otp)

        send_mail(
            'your login OTP',
            f'your otp is {otp}',
            'shanusp17@gmail.com',
            [email],

        )
        request.session['login_email']=email
        request.session['next'] = next_url  # SAVE NEXT URL

        return redirect('verify_login_otp')
    return render(request,'store/login.html')



def verify_login_otp(request):
    email = request.session.get('login_email')

    # ✅ Safety check
    if not email:
        messages.error(request, "Session expired. Please login again.")
        return redirect('login')

    if request.method == 'POST':
        otp = request.POST.get('otp')

        otp_obj = EmailOTP.objects.filter(email=email, otp=otp).first()

        if otp_obj:
            # ⏱ OTP EXPIRY CHECK
            if timezone.now() - otp_obj.created_at > timedelta(minutes=5):
                otp_obj.delete()
                messages.error(request, "OTP expired. Please resend OTP.")
                return redirect('verify_login_otp')

            user = User.objects.get(email=email)
            login(request, user)

            # ✅ Cleanup
            otp_obj.delete()
            del request.session['login_email']

            next_url = request.session.get('next')
            if next_url:
                return redirect(next_url)

            messages.success(request, "Login successful")
            return redirect('home')
        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'store/verify_otp.html')



def logout_view(request):
    logout(request)
    return redirect('login')   # or 'login'


def resend_otp(request):
    email=request.session.get('signup_email') or request.session.get('login_email')

    if not email:
        messages.error(request,'Session expired,Please try again')
        return redirect('login')

    otp=str(random.randint(10000,99999))
    EmailOTP.objects.update_or_create(
        email=email,
        defaults={'otp':otp}

    )
    send_mail(
        'Your OTP ',
        f'Your otp is {otp} ',
        'shanualr20@gmail.com',
        [email],

    )
    messages.success(request,'New OTP send to your email')
    return redirect(request.META.get('HTTP_REFERER', 'login'))



def cart_view(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())

    total = 0
    for p in products:
        total += p.price * cart[str(p.id)]

    return render(request, 'store/cart.html', {
        'products': products,
        'cart': cart,
        'total': total
    })



@login_required(login_url='login')
def checkout(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())

    total = 0
    for p in products:
        total += p.price * cart[str(p.id)]

    if request.method == 'POST':
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        order = Order.objects.create(
            user=request.user,
            address=address,
            phone=phone,
            total_amount=total
        )

        for p in products:
            OrderItem.objects.create(
                order=order,
                product=p,
                price=p.price,
                quantity=cart[str(p.id)]
            )

        request.session['cart'] = {}
        return redirect('order_success')   # POST return

    # GET return
    return render(request, 'store/checkout.html', {
        'products': products,
        'total': total
    })



def order_success(request):
    return render(request,'store/order_success.html')







