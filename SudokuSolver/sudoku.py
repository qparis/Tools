#!/usr/bin/python

# Python sudoku solver
# Made by Quentin PÂRIS - http://www.qparis.fr
#
# Licence: GPLv3

import sys
import time
import os

def load_file(file_grid):
	grid = open(file_grid,"r").read().replace("\n","").replace(".","0")
	if(len(grid) != 81):
		print "Fatal Error : Bad size ! "+str(len(grid))
		sys.exit()
		
	return grid

def get_line(i):
	return i % 9

def get_cols(i):
	return i / 9

def string_to_grid(string):
	grid = 9*[0]  
	for i in range(len(grid)):	
		grid[i] = 9*[0]

	i = 0
	while(i < 81):
		line = get_line(i)
		cols = get_cols(i)
		grid[cols][line] = int(string[i])
		i += 1
	#print string
	return grid

def show_grid(grid):
	curseur = 0
		
	while(curseur < 81):
		line = get_line(curseur)
		cols = get_cols(curseur)
		sys.stdout.write(str(grid[cols][line]).replace("0",".")+" ")
		if(line == 2 or line == 5):
			sys.stdout.write("| ")
		if(line == 8):
			if(cols == 2 or cols == 5):
				print("\n---------------------")
			else:
				print("")
		curseur += 1

def get_area(num):
	x = get_line(num)
	y = get_cols(num)
	if(y < 3):
		if(x < 3):
			area = 1
		if(x > 2 and x < 6):
			area = 2
		if(x > 5):
			area = 3

	if(y > 2 and y < 6):
		if(x < 3):
			area = 4
		if(x > 2 and x < 6):
			area = 5
		if(x > 5):
			area = 6

	if(y > 5):
		if(x < 3):
			area = 7
		if(x > 2 and x < 6):
			area = 8
		if(x > 5):
			area = 9
	return area

def make_areas(grid):
	areas = 9*[0]  
	for i in range(len(areas)):	
		areas[i] = []
	i = 0
	while(i < 81):
		x = get_line(i)
		y = get_cols(i)
		area = get_area(i) - 1
		areas[area].append(grid[x][y])
		i += 1
	return areas

def check_grid(grid):
	failed = False
	boucle = 0
	# Lines	
	while(boucle < 9):
		j = 0
		while(j < 9):
			i = 0
			while(i < 9):
				if(i != j):
					if(grid[boucle][j] == grid[boucle][i] and grid[boucle][j] != 0):
						failed = True		
				i += 1
			j += 1
		boucle += 1 

	# Cols
	boucle = 0
	while(boucle < 9):
		j = 0
		while(j < 9):
			i = 0
			while(i < 9):
				if(i != j):
					if(grid[j][boucle] == grid[i][boucle] and grid[j][boucle] != 0):
						failed = True		
				i += 1
			j += 1
		boucle += 1 
	# Area
	boucle = 0
	area = make_areas(grid)
	while(boucle < 9):
		j = 0
		while(j < 9):
			i = 0
			while(i < 9):	
				if(i != j):
					if(area[boucle][j] == area[boucle][i] and area[boucle][j] != 0):
						failed = True
				i += 1	
			j += 1
		boucle += 1
	if(failed):
		return False
	else:
		return True
def solved(grid):
	solved = True
	i = 0
	while(i < 9):
		if(0 in grid[i]):
			solved = False
		i += 1
	return solved

def solve(grid):
	if(check_grid(grid) == False):
		print "La grille n'est pas valable"
		return False

	print "Please wait while the grid is solved ..."

	blanks = []
	index = 0
	while(index < 81):
		x = get_line(index)
		y = get_cols(index)
		
		if(grid[y][x] == 0):	
			blanks.append(index)
		index += 1
	i = 0
	while(i < len(blanks)):
		x = get_line(blanks[i])
		y = get_cols(blanks[i])

		if(grid[y][x] < 9):
			grid[y][x] += 1
			if(check_grid(grid) == False):
				if(grid[y][x] >= 9):
					grid[y][x] = 0
					i -= 1
			else:
				i += 1
		else :
			grid[y][x] = 0
			i -= 1
		if(len(sys.argv) > 1):
			os.system("clear")
			show_grid(grid)
grid = string_to_grid(load_file("grille.sk"))
show_grid(grid)
solve(grid)
print ""
if(len(sys.argv) == 1):
	show_grid(grid)

print ""

