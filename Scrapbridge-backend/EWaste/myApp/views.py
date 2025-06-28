from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import *
from .forms import *
from django.http import JsonResponse
from decouple import config
# from .predict import classify_image
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from social_django.utils import psa
import razorpay
from EWaste.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.core.exceptions import ObjectDoesNotExist
import requests
from myApp.tasks import send_mail_via_brevo, get_ml_prediction_from_hf
BREVO_API_KEY = config('BREVO_API_KEY')
@api_view(['POST'])
@permission_classes([AllowAny])
def sendMail(request):
    html_content = request.data.get("message")
    receiver_email = request.data.get("receiver_email")
    receiver_name = request.data.get("receiver_name")
    subject = request.data.get("subject")

    if not html_content:
        return Response({"error": "Message content is required."}, status=status.HTTP_400_BAD_REQUEST)

    # 🔥 Offload the task
    send_mail_via_brevo.delay(receiver_email, receiver_name, subject, html_content)

    return Response({"message": "Mail is being sent in background."}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([])
def delete_all_tokens(request):
    count, _ = OutstandingToken.objects.all().delete()
    print("Deleted all tokens")
    return JsonResponse({'message': f'Deleted {count} tokens'})

@api_view(['GET'])
@permission_classes([])  # or use [] to remove auth for testing
def list_tokens(request):
    tokens = OutstandingToken.objects.all()
    return Response({
        'total_tokens': tokens.count(),
        'tokens': [
            {
                'user_id': token.user_id,
                'jti': token.jti,
                'created_at': token.created_at,
                'expires_at': token.expires_at,
            } for token in tokens
        ]
    })
# conn = http.client.HTTPSConnection("mail-sender-api1.p.rapidapi.com")
# headers = {
#     'x-rapidapi-key': "41f8c5c26emsh33af3107ae7eb1fp165595jsnd6e414bce373",
#     'x-rapidapi-host': "mail-sender-api1.p.rapidapi.com",
#     'Content-Type': "application/json"
# }
@api_view(['GET'])
def checkAuthentication(request):
    user = request.user
    IsAuthenticated = True if user.is_authenticated else False
    if(IsAuthenticated):
        role = 'user' if hasattr(user, 'enduser') else 'recycler'
    else:
        role = ''
    return Response({'isAuthenticated': IsAuthenticated, 'role': role}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    API to get logged-in user details.
    """
    user = request.user
    role = 'user' if hasattr(user, 'enduser') else 'recycler'
    try:
        if role == 'user':
            userProfile = user.enduser.image.url if user.enduser.image else None
        else:
            userProfile = user.owner.image.url if user.owner.image else None
    except Exception as e:
        userProfile = None  # fallback if image is missing or error occurs

    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": role,
        "user_profile": userProfile,
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    API to register a new user with email & password.
    OAuth users should register via Google.
    """
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    role = request.data.get("role")

    if not username or not email or not password or not role:
        return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_403_FORBIDDEN)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=status.HTTP_403_FORBIDDEN)

    if role not in ['user', 'recycler']:
        return Response({"error": "Invalid role specified"}, status=status.HTTP_400_BAD_REQUEST)

    # Create user
    user = User.objects.create_user(username=username, email=email, password=password)

    if role == 'user':
        enduser = endUser.objects.create(user=user)
    elif role == 'recycler':
        owner = Owner.objects.create(user=user, organisation_name=username)

    return Response({
        "message": "User registered successfully. Please log in to get tokens.",
    }, status=status.HTTP_201_CREATED)

# Google login : Takes access token : user information
@api_view(['POST'])
@permission_classes([AllowAny])
@psa('social:complete')
def google_login(request, backend):
    """
    Accepts Google OAuth token, logs in user, and assigns role (Simple User or Recycler).
    """
    token = request.data.get("access_token")
    user_type = request.data.get("user_type")  # Expect 'user' or 'recycler'

    if not token:
        return Response({'error': 'Access token is required'}, status=400)

    user = request.backend.do_auth(token)

    if user and user.is_active:
        login(request, user)  # Create session

        # Check if the user already has a role
        if endUser.objects.filter(user=user).exists():
            role = "user"
        elif Owner.objects.filter(user=user).exists():
            role = "recycler"
        else:
            # New user, assign role based on user input
            if user_type == "user":
                endUser.objects.create(user=user, phone="1234567890")
                role = "user"
            elif user_type == "recycler":
                Owner.objects.create(user=user, organisation_name=user.username, phone="1234567890")
                role = "recycler"
            else:
                return Response({'error': 'Invalid user type'}, status=400)

        return Response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": role
            }
        }, status=200)
    
    return Response({'error': 'Invalid token'}, status=400)

