from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    BatchNormalization, SeparableConv2D, Conv2D, MaxPooling2D, Activation, Flatten, Dropout, Dense
)
from tensorflow.keras import backend as K
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from imageai.Detection import ObjectDetection
import os
from os import listdir
from os.path import isfile, join
import cv2
import re
import numpy as np
import matplotlib.pyplot as plt
from google.colab.patches import cv2_imshow

#-------------------------------------------OBJECT DETECTION PHASE-------------------------------------------

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
execution_path = os.getcwd()


detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath( os.path.join(execution_path , "/content/drive/MyDrive/Project/yolo.h5"))
detector.loadModel()
#custom_objects = detector.CustomObjects(car=True, motorcycle=True, pizza=True)
detections, objects_path = detector.detectObjectsFromImage(input_image=os.path.join(execution_path , "/content/drive/MyDrive/Project/input.jpg"), 
                                                           output_image_path=os.path.join(execution_path , "object_output.jpg"),
                                                           minimum_percentage_probability=50,  extract_detected_objects=True)
#detections = detector.detectCustomObjectsFromImage(custom_objects=custom_objects, input_image=os.path.join(execution_path , "input.jpg"), output_image_path=os.path.join(execution_path , "output.jpg"), minimum_percentage_probability=30)
lst = []
object_list = []
obS = 0
for eachObject, eachObjectPath in zip(detections, objects_path):
    print(eachObject["name"] , " : " , eachObject["percentage_probability"], " : ", eachObject["box_points"] )
    if eachObject["name"] != "person":
      object_list.append(eachObject["name"])
    lst.append(eachObject["percentage_probability"])
    print("Object's image saved in " + eachObjectPath)
    print("--------------------------------")
obS = sum(lst)
avg = obS/len(detections)
print(avg)
    
 # images[n] = cv2.imread( join(mypath,onlyfiles[n]) )
files = os.listdir('/content/')

#-------------------------------------------EMOTION DETECTION PHASE-------------------------------------------

# plots accuracy and loss curves
def plot_model_history(model_history):
    """
    Plot Accuracy and Loss curves given the model_history
    """
    fig, axs = plt.subplots(1,2,figsize=(15,5))
    # summarize history for accuracy
    axs[0].plot(range(1,len(model_history.history['accuracy'])+1),model_history.history['accuracy'])
    axs[0].plot(range(1,len(model_history.history['val_accuracy'])+1),model_history.history['val_accuracy'])
    axs[0].set_title('Model Accuracy')
    axs[0].set_ylabel('Accuracy')
    axs[0].set_xlabel('Epoch')
    axs[0].set_xticks(np.arange(1,len(model_history.history['accuracy'])+1),len(model_history.history['accuracy'])/10)
    axs[0].legend(['train', 'val'], loc='best')
    # summarize history for loss
    axs[1].plot(range(1,len(model_history.history['loss'])+1),model_history.history['loss'])
    axs[1].plot(range(1,len(model_history.history['val_loss'])+1),model_history.history['val_loss'])
    axs[1].set_title('Model Loss')
    axs[1].set_ylabel('Loss')
    axs[1].set_xlabel('Epoch')
    axs[1].set_xticks(np.arange(1,len(model_history.history['loss'])+1),len(model_history.history['loss'])/10)
    axs[1].legend(['train', 'val'], loc='best')
    fig.savefig('plot.png')
    plt.show()

# Define data generators
#train_dir = 'data/train'
#val_dir = 'data/test'

num_train = 28709
num_val = 7178
batch_size = 64
num_epoch = 50

'''train_datagen = ImageDataGenerator(rescale=1./255)
val_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(48,48),
        batch_size=batch_size,
        color_mode="grayscale",
        class_mode='categorical')

validation_generator = val_datagen.flow_from_directory(
        val_dir,
        target_size=(48,48),
        batch_size=batch_size,
        color_mode="grayscale",
        class_mode='categorical')
'''
# Create the model
model = Sequential()

model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48,48,1)))
model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(1024, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(7, activation='softmax'))
'''
# Training the model
if mode == "train":
    model.compile(loss='categorical_crossentropy',optimizer=Adam(lr=0.0001, decay=1e-6),metrics=['accuracy'])
    model_info = model.fit_generator(
            train_generator,
            steps_per_epoch=num_train // batch_size,
            epochs=num_epoch,
            validation_data=validation_generator,
            validation_steps=num_val // batch_size)
    plot_model_history(model_info)
    model.save_weights('model.h5')
'''
# loading the model

model.load_weights('/content/drive/MyDrive/Project/model.h5')

# prevents openCL usage and unnecessary logging messages
cv2.ocl.setUseOpenCL(False)

# dictionary which assigns each label an emotion (alphabetical order)
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}


frame = cv2.imread("/content/object_output.jpg")
facecasc = cv2.CascadeClassifier('/content/drive/MyDrive/Project/haarcascade_frontalface_default.xml')
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
faces = facecasc.detectMultiScale(gray,scaleFactor=1.3, minNeighbors=5)

expression_list = []

for (x, y, w, h) in faces:
    cv2.rectangle(frame, (x, y), (x+w, y+h+10), (255, 0, 0), 2)
    roi_gray = gray[y:y + h, x:x + w]
    cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
    prediction = model.predict(cropped_img)
    maxindex = int(np.argmax(prediction))
    expression_list.append(maxindex)
    cv2.putText(frame, emotion_dict[maxindex], (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
cv2.imwrite('/content/output.png', frame)

small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5) 
cv2_imshow(small)

#function to check if all elements are the same in expression_list
res = False
def check_match(cst):
    if len(cst) < 0 :
        res = True
    res = all(ele == cst[0] for ele in cst)
      
    if(res):
      print("They are all",emotion_dict[expression_list[0]])
    else:
      for pp in range(len(faces)):
        print("The expression of person", pp+1, "is", emotion_dict[expression_list[pp]])

if len(faces) > 0:
  if len(faces) == 1:
    print("\n\nThere is 1 person in this image. The expression of the person is" ,emotion_dict[maxindex])
  else:
    print("\nThere are",len(faces),"people in this image.")
    check_match(expression_list)
else:
  print("\n\nThere is nobody in this image.")

if not object_list:
  print("There are no objects near the person.")
else:
  print ("The objects that are found in the image are:")
  for op in range(len(object_list)):
    print(object_list[op])
