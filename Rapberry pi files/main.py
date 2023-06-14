import Classes as cl
import os
from models import Models
import RPi.GPIO as GPIO
import time
from livenessnet import LivenessNet
'''
Define all the input\output from the RP
'''
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO_SIG_RELAY = 23
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_SIG_RELAY, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

user_id = None

directory_frames = "frames"
#ip_rp = "http://172.20.19.183:5000" 
#ip_rp = 'http://192.168.1.106:5000'
#ip_rp = 'http://172.20.27.4:5000'
ip_rp =  "http://192.168.134.236:5000"

while True: 
	
	new_user_id = Models.check_user_id(user_id)
	'''
	first we check which user is on the website, and if it changes so we upload all
	the data of the ''approved'' in the system the user
	'''
	#still need to see hao we update a new aprroved that uplaod
	if new_user_id != user_id:
		user_id = new_user_id
		'''
		We create a list of objects that include all images on the RP that belong to user_x
		and the information that is relevant to the algorithm of the face recognition.
		'''
		approved_list=[]
		encoding_lst = []
		
		file_list = os.listdir(f"user_{new_user_id}/Approved")
		for i in range(len(file_list)):
			file_name = file_list[i]
			
			# Extract the full name from the file name e.g. file name = Jhon Doe.jpg ->full_name = Jhon Doe
			full_name = file_name.split('.')[0] 
			path_of_img = (f"user_{new_user_id}/Approved/{file_name}")
			approved_list.append(cl.database_of_img(name = full_name, img_path = path_of_img))
			print(f'{full_name}')
			print(f'{approved_list[i].face_location}')
		
			
			# Need to check from the web that is has one loc print(f"{approved_list[0].face_location}")	

		for aprroved in approved_list :
			encoding_lst.append(aprroved.face_encoding[0])
	
	'''
	until here the system uploaded all the data of the user and from here we will check repetitively
	 the distance from the ultrasonic sensor and only if there is an object it will start
	 (need to verify that the object is a person)
	'''
	time.sleep(0.5)
	distnace_from_camera = Models.distance(GPIO_TRIGGER,GPIO_ECHO)
	print(f'the distance is:{distnace_from_camera}')
	if distnace_from_camera <= 50:
		start=time.time()
		time_frames = Models.creating_frames()
		frames_time = time.time()-start
		print(f'time of frames function:{frames_time}')
		Models.start_process(new_user_id, approved_list, encoding_lst, ip_rp, GPIO_SIG_RELAY)
		print(f'all process:{time.time()-start}')

