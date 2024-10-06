from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('login/', views.loginPage, name='login'),
    path('recycler-login/', views.staff, name='recycler-login'),
    path('logout/', views.logoutUser, name='logout'),
    path('signup/', views.registerPage, name='signup'),
    path('profile/', views.userProfile, name='profile'),
    path('about/', views.about, name='about'),
    path('e-facility/', views.E_facility, name='e-facility'),
    path('recycle/', views.recycle, name='recycle'),
    path('education/', views.Education, name='education'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search, name='search'),
    path('notification/', views.notification, name='notification'),
    path('recycle_main/<str:pk>/', views.recycle_main_str, name='recycle_main'),
    path('recycle_main/', views.recycle_main, name='recycle_main'),
    path('index_mails/', views.collected_gmails, name='mails'),
    path('settings/<str:pk>/', views.createOwner, name='settings'),
    path('orders/', views.Orders, name='orders'),
    path('inspect/<str:pk>/', views.Inspect, name='inspect'),
    path('reject/<str:pk>/', views.RejectOrder, name='rejectOrder'),
    path('status/', views.Status, name='orderstatus'),
    path('pending/', views.Pending, name='orderpending'),
    path('completed/', views.Completed, name='ordercompleted'),
    path('payment/<str:pk>/', views.payment, name='payment'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

