from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# End User Model
class endUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enduser_id = models.AutoField(primary_key=True)
    image = CloudinaryField('image', folder='images', null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    street = models.CharField(max_length=400, null=True, blank=True, default="")
    city = models.CharField(max_length=400, null=True, blank=True, default="")
    state = models.CharField(max_length=400, null=True, blank=True, default="")
    zipcode = models.CharField(max_length=20, null=True, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

# QNA Model
class QNA(models.Model):
    questions = models.CharField(max_length=1000)
    answers = models.TextField()  # Use TextField for longer answers

# Index Gmails Model
class Index_gmails(models.Model):
    emails = models.EmailField(unique=True)  # Ensure unique emails

class Owner(models.Model):
    # *** Applied Indexing here ***
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_index=True)  # frequently queried
    organisation_id = models.AutoField(primary_key=True, db_index=True)
    organisation_name = models.CharField(max_length=200, db_index=True)  # useful if searched or listed
    image = CloudinaryField('image', folder='images', null=True, blank=True)
    phone = models.CharField(max_length=16, null=True, blank=True)

    # Address section
    city = models.CharField(max_length=400, null=True, blank=True, default="", db_index=True)
    state = models.CharField(max_length=400, null=True, blank=True, default="", db_index=True)
    street = models.CharField(max_length=400, null=True, blank=True, default="")
    zipcode = models.CharField(max_length=20, null=True, blank=True, default="", db_index=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # if sorted by recency

    class Meta:
        indexes = [
            models.Index(fields=['city', 'state']),
            models.Index(fields=['user']),
        ]
    # db_index=True for single fields used individually.
    # Meta.indexes for compound (multi-field) filters

# Contact Form Model
class ContactForm(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=16)  # Change to CharField
    message = models.TextField()

# Recycle Form Model
class RecycleForm(models.Model):
    order_id = models.CharField(max_length=100, primary_key=True)
    user = models.ForeignKey(endUser, on_delete=models.CASCADE, null=True, db_index=True)
    organisation = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, db_index=True)
    item_type = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    date = models.DateTimeField(null=True, blank=True, db_index=True)
    phone = models.CharField(max_length=16, null=True, blank=True)
    image = CloudinaryField('image', folder='recycle_images', null=True, blank=True)
    weight = models.IntegerField(null=True, default=0)
    location = models.CharField(max_length=200, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['user', 'status']),             # compound index for filtering active/inactive user requests
            models.Index(fields=['item_type', 'created']),       # filter by item type + recent
        ]


# Notification Model
class Notification(models.Model):
    user = models.ForeignKey(endUser, on_delete=models.CASCADE, null=True)  # Use ForeignKey
    status = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    seen = models.BooleanField(default=False)
    class Meta:
        ordering = ['-created']

# Payments Model
class Payments(models.Model):
    user = models.ForeignKey(endUser, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, default=1)
    transaction_id = models.CharField(max_length=200, default=None, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Use DecimalField
    created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-created']