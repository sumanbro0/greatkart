from django.db import models

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    full_name=models.CharField(max_length=50,blank=True,null=True)
    bio=models.TextField()
    is_email_verified=models.BooleanField(default=False)
    email_token=models.CharField(max_length=100,blank=True,null=True)
    avatar=models.ImageField(upload_to='avatars',blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name if self.full_name else self.user.username
    

class Address(models.Model):
    profile=models.ForeignKey(Profile,on_delete=models.CASCADE)
    address=models.CharField(max_length=100)
    city=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    country=models.CharField(max_length=50)
    zip_code=models.CharField(max_length=10)

    def __str__(self):
        return (self.address.split(',')[0] or "") + ', ' + (self.city or "") + ', ' + (self.state or "")