# Scrap classifier : Takes image of scrap : predicted class and accuracy
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def classify_image_view(request):
#     serializer = ImageUploadSerializer(data=request.data)
    
#     if serializer.is_valid():
#         image = serializer.validated_data['image']
        
#         try:
#             # Save the image and get the path
#             image_path = default_storage.save(image.name, image)
            
#             # Get the full path to the image
#             full_image_path = os.path.join(default_storage.location, image_path)
            
#             # Call your classification function
#             result = classify_image(full_image_path)  # Adjust based on your function
            
#             # Delete the image after processing
#             if os.path.exists(full_image_path):
#                 os.remove(full_image_path)
            
#             return Response({'classification': result}, status=status.HTTP_200_OK)
        
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User role : Take user_id : Return whether user is Recycler or Simple user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_role(request, user_id):
    """
    API to return the role of the logged-in user.
    """
    user = User.objects.get(id = user_id)
    role = "unknown"

    if endUser.objects.filter(user=user).exists():
        role = "user"
    elif Owner.objects.filter(user=user).exists():
        role = "recycler"

    return Response({
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": role
    })

# Owner details : Takes recycler id : return data about specific recycler
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ownerDetails(request, user_id):
    try:
        user = User.objects.get(pk = user_id)
        owner = Owner.objects.get(user = user)
        serializer = OwnerSerializer(owner)
        return Response(serializer.data, status = status.HTTP_200_OK)
    except Owner.DoesNotExist:
        return Response({"Error":"Owner does not exist"}, status=status.HTTP_404_NOT_FOUND)

