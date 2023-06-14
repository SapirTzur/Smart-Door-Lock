import face_recognition as fc
import cv2
class database_of_img:
   
    def __init__(self, name, img_path):
        self.name = name
        self.img_path = img_path
    # allows us to use the name of the function as instance    
    @property
    def data_img(self):
        return fc.load_image_file(self.img_path)      
                
    @property
    def face_location(self):
        return [fc.face_locations(self.data_img)[0]]
    @property
    def face_encoding(self):
        return fc.face_encodings(self.data_img, self.face_location, num_jitters =  30 ,model = 'large')
#Super() connect between the init func from data_base_img to the init func of the approved    
class approved(database_of_img):
    num_of_app=0
    def __init__(self, name, img_path):
        super().__init__(name, img_path)
        approved.num_of_app+=1 
    

class verification:
    def __init__(self, frame, face_location, name):
        self.frame = frame
        self.face_location = face_location
        self.name = name
        self.fltr_lst = []
               
    @property
    def face_encoding(self):
        return fc.face_encodings(self.frame, self.face_location)
    

        
     



