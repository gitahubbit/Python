###################################################
# SUDOKU Generator
# Author: Andreas Senn
# Date: November 2013, Zurich
###################################################
# Setup:
generateRandomPuzzle = True
level = 43  # number of blank fields (out of 81 fields)

#page_sizeX = 148.5
#page_sizeY = 210.0

margins = 20
page_sizeX = 210
page_sizeY = 297

page_nX = 1
page_nY = 2

pages = 10

scale = 0.6*min(page_sizeX/page_nX, page_sizeY/page_nY)/9
# scale = 8 # size of puzzle square in mm

###################################################

page_sizeX -= 2*margins
page_sizeY -= 2*margins


import sys
import os
import subprocess

from copy import copy, deepcopy
from random import seed, randint
import time

millis = int(round(time.time() * 1000))
# seed(1003)
seed(millis)

pageCounter = 1
findAllSolutions = True

global solutions
solutions = []

def verifyPosition(field, coord):
	numberCheckList = [0 for i in range(9)]
	success = True

	# fast check for change on (x,y)
	(cx,cy) = coord
	for x in range(9):
		if 0 != field[cy][x]:
			numberCheckList[field[cy][x]-1] += 1
	for i in range(9):
		if numberCheckList[i] > 1:
			success = False
		numberCheckList[i] = 0

	for y in range(9):
		if 0 != field[y][cx]:
			numberCheckList[field[y][cx]-1] += 1
	for i in range(9):
		if numberCheckList[i] > 1:
			success = False
		numberCheckList[i] = 0

	a = cx // 3
	b = cy // 3
	for y in range(3):
		for x in range(3):
			if 0 != field[b*3+y][a*3+x]:
				numberCheckList[field[b*3+y][a*3+x]-1] += 1
	for i in range(9):
		if numberCheckList[i] > 1:
			success = False
		numberCheckList[i] = 0

	return success

def verifyField(field):
	numberCheckList = [0 for i in range(9)]
	success = True

	# full check
	for y in range(9):
		for x in range(9):
			if 0 != field[y][x]:
				numberCheckList[field[y][x]-1] += 1
		for i in range(9):
			if numberCheckList[i] > 1:
				success = False
			numberCheckList[i] = 0

	for x in range(9):
		for y in range(9):
			if 0 != field[y][x]:
				numberCheckList[field[y][x]-1] += 1
		for i in range(9):
			if numberCheckList[i] > 1:
				success = False
			numberCheckList[i] = 0

	for a in range(3):
		for b in range(3):	
			for y in range(3):
				for x in range(3):
					if 0 != field[b*3+y][a*3+x]:
						numberCheckList[field[b*3+y][a*3+x]-1] += 1
			for i in range(9):
				if numberCheckList[i] > 1:
					success = False
				numberCheckList[i] = 0

	return success

def PStext(file, x1, y1, txt, size = 5):
	file.write('newpath\n')
	file.write('/TimesRoman findfont\n')
	file.write( str(size) + ' mm scalefont\n')
	file.write('setfont\n')
	file.write(str(x1) + ' mm ' + str(y1) + ' mm moveto\n')
	file.write('(' + txt + ') show\n')
	#file.write('1 setlinewidth\n')
	file.write('stroke\n')


def PSbegin(f):
	# open and initialize file
	f.write('%!PS\n')
	#f.write('%!PS-Adobe-3.0\n')
	#f.write('%!PS-Adobe-2.0\n')
	f.write('/setA4Paper {<</PageSize [595 842] >> setpagedevice} def\n')
	f.write('/setA5Paper {<</PageSize [420 595] >> setpagedevice} def\n')
	f.write('setA4Paper\n')
	f.write('/mm {72 mul 25.4 div} def\n')
	#f.write('0.00 setlinewidth\n')
	f.write('1 setlinecap\n')
	f.write('[] 0 setdash\n')

	#f.write('%%Pages: 1\n')
	

def PSend(f):
	f.write('showpage\n')
	#f.write('')
	#f.write('%%EOF\n')
	#f.close() # you can omit in most cases as the destructor will call if

def PSline(file, x1, y1, x2, y2, w):
	file.write('newpath\n')
	file.write(str(x1) + ' mm ' + str(y1) + ' mm moveto\n')
	file.write(str(x2) + ' mm ' + str(y2) + ' mm lineto\n')
	file.write(str(w) + ' setlinewidth\n')
	file.write('stroke\n')

