from itertools import product
from multiprocessing.connection import address_type

from django.shortcuts import render,redirect,get_object_or_404
from .models import Product, OrderItem
from .models import Brand
import random
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import EmailOTP
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth import logout
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Order
from django.db.models import Q



def home(request):
    brands = Brand.objects.all()
    return render(request, 'store/home.html', {'brands': brands})

def product_detail(request,pk):
    product = get_object_or_404(Product,pk=pk)
    return render(request,'store/detail.html',{'product':product})


def brand_products(request, brand_id):
    brand = Brand.objects.get(id=brand_id)   #  get selected brand
    products = Product.objects.filter(brand=brand)

    return render(
        request,
        'store/brand_products.html',
        {
            'products': products,
            'brand': brand   # send brand to template
        }
    )
    


def search(request):
    query = request.GET.get('q', '').strip()
    products = []

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query)
        )

    return render(request, 'store/search_results.html', {
        'query': query,
        'products': products
    })




def add_to_cart(request, pk):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})   # get cart or empty

        # if product already exists → increase quantity
        if str(pk) in cart:
            cart[str(pk)] += quantity
        else:
            cart[str(pk)] = quantity

        request.session['cart'] = cart
        request.session.modified = True
        return redirect('home')
    else:
        return redirect('detail', pk=pk)


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
       username=request.POST['username']
       email=request.POST['email']
       password = request.POST['password']
       confirm_password = request.POST['confirm_password']

       if password != confirm_password:
           messages.error(request, 'Passwords do not match.')
           return render(request,'store/signup.html')

       #  CHECK IF USER ALREADY EXISTS
       if User.objects.filter(username=username).exists():
           messages.error(request, 'Username already exists. Please choose another.')
           return render(request,'store/signup.html')

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
       request.session['signup_username']=username
       request.session['signup_email']=email
       request.session['signup_password']=password
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
                #  OTP EXPIRY CHECK
                if timezone.now() - otp_obj.created_at > timedelta(minutes=5):
                    otp_obj.delete()
                    messages.error(request, "OTP expired. Please resend OTP.")
                    return redirect('verify_signup_otp')

            if not User.objects.filter(email=email).exists():
                password = request.session.get('signup_password')
                username = request.session.get('signup_username')
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

            otp_obj.delete()
            del request.session['signup_username']
            del request.session['signup_email']
            del request.session['signup_password']
            messages.success(request, "Signup successful. Please login.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'store/verify_otp.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        # Check if user exists
        if not User.objects.filter(email=email).exists():
            messages.error(request, 'No account found with this email.')
            return render(request, 'store/forgot_password.html')

        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(
            email=email,
            defaults={'otp': otp}
        )

        send_mail(
            'Password Reset OTP',
            f'Your OTP for password reset is {otp}',
            'shanusp17@gmail.com',
            [email],
        )
        request.session['forgot_email'] = email
        return redirect('verify_forgot_otp')
    return render(request, 'store/forgot_password.html')



def reset_password(request):
    email = request.session.get('forgot_email')

    if not email:
        messages.error(request, "Session expired. Please try again.")
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'store/reset_password.html')

        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        del request.session['forgot_email']
        messages.success(request, "Password reset successful. Please login.")
        return redirect('login')

    return render(request, 'store/reset_password.html')



def login_request(request):
    
    next_url = request.GET.get('next') or request.POST.get('next')
    
    if request.method == 'POST':
        
        username= request.POST['username']
        password= request.POST['password']
        
        user=authenticate(request, username=username,password=password)
        
        if user is not None:
            login(request,user)
            messages.success(request,'Login successful')
            
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request,'Invalid username or password,please try again')
           
           
    return render(request,'store/login.html',{'next':next_url})
        
           
       
        
        



def verify_login_otp(request):
    email = request.session.get('login_email')

    #  Safety check
    if not email:
        messages.error(request, "Session expired. Please login again.")
        return redirect('login')

    if request.method == 'POST':
        otp = request.POST.get('otp')

        otp_obj = EmailOTP.objects.filter(email=email, otp=otp).first()

        if otp_obj:
            #  OTP EXPIRY CHECK
            if timezone.now() - otp_obj.created_at > timedelta(minutes=5):
                otp_obj.delete()
                messages.error(request, "OTP expired. Please resend OTP.")
                return redirect('verify_login_otp')

            user = User.objects.get(email=email)
            login(request, user)

            #  Cleanup
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



def verify_forgot_otp(request):
    email = request.session.get('forgot_email')

    if not email:
        messages.error(request, "Session expired. Please try again.")
        return redirect('forgot_password')

    if request.method == 'POST':
        otp = request.POST.get('otp')

        otp_obj = EmailOTP.objects.filter(email=email, otp=otp).first()

        if otp_obj:
            # OTP EXPIRY CHECK
            if timezone.now() - otp_obj.created_at > timedelta(minutes=5):
                otp_obj.delete()
                messages.error(request, "OTP expired. Please resend OTP.")
                return redirect('verify_forgot_otp')

            otp_obj.delete()
            return redirect('reset_password')
        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'store/verify_otp.html')


def resend_otp(request):
    email = request.session.get('signup_email') or request.session.get('login_email') or request.session.get('forgot_email')

    if not email:
        messages.error(request,'Session expired,Please try again')
        return redirect('login')

    otp = str(random.randint(100000, 999999))
    EmailOTP.objects.update_or_create(
        email=email,
        defaults={'otp': otp}

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
    
    
@login_required
def profile(request):
    orders=Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request,'store/profile.html',{'orders':orders})

def collection(request,brand,category):
    products = Product.objects.filter(brand__iexact=brand, category__iexact=category)

    context = {
        'brand': brand.capitalize(),
        'category': category.capitalize(),
        'products': products
    }
    return render(request, 'store/collection.html', context)


def order_success(request):
    return render(request,'store/order_success.html')
