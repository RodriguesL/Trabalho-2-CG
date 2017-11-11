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

width = 800
height = 600

class ColoredPolygon(Polygon):
	def __init__(self,points, r, g, b):
		super(ColoredPolygon, self ).__init__(points)
		self.r = r
		self.g = g
		self.b = b
		self.parents = []
		self.children = []
		self.nails = []


	def setColor(self, r, g, b):
		self.r = r
		self.g = g
		self.b = b

	def centerPoint(self):
		box = Box()
		for p in self.points:
			box.add(p)
		return box.centre()

class DoubleClick(object):
	def __init__(self, time):
		self.time = time

	def isDoubleClicked(self, finalTime):
		return finalTime - self.time < 0.2

class TemporaryLine:
	def __init__(self, point):
		self.startPoint = point
		self.endPoint = Point(self.startPoint.x, self.startPoint.y)

tempLine = TemporaryLine(Point(0,0))
polygons = []
nails = []
clicked = False
currentPolygon = []
selectedPolygon = None
doubleClick = DoubleClick(time())

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
						print("RemoveNail")
						for child in children:
							parent.children.remove(child)
							child.parents.remove(parent)
							child.nails.remove(removeNail)
					else:
						nails.append(nail)
						print("Nail")
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
				print("Pegou o poligono")

			else:
				clicked = True
				tempLine = TemporaryLine(point)
				currentPolygon.append(point)

				if len(currentPolygon) > 2 and currentPolygon[-1].dist(currentPolygon[0]) <= 15:
					del currentPolygon[-1]
					clicked = False
					tempLine = TemporaryLine(Point(0,0))
					poly = ColoredPolygon(currentPolygon[:],uniform(0,1), uniform(0,1), uniform(0,1))
					print("Adicionou Polygon")
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
						testLine = Line(previousPoint, p)
						previousPoint = p
						if intersects(line, testLine):
							print("intersects")
							del currentPolygon[:]
							clicked = False
							tempLine = TemporaryLine(Point(0,0))
	if (button == GLUT_LEFT_BUTTON and state == GLUT_UP):
		selectedPolygon = None

	if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
		cancelPolygon()

def cancelPolygon():
	global clicked
	global tempLine
	for p in currentPolygon:
		allPoints.remove(p) 
	del currentPolygon[:]
	clicked = False
	tempLine = TemporaryLine(Point(0,0))

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

def translatePolygon(polygon, point):
	global startedPoint
	distX = point.x - startedPoint.x
	distY = point.y - startedPoint.y
	matrix = translate(distX,distY,0)
	if(polygon.children):
		applyTransformationToChildren(polygon, matrix)
	applyTransformationToPoints(polygon, matrix)
	startedPoint = point

def applyTransformationToChildren(polygon,matrix):
	for child in polygon.children:
		applyTransformationToPoints(child,matrix)
		if(child.children):
			applyTransformationToChildren(child,matrix)

def applyTransformationToPoints(polygon,matrix):
	matrix = np.array(matrix)
	for p in polygon.points:
		pointN = np.array([p.x,p.y,0,1])
		
		result = matrix.dot(pointN)
		p.x = result[0]
		p.y = result[1]

	for p in polygon.nails:
		pointN = np.array([p.x,p.y,0,1])
		result = matrix.dot(pointN)
		p.x = result[0]
		p.y = result[1]

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

def mouseMotion(x, y):
	global startedPoint
	point = Point(x,y)
	if(selectedPolygon is not None):
		if(selectedPolygon.parents and len(selectedPolygon.nails) == 1):
			rotatePolygon(point)
		elif(not selectedPolygon.parents):
			translatePolygon(selectedPolygon, point)

def mouseDrag (x, y):
	point = Point(x, y)
	if(clicked):
		tempLine.endPoint.x = point.x
		tempLine.endPoint.y = point.y
	glutPostRedisplay()

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

def drawPolygon(polygon):
	tess = tessellate(polygon)
	glCallList(tess)

def drawNails(polygon):
	glPointSize(10.0)
	glBegin(GL_POINTS)
	for nail in polygon.nails:
		glColor3f(0.3,0.3,0.3)
		glVertex3f(nail.x, nail.y, 0.0)
	glEnd()

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
	glutMainLoop()

if __name__=="__main__":
	main()