def PSplotField(f, field, osx = 0, osy = 0):

	#offsetX =  (148.5-9*scale)/2
	#offsetY =  (210-9*scale)/2
	
	offsetX = margins + osx + (page_sizeX/page_nX-9*scale)/2
	offsetY = margins + osy + (page_sizeY/page_nY-9*scale)/2

	#offsetX =  margins + osx + ((page_sizeX-2*margins)/page_nX-9*scale)/2
	#offsetY =  margins + osy + ((page_sizeY-2*margins)/page_nY-9*scale)/2

	# new page
	#f.write('%%Page: ' + str(pageCounter) + ' ' + str(pageCounter) + '\n')
	#f.write('%%BeginPageSetup\n')
	#f.write('/pgsave save def\n')
	#f.write('%%IncludeResource: font TimesRoman\n')
	#f.write('%%EndPageSetup	\n')

	# center puzzle
	f.write(str(offsetX) + ' mm ' + str(offsetY) + ' mm translate\n')

	# generate mesh
	for i in range(10):
		if (i%3 == 0):
			w = 2
		else:
			w = 1
		PSline(f, 0, i * scale, scale * 9, i * scale, w)
		PSline(f, i * scale, 0, i * scale, scale * 9, w)

	# write numbers
	for y in range(9):
		for x in range(9):
			if (0 != field[y][x]):
				size = scale/1.5
				PStext(f, (x+0.5) * scale - size*.25, (y+0.5) * scale - size*.35, str(field[y][x]), size)

	f.write(str(-offsetX) + ' mm ' + str(-offsetY) + ' mm translate\n')


def plotField(field):
	for y in range(9):
		sys.stdout.write("+-+-+-+-+-+-+-+-+-+\n")
		for x in range(9):
			sys.stdout.write("|")
			if 0 != field[y][x]:
				sys.stdout.write(str(field[y][x]))
			else:
				sys.stdout.write(' ')
			#print (field[y][x])
		sys.stdout.write("|\n")
	sys.stdout.write("+-+-+-+-+-+-+-+-+-+\n")
	sys.stdout.write('\n')

def shuffleField(field, coord, pos1, pos2):
	tempField = deepcopy(field)
	tempRow = [0 for z in range(9)]
	# row wise
	if "sy" == coord:
		for x in range(9):
			tempField[pos1][x] = int(field[pos2][x])
			tempField[pos2][x] = int(field[pos1][x])
	if "sx" == coord:
		for y in range(9):
			tempField[y][pos1] = int(field[y][pos2])
			tempField[y][pos2] = int(field[y][pos1])
	# block wise
	if "my" == coord:
		for x in range(9):
			for i in range(3):
				tempField[pos1*3+i][x] = int(field[pos2*3+i][x])
				tempField[pos2*3+i][x] = int(field[pos1*3+i][x])
	if "mx" == coord:
		for y in range(9):
			for i in range(3):
				tempField[y][pos1*3+i] = int(field[y][pos2*3+i])
				tempField[y][pos2*3+i] = int(field[y][pos1*3+i])
	# number wise
	if "n" == coord:
		for y in range(9):
			for x in range(9):
				if pos1 == field[y][x]:
					tempField[y][x] = pos2
				if pos2 == field[y][x]:
					tempField[y][x] = pos1
	return tempField

def shuffleFieldRnd(field):
	tempField = deepcopy(field)
	c0 = randint(0,2)
	if 0 == c0:
		# single row/col
		c1 = randint(0,1)
		t0 = randint(0,2)
		t1 = randint(0,2)
		t2 = randint(0,2)
		if 0 == c1:
			coord = 'sx'
		if 1 == c1:
			coord = 'sy'
		return shuffleField(field, coord, t0*3 + t1, t0*3 + t2)
	if 1 == c0:
		# multiple row/col (blocks)
		c1 = randint(0,1)
		t1 = randint(0,2)
		t2 = randint(0,2)
		if 0 == c1:
			coord = 'mx'
		if 1 == c1:
			coord = 'my'
		return shuffleField(field, coord, t1, t2)
	if 2 == c0:
		# number swap
		coord = 'n'
		t1 = randint(1,9)
		t2 = randint(1,9)
		return shuffleField(field, coord, t1, t2)

