import numpy as np

import glob

import sys,os

import cv2 as cv
from scipy.ndimage.filters import gaussian_filter
import math

import scipy.ndimage as ndimage
import scipy.misc as misc

from io import StringIO

import matplotlib as mpl
# mpl.use('Agg')  # optimization for faster rendering than Agg (at least, it is supposed to be)
mpl.rc('pdf', fonttype=42)   # to embed fonts in PDF
import matplotlib.pyplot as plt
plt.ion()
plt.show()

from numpy.fft import fft2,ifft2

import pdb

import pickle as pickle

import RunWeka
#######################################################################
#######################################################################

# image loading functions

# load an image, rescale it, and return it
def imgLoad(fname,scale):
	img = cv.imread(fname,cv.IMREAD_ANYDEPTH)
	#rarely, imread fails, so we try again
	if (img is None):
		img = cv.imread(fname,cv.IMREAD_GRAYSCALE)
	img = scaleDown(img,scale)
	return img
	
def imgColorLoad(fname,scale):
	#~ img = cv.imread(fname,cv.IMREAD_ANYDEPTH)
	img = cv.imread(fname,cv.IMREAD_COLOR)
	#rarely, imread fails, so we try again
	if (img is None):
		img = cv.imread(fname,cv.IMREAD_GRAYSCALE)
	img = scaleDown(img,scale)
	return img

# scale an image and return it
def scaleDown(img,scale):
	newx,newy = int(img.shape[1]*scale),int(img.shape[0]*scale)
	return cv.resize(img, (newx,newy))

####################################################################
####################################################################

#function to I.D. individual plates
def IDplate(filename):
	#filename = '042518/042518-001.tif'
	img = imgLoad(filename, 1)
	#img = img/255
	#print img.shape
	
	#threshold image (img, threshhold value, max value, type)
	val1, pmask = cv.threshold(img, 16000, 65025, cv.THRESH_BINARY)
	#cv.imwrite('testmask.png', pmask)
	
	#list for plate xy positions
	PlateXY = []
	#label image and get lable xy locations
	label, nlabels = ndimage.label(pmask)
	comXY = ndimage.center_of_mass(label*0 + 1.0, label, list(range(nlabels)))
	AREA = ndimage.sum(label*0 + 1.0, label, list(range(nlabels)))


	#print AREA.shape[0]
	for l in range(AREA.shape[0]):
		
		area = AREA[l]
		
		#restrict to labels with areas the size of a plate
		if area > 700000 and area < 1000000 :
			#print area
			XY = comXY[l]
			PlateXY.append(XY)
			
	shape = img.shape
	circles = np.zeros(shape)

	
	#draw image with black circles for plates
	for xy in PlateXY:
		#print xy
		cv.circle(circles, (int(xy[1]),int(xy[0])), 470, 255, thickness=-1)
	
	return circles
		
####################################################################
####################################################################

#function for getting image in ROI
def getROI(img,roi,bDisplay=False):
	roi = roi[1:]
	#print roi
	#pdb.set_trace()
	imgroi = img[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]

	return imgroi
	
####################################################################
####################################################################
#make array from ROIFile
def processROIFile(ROIFILE):
	
	ROI = np.loadtxt(ROIFILE, delimiter=",",skiprows=1, dtype='int')
	#print 'IMPORTED ROI\'S'

	ROI = np.reshape(ROI, (-1,5))
	
	return ROI


#######################################################################
#######################################################################

