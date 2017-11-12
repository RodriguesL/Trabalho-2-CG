## @package main
# The main function, where all the critical parts of the implementation are.
#
# @author Lucas Rodrigues
#

from __future__ import division
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
from geometry import *
from random import uniform
from tessellator import *
from matrix import *
import numpy as np
from time import time
from additional_classes import *

width = 800
height = 600

tempLine = TemporaryLine(Point(0,0))
polygons = []
nails = []
clicked = False
currentPolygon = []
selectedPolygon = None
doubleClick = DoubleClick(time())
transformedChildren = []
transformedNails = []

## Function to resize the window
# @param w The screen width
# @param h The screen height
#
def changeSize(w, h):

	# Prevent a divide by zero, when window is too short
	# (you cant make a window of zero width).
	if h == 0:
		h = 1

	ratio = 1.0* w / h

	# Reset the coordinate system before modifying
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	global height
	global width
	
	# Set the viewport to be the entire window
	width = w
	height = h
	glViewport(0, 0, w, h)

## Function that determines whether if a polygon can be translated based on its position in the hierarchy.
# @param polygon The polygon being tested
# @param children The list of polygons that are below polygon on the hierarchy
# @return Returns true if the polygon can be translated, and False otherwise
#
def canTranslate(polygon, children):
	for child in children:
		for parent in child.parents:
			if polygons.index(polygon) > polygons.index(parent) or len(child.parents) >= 2:
				return False
		if(child.children):
			return canTranslate(polygon, child.children)
	return True

## Function that determines whether if a polygon can be rotated based on its position in the hierarchy.
# @param polygon The polygon being tested
# @return Returns true if the polygon can be rotated, and False otherwise
#
def canRotate(polygon):
	for child in polygon.children:
		if len(child.parents) >= 2:
			return False
		elif(child.children):
			return canRotate(child)
	return True

## Callback function to handle mouse input
# @param button The mouse button
# @param state Determines whether the button was pressed or released
# @param x The x coordinate of the mouse
# @param y The y coordinate of the mouse
#
def myMouse (button, state, x, y):
	global currentPolygon
	global clicked
	global tempLine
	global selectedPolygon
	global startedPoint
	global doubleClick
	if (button == GLUT_LEFT_BUTTON and state == GLUT_DOWN):
		point = Point(x,y)
		if(doubleClick.isDoubleClicked(time())):
			cancelPolygon()
			firstPolygon = True
			children = []
			parent = None
			removeNail = None 
			for nail in nails:
				if nail.dist(point) <= 15:
					removeNail = nail

			for polygon in polygons:
				if(polygon.contains(point)):
					if(firstPolygon):
						parent = polygon
						nail = point
						firstPolygon = False
					else:
						children.append(polygon)
				if(children):
					if(removeNail):
						nails.remove(removeNail)
						print("Removed nail")
						for child in children:
							parent.children.remove(child)
							child.parents.remove(parent)
							child.nails.remove(removeNail)
					else:
						if not polygon.parents:
							nails.append(nail)
							print("Nail placed")
							parent.children += children
							for child in children:
								child.parents.append(parent)
								child.nails.append(nail)
		
		else:
			doubleClick = DoubleClick(time())
			for polygon in reversed(polygons):
				if(polygon.contains(point)):
					selectedPolygon = polygon
					break

			if selectedPolygon:
				startedPoint = point
				print("Dragging polygon")

			else:
				clicked = True
				tempLine = TemporaryLine(point)
				currentPolygon.append(point)

				if len(currentPolygon) > 2 and currentPolygon[-1].dist(currentPolygon[0]) <= 15:
					del currentPolygon[-1]
					clicked = False
					tempLine = TemporaryLine(Point(0,0))
					poly = ColoredPolygon(currentPolygon[:],uniform(0,1), uniform(0,1), uniform(0,1))
					print("Added polygon")
					polygons.append(poly)
					del currentPolygon[:]

				if len(currentPolygon) > 2:
					lastPoint = currentPolygon[-2]
					line = Line(point, lastPoint)
					previousPoint = None
					for p in currentPolygon:
						if previousPoint is None:
							previousPoint = p
							continue
						if p == lastPoint:
							break
						testLine = Line(p, previousPoint)
						previousPoint = p
						if intersects(testLine, line):
							print("intersects")
							del currentPolygon[:]
							clicked = False
							tempLine = TemporaryLine(Point(0,0))

	if (button == GLUT_LEFT_BUTTON and state == GLUT_UP):
		selectedPolygon = None

	if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
		cancelPolygon()

