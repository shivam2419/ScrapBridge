from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from geopy.geocoders import Nominatim
from .models import *
from .forms import *
from django.db import transaction
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
# import the OpenAI Python library for calling the OpenAI API
from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# openai.api_key = open_api_key
def index(request):
    page = ''
    questions = QNA.objects.all()
    context = {
        'questions' : questions,
        'page' : page
    }
    return render(request, 'index.html', context)

def staff(request):
    return render(request, 'staff/index.html')

def home(request):
    # return HttpResponse("request, 'index.html'")
    return render(request, 'home.html')

def loginPage(request):
    
    page='login'
    message = ""
    # This checks whether the user is logged in or not or is authenticated or not?
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        # Checking validity of user

        # CASE : 1
        try:
            user = User.objects.get(username=username) # if User exsits in database then this will return true
        except:
            messages.error(request, 'User does not exist')

        # CASE : 2
        user = authenticate(request, username=username, password=password) # Checking whether the given username and password is correct or not
        
        if user is not None:
            if user.is_staff:
                print("Staff logging in")
                login(request, user)
                return redirect('recycler-login') 
            else:
                print("User logging in")
                login(request, user)
                return redirect('index') 
            # message = user.message_set.all()
        else:
            messages.error(request, 'Password is incorrect')
        # In the above condition there are two cases to check validity of user you can use any of them
    context={'page':page, 'messsages':message}
    return render(request, 'login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('index')

def registerPage(request):
    if request.method == 'POST':
        name = request.POST.get('Full_Name').lower()
        mail = request.POST.get('Email')
        pswrd = request.POST.get('Password')
        confirm_pswrd = request.POST.get('confirm_Password') 
        user_type = request.POST.get('type').lower()
        
        if(pswrd!=confirm_pswrd):
            messages.error(request, 'Password and Confirm password details are not same')

        if User.objects.filter(username=name).exists():
            messages.error(request, 'Username is already taken. Please choose a different one.')
            return redirect('signup')
        
        if user_type == 'user':
            try:
                # Create the user
                user = User.objects.create_user(username=name, email=mail, password=pswrd) # if User exsits in database then this will return true
            except:
                messages.error(request, 'Username already exists')
            user = authenticate(username=name, password=pswrd)
            if user is not None:
                print('User signing up')
                login(request, user)
                return redirect('index') 
        else:
            try:
                # Create the staff
                user = User.objects.create_user(username=name, email=mail, password=pswrd) # if User exsits in database then this will return true
                user.is_staff = True
            except:
                messages.error(request, 'Username already exists')
            
            user = authenticate(username=name, password=pswrd)
            if user is not None:
                print("Staff signing up")
                login(request, user)
                return redirect('recycler-login') 
                
        ''' 
        registerObj = Signup.objects.create(username = name, email = mail, password = pswrd, confirm_password = confirm_pswrd)
        registerObj.save()
        Log the user in
        '''
    return render(request, 'signup.html')

def about(request):
    return render(request, 'about.html')

def E_facility(request):
    q = request.GET.get('q', '')  # Get the query string, default to empty string if not provided
    rooms = Owner.objects.filter(
        #t he icontains lookup is used to perform case-insensitive containment checks in queries. It is commonly used in Django's ORM (Object-Relational Mapping) to filter querysets based on whether a field contains a specific value, ignoring case sensitivity.
        
        Q(organisation_name__icontains=q) |
        Q(phone__icontains=q)
        ) #with 'q' value, it will filter by matching characters whether it's whole name or only one character.
    
    print('help',q)
    context = {'search_query':q, 'rooms':rooms}
    return render(request, 'efacility.html',context)

def Waste_owner(request):
    return render(request, 'efacility.html')

def recycle(request):
    return render(request, 'recycle.html')

def Education(request):
    return render(request, 'education.html')

def contact(request):
    if request.method == "POST":
        contact_name = request.POST.get('contact-name')
        contact_email = request.POST.get('contact-email')
        contact_phone = request.POST.get('contact-number')
        contact_message = request.POST.get('contact-message')

        obj = ContactForm(name=contact_name, email = contact_email, phone_number = contact_phone, message = contact_message)
        obj.save()
    return render(request, 'contact.html')

def ask_openai(message):
    # Example OpenAI Python library request
    MODEL = "gpt-3.5-turbo"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Knock knock."},
            {"role": "assistant", "content": "Who's there?"},
            {"role": "user", "content": "Orange."},
        ],
        temperature=0,
    )
    print(json.dumps(json.loads(response.model_dump_json()), indent=4))

def search(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)
        return JsonResponse({'message':message, 'response':response})
    return render(request, 'help.html')

@login_required(login_url='login')
def collected_gmails(request):
    if request.method == 'POST':
        mails = request.POST.get('index_gmail')
        data = Index_gmails(emails = mails)
        data.save()
        return redirect('index')
    print('helo')
    return render(request, 'index.html')

@login_required(login_url='login')
def notification(request):
    pk = request.user.id
    data = Notification.objects.filter(user = pk)
    context = {
        'data' : data
    }
    return render(request, 'notification.html', context)

@login_required(login_url='login')
def userProfile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')  # Redirect to user profile page after successful update
        else:
            print(form.errors)
    else:
        form = UserUpdateForm(instance=request.user)
        
    context = {'form': form}
    return render(request, 'profile.html', context)

