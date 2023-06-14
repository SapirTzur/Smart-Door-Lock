import requests
import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import os
from livenessnet import LivenessNet
import face_recognition
import Classes as cl

model = LivenessNet.build(width=32, height=32, depth=3,
		classes=2)
model.load_weights("model_weights.h5")

class Models:

    def check_user_id(user_id):
        
        
        with open('user_id.txt', 'r') as file:
            new_user_id = file.read()
        
        if new_user_id != user_id:
            user_id = new_user_id
            print(f"Received user_id in main program: {user_id}")
            
        return user_id
            
    def image_preprocessing(rgb_frame,face_dim):
            #Preprocess for the model. Extract the face from the frame.
            # top:bottom, left:right
            face_image = rgb_frame[face_dim[0]:face_dim[2],face_dim[3]:face_dim[1]]
            face_image = cv2.resize(face_image, (32, 32))                                       
            face_image = face_image.astype("float") / 255.0
            face_image = np.expand_dims(face_image, axis=0)
            return face_image
            
    def creating_frames ():

        #start_time = time.time()
        directory_frames = "frames"
        # Open the video capture device
        video_capture = cv2.VideoCapture(0) 
        # Start the timer

        counter = 0

        while True:
            ret, frame = video_capture.read()               
            frame = cv2.resize(frame, (640, 480)) 
            cv2.imwrite("{}/frame_{}.jpeg".format(directory_frames, counter), frame)
            counter +=1

            if counter ==2:

                break

        # Release the video capture device and close any open windows
        video_capture.release()
        cv2.destroyAllWindows()
        #time_frames_process  = time.time()- start_time
        return #time_frames_process
  

 
    def distance(GPIO_TRIGGER,GPIO_ECHO):
        # set Trigger to HIGH
        GPIO.output(GPIO_TRIGGER, True)
     
        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER, False)
     
        StartTime = time.time()
        StopTime = time.time()
     
        # save StartTime
        while GPIO.input(GPIO_ECHO) == 0:
            StartTime = time.time()
     
        # save time of arrival
        while GPIO.input(GPIO_ECHO) == 1:
            StopTime = time.time()
     
        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (TimeElapsed * 34340) / 2
     
        return distance

    def start_process(new_user_id, approved_list, encoding_lst, ip_rp, GPIO_SIG_RELAY):
        '''
        We create a list of objects that include all images on the RP
        and the information that relevant to the algorithm of the face recognition.
        '''
        #We start the timer to check how long the process is taking.
        #start_time = time.time()
        verification_lst = []
        objects_to_delete = []
        matches = []
        directory_frames = "frames"
        print("start the process")
        #model = LivenessNet.build(width=32, height=32, depth=3,
		#classes=2)
        #model.load_weights("model_weights.h5")
        lock_state = True
        #frame_list hold all the names of the frames inside the folder frames
        frame_list = os.listdir(directory_frames)
        '''
        Checking the frames with liveness detection
        
        '''

        for k in range(0, len(frame_list)):

            rgb_frame = face_recognition.load_image_file('{}/frame_{}.jpeg'.format(directory_frames, k))


            # Find all the faces and face enqcodings in the frame of video
            face_locations = face_recognition.face_locations(rgb_frame)
            print("{}".format(face_locations))

            '''
            Checking each frame which faces are real and spoof 
            '''
            #may check serias ant not parallel

            for j in range(len(face_locations)):

                face_dim = face_locations[j]


                '''
                Checking if we start to check the frames from the beginning. If it 
                does, so need to create an object for each face, if not then need
                to check the faces in the objects.
                '''


                if  k ==0:

                    print("k={}".format(k))
                    verification_lst.append(cl.verification(frame = rgb_frame,
                            face_location = [face_dim],
                            name = "face_{}".format(j)))             

                    #Preprocess for the model. Extract the face from the frame.

                    face_image = Models.image_preprocessing(rgb_frame,face_dim)

                    # Make predictions
                    predictions = model.predict(face_image)
                    predicted_class = np.argmax(predictions[0])
                    confidence = predictions[0][predicted_class]
                    print("the predicted_class is:",predicted_class," and the confidence is: ", confidence)
                    with open("output.txt", "a") as file:
                        file.write(f"the predicted_class is: {predicted_class} and the confidence is: {confidence}\n")
                    # Determine if face is real or fake based on predicted class when 1 is real and 0 is fake


                    if predicted_class == 1 and confidence >= 0.9 :
                        #means the face is real, and the model sure over 90%
                        verification_lst[j].fltr_lst.append(1)


                    else:
                        verification_lst[j].fltr_lst.append(0)


                else:		
                   

                    #Encoding one face from the frame
                    print("k={}".format(k))
                    frame_face_encoding = face_recognition.face_encodings(rgb_frame,[face_dim])	
                   
                    '''
                    Check if frame_face_encoding exists in the list.
                    If it did than we continue with the process.
                    '''


                    for verification in verification_lst:
                        checking_likeness = face_recognition.compare_faces(verification.face_encoding, frame_face_encoding[0])
                        print("likenes:{}" .format(checking_likeness[0]))


                        if checking_likeness[0]:
                            name = verification.name

                            #Preprocess for the model. Extract the face from the frame.
                            face_image =Models.image_preprocessing(rgb_frame,face_dim)
                            # Make predictions
                            predictions = model.predict(face_image)
                            predicted_class = np.argmax(predictions[0])
                            confidence = predictions[0][predicted_class]

                            print("the predicted_class is:",predicted_class," and the confidence is: ", confidence)
                            with open("output.txt", "a") as file:
                                file.write(f"the predicted_class is: {predicted_class} and the confidence is: {confidence}\n")


                        # Determine if face is real or fake based on predicted class when 1 is real and 0 is fake


                            if predicted_class == 1 and confidence >= 0.9 :
                            #means the face is real, and the model sure over 90%
                                verification.fltr_lst.append(1)


                            else:
                                verification.fltr_lst.append(0)



                            # true if this is the last iteration of k    
                            if (k+1 == len(frame_list)):

                                #we pull the filter list and check if there is more than 80% of the value 1 -->real face  
                                filtr = verification.fltr_lst
                                count_1 = filtr.count(1)
                                print("number of 1:{}" .format(count_1))

                                real_or_spoof_pred = count_1/(k+1)
                                print(f'pred = {real_or_spoof_pred}')
                                if (real_or_spoof_pred < 1.0):
                                    objects_to_delete.append(verification )

		
        for obj in objects_to_delete: 
            print('del obj')               
            verification_lst.remove(obj)
            del obj

        '''%
        All the section above(inside the while loop) deals about the face liveness.
        From here it deals with face recogntion.

        '''

        #Encodings all the real faces
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters = 5 , model = 'large')
        print("len:{}" .format(len(verification_lst)))


        for verification in verification_lst:
        #for index, face_encoding in enumerate(face_encodings):
            if len(verification.fltr_lst) == len(frame_list):
                matches = face_recognition.compare_faces(encoding_lst,verification.face_encoding[0], tolerance = 0.58)
                print("matches: {} ".format(matches))
                name = "Unknown"


                if True in matches:
                    lock_state = False
                                    
                    # At least one known face matches the current face encoding
                    matched_idx = matches.index(True)
                    name = approved_list[matched_idx].name
                    print("{} open the lock".format(name))
                    #Calulate how long take the process
                   # process_time = time.time() - start_time
                    #print("Process time:", process_time, "Second")

                  #  with open("output.txt", "a") as file:
                   #     file.write("Open the lock process:\n")
                    #    file.write(f"Process time: {process_time}\n")

                     # set Trigger to HIGH
                    GPIO.output(GPIO_SIG_RELAY, True)
                    time.sleep(2)
                    GPIO.output(GPIO_SIG_RELAY, False)
                    break
                    
                    #start_time = time.time()


        if lock_state and len(verification_lst)>=1 and len(verification_lst[0].fltr_lst) == len(frame_list) :

            cv2.imwrite(f"user_{new_user_id}/Not_Approved/Unknown.jpeg", rgb_frame[:,:,::-1])

            print("still unlock")
            #Calulate how long take the process
            #process_time = time.time() - start_time
            #print("Process time:", process_time, "Second")

            #Sending the connection file a trigger to seand the iamge
            
            #break#only for check without send image
            url = f'{ip_rp}/send_image'
            response = requests.post(url)
            if response.status_code == 200:
                print('Image sending request sent successfully')

            else:
                print('Failed to send the image sending request')
            
            #with open("output.txt", "a") as file:
             #   file.write("Unknown process:\n")
              #  file.write(f"Process time: {process_time}\n")

            #start_time = time.time()

            lock_state = True




        for obj in verification_lst:                
            del obj
            verification_lst = []
            objects_to_delete = []
            print("End process and start again\n")
            print(f'len ver_lst: {len(verification_lst)}')
            print(f'len match: {len(matches)}')
            
            print(f'len match: {len(matches)}')
            
         #  with open("output.txt", "a") as file:
          #      file.write(f"Amount inside cerification list: {len(verification_lst)}\n")
            
                
        return