#go through images and make new image for each plate
def platePROCESS (fname, nfiles,INDIR,OUTDIR,ROI,INPLATE = False, SAVEIMG = False, TESTDIR = None, RED = False):
	CIRCLES = []
	for pic in range(1,nfiles+1):
		filename = INDIR + '/' + fname + '-%03d.tif' % pic
		print(filename)
		if RED:
			img = imgColorLoad(filename, 1)
		else:
			img = imgLoad(filename, 1)
		
		
		if INPLATE:
			circle = IDplate(filename)
			if SAVEIMG:
				circlename = 'circles-%03d.tif' %pic
				cv.imwrite(TESTDIR + '/' + circlename, circle)
		
		i = 0
		#print(ROI.shape)
		for roi in ROI:
			i  +=1
			iplate = getROI(img,roi)
			iplatename = fname + '-%03d.tif' % ((pic-1)*6+i)
			if RED:
				#print('getting red channel')
				iplate = iplate[:,:,2]
			cv.imwrite(OUTDIR + '/' + iplatename, iplate)
			
			if INPLATE:
				icircle = getROI(circle,roi)
				CIRCLES.append(icircle)

			#cv.imwrite(OUTDIR + '/' + 'test2.tif', img)
	
	if INPLATE:		
		with open(fname + '_platecircles.pkl', 'w') as f:
			pickle.dump(CIRCLES, f, protocol=pickle.HIGHEST_PROTOCOL)
		
 
			
#######################################################################
#######################################################################

def plateCOUNT(fname, nfiles, Mask1Dir, minAREA, maxAREA, CSVname, INPLATE = False, SAVEIMG = False, TESTDIR = None):
	
	#load CIRCLE ROIs
	if INPLATE:
		INPLATE = os.path.isfile(fname+'_platecircles.pkl')
		if INPLATE:
			with open(fname+'_platecircles.pkl', 'rb') as f:
				CIRCLES = pickle.load(f)
				
	#######################################################################
	#go through masks and count colonies and write counts to csv file
	
	#Colonies = np.empty[nfiles*6,2]
	f = open(CSVname, 'w')
	f.write('Plate,')
	f.write('Colonies,')
	f.write('\n')
		
	for plate in range(1,nfiles*+1):
		print('processing plate ', plate)
		filename = Mask1Dir + '/' + fname + '-%03d.png' % plate
		img = imgLoad(filename, 1)
		img = 255-img
		im2, contours, hierarchy = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
		
		contours_plate = []
		
		if INPLATE:
			platetest = np.where(CIRCLES[plate-1] !=0)

			if platetest[0] != []:
				GOODPLATE = True
			else:
				GOODPLATE = False
		else:
			GOODPLATE = True
			
		# calculate area and filter into new array
		for con in contours:
			if INPLATE and GOODPLATE:
				GoodCon = False
				for point in con:
					y = point[0][0]
					x = point[0][1]

					if CIRCLES[plate-1][x,y] != 0:
						GoodCon = True

				if not GoodCon:
					continue
			#check area
			area = cv.contourArea(con)
			#print 'area = ', area
			if not minAREA < area < maxAREA:
				continue
			
			#circularity is not super useful
			#~ #check circularity 
			#~ perimeter = cv.arcLength(con, True)
			#~ #print 'perimeter = ', perimeter
			#~ if perimeter == 0:
				#~ continue
			#~ circularity = 4*math.pi*(area/(perimeter*perimeter))
			#~ #print circularity
			#~ if 0.4 < circularity < 1.0:
			contours_plate.append(con)

			
		####################################################################
		
		if SAVEIMG:
			#pdb.set_trace()
			fimg = np.zeros(img.shape)

			cv.drawContours(fimg, contours_plate, -1, 255, 1)
			if INPLATE:
				plateimg = CIRCLES[plate-1]
				testimg = plateimg*.5 + fimg
			else:
				testimg = fimg
			testname = 'countimg-%03d.tif' %plate
			cv.imwrite(TESTDIR +'/'+testname, testimg)
			
		
			
		f.write(str(plate) + ',')
		f.write(str(len(contours_plate)) + ',')
		f.write('\n')			
		

	f.close()	

####################################################################
###################################################################

