# CountColonies
Using machine learning to identify and count objects (e.g. colonies on agar plates). We use Weka Segmentation (available through ImageJ) to train the classifier and classify images. The entire pipeline is run using CountColoniesCSV.py.

**Important note:** Images must be saved as name-001.tif, in which name can be any string (e.g. 050318-001.tif, plate-001.tif) and the number increases in increments of one (001, 002, etc).

**Applications:**
The Butzin lab (https://sites.google.com/site/nicholascbutzin/) uses these scripts to count colonies on agar plates scanned using a flatbed scanner. However, the scripts could also be applied to count any objects identifiable with the Weka Machine learning tool. 

**Prerequisite Software Installation (Linux or Mac)**
1.	Install Anaconda 3.7 (https://www.anaconda.com/distribution/) 
2.	Add conda to the PATH: export PATH=~/anaconda3/bin:$PATH
3.	Install OpenCV through Anaconda: conda install opencv
4.	Download and install Fiji ImageJ (available here: https://imagej.net/Fiji/Downloads)

**Running CountColoniesCSV.py**
1. In the terminal change directory to the file containing the scripts (e.g. cd /home/directory).
2. Ensure that a folder containing the images to count is in the same directory as the scripts.
3. Enter the command "python CountColonyCSV.py"
4. Follow the prompts in the terminal

**Training a classifier**
A classifier is trained through the Trainable Weka Segmentation plugin in Fiji (https://imagej.net/Trainable_Weka_Segmentation). The training pipeline can be run through CountColonyCSV.py or by running Segmentation.ijm directly in Fiji. 

**Using the prompts file:**
There is an option to use a csv file to answer the prompts rather than answering them in the terminal. It requires that the first column of the file match the prompts exactly, and as such a template file is provided (prompts.csv). The prompts may then be answered in the second column as one would respond in the terminal.

**Making a a csv file to indicate regions of interest (ROIs):**
There is an option to count multiple plates (i.e. regions of interest) within a single image that assumes the plates are within the same regions throughout each image. To do so requires an ROI file that indicates these regions, which can be made in ImageJ using the following method.
1.	Open the image for which you are creating an ROI in ImageJ. To observe the same region throughout multiple images import an image sequence using “File” ➔ “Import” ➔ “Image Sequence.”
2.	Remove any scale associated with the images using the “Set Scale” feature under the Analyze tab (the scale must be in pixels).
3.	Set measurements (under the Analyze tab) to only measure the bounding rectangle (“Bounding rectangle” should be the only checked box) with 0 decimal places (the results need to be whole numbers). 
4.	Select the desired region with the rectangular selection tool and use the Measure tool (Ctrl+M), located in the Analyze tab.
5.	Repeat step 4 for each region of interest.
6.	Save the measurements table as a csv file (e.g. filename.csv) in the same directory as the scripts. 

The final table should have five columns. Left to right: ROI number, BX, BY, Width and Height. BX and BY indicate the X and Y  coordinates for the top left corner of the selection.

**Citation information**
Please cite Deter et al. ACS Synth. Biol. 2020, 9, 1, 95-103 (https://doi.org/10.1021/acssynbio.9b00358)

**Contact information:**
Heather S. Deter. Graduate Assistant, South Dakota State University. Email: hdeter2013@gmail.com

