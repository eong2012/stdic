import sys
import os
import re
from deformdata import DeformationData
import masterdata
import time
from dffexporter import DffExporter, DffExportParameters

class FolderAnalyzer:

	def __init__(self, pathname, dffpath, masterdata, deformdata):
		if not os.path.exists(pathname):
			raise Exception("Invalid path: " + pathname)
		if not os.path.exists(dffpath):
			os.mkdir(dffpath)
		self.deformdata = deformdata
		self.masterdata = masterdata
		self.set('Pathname', pathname)
		self.set('DffPathname', dffpath)
		if self.check('Verbose'):
			self.verbose = self.get('Verbose')
		else:
			self.verbose = 3

	def analyze(self):
		self.__analyzePictures__()

	def __analyzePictures__(self):		
		pathname = self.get('Pathname')
		if self.verbose > 2:
			print "Searching path: " + pathname
		pathsplit = os.path.split(pathname)
		if len(pathsplit[1]) == 0:
			pathsplit = os.path.split(pathsplit[0])
		self.set('Name', pathsplit[1])
		self.set('Pictures', self.sortPictures(pathname))
		if self.verbose > 0:
			print "Starting registeration..."
		analyzesDone	= 0
		analyzesSkipped	= 0
		analyzesLeft	= len(self.get('Pictures'))-1
		analyzesMaxExists = self.check('AnalyzesMax')
		if analyzesMaxExists:
			analyzesMax = self.get('AnalyzesMax')
			if analyzesMax < analyzesLeft:
				analyzesLeft = analyzesMax		
		writeCoefs = False
		if self.check('WriteCoefs'):
			if self.get('WriteCoefs') == 'True':
				writeCoefs = True
		timetaken		= 0
		totaltimetaken	= 0
		pictures	= self.get('Pictures')
		analyzeTo = self.get('AnalyzeTo')
		if self.get('OverwriteDffs') == 'True':
			overwrite = True
		else:
			overwrite = False
		analysispicture = pictures[0]
		if self.get("Analyze") == 'True':		
			for picture in pictures:
				if picture != analysispicture:
					filename = os.path.join(self.get('DffPathname'),"%s-%s-%s" % (self.get('Name'), analysispicture[0], picture[0]))
					if self.verbose > 1:
						print "Registrations left: " + str(analyzesLeft)
					if self.verbose > 3:
						print "Registering deformation from picture " + str(analysispicture[0]) + " to picture " + str(picture[0])
					time1 = time.clock()
					deformation = DeformationData(analysispicture[1], picture[1], self.deformdata)
					time2 = time.clock()
					timetaken = time2 - time1
					totaltimetaken += timetaken
					if self.verbose > 1:
						print "Registration took: " + str(timetaken) + " seconds."
					deformation.set('PictureData1', analysispicture[2])
					deformation.set('PictureData2', picture[2])
					exporter = DffExporter(deformation, 
											  DffExportParameters(overwrite=overwrite, 
												dffstep=self.masterdata.get("DffStep"),
												writeCoefs=writeCoefs,
												diccoreParameters=deformation.dic.parameters), 
											filename + ".dff")
					if exporter.export() == False:
					   analyzesSkipped += 1
					analyzesDone += 1
					analyzesLeft -= 1
					if analyzesMaxExists:
						if analyzesDone == analyzesMax:
							if self.verbose > 1:
								print "Maximum number of analyzes done."
							break
					try:
						if self.verbose > 1:
							print "Time left: " + str("%d" % (analyzesLeft * totaltimetaken/(analyzesDone-analyzesSkipped))) + " seconds."
					except ZeroDivisionError:
						pass
					if analyzeTo == "Previous":
						analysispicture = picture
				
		if self.verbose > 0:	
			print "Registration done."

	def get(self, key):
		return self.masterdata.get(key)

	def set(self, key, value):
		self.masterdata.set(key, value)

	def check(self, key):
		return self.masterdata.check(key)

### Refactor this, please! This does not sort pictures!
	def sortPictures(self, pathname):
		"""
		Seeks for pictures that match the format and arranges them.
		Returns an array that has a three-cell array in every cell.
		The first cell has the picture's number, the second has it's
		name with path included and the third has a dictionary formed 
		from the regular expression keywords that user supplies
		with PictureForm.
		
		Configuration flags:
		
		PictureForm regular expression is required so that the program
		can find the pictures. All other data can be <ignore>'d but
		PictureNumber is essential and must be present. Rest of the
		keywords (<key>) are user definable and show up only at the
		dff-file.
		
		If AnalyzeTo-flag is a picture's name the program takes
		only the pictures following that picture.
		
		Same if FirstPicture is defined. If FirstPicture is a picture
		taken before analysispicture, no pictures are found.
		
		If LastPicture is defined the program will ignore pictures
		taken after that.
		
		If PictureSkip's name is self-explanatory. LastPicture will
		always be the last picture, even if it isn't a skip:th
		picture.
		"""
		files = os.listdir(pathname)
		files.sort()
		pictures = []
		analyzeTo = self.get('AnalyzeTo')
		findanalysispicture = (analyzeTo != "First" and analyzeTo != "Previous")
		if findanalysispicture:
			analysispicture = analyzeTo
		else:
			analysispicture = None
		findfirstpicture = self.check('FirstPicture')
		if findfirstpicture:
			firstpicture = self.get('FirstPicture')
		findlastpicture	= self.check('LastPicture')
		if findlastpicture:
			lastpicture = self.get('LastPicture')
		testExpression = re.compile(self.get('PictureForm'))
		if 'PictureNumber' not in testExpression.groupindex:
			raise Exception("No PictureNumber key in the picture name expression.")
		for possiblePicture in files:
			if possiblePicture == analysispicture:
				findanalysispicture = False
				pictureMatch = testExpression.match(possiblePicture, 0, len(possiblePicture))
				if pictureMatch != None:
					analysispicture = [int(pictureMatch.group('PictureNumber')), os.path.join(pathname,possiblePicture), pictureMatch.groupdict()]
			if not findanalysispicture:
				if (not findfirstpicture) or possiblePicture == firstpicture:
					findfirstpicture = False
					pictureMatch = testExpression.match(possiblePicture, 0, len(possiblePicture))
					if pictureMatch != None:
						pictures.append([int(pictureMatch.group('PictureNumber')), os.path.join(pathname,possiblePicture), pictureMatch.groupdict()])
					elif self.verbose > 4:
						print "Picture filename '" + possiblePicture + "' is in wrong format."
					if findlastpicture:
						if possiblePicture == lastpicture:
							break
		pictures.sort()
		if self.verbose > 2:
			print "Found " + str(len(pictures)) + " pictures."
		chosenPictures = []
		if analysispicture != None:
			chosenPictures.append(analysispicture)
		if self.check('PictureSkip') == 'True':
			skip = self.get('PictureSkip')
		else:
			skip = 0
		multiplier = 0
		index = 0
		if skip == 0 or skip == 1:
			if self.verbose > 2:
				print "Taking every picture."
			chosenPictures.extend(pictures)
		else:
			while index < len(pictures):
				chosenPictures.append(pictures[index])
				multiplier += 1
				index = multiplier * skip
		if findlastpicture:
			if chosenPictures[len(chosenPictures) -1][0] != pictures[len(pictures) - 1][0]:
				chosenPictures.append(pictures[len(pictures) - 1])
		if len(chosenPictures) < 2:
			raise Exception("Could not get two images from directory %s." % pathname)
		if self.verbose > 2:
			print str(len(chosenPictures)) + " pictures to be analyzed."
		return chosenPictures