def seedField():
	field = [[0 for x in range(9)] for y in range(9)] 
	for x in range(9):
		for y in range(9):
			field[y][x] = 1 + (x + y*3 + (y//3)) % 9
	return field

def countHiddenFields(field):
	n = 0
	for y in range(9):
		for x in range(9):
			if 0 == field[y][x]:
				n = n + 1
	return n

def getHiddenFields(field):
	blanks = []
	for y in range(9):
		for x in range(9):
			if 0 == field[y][x]:
				blank = x, y
				blanks.append(blank)
	return blanks

def getVisibleFields(field):
	visibles = []
	for y in range(9):
		for x in range(9):
			if 0 != field[y][x]:
				visible = x, y
				visibles.append(visible)
	return visibles

def getNextHiddenField(field):
	# TODO: return only one field
	blanks = []
	for y in range(9):
		for x in range(9):
			if 0 == field[y][x]:
				blank = x, y
				blanks.append(blank)
	return blanks

def hideFields(field, count):
	n0 = countHiddenFields(field)
	n = 0
	tempField = deepcopy(field)
	trials = 0
	if 81 < n0 + count:
		success = False
		print ("Too many fields to hide")
	else:
		success = True
		visibles = getVisibleFields(tempField)
		while (n < count and True == success):
			if 0 != len(visibles):
				index = randint(0,len(visibles)-1)
				(x, y) = visibles[index]
				visibles.pop(index)
				temp = tempField[x][y]
				tempField[x][y] = 0
				if 1 != solve(tempField, True):
					tempField[x][y] = temp
				else:
					n += 1
			else:
				success = 0
	if not success:
		print ("No more fields to hide")
	return tempField

def solve(field, fullSolve = False):
	# consistent field assumed
	global solutions
	solutionCount = 0
	#blanks = getHiddenFields(field)
	blanks = getNextHiddenField(field)
	if 0 == len(blanks):
		solutionCount = 1
		solutions.append(deepcopy(field))
	else:
		(x,y) = blanks[0]
		for i in range (9):
			tempField = deepcopy(field)
			tempField[y][x] = i+1
			if True == verifyPosition(tempField, (x,y)):
			#if True == verifyField(tempField):
				nsol = solve(tempField, fullSolve)
				if 0 < nsol:
					if True == fullSolve:
						solutionCount += nsol
					else:
						solutionCount = 1
						break
	return solutionCount

def PDFgeneratePuzzles(n):
	fileNames = []
	for j in range(n):
		print ("Generating Puzzle " + str(j) + " with difficulty " + str(level))
		print ("Seeding...")
		field0 = seedField()
		print ("Shuffleing...")
		for i in range(2000):
			field0 = shuffleFieldRnd(field0)
		#print ("Original:")
		#plotField(field0)
		print ("Hiding...")
		field1 = hideFields(field0, level)
		print ("Testing...")
		if not verifyField(field1):
			Print ("ERROR: Field could not be verified")
			j -= 1
			continue;
		if not 1 == solve(field1):
			Print ("ERROR: Field could not be solved or has multiple solutions")
			j -= 1
			continue;

		if (j%(page_nX*page_nY) == 0):
			f = open(os.getcwd() + '\\sudoku.ps','w')
			PSbegin(f)
		
		osx = (j % page_nX) * (page_sizeX/page_nX)
		osy = ((j//page_nX) % page_nY ) * (page_sizeY/page_nY)

		PSplotField(f, field1, osx, osy)

		if (j%(page_nX*page_nY) == (page_nX*page_nY)-1 or j == n-1):

			#PStext(f, page_sizeY/2, page_sizeY*0.9, "This is a demo caption", size = 10)

			PSend(f)
			f.close()
			fileName = "sudoku_" + str(j).zfill(3) + ".pdf"
			print ("Generated " + fileName)
			cmdStr = "ps2pdf.exe " + os.getcwd() + "\\sudoku.ps " + os.getcwd() + "\\" + fileName
			os.system(cmdStr)
			fileNames.append(fileName)

	allPDFs = fileNames[0]
	for j in range(len(fileNames)-1):
		allPDFs += " " + fileNames[j+1]
	cmdStr = "pdftk.exe " + allPDFs + " cat output " + os.getcwd() + "\\sudoku.pdf"
	print (cmdStr)
	os.system(cmdStr)

def demo(generateRandomPuzzle = True):
	if True == generateRandomPuzzle:
		print ("Generating Puzzle...")
		field0 = seedField()
		for i in range(500):
			field0 = shuffleFieldRnd(field0)
		print ("Original:")
		plotField(field0)
		field0 = hideFields(field0, level)
	else:
		print ("Using hard-coded Puzzle.")
		# Puzzle from NZZ website
		field0 = []
		field0.append([0,0,0,3,0,9,7,0,2])
		field0.append([0,0,2,0,0,5,0,0,0])
		field0.append([8,9,0,0,0,0,4,0,0])
		field0.append([0,0,5,0,0,0,0,4,9])
		field0.append([0,4,6,9,2,0,0,0,0])
		field0.append([0,0,0,0,5,0,1,0,0])
		field0.append([1,0,0,0,0,0,0,8,0])
		field0.append([0,8,0,4,1,3,0,7,0])
		field0.append([3,0,0,8,6,7,0,0,5])

	verifyField(field0)

	print ("Puzzle:")
	plotField(field0)

	print ("Solving puzzle...")

	nsoL = solve(field0, findAllSolutions)
	if 0 < nsoL:
		print("Puzzle solved:")
		print(str(nsoL) + " Solutions exist")
		if True != verifyField(solutions[0]):
			print ("Error occured")
		plotField(solutions[0])
	else:
		print ("Could not solve Puzzle")

#demo(generateRandomPuzzle)

PDFgeneratePuzzles(pages*page_nX*page_nY)