#main argument
def main(argv):
	if argv[0] != None:
		fname,nfiles,INDIR,OUTDIR,ROI,INPLATE, SAVEIMG, TESTDIR,RED = argv[0]
		platePROCESS(fname,nfiles,INDIR,OUTDIR,ROI,INPLATE, SAVEIMG, TESTDIR,RED)
	if argv[1] != None:
		RunWeka.batchsegment(argv[1])
	if argv[2] !=None:
		fname, nfiles, Mask1Dir, minAREA, maxAREA, CSVname, INPLATE, SAVEIMG, TESTDIR = argv[2]
		plateCOUNT(fname, nfiles, Mask1Dir, minAREA, maxAREA, CSVname, INPLATE, SAVEIMG, TESTDIR)
		
###################################################################
###################################################################

# way to run as a module
def run(argv):
	main(argv)
	
###################################################################
###################################################################
# parameters that need to be adjusted when running from terminal


if __name__ == "__main__":
	
	#Image filename preceding channel indication (e.g. 20171212_book)
	#must precede -%03d.tif
	fname = '051218'
	#number of images (assumes 6 plates per image)
	nfiles = 32
	OUTDIR = fname+'plates'
	if not os.path.isdir(OUTDIR):
		os.system('mkdir ' + OUTDIR)
	#set to true to make individual plate images
	iPLATES = False
	#set to true to classify individual plate images
	MASKS = False
	#are you counting the colonies
	COUNT = True
	#limit to within plates itself based on thresholding
	INPLATE = True
	
	INDIR = '051218'
	
	#set to true to save contoured masks and plate outline used to get final counts
	SAVEIMG = True
	if SAVEIMG:
		TESTDIR = INDIR + '_test'
		if not os.path.isdir(TESTDIR):
			os.system('mkdir ' + TESTDIR)
	else:
		TESTDIR = None

	if iPLATES:
		ROIFILE = '042518_ROIs.csv'
		ROI = processROIFile(ROIFILE)
		RED = False

	if MASKS:
		#location of ImageJ executable file
		IMAGEJ = '/media/shared/drive/programs/newFiji/Fiji.app/ImageJ-linux64'
		#get working directory
		WorkDir = os.getcwd()

		#Directory containing the images
		ImageDir = OUTDIR
		AlignDir = ImageDir
		
		#first frame of images
		FIRSTFRAME = 1
		#last frame of images
		FRAMEMAX = nfiles*6
		
		#name of Directory to output Masks made relative to image directory
		Mask1Dir = INDIR + '_masks'
		runMask1Dir = Mask1Dir
		
		#classifier file relative to working directory
		classifierfile1 = '022218_colonies2.model'
		#classifierfile1 = getfilename('Enter path to classifier relative to working directory (e.g. Aligned/classifier.model): ')
		
		#True if producting probablity masks; False for binary masks
		Useprobability = False
		
		ext = 'tif'
		
		cores = 21
		

		
		if not os.path.isdir(runMask1Dir):
			os.system('mkdir ' + runMask1Dir)
		#else:
			#os.system('rm ' + runMask1Dir + '/' + fname + '*.png')

	if COUNT:
		if not MASKS:
			Mask1Dir = INDIR + '_masks'
		CSVname = INDIR + '_colony_count.csv'
		

				
		#parameters to exclude labels of a certain size
		minAREA = 10
		maxAREA= 10000
	
	if iPLATES:
		PLATEPROCESS = [fname,nfiles,INDIR,OUTDIR,ROI,INPLATE, SAVEIMG, TESTDIR,RED]
	else:
		PLATEPROCESS = None
	if MASKS:
		WekaARG2 = [IMAGEJ, Useprobability, WorkDir + '/', AlignDir + '/', runMask1Dir + '/', FIRSTFRAME, FRAMEMAX, fname, ext, classifierfile1, cores] 
	else:
		WekaARG2 = None
	if COUNT:
		PLATECOUNT = [fname, nfiles, Mask1Dir, minAREA, maxAREA, CSVname, INPLATE, SAVEIMG, TESTDIR]
	else:
		PLATECOUNT = None

	main([PLATEPROCESS,WekaARG2,PLATECOUNT])
#######################################################################
#######################################################################


