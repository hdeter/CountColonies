
///////////////////////////////////
///////////////////////////////////

// set to true if this is the first image in training
//bFirstImage = false
bFirstImage = getBoolean("Would you like to make a new classifier?");
//set to true if training a classifier
if (bFirstImage){
	training = false;
}
else{
	training =  getBoolean("Would you like to train an existing classifier?");
}

//set to true if classifying a phase image (will get probabilities)
notMask = false;

// root directory (directory with images and classifier)
//be sure to include the slash at the end
//rootDir="/home/hdeter/Downloads/Aligned/"
rootDir = getString("Enter the path to your image directory", "/home/user/DeterZip20/Aligned");
rootDir = rootDir + "/";

//root filenames to open 

//filename= "Ecoli_GFPtetLAA-p-"
filename= getString("Filename of image to classify preceding number", "040518-");



//ext = getString("File type of images (e.g. tif)", "tif");
//ext = "." + ext
ext = "."+ "tif";
///////////////////////////////////
///////////////////////////////////



// scaling factor for image (try to make this consistent across images)
//SCALE = 1

function classify(classiferFile,dataFile){
	// get image title information (sometimes useful)
	origTitle = getTitle();
	origTitle = origTitle;
	scaleTitle = origTitle + "_scaled";
	//print(origTitle);
	
	// shrink image
	//run("Scale...", "x="+SCALE+" y="+SCALE+" interpolation=Bilinear average create title=" + scaleTitle);


	// turn the image into grayscale (many ways to do this, but this is one way)
	run("32-bit");
		
	if (notMask){	
		// size to filter for background substration and regularization
		MAX_SIZE_FILTER = 100;
		run("Bandpass Filter...", "filter_large="+MAX_SIZE_FILTER+" filter_small=0 suppress=None tolerance=5");

	}

	///////////////////////////////////
	///////////////////////////////////
	
	
	// open segmentation tool, apply segmentation
	run("Trainable Weka Segmentation");
	wait(2000);			// wait to allow Weka tool to open
	

	call("trainableSegmentation.Weka_Segmentation.loadClassifier", classifierFile);
	call("trainableSegmentation.Weka_Segmentation.loadData", dataFile);
	}
	

	///////////////////////////////////
	///////////////////////////////////
function firstclassify(){
	// get image title information (sometimes useful)
	origTitle = getTitle();
	origTitle = origTitle;
	scaleTitle = origTitle + "_scaled";
	//print(origTitle);
	
	// shrink image
	//run("Scale...", "x="+SCALE+" y="+SCALE+" interpolation=Bilinear average create title=" + scaleTitle);


	// turn the image into grayscale (many ways to do this, but this is one way)
	run("32-bit");
		
	if (notMask){	
		// size to filter for background substration and regularization
		MAX_SIZE_FILTER = 100;
		run("Bandpass Filter...", "filter_large="+MAX_SIZE_FILTER+" filter_small=0 suppress=None tolerance=5");

	}

	///////////////////////////////////
	///////////////////////////////////
	
	
	// open segmentation tool, apply segmentation
	run("Trainable Weka Segmentation");
	wait(2000);			// wait to allow Weka tool to open
	
	
}
	///////////////////////////////////
	///////////////////////////////////
function runClassify(rootDir,filename,model,data,frame){
		frame = IJ.pad(frame,3);
		open(rootDir+filename+frame + ext);
		classify(model,data); }
	///////////////////////////////////
	///////////////////////////////////
function runfirstClassify(rootDir,filename,frame){
		frame = IJ.pad(frame,3);
		print (rootDir+filename+frame + ext);
		open(rootDir+filename+frame + ext);
		firstclassify(); }

frame = getNumber("What number image do you wish to train your classifier on?", 1);
if (bFirstImage){
	runfirstClassify(rootDir,filename,frame);
	waitForUser("Train and save the classifier (into the image directory) in Weka. When finished close Weka and image (DO NOT save changes to the original image) then press OK below");
	training = getBoolean("Do you wish to continue training your classifier?");
	if (training){
		frame = getNumber("What number image do you wish to train your classifier on?", 2);
	}
}
while (training){
	// segmentation files for use
	classifierFile = getString("Name of classifier (relative to the working directory)", "classifier.model");
	classifierFile = rootDir+classifierFile;
	dataFile = getString("Name of data file (relative to the working directory)", "data.arff");
	dataFile = rootDir+dataFile;
	runClassify(rootDir,filename,classifierFile,dataFile,frame);
	waitForUser("Train and save the classifier (into the image directory) in Weka. When finished close Weka and image (DO NOT save changes to the original image) then press OK below");
	training = getBoolean("Do you wish to continue training your classifier?");
	if (training){
		frame = getNumber("What number image do you wish to train your classifier on?", 2);
	}
	//runClassify(rootDir2,filename2,frame2,classifierFile2,dataFile2);
} 
//eval("script", "System.exit(0);");
run("Quit");
