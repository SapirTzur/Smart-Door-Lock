from django.db import models


class Member(models.Model):
     #unique =ensure oe and ony mail   
    email = models.EmailField(unique = True)
    password = models.CharField(max_length=255)
    def __str__(self):
           return f"{self.email}"
    

class Approved(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='approved_images/', blank=False, null=False)

    def __str__(self):
           return f"{self.full_name}"


