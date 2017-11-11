from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
from geometry import *
from random import uniform
from tessellator import *
from matrix import *
import numpy as np
import time

width = 800
height = 600

class ColoredPolygon(Polygon):
	def __init__(self,points, r, g, b):
		super(ColoredPolygon, self ).__init__(points)
		self.r = r
		self.g = g
		self.b = b
		self.dist = Point(0,0)

	def setColor(self, r, g, b):
		self.r = r
		self.g = g
		self.b = b	


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
	glMatrixMode(GL_MODELVIEW)

def myMouse (button, state, x, y):
	global currentPolygon
	global clicked
	global tempLine
	global point
	global selectedPolygon
	global startedPoint
	global waitingSecondClick
	point = Point(x, y)
	if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
		for polygon in polygons:
			if(polygon.contains(point)):
				selectedPolygon = polygon
				break
		if selectedPolygon:
			startedPoint = point
			print("Pegou o poligono")
		else:
			clicked = True
			print(point.x, point.y)
			tempLine = TemporaryLine(point)
			currentPolygon.append(point)
			if len(currentPolygon) > 2 and currentPolygon[-1].dist(currentPolygon[0]) <= 10:
				del currentPolygon[-1]
				clicked = False
				tempLine = TemporaryLine(Point(0,0))
				poly = ColoredPolygon(currentPolygon[:], uniform(0,1), uniform(0,1), uniform(0,1))
				polygons.append(poly)
				del currentPolygon[:]
			if len(currentPolygon) > 2:
				lastPoint = currentPolygon[-2]
				line = Line(point, lastPoint)
				previousPoint = None
				for vertex in currentPolygon:
					if previousPoint is None:
						previousPoint = vertex
						continue
					if vertex == lastPoint:
						break
					testLine = Line(previousPoint, vertex)
					previousPoint = vertex
					print(testLine.intersection(line))
					if line.intersection(testLine):
						del currentPolygon[:]
						clicked = False
						tempLine = TemporaryLine(Point(0,0))
			

	if button == GLUT_LEFT_BUTTON and state == GLUT_UP and selectedPolygon:
		selectedPolygon = None
		print("Soltou o poligono")

	if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
		if any(polygon.contains(point) for polygon in polygons):
			print("Prego colocado")
			nails.append(point)

def mouseMotion(x, y):
	global startedPoint
	point = Point(x,y)
	if selectedPolygon:
		selectedPolygon.dist.x = point.x - startedPoint.x
		selectedPolygon.dist.y = point.y - startedPoint.y
		matrix = np.array(translate(selectedPolygon.dist.x,selectedPolygon.dist.y,0))
		for i,pointB in enumerate(selectedPolygon.points):
			pointN = np.array([pointB.x,pointB.y,0,1])
			print("Point " + str(i) +": " + str(pointN))
			result = matrix.dot(pointN)
			print("Result " + str(i) +": " + str(result))
			pointB.x = result[0]
			pointB.y = result[1]

		startedPoint = point
	glutPostRedisplay()

def mouseDrag (x, y):
	point = Point(x, y)
	if(clicked):
		tempLine.endPoint.x = x
		tempLine.endPoint.y = y
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

def drawNails():
	glPointSize(10.0)
	glBegin(GL_POINTS)
	for nail in nails:
		glColor3f(0.3,0.3,0.3)
		glVertex3f(nail.x, nail.y, 0.0)
	glEnd()

def renderScene ():
	glEnable(GL_POINT_SMOOTH)
	glEnable(GL_LINE_SMOOTH)
	glEnable(GL_POLYGON_SMOOTH)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode (GL_MODELVIEW)
	drawTempLines()
	for polygon in polygons:
		drawPolygon(polygon)
	drawNails()
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
	gluOrtho2D (0.0, width, height, 0.0)
	glutMouseFunc(myMouse)
	glutPassiveMotionFunc(mouseDrag)
	glutMotionFunc(mouseMotion)
	glutReshapeFunc(changeSize)
	glutDisplayFunc(renderScene)
	glutIdleFunc(renderScene)
	print("Instrucao: Botao direito do mouse coloca os pregos")
	glutMainLoop()

if __name__=="__main__":
	main()