@login_required(login_url='login')
def recycle_main_str(request, pk):
    message = ""
    if request.method == "POST":
        user_id = request.user.id
        org_id = pk
        item_type = request.POST.get('item_type')
        date = request.POST.get('date')
        phone = request.POST.get('pnum')
        images = request.FILES.get('image')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        location = latitude + " " + longitude
        obj = RecycleForm.objects.create(user_id = user_id, organisation_id = org_id, item_type = item_type, date = date, location=location, image=images, phone = phone)

        return redirect('index')
    data = Owner.objects.get(organisation_id = pk)
    context = {'item': data,
               'msg' : message}
    return render(request, 'recycle_main.html', context)

@login_required(login_url='login')
def recycle_main(request):
    # id = request.user
    # print(id)
    # if request.method == "POST":
    #     username = id.username
    #     user_id = id.id
    #     organisation_id = request.POST.get('id')
    #     organisation_name = request.POST.get('organisation_name')
    #     brand = request.POST.get('brand')
    #     model = request.POST.get('model')
    #     price = request.POST.get('price')
    #     date = request.POST.get('date')
    #     location = request.POST.get('location')
    #     images = request.FILES.get('image')
    #     phone = request.POST.get('phone')
    #     facility = request.POST.get('facility')

    #     obj = RecycleForm.objects.create(name=username, user_id = id, organisation_id = organisation_id, organisation_name=organisation_name, brand=brand, model = model, price = price, date=date, location=location, image=images, phone = phone,facility=facility)
    return render(request, 'efacility.html',)

@login_required(login_url='login')
def createOwner(request, pk):
    if request.method == 'POST':
        image = request.FILES.get('image')
        # about = request.POST.get('about')
        # email = request.POST.get('date')
        user = User.objects.get(pk = request.user.id)
        organisation_id = user.id
        organisation_name = request.POST.get('organisation_name')
        phone = request.POST.get('phone')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zipcode')
        lat = request.POST.get('latitude')
        longi = request.POST.get('longitude')

        obj = Owner(image=image,
                                   organisation_id=organisation_id,organisation_name=organisation_name, phone=phone, street=street, city=city, state=state, zipcode = zip_code, latitude= lat, longitude = longi)
        obj.save()
        return render(request, 'staff/index.html')
    organisation_data = Owner.objects.get(organisation_id=pk)
    context = {
        'organisation' : organisation_data
    }
    return render(request, 'staff/owner.html', context)
        
@login_required(login_url='login')
def Orders(request):
    user = User.objects.get(pk = request.user.id)
    to_id = user.id
    data = RecycleForm.objects.filter(organisation_id = to_id)
    data = [(index + 1, item) for index, item in enumerate(data)]
    owner_info = Owner.objects.filter(organisation_id = to_id)
    context = {
        'items' : data,
        'user' : owner_info
    }
    return render(request, 'staff/order.html', context)

@login_required(login_url='login')
def Inspect(request, pk):
    recycle_data = RecycleForm.objects.get(id = pk, organisation_id = request.user.id)
    full_location = str(recycle_data.location)
    split_location = full_location.split()  # This will create a list ['shivam', 'sharma']
    context = { 
        'recycle_data' : recycle_data,
        'latitude' : split_location[0],
        'longitude' : split_location[1]
    }
    if request.method == 'POST':
        status = 'True'
        user = recycle_data.user_id
        data = "Your request has been accepted by the supplier. Delievery boy will reach to you within given period."
        obj = Notification(status = status, user = user, message = data)
        obj.save()
        recycle_data = recycle_data.first()
        recycle_data.delete()
        return render(request, 'staff/index.html')
    return render(request, 'staff/inspect.html', context)

@login_required(login_url='login')
def RejectOrder(request, pk):
    recycle_data = RecycleForm.objects.filter(user_id = pk, organisation_id = request.user.id)
    context = { 
        'recycle_data' : recycle_data
    }
    if request.method == 'POST':
        status = 'False'
        user = pk
        data = request.POST.get('reason')
        data = "Your order has been cancelled. Scrap Collector said  ' " + data + " '"
        obj = Notification(status = status, user = user, message = data)
        obj.save()
        recycle_data = recycle_data.first()
        recycle_data.delete()
        return render(request, 'staff/index.html')
    return render(request, 'staff/reject_order.html', context)

def Status(request):
    return render(request, 'staff/order_status.html')
def Pending(request):
    recycle_data = RecycleForm.objects.filter(status="False", organisation_id = request.user.id)
    context = {
        'data' : recycle_data
    }
    return render(request, 'staff/order_pending.html', context)
def Completed(request):
    recycle_data = RecycleForm.objects.filter(status="True", organisation_id = request.user.id)
    context = {
        'data' : recycle_data
    }
    return render(request, 'staff/order_completed.html', context)

def payment(request, pk):
    user = RecycleForm.objects.get(user_id = pk)
    user_name = user.name
    your_name = request.user.username   
    if request.method == 'POST':
        try:
            user_one = request.POST.get('user')
            user_two = your_name
            amount = request.POST.get('amount')
            # with transaction.atomic(): 
            user_one_obj = Payments.objects.get(user = user_one)
            user_one_obj.amount += int(amount)
            user_one_obj.save()
            print(user_one)

            user_two_obj = Payments.objects.get(user = user_two)
            user_two_obj.amount -= int(amount)
            user_two_obj.save()
            messages.success(request, 'Your amount is transfered')
        except Exception as e:
            print(e)
            messages.success(request, "Something went wrong.")
    context = {
        'user' : user_name,
        'you' : your_name
    }
    return render(request, 'staff/payment.html', context)