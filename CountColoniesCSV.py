
import string
import sys
import os
import time
from multiprocessing import Pool
from StringIO import StringIO
import numpy as np
import pdb


#import custom python scripts
import Agar_plate_processing
import RunWeka
#######################################################################
#######################################################################

def processCSV(CSVFILE):
    print 'Processing ' + CSVFILE
    TXT = open(CSVFILE, 'rb').read()

    # trick for newline problems
    TXT = StringIO(TXT.replace('\r','\n\r'))
    TXT2 = TXT
    #method that removes headers
    CSV = np.genfromtxt(TXT, delimiter=",",skip_header=1, dtype='str')  
    rows = CSV.shape[0]
    
    print 'process complete'
    
    return CSV

############################################################################
############################################################################

def FindPrompt(Prompt,loc = 1):
	row = np.where(PROMPTS[:,0] == Prompt)[0]
	print Prompt, PROMPTS[row,loc][0]
	return PROMPTS[row,loc][0]

############################################################################
############################################################################

# helper function for input
def text_input(DISPLAY,loc=1):
	if CSVPrompt:
		return str(FindPrompt(DISPLAY,loc))
	else:
		string = ''
		while (string == ''):
			string = raw_input(DISPLAY)	
		return string
		
def raw_text_input(DISPLAY):
	str = ''
	while (str == ''):
		str = raw_input(DISPLAY)	
	return str
	
# helper function for input
def bool_input(DISPLAY):
	if CSVPrompt:
		if (FindPrompt(DISPLAY) == 'y' or FindPrompt(DISPLAY) == 'Y'): 
			return True
		else: 
			return False
	else:
		bValue = None
		while (bValue is None):
			str = raw_input(DISPLAY)
			if (str=='y' or str=='Y'):
				bValue = True
			elif (str=='n' or str=='N'):
				bValue = False
		return bValue

# helper function for input
def raw_bool_input(DISPLAY):
	bValue = None
	while (bValue is None):
		str = raw_input(DISPLAY)
		if (str=='y' or str=='Y'):
			bValue = True
		elif (str=='n' or str=='N'):
			bValue = False
	return bValue

# helper function for input
def int_input(DISPLAY, loc = 1):
	if CSVPrompt:
		return int(FindPrompt(DISPLAY,loc))
	else:
		iValue = None
		while (iValue is None):
			str = raw_input(DISPLAY)
			try:
				iValue = int(str)
			except:
				iValue = None
		return iValue
	
# helper function for input
def float_input(DISPLAY):
	if CSVPrompt:
		return float(FindPrompt(DISPLAY))
	else:
		iValue = None
		while (iValue is None):
			str = raw_input(DISPLAY)
			try:
				iValue = float(str)
			except:
				iValue = None
		return iValue
####################################################################
####################################################################

def getfilename(prompt):
	ISFILE = False
	#check once with prompt answers
	FILENAME = text_input(prompt)
	ISFILE = os.path.isfile(FILENAME)
	if not ISFILE:
		print 'cannot find file'
	
	#assume prompt answer was wrong and reprompt question in terminal
	while not ISFILE:
		FILENAME = text_input(prompt)
		ISFILE = os.path.isfile(FILENAME)
		if not ISFILE:
			print 'cannot find file'
	return FILENAME
	
def getdirname(prompt):
	ISPATH = False
	#check once with prompt answers
	PATHNAME = text_input(prompt)
	ISPATH = os.path.isdir(PATHNAME)
	if not ISPATH:
		print 'cannot find directory ' + PATHNAME
	
	#assume prompt answers was wrong and reprompt question in terminal
	while not ISPATH:
		PATHNAME = raw_text_input(prompt)
		ISPATH = os.path.isdir(PATHNAME)
		if not ISPATH:
			print 'cannot find directory ' + PATHNAME
	return PATHNAME

#this one just used for prompt file
def getcsvname(prompt):
	ISFILE = False
	while not ISFILE:
		FILENAME = raw_text_input(prompt)
		ISFILE = os.path.isfile(FILENAME)
		if not ISFILE:
			print 'cannot find file ' + FILENAME
	return FILENAME

####################################################################
####################################################################
####################################################################

CSVPrompt = False

CSVPrompt = bool_input('Do you have a csv file with prompted answers? (Y/N):')
#~ print CSVPrompt
if CSVPrompt:
	PROMPTCSV = getcsvname('Enter the filename of the csv file containing prompted answers relative to the working directory (e.g. prompts.csv):')
	PROMPTS = processCSV(PROMPTCSV)
	
####################################################################
####################################################################

iPLATES = bool_input('Are there multiple plates in your images (Y/N):')
if not iPLATES:
	MASKS = bool_input('Do you need to classify the images (Y/N):')
else:
	MASKS = True
COUNT = bool_input('Do you wish to count the number of colonies (Y/N):')
#~ if COUNT:
	#~ INPLATE = bool_input('Do you wish to exclude the edges of the plate (Y/N):')
#~ else:
	#~ INPLATE = False
INPLATE = False
SAVEIMG = bool_input('Do you wish to save an image with counted colonies outlined (Y/N):')

#get working directory
WorkDir = os.getcwd()
print 'Your working directory is ', WorkDir

INDIR = getdirname('Enter the name of the directory (relative to the working directory) containing the images to process:')
FNAMECHECK = False
while not FNAMECHECK:
	fname = text_input('Enter the filename preceding "-plate number" (e.g. 050318):')
	FNAMECHECK = os.path.isfile(INDIR + '/' + fname + '-001.tif')
	if not FNAMECHECK:
		print 'Could not find file ', fname + '-001.tif', ' in ', INDIR
NFILECHECK = False
while not NFILECHECK:
	nfiles = int_input('How many images are there?:')
	nfilename = fname + '-%03d.tif' %nfiles
	NFILECHECK = os.path.isfile(INDIR + '/' + nfilename)
	if not NFILECHECK:
		print 'could not find file:', nfilename, ' in ', INDIR
OUTDIR = INDIR + '_plates'
if not os.path.isdir(OUTDIR):
	os.system('mkdir ' + OUTDIR)

if SAVEIMG:
	TESTDIR = INDIR + '_counts'
	if not os.path.isdir(TESTDIR):
		os.system('mkdir ' + TESTDIR)
else:
	TESTDIR = None

if iPLATES:
	ROIFILE = getfilename('Please enter the path (relative to the working directory) to the CSV file containing ROIs for individual plates (e.g. 042518_ROIs.csv):')
	ROI = Agar_plate_processing.processROIFile(ROIFILE)
	PLATEPROCESS = fname,nfiles,INDIR,OUTDIR,ROI,INPLATE, SAVEIMG, TESTDIR
else:
	PLATEPROCESS = None
if MASKS:
	IJPATH = False
	while not IJPATH:
		IMAGEJ = text_input('Enter absolute path to ImageJ executable file (e.g. /media/shared/drive/programs/newFiji/Fiji.app/ImageJ-linux64):')
		IJPATH = os.path.isfile(IMAGEJ)
		IJEX = os.access(IMAGEJ,os.X_OK)
		if not IJPATH and IJEX:
			print 'could not find application'

	
	CLASSIFIER = bool_input('Do you have a trained classifier (Y/N):')
	if not CLASSIFIER:
		#to use with RunWeka.training
		WekaARG1 = [IMAGEJ, WorkDir + '/']
		openFiji = False
		while not openFiji:
			print 'Please open an instance of Fiji. '
			time.sleep(2)
			openFiji = bool_input('Is there an open instance of Fiji (Y/N):')
			if not openFiji:
				print 'Please open Fiji'
		RunWeka.training(WekaARG1)

	if 'linux' in IMAGEJ:
		PROCESS = bool_input('Would you like to batch classify the images in the background (it is faster Y/N):')
	else:
		PROCESS = False
	if PROCESS:
		cores = int_input('How many processes are available to use for multiprocessing (set to 1 for no multiprocessing):')
	else:
		cores = None	
		#Directory containing the images
	
	if iPLATES:
		ImageDir = OUTDIR
	else:
		ImageDir = INDIR
	AlignDir = ImageDir
	
	#first frame of images
	FIRSTFRAME = 1
	#last frame of images
	FRAMEMAX = nfiles*6
	
	#name of Directory to output Masks made relative to image directory
	Mask1Dir = INDIR + '_masks'
	runMask1Dir = Mask1Dir
	
	#classifier file relative to working directory
	classifierfile1 = getfilename('Enter path to classifier relative to working directory (e.g. 022218_colonies2.model):')
	#classifierfile1 = getfilename('Enter path to classifier relative to working directory (e.g. Aligned/classifier.model): ')
	
	#True if producting probablity masks; False for binary masks
	Useprobability = False
	
	ext = 'tif'
	
	if not os.path.isdir(runMask1Dir):
		os.system('mkdir ' + runMask1Dir)
	WekaARG2 = [IMAGEJ, Useprobability, WorkDir + '/', AlignDir + '/', runMask1Dir + '/', FIRSTFRAME, FRAMEMAX, fname, ext, classifierfile1, cores] 
else:
	WekaARG2 = None
if COUNT:
	if not MASKS:
		Mask1Dir = getdirname('Enter path to directory (relative to the working directory) containing binary masks of plates (e.g. 050318_masks):')
	CSVname = INDIR + '_colony_count.csv'
	minAREA = int_input('Enter the minimum area to count (e.g. 10):')
	maxAREA = int_input('Enter the max area to count (e.g. 10000):')
	PLATECOUNT = fname, nfiles, Mask1Dir, minAREA, maxAREA, CSVname, INPLATE, SAVEIMG, TESTDIR
else:
	PLATECOUNT = None



ARG = [PLATEPROCESS,WekaARG2,PLATECOUNT]
Agar_plate_processing.run(ARG)
