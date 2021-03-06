
# -*- coding:Utf_8 -*-
#This script is for using the trained U-NET model, To make predictions on other images of our dataset.
# uploading packages 

from PIL import Image
import matplotlib.pyplot as plt
import numpy  as np
import math
import os
import sys
import random
from skimage.io import imsave,imread

import time
import datetime

import model_unet 
import data_normalizing
import load_train_test_data
import measurment_functions


from tensorflow import keras
from keras.models import Model,load_model,save_model
from keras.layers import Input
from keras.layers.core import Dropout
from keras.layers.convolutional import Conv2D, Conv2DTranspose
from keras.layers.pooling import MaxPooling2D
from keras.layers.merge import concatenate
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.preprocessing.image import ImageDataGenerator


# Load_weights = True : if we load the existing model that is already driven.
# validation_split, batch_size, epochs are the parameters of the model.
# INPUT_WIDTH =96(256), INPUT_HEIGHT = 96(256), INPUT_CHANNELS = 7 the sizes of our data.
# path : is the folder's path of image to predict.
# threshold : it is the discrimination value of the predicted pixels, we say a pixel belongs to the class 'leaves' 
# if its predicted value exceeds such threshold, otherwise it is of the calasse 'other'. To find an optimal threshold,
# you can use the function "optimal_threshold_desc" in the script "measurement_functions".
# Prediction_Images_Mean : 
# Normalization : is the type of normalization
# step : is the displacement step of the prediction patch


