from flask import Flask, request
import os
import json
import requests


app = Flask(__name__)

user_id = None

#ip_adress = "http://192.168.1.116:8000"
#ip_adress =  "http://172.20.25.61:8000"
ip_adress =  "http://192.168.134.226:8000"

@app.route('/receive_user_id', methods=['POST'])
def receive_user_id():
    global user_id 
    user_id = request.form['user_id']
    folder_name = f"user_{user_id}"
    if not os.path.exists(folder_name):
       os.makedirs(folder_name)
       os.makedirs(f'{folder_name}/Approved')
       os.makedirs(f'{folder_name}/Not_Approved')
       print(f"Folder '{folder_name}' created successfully.")
    else:
       print(f"Folder '{folder_name}' already exists.")
    print(f"Received user_id: {user_id}")
    with open('user_id.txt', 'w') as file:
          file.write(user_id)


    return 'Success'
    
   

@app.route('/receive_person_data', methods=['POST'])
def receive_person_data():
    user_id = request.form['user_id']
    full_name = request.form['full_name']
    image = request.files['image']
    image_data = image.read()
      # Save the image inside the user's folder with the full name as the image name
    folder_name = f"user_{user_id}/Approved"
    image_path = os.path.join(folder_name, f"{full_name}.jpeg")
    
    with open(image_path,"wb") as f:
        f.write(image_data)
    print(f"Received person data - User ID: {user_id}, Full Name: {full_name}")
 

    return 'Success'

@app.route('/remove_person_data', methods=['POST'])
def remove_person_data():
    user_id = request.form['user_id']
    full_names =json.loads(request.form['full_names'])
    folder_name = f"user_{user_id}/Approved"
    print(f"Deleted person data - User ID: {user_id}, Approved ID: {full_names}")
    for name in full_names:
        image_path = os.path.join(folder_name, f"{name}.jpeg")
        os.remove(image_path)
        

    # Process the received data as needed
    # For example, delete the image file from the Raspberry Pi
    #
    print(f"Deleted person data - User ID: {user_id}, Approved ID: {full_names}")

    return 'Success'
    
    

@app.route('/send_image', methods=['POST'])
def send_image():
    global user_id 
    print(user_id)
    folder_name = f"user_{user_id}/Not_Approved/Unknown.jpeg"
    if os.path.exists(folder_name):
        with open(folder_name, "rb") as f:
            image_data = f.read()

        web_url = f"{ip_adress}/notification_alert/{user_id}/"
       
        response = requests.post(web_url, files = {"image": image_data})

        if response.status_code == 200:
            print('Image data sent successfully')
            print("Response:", response.text)  # Print the response content

        else:
            print('Failed to send the image data')
    else:
        print("Image file not found")

    return "Image sent function from the RP"  # Optionally, return a response to the client


        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