## Function that cancels the polygon that is being currently drawn
#
def cancelPolygon():
	global clicked
	global tempLine
	del currentPolygon[:]
	clicked = False
	tempLine = TemporaryLine(Point(0,0))

## Function that rotates a polygon using the given point as axis.
# @param point The point which will be used as the rotation axis
#
def rotatePolygon(point):
	global startedPoint
	rotatePoint = selectedPolygon.nails[0]

	startPoint = startedPoint - rotatePoint
	anglePoint = point - rotatePoint

	inner_product = startPoint.x*anglePoint.x + startPoint.y*anglePoint.y

	len1 = math.hypot(startPoint.x, startPoint.y)
	len2 = math.hypot(anglePoint.x, anglePoint.y)

	angle = math.acos(inner_product/(len1*len2))

	angle = angle*180/math.pi
	angle = math.copysign(angle, anglePoint.crossProd(startPoint).z)
	angle *= -1

	matrix = translateAndRotate(angle, rotatePoint, Point(0,0,1))
	applyTransformationToPoints(selectedPolygon, matrix)
	if(selectedPolygon.children):
		applyTransformationToChildren(selectedPolygon, matrix)
	startedPoint = point

## Function that translates the polygon to a point of destination
# @param polygon The polygon being translated
# @param point The point to which the polygon will be translated to
#
def translatePolygon(polygon, point):
	global startedPoint
	distX = point.x - startedPoint.x
	distY = point.y - startedPoint.y
	matrix = translate(distX,distY,0)
	if(polygon.children):
		applyTransformationToChildren(polygon, matrix)
	applyTransformationToPoints(polygon, matrix)
	startedPoint = point

## Function that applies transformations to their children in the hierarchy
# @param polygon The parent polygon
# @param matrix The transformation matrix being applied
#
def applyTransformationToChildren(polygon,matrix):
	for child in set(polygon.children):
		applyTransformationToPoints(child,matrix)
		if(child.children):
			applyTransformationToChildren(child,matrix)

## Function that applies the transformation to points (nails)
# @param polygon The polygon which has the nails
# @param matrix The transformation matrix being applied
# 
def applyTransformationToPoints(polygon,matrix):
	matrix = np.array(matrix)
	for p in polygon.points:
		pointN = np.array([p.x,p.y,0,1])
		
		result = matrix.dot(pointN)
		p.x = result[0]
		p.y = result[1]

	for nail in polygon.nails:
		pointN = np.array([nail.x,nail.y,0,1])
		result = matrix.dot(pointN)
		nail.x = result[0]
		nail.y = result[1]
## Function that checks whether two lines intersect
#
# This function is used to cancel the drawing of autointersecting polygons
# @param l1 A line
# @param l2 The other line
#
def intersects(l1, l2):
	
	vector1 = Point(0,0)
	vector2 = Point(0,0)

	vector1.x = l1.p2.x - l1.p1.x
	vector1.y = l1.p2.y - l1.p1.y

	vector2.x = l2.p2.x - l2.p1.x
	vector2.y = l2.p2.y - l2.p1.y

	s = (-vector1.y * (l1.p1.x - l2.p1.x) + vector1.x * (l1.p1.y - l2.p1.y)) / (-vector2.x * vector1.y + vector1.x * vector2.y)
	t = ( vector2.x * (l1.p1.y - l2.p1.y) - vector2.y * (l1.p1.x - l2.p1.x)) / (-vector2.x * vector1.y + vector1.x * vector2.y)

	if (s >= 0 and s <= 1 and t >= 0 and t <= 1):
		return True
	return False