def Prediction(Path='',INPUT_WIDTH =256, INPUT_HEIGHT = 256,INPUT_CHANNELS = 7,threshold=0.5,Prediction_Images_Mean=True,
	Normalization='Normalisation_by_image_by_colomn',step=30):

	# Load model U-NET
	model=model_unet.Model_Unet(INPUT_WIDTH =INPUT_WIDTH , INPUT_HEIGHT = INPUT_HEIGHT,INPUT_CHANNELS = INPUT_CHANNELS)
	# Load of weights's model
	model = load_model('model-U_NET.h5')

	print(Path+'/'+'measure.txt')
	f=open(Path+'/'+'measure.txt','w')

	f.write('image prediction date: '+str(datetime.datetime.now())+'\n')
	f.write('the size of images input and output:'+'\n')
	f.write('INPUT_WIDTH= '+str(INPUT_WIDTH)+'  '+'INPUT_CHANNELS='+str(INPUT_CHANNELS)+'\n')
	f.write('Normalization_data:'+str(Normalization)+' threshold_opt='+str(threshold)+'\n')

	# Image prediction time
	start = time. time()
	if Prediction_Images_Mean==False:
		# Classical rediction of Images
		# In the classic prediction, we take the multspectral and thermal images, we do the normalization, then we apply the trained model of U-NET.
		for image in os.listdir(Path+str(ImageArray)):
			image_Path=Path+str(ImageArray)+str(image)
			Image=np.load(image_path)
			
			X_Image=Image[0:(np.shape(Image)[0]//INPUT_WIDTH)*INPUT_WIDTH,0:(np.shape(Image)[1]//INPUT_HEIGHT)*INPUT_HEIGHT]
			Y_Image=Image[0:(np.shape(Image)[0]//INPUT_WIDTH)*INPUT_WIDTH,0:(np.shape(Image)[1]//INPUT_HEIGHT)*INPUT_HEIGHT,0]
			
			X_Image_data=np.zeros([1,(np.shape(Image)[0]//INPUT_WIDTH)*INPUT_WIDTH,(np.shape(Image)[1]//INPUT_HEIGHT)*INPUT_HEIGHT,INPUT_CHANNELS], dtype=np.float32)
			X_Image_data[0,:,:,:]=X_Image
			X_Image_data_Normal=(X_Image_data)
			print(np.max(X_Image_data_Normal))
			print(np.min(X_Image_data_Normal))
			for ii in range(0,np.shape(X_Image_data_Normal)[1]-INPUT_WIDTH,INPUT_WIDTH):
				for jj in range(0,np.shape(X_Image_data_Normal)[2]-INPUT_HEIGHT,INPUT_HEIGHT):
					print(ii,jj)
					X_pred=np.zeros((INPUT_WIDTH,INPUT_HEIGHT,7),dtype=np.float32)
					Mask_pred=np.zeros((INPUT_WIDTH,INPUT_HEIGHT),dtype=np.uint8)
					X_pred=data_normalizing.Normalizing_by_image_by_column(X_Image_data_Normal[:,ii:ii+INPUT_WIDTH,jj:jj+INPUT_HEIGHT,:])
					results = model.predict(X_pred,verbose=1)
					print(np.shape(results))
					for i in range(INPUT_WIDTH):
						for j in range(INPUT_HEIGHT):
							if results[0,i,j] >= seuil_desc: 
								Mask_pred[i,j]=255
							else:
								Mask_pred[i,j]=0
			
					Y_Image[ii:ii+INPUT_WIDTH,jj:jj+INPUT_HEIGHT]=Mask_pred
			Y_Image_pred=Image.fromarray(Y_Image.astype('uint8')) 
			Y_Image_pred.save(EVALUATION_PATH+'/'+str(seuil_desc)+str(image))

			end = time. time()
			f.write('\n The prediction time of this Image +',str(image)+' :'+str(end-start)+'seconds')

	else:
		
		for image in os.listdir(Path+str(ImageArray)):
			image_Path=Path+str(ImageArray)+str(image)
			Image=np.load(image_path)
			# To improve the prediction, we have introduce the array_mean variable. We make several predictions 
			# on the image by moving the patch square of 256 * 256 pxels (96 * 96, resp) with a step called "step".
			# At the end, we take the average of the values obtained from each pixel on the different predictions.
			# NB_Pred : it is the matrix of prediction numbers of each pixel of the image to predict
			NB_Pred=np.zeros([Image.shape[0],Image.shape[1]],dtype=np.uint16)
			INPUT=np.zeros([1,Image.shape[0],Image.shape[1],INPUT_CHANNELS],dtype=np.float32)
			INPUT[0,:,:,:]=Image
			INPUT_Normal=Data_Normalization.data_Normalisation_by_image_by_column(INPUT)
			for x in range(0,Image.shape[0]-INPUT_WIDTH,step):
				for y in range(0,Image.shape[1]-INPUT_HEIGHT,step):
					Input_data=np.zeros([1,INPUT_WIDTH,INPUT_HEIGHT,INPUT_CHANNELS],dtype=np.float32)
					Input_data[0,:,:,:]=INPUT_Normal[:,x:x+INPUT_WIDTH,y:y+INPUT_HEIGHT,:]
					results = model.predict(Input_data,verbose=1)
					for i in range(INPUT_WIDTH):
						for j in range(INPUT_HEIGHT):
							Prediction[x+i,y+j]+=results[0,i,j]
							NB_Pred[x+i,y+j]+=1	
			Prediction[np.where(NB_Pred>0)]/=NB_Pred[np.where(NB_Pred>0)]
			Prediction[Prediction<=seuil_desc]=0
			Prediction[Prediction>=seuil_desc]=255
			imsave(EVALUATION_PATH+'/'+str(seuil_desc)+str(image),Prediction)
			end = time. time()
			f.write('\n The time of execution"s prediction of the Image +',str(image)+' :'+str(end-start)+'seconds')
	f.close()

# Example of prediction 

path='⁨/Users/rafikarezki/Desktop/U-NET_SEGMENTATION/data⁩/Image_to_pred⁩'

Prediction(Path=path,INPUT_WIDTH =96, INPUT_HEIGHT = 96,INPUT_CHANNELS = 7, threshold=0.5, Prediction_Images_Mean=True,
	Normalization='Normalisation_by_image_by_colomn', step=30)











