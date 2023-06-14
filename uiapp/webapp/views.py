from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import Member,Approved
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pdb
import os
import requests
import json
import piexif
from django.core.mail import EmailMessage
from django.conf import settings
from PIL import Image
import io
import gzip



#ip_adress = 'http://192.168.1.106:5000' 
#ip_adress = 'http://172.20.27.4:5000' 
ip_adress = 'http://192.168.134.236:5000/' 


def compress_image(image):
    # Open the image using PIL
    pdb.set_trace()
    image_pil = Image.open(image)

    # Create a buffer to hold the compressed image data
    compressed_image_data = io.BytesIO()
    
    # Compress the image using gzip
    with gzip.GzipFile(fileobj=compressed_image_data, mode='wb') as f:
        image_pil.save(f, 'JPEG')
    
    # Set the buffer's position to the beginning for reading
    compressed_image_data.seek(0)
    
    # Create a new PIL Image object from the compressed image data
    compressed_image = Image.open(compressed_image_data)
     
    return compressed_image





@csrf_exempt
def add_person(request,user_id):
    if request.method == 'POST':
       # pdb.set_trace()
        full_name = request.POST.get('fullname')
        image = request.FILES.get('image')
        print(f'{image.size}')
        # Check if the image size exceeds 1 MB (1,048,576 bytes)
        #while image.size > 1048576:
         #   print('start while')
    
          #  image = compress_image(image)
           # print(f'{image.size}')
     
            
    
        img = Image.open(image)
        #Extract the metadata of the image
        exif = img.info.get('exif')
      
        if exif:
            exif_data = piexif.load(exif)
            orientation = exif_data.get('0th', {}).get(piexif.ImageIFD.Orientation)
            #3 = 180 degrees, 6= 90 degrees clockwise, 8=  90 degrees counterclockwise
            if orientation == 3:
                
               img = img.rotate(180)
               
            elif orientation == 6 :
                
                img = img.rotate(270)
                
            elif orientation == 8:
                    img = img.rotate(90)
                
            print(f'{orientation}')
        
       # width, height = img.size
       # print(f'w = {width}, h = {height}')
        #img = img.resize((math.ceil(float(width)*0.75), math.ceil(float(height)*0.75)))
        
    # Fix image rotation by removing the orientation tag from EXIF metadata
       # print(f'{img.size}')
       
        # Save the resized image to a temporary file
        # Save the image to a specific directory
        path = 'original_images'
        image_path = f'{path}/temp_image.jpeg'  # Replace 'custom_directory' with your desired directory path
        with default_storage.open(image_path, 'wb') as destination:
            img.save(destination)
               
        
        person = Approved.objects.create(
            member = Member.objects.get(id=user_id),
            full_name=full_name,
            )
        # Open the resized image file and assign it to the 'image' field
        with default_storage.open(image_path, 'rb') as file:
           person.image.save('temp_image.jpeg', ContentFile(file.read()))
        
        person.save()
        # Prepare data for the request
        data = {
           'user_id': user_id,
           'full_name': full_name
        }
        files = {
           'image':person.image.read()  # Read the image data
        }
        
        # Send data to Raspberry Pi API
        raspberry_pi_url = f'{ip_adress}/receive_person_data'
        response = requests.post(raspberry_pi_url, data=data, files=files)
        return redirect('user', user_id)
    template = loader.get_template('add_person.html')

    return HttpResponse(template.render())


@csrf_exempt
def delete_approved(request,user_id):
    if request.method == 'POST':
      # pdb.set_trace()
       member = Member.objects.get(id=user_id)
       approved_ids = request.POST.getlist('selected_approved')
       full_names = []
       for approved_id in approved_ids:
            approved = Approved.objects.filter(id=approved_id,member = member).first()
            if approved:
                # Prepare data for the request
                full_names.append(approved.full_name) 
                data = {
                    'user_id': user_id,
                    'full_names': json.dumps(full_names)  # Convert the list to a JSON array
                }
                
                 #Send data to Raspberry Pi API
                raspberry_pi_url = f'{ip_adress}/remove_person_data'
                response = requests.post(raspberry_pi_url, data=data)
                
                #Delete approved object
                os.remove(approved.image.path)
                approved.delete()
            
    return redirect('user', user_id)

def member_account(request, user_id):
  member = Member.objects.get(id=user_id)
  lst_approved = Approved.objects.filter(member = member)
  template = loader.get_template('users.html')
  context = {
    'my_approved': lst_approved,
    'user_id': user_id
  }
  
  #Send user_id to Raspberry Pi
  
  raspberry_pi_url = f'{ip_adress}/receive_user_id'
  data = {
       'user_id': user_id
   }
  response = requests.post(raspberry_pi_url, data=data)
  
  return HttpResponse(template.render(context, request))

def details(request, id):
  mymember = Member.objects.get(id=id)
  template = loader.get_template('details.html')
  context = {
    'mymember': mymember,
  }
  return HttpResponse(template.render(context, request))


def main(request):
  template = loader.get_template('main.html')

  return HttpResponse(template.render())          


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email').lower()
       
        password = request.POST.get('password')
    
        try:
            
            new_member = Member.objects.create(
                email = email,
                password=password,
                )
            new_member.save()
            return redirect('main')
        except IntegrityError:
            # If the email already exists, render the same signup page with an error message
          error_message = 'Email already exists in the system. Please use a different email.'
          template = loader.get_template('signup.html')
          return HttpResponse(template.render( {'error_message': error_message}))
        
    template = loader.get_template('signup.html')

    return HttpResponse(template.render())
   

@csrf_exempt
def main_login (request):
    
    if request.method == 'POST':
        
    #sign in request
        email_front = request.POST.get('email').lower()
        password_front = request.POST.get('password')
        try:
            user = Member.objects.get(email = email_front)
            if password_front == user.password:
              

                template = loader.get_template('users.html')
                return redirect('user',user_id = user.id )
            
            else:
                error_message = 'Email or password is incorrect, try again'
                template = loader.get_template('main.html')
                return HttpResponse(template.render( {'error_message': error_message}))
            
        except Member.DoesNotExist:
            error_message = 'Email or password is incorrect, try again'
            template = loader.get_template('main.html')
            return HttpResponse(template.render( {'error_message': error_message}))   

    template = loader.get_template('main.html')

    return HttpResponse(template.render())          
    
    
@csrf_exempt
def notification_alert(request,user_id):
    if request.method == 'POST' and 'image' in request.FILES:
        print("hi")
        image_file = request.FILES['image']
        user = Member.objects.get(id = user_id)
        recipient_email = user.email
        folder_name = 'Not_approved'
        file_path = default_storage.save(f'{folder_name}/Unknown.jpeg', image_file)
        # Process the image file as needed (e.g., save it, perform operations on it, etc.)
        print(f"image file:{image_file}\n")
        print(f"image content: {image_file.read()}")
        subject = 'Email with Image Attachment'
        message = 'Unknown people try to open the lock.'
        email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [recipient_email])
        
        # Attach the image file
        image_path = f'media/{folder_name}/Unknown.jpeg'
        #content_type, _ = mimetypes.guess_type(image_path)
        with open(image_path, 'rb') as image_f:
            email.attach(filename='Unknown.jpeg', content=image_f.read(), mimetype='image/jpeg')
        # Send the email
        email.send()       
                
        # Return a response if desired
        return HttpResponse("Image received and processed.")
    else:
        return HttpResponse("Invalid request.")

                
      
    
      
