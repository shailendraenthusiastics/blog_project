from django.db import models
from django.contrib.auth.models import User

class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class BlogTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
class BlogImage(models.Model):
    image = models.ImageField(upload_to='gallery/')
    is_active = models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    

class Blog(models.Model):
    title = models.CharField(max_length=150 )
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    view_count = models.PositiveIntegerField(default=0)
    author_name = models.CharField(max_length=50, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    gallery = models.ManyToManyField(BlogImage, related_name='blogs', blank=True)
    featured_image = models.ImageField(upload_to='featured/')
    categories = models.ManyToManyField(BlogCategory, related_name='blogs')
    tags = models.ManyToManyField(BlogTag, related_name='blogs')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


billingChoice = (
 ('1-15', '1-15'),
 ('16-30', '16-30')
 )

class UserInfo(models.Model):
    whichUser = models.OneToOneField(User,on_delete=models.CASCADE)
    billingType = models.CharField(max_length=15, choices=billingChoice,default='1-15')
    userSetting = models.TextField(null=True,blank=True)
    isActive = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.whichUser.username



class LicenseModel(models.Model):
    licenseKey = models.CharField(max_length=20,unique=True)
    deviceSerialNumber = models.CharField(null=True,blank=True,max_length=100)
    generatedBy = models.ForeignKey(User,on_delete=models.CASCADE)
    licenseUseTime = models.DateTimeField(null=True,blank=True)
    licenseGenerateTime = models.DateTimeField(null=True,blank=True)
    linkUser = models.ForeignKey(UserInfo,on_delete=models.CASCADE,null=True,blank=True)
    isActive = models.BooleanField(default=True)
    isSuspended = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class UserAdvertisementTransaction(models.Model):
    linkUser = models.ForeignKey(UserInfo,on_delete=models.CASCADE,related_name='adTransactionLinkUser',null=True,blank=True)
    loginTime = models.DateTimeField(null=True,blank=True)
    logoutTime = models.DateTimeField(null=True,blank=True)
    lastSyncTime = models.DateTimeField(null=True,blank=True)
    duration = models.IntegerField(default=0)
    redisDuration = models.IntegerField(default=0)
    isActive = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)