## Callback function used to monitor the mouse motion while clicked
# @param x The x coordinate of the mouse
# @param y The y coordinate of the mouse
#
def mouseMotion(x, y):
	global startedPoint
	global transformedNails
	global transformedChildren
	point = Point(x,y)
	if selectedPolygon is not None:
		if selectedPolygon.parents and len(selectedPolygon.nails) == 1 and canRotate(selectedPolygon):
			rotatePolygon(point)
		elif not selectedPolygon.parents and canTranslate(selectedPolygon, selectedPolygon.children):
			translatePolygon(selectedPolygon, point)
	transformedChildren = []
	transformedNails = []

## Callback function that passively monitors mouse motion
# @param x The x coordinate of the mouse
# @param y The y coordinate of the mouse
#
def mouseDrag (x, y):
	point = Point(x, y)
	if clicked:
		tempLine.endPoint.x = point.x
		tempLine.endPoint.y = point.y
	glutPostRedisplay()

## Function that draws the temporary lines that represent the polygon edges
#
def drawTempLines():
	glLineWidth(3.0)
	glBegin(GL_LINES)
	for i in range(1, len(currentPolygon)):
		glColor3f(0, 0, 0)
		glVertex3f(currentPolygon[i-1].x, currentPolygon[i-1].y, 0.0)
		glVertex3f(currentPolygon[i].x, currentPolygon[i].y, 0.0)
	glEnd()
	glLineWidth(3.0)
	glBegin(GL_LINES)
	glColor3f(0, 0, 0)
	glVertex3f(tempLine.startPoint.x, tempLine.startPoint.y, 0.0)
	glVertex3f(tempLine.endPoint.x, tempLine.endPoint.y, 0.0)
	glEnd()

## Function that draws the polygons
# @param polygon The polygon being drawn
#
def drawPolygon(polygon):
	tess = tessellate(polygon)
	glCallList(tess)

## Function that draws the nails
# @param polygon The polygon which has nails associated to it
#
def drawNails(polygon):
	glPointSize(10.0)
	glBegin(GL_POINTS)
	for nail in polygon.nails:
		glColor3f(0,0,0)
		glVertex3f(nail.x, nail.y, 0.0)
	glEnd()

## Callback function that renders the scene
#
def renderScene ():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glEnable(GL_POINT_SMOOTH)
	glEnable(GL_LINE_SMOOTH)
	glPushMatrix()
	glMatrixMode (GL_PROJECTION)
	gluOrtho2D (0.0, width, height, 0.0)
	for polygon in polygons:
		drawPolygon(polygon)
		drawNails(polygon)
	drawTempLines()
	glPopMatrix()
	glutSwapBuffers()
	glutPostRedisplay()
	glFlush()

## Main function
#
def main(argv = None):
	global window

	if argv is None:
		argv = sys.argv

	glutInit(argv)
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
	glutInitWindowPosition(100,100)
	glutInitWindowSize(width,height)
	window = glutCreateWindow(b'Trabalho 2 - CG - Lucas Rodrigues')
	glClearColor(1.0, 1.0, 1.0, 1.0)
	glutMouseFunc(myMouse)
	glutPassiveMotionFunc(mouseDrag)
	glutMotionFunc(mouseMotion)
	glutReshapeFunc(changeSize)
	glutIdleFunc(renderScene)
	glutDisplayFunc(renderScene)
	glutIdleFunc(renderScene)
	print("Left button: place polygon vertices")
	print("Right button: cancel drawing")
	print("Double click: place/remove nail")
	glutMainLoop()

if __name__=="__main__":
	main()