# User detail : Takes user id : return data about specific user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userDetails(request, user_id):
    try:
        user = User.objects.get(id = user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status = status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"Error":"User does not exist"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def endUserDetails(request, enduser_id):
    try:
        enduser = endUser.objects.get(enduser_id = enduser_id)
        user = enduser.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status = status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"Error":"User does not exist"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getEndUserDetails(request, user_id):
    try:
        user = User.objects.get(pk = user_id)
        enduser = endUser.objects.get(user = user)
        serializer = EndUserSerializer(enduser)
        return Response(serializer.data, status = status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"Error":"User does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        enduser = None
        owner = None

        # Update related profile models
        if hasattr(user, 'enduser'):
            enduser = endUser.objects.get(user=user)
            enduser.phone = request.data.get("phone", enduser.phone)
            enduser.street = request.data.get("street", enduser.street)
            enduser.city = request.data.get("city", enduser.city)
            enduser.state = request.data.get("state", enduser.state)
            enduser.zipcode = request.data.get("zipcode", enduser.zipcode)
            enduser.save()
        elif hasattr(user, 'owner'):
            owner = Owner.objects.get(user=user)
            owner.phone = request.data.get("phone", owner.phone)
            owner.street = request.data.get("street", owner.street)
            owner.city = request.data.get("city", owner.city)
            owner.state = request.data.get("state", owner.state)
            owner.zipcode = request.data.get("zipcode", owner.zipcode)
            owner.latitude = request.data.get("latitude", owner.latitude)
            owner.longitude = request.data.get("longitude", owner.longitude)
            owner.save()

        # Update email in User model
        email = request.data.get("email")
        if email:
            user.email = email
            user.save()

        # Serialize and update profile
        if enduser:
            serializer = EndUserSerializer(enduser, data=request.data, partial=True)
        elif owner:
            serializer = OwnerSerializer(owner, data=request.data, partial=True)
        else:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User info updated successfully!",
                "data": serializer.data,
                "email": user.email
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# All owners detail : Takes nothing : returns all the owner available
@api_view(['GET'])
@permission_classes([AllowAny])
def getOwnerDetails(request):
    try:
        owner = Owner.objects.all()
        serializer = OwnerSerializer(owner, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({'Error':'Some error occured'}, status=status.HTTP_404_NOT_FOUND)

# All users detail : Takes nothing : returns all the user available (not needed API, gonna kill)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserDetails(request):
    try:
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({'Error':'Some error occured'}, status=status.HTTP_404_NOT_FOUND)
        
# Submit pickup request : Takes pickup specific data : return true/false response and send pickup request to recycler
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_scrap_request(request):
    mutable_data = request.data.copy()  # QueryDict ko mutable bana le

    # User ko endUser model se uthakar daal
    try:
        enduser = endUser.objects.get(user=request.user)
        mutable_data['user'] = enduser.enduser_id  # ID pass karni hai
    except endUser.DoesNotExist:
        return Response({"error": "EndUser not found"}, status=400)

    # Organisation ka ID uthakar object ka ID daal
    try:
        organisation_id = request.data.get('organisation')
        organisation = Owner.objects.get(organisation_id=organisation_id)
        mutable_data['organisation'] = organisation.pk
    except (KeyError, Owner.DoesNotExist):
        return Response({"error": "Valid organisation ID required"}, status=400)

    # Ab serialize karle
    serializer = RecycleFormSerializer(data=mutable_data)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Scrap request submitted successfully!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Registration for any query : Takes email id : sends query of user to admin
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_contact_details(request):
    serializer = ContactFormSerializer(data=request.data)  # Corrected serializer
    if serializer.is_valid():
        serializer.save()
        return Response({'message' : 'Contact details submitted successfully', 'data':serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response({'Error' : 'Contact details not submitted'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def showNotifications(request):
    try:
        pk = request.data.get("user_id")
        mark_seen = request.data.get("mark_seen", False)  # Default: don't mark

        user = User.objects.get(pk=pk)
        enduser = endUser.objects.get(user=user)

        # Mark as seen only if flag is passed
        if mark_seen:
            Notification.objects.filter(user=enduser, seen=False).update(seen=True)

        data = Notification.objects.filter(user=enduser)
        serializer = NotificationSerializer(instance=data, many=True)

        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Get all past/pngoing orders for a user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def scrapOrders(request, user_id):
    try:
        enduser_obj = endUser.objects.get(user_id=user_id)
        ongoing_orders = RecycleForm.objects.filter(user=enduser_obj)
        completed_orders = Payments.objects.filter(user=enduser_obj)

        ongoing_data = []
        for order in ongoing_orders:
            org_id = order.organisation.organisation_id if order.organisation else None
            org_name = order.organisation.user.username
            # safe image url check
            image_url = None
            if order.image and hasattr(order.image, 'url'):
                image_url = order.image.url

            ongoing_data.append({
                "order_id": order.order_id,
                "item_type": order.item_type,
                "weight": order.weight,
                "date": order.date.isoformat() if order.date else None,
                "location": order.location,
                "image": image_url,
                "organisation_id": org_id,
                "organisation_name": org_name,
                "status": order.status,
            })

        completed_data = []
        for payment in completed_orders:
            owner_id = payment.owner.organisation_id if payment.owner else None
            owner_name = payment.owner.user.username if payment.owner else None
            completed_data.append({
                "transaction_id": payment.transaction_id,
                "amount": float(payment.amount),
                "created": payment.created.isoformat() if payment.created else None,
                "organisation_name": owner_id,
                "organisation_name": owner_name,
            })

        return JsonResponse({
            "enduser_id": enduser_obj.enduser_id,
            "ongoing_orders": ongoing_data,
            "completed_orders": completed_data,
        }, safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({"error": "User or endUser not found."}, status=404)

    except Exception as e:
        import traceback
        print("Exception in scrapOrders view:", e)
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

# All orders of specific recycler : Takes recycler id : return all the orders of that recycler
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllOrders(request, user_id):
    try:
        user = User.objects.get(pk = user_id)
        owner = Owner.objects.get(user = user)
        data = RecycleForm.objects.filter(organisation = owner, status = False)
        serializer = RecycleFormSerializer(data, many=True)
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:  # Catch all errors instead
        return Response({'Error': f'Some error occurred: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)

# All pending orders of specific recycler : Takes recycler id : return all the orders of that recycler
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllPendingOrders(request, user_id):
    try:
        user = User.objects.get(pk = user_id)
        owner = Owner.objects.get(user = user)
        data = RecycleForm.objects.filter(organisation = owner, status = True)
        serializer = RecycleFormSerializer(data, many=True)
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:  # Catch all errors instead
        return Response({'Error': f'Some error occurred: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)

# Detail of specific order : Takes order_id : return all the details regarding that order
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderDetail(request, order_id):
    try:
        recycle_data = RecycleForm.objects.get(order_id=order_id)

        # Fetch the user using the user_id from the recycle_data
        user = User.objects.get(enduser=recycle_data.user)  # Assuming user_id is a field in RecycleForm
        enduser = endUser.objects.get(user = user)
        owner = recycle_data.organisation
        # Add the username to the serializer data
        recycle_data_serialized = RecycleFormSerializer(recycle_data)
        response_data = recycle_data_serialized.data
        response_data['user'] = user.username  # Add the username to the response
        response_data['email'] = user.email  # Add the username to the response
        response_data['street'] = enduser.street
        response_data['city'] = enduser.city
        response_data['state'] = enduser.state
        response_data['zipcode'] = enduser.zipcode
        response_data['phone'] = enduser.phone
        response_data['organisation_phone_number'] = owner.phone  # Add the username to the response
        
        return Response({'data': response_data}, status=status.HTTP_200_OK)

    except RecycleForm.DoesNotExist:
        return Response({'Error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'Error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# Order acceptance : Takes order id : return true/false
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orderAccepted(request, order_id):
    try:
        recycle_data = get_object_or_404(RecycleForm, order_id=order_id)  # Ensure object exists
        owner = recycle_data.organisation  # Corrected organisation reference
        enduser = recycle_data.user if recycle_data.user else None
        if(enduser == None): 
            return Response({'data':'Some error occured'}, status=status.HTTP_400_BAD_REQUEST)
        data = f"Your request has been accepted by {owner.organisation_name}. " \
            f"Delivery will arrive soon.\nScrap collector: {owner.user.username}\nEmail: {owner.user.email}"
        Notification.objects.create(status=True, user=enduser, message=data)
        recycle_data.status = True  # Remove order after acceptance
        print(recycle_data)
        recycle_data.save()
        return Response({'data': 'Order accepted'}, status=status.HTTP_200_OK)
    except:
        return Response({'data':'Some error occured'}, status=status.HTTP_400_BAD_REQUEST)
    
# Order rejected : Takes order id : return description of rejection
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def orderRejected(request, order_id):
    try:
        try:
            recycle_obj = RecycleForm.objects.get(order_id=order_id)
        except RecycleForm.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        reason = f"Your request has been rejected by {recycle_obj.organisation.user.username}. Scrap collector said '{request.data.get('reason')}'"
        print(reason)
        enduser = recycle_obj.user
        obj = Notification.objects.create(status = False, user = enduser, message = reason)
        recycle_obj.delete()

        return Response({'message': 'Order rejected successfully.'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def makePayment(request):
    # Assume you're passing amount in query params, e.g., ?amount=50000
    order_amount = int(request.data.get('amount'))  # amount in paise
    order_currency = 'INR'
    print(order_amount)
    # Create order with Razorpay
    payment_order = client.order.create(dict(amount=order_amount, currency=order_currency, payment_capture=1))

    return JsonResponse({
        'payment_id': payment_order['id'],
        'amount': order_amount,
        'api_key': RAZORPAY_API_KEY
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def addPaymentStatus(request, order_id, username, owner_id, amount, transaction_id):
    try:
        enduser = User.objects.get(username=username).enduser
        owner = User.objects.get(pk=owner_id).owner
        recycle_obj = RecycleForm.objects.get(order_id=order_id)

        # Create notification and payment record
        data_msg = f"Payment of {amount} received by {owner.user.username}, Transaction Id : {transaction_id}, Amount : {amount}"
        Notification.objects.create(status=True, user=enduser, message=data_msg)
        Payments.objects.create(user=enduser, owner=owner, transaction_id=transaction_id, amount=amount)

        # Common email sending details
        url = "https://api.brevo.com/v3/smtp/email"
        api_key = BREVO_API_KEY
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        sender = {"name": "Scrapbridge", "email": "csdslt2309@glbitm.ac.in"}
        subject = "💸 Payment Instantiated 💸"
        text_content = "Scrapbridge - Connecting you to World 🌍 !!"

        # Email to user
        html_content_user = f'''<body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
  <table width="100%" style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 8px;">
    <tr><td style="text-align: center;"><h2 style="color: #28a745;">✅ Payment Successful</h2></td></tr>
    <tr><td>
      <p>Dear <strong>{enduser.user.username.upper()}</strong>,</p>
      <p>We are pleased to inform you that your payment has been successfully processed for the scrap collection order.</p>
      <h3 style="color: #333;">🧾 Payment Details</h3>
      <ul style="list-style-type: none; padding-left: 0;">
        <li><strong>Transaction ID:</strong> {transaction_id}</li>
        <li><strong>Amount Paid:</strong> ₹{amount}</li>
        <li><strong>Order ID:</strong> {order_id}</li>
      </ul>
      <h3 style="color: #333;">🗑 Scrap Request Details</h3>
      <ul style="list-style-type: none; padding-left: 0;">
        <li><strong>Item Type:</strong> {recycle_obj.item_type}</li>
        <li><strong>Weight:</strong> {recycle_obj.weight/1000} kg</li>
        <li><strong>Requested On:</strong> {recycle_obj.date.strftime('%Y-%m-%d')}</li>
      </ul>
      <h3 style="color: #333;">🙋‍♂️ Scrap Collector Info</h3>
      <ul style="list-style-type: none; padding-left: 0;">
        <li><strong>Name:</strong> {owner.user.username.upper()}</li>
        <li><strong>Email:</strong> {owner.user.email}</li>
        <li><strong>Phone:</strong> {owner.phone}</li>
      </ul>
      <p>Thank you for contributing to a cleaner environment! 🌍</p>
      <p style="margin-top: 30px;">Warm regards,<br><strong>ScrapBridge Team</strong></p>
    </td></tr>
  </table>
</body>'''

        data_user = {
            "sender": sender,
            "to": [{"email": enduser.user.email, "name": enduser.user.username}],
            "subject": subject,
            "htmlContent": html_content_user,
            "textContent": text_content
        }
        
        response = requests.post(url, json=data_user, headers=headers)
        if not response.ok:
            try:
                error_detail = response.json()  # parse JSON error details from API response
            except Exception:
                error_detail = response.text  # fallback to raw text if JSON parsing fails

            return Response({
                "Error": "Payment notification email to User failed",
                "Details": error_detail
            }, status=status.HTTP_400_BAD_REQUEST)
        # Email to scrap collector
        html_content_owner = f'''<body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 10px;">
  <table width="100%" style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 20px; border-radius: 8px;">
    <tr><td style="text-align: center;"><h2 style="color: #28a745;">✅ Payment Successful</h2></td></tr>
    <tr><td>
      <p>Dear <strong>{owner.user.username.upper()}</strong>,</p>
      <p>We are pleased to inform you that your payment has been successfully processed for the scrap collection order.</p>
      <h3 style="color: #333;">🧾 Payment Details</h3>
      <ul style="list-style-type: none; padding-left: 0;">
        <li><strong>Transaction ID:</strong> {transaction_id}</li>
        <li><strong>Amount Paid:</strong> ₹{amount}</li>
        <li><strong>Order ID:</strong> {order_id}</li>
      </ul>
      <h3 style="color: #333;">🗑 Scrap Request Details</h3>
      <ul style="list-style-type: none; padding-left: 0;">
        <li><strong>Item Type:</strong> {recycle_obj.item_type}</li>
        <li><strong>Weight:</strong> {recycle_obj.weight/1000} kg</li>
        <li><strong>Requested On:</strong> {recycle_obj.date.strftime('%Y-%m-%d')}</li>
      </ul>
      <h3 style="color: #333;">🙋‍♂️ Receiver Info</h3>
      <ul style="list-style-type: none; padding-left: 0;">
        <li><strong>Name:</strong> {enduser.user.username.upper()}</li>
        <li><strong>Email:</strong> {enduser.user.email}</li>
        <li><strong>Phone:</strong> {enduser.phone}</li>
      </ul>
      <p>Thank you for contributing to a cleaner environment! 🌍</p>
      <p style="margin-top: 30px;">Warm regards,<br><strong>ScrapBridge Team</strong></p>
    </td></tr>
  </table>
</body>'''

        data_owner = {
            "sender": sender,
            "to": [{"email": owner.user.email, "name": owner.user.username}],
            "subject": subject,
            "htmlContent": html_content_owner,
            "textContent": text_content
        }
        
        response = requests.post(url, json=data_owner, headers=headers)
        if not response.ok:
            try:
                error_detail = response.json()  # parse JSON error details from API response
            except Exception:
                error_detail = response.text  # fallback to raw text if JSON parsing fails

            return Response({
                "Error": "Payment notification email to User failed",
                "Details": error_detail
            }, status=status.HTTP_400_BAD_REQUEST)

        recycle_obj.delete()

        return Response({"Success": "Payment done successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Successful payments : Takes user id and return all the payments done by a specific scrap collector
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def successfulPayments(request, user_id):
    try:
        user = User.objects.get(pk = user_id)
        owner = Owner.objects.get(user=user)
        allTransactions = Payments.objects.filter(owner = owner)
        serializer = PaymentsSerializer(allTransactions, many = True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Non api work


def index(request):
    return render(request, 'index.html')

