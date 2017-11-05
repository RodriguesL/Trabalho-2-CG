from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
from geometry import *
from triangulate import *


global height
global width

width = 800
height = 600


class DegeneratedLine:
	def __init__(self, point):
		self.startPoint = point
		self.endPoint = Point(self.startPoint.x, self.startPoint.y)

tempLine = DegeneratedLine(Point(0,0))
polygons = []
vertices = []
clicked = False
currentPolygon = []

def changeSize(w, h):

	# Prevent a divide by zero, when window is too short
	# (you cant make a window of zero width).
	if h == 0:
		h = 1

	ratio = 1.0* w / h

	# Reset the coordinate system before modifying
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	
	# Set the viewport to be the entire window
	width = w
	height = h
	glViewport(0, 0, w, h)

def myMouse (button, state, x, y):
	point = Point(x, y)
	if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
		clicked = True 
		print(point.x, point.y)
		tempLine = DegeneratedLine(point)
		currentPolygon.append(point)
		vertices.append(point)
		if len(currentPolygon) > 2 and currentPolygon[-1].dist(currentPolygon[0]) <= 20:
			del vertices[-1]
			currentPolygon[-1] = currentPolygon[0]
			clicked = False
			tempLine = DegeneratedLine(Point(0,0))
			poly = Polygon(currentPolygon[:])
			polygons.append(poly)
			del currentPolygon[:]


def mouseDrag (x, y):
	if(clicked):
		tempLine.endPoint.x = x
		tempLine.endPoint.y = y
	glutPostRedisplay()


def renderScene ():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glPushMatrix()
	glMatrixMode (GL_PROJECTION)
	gluOrtho2D (0.0, width, height, 0.0)
	glLineWidth(3.0)
	glBegin(GL_LINES)
	for i in range(1, len(currentPolygon)):
		glColor3f(255.0, 0, 255.0)
		glVertex3f(currentPolygon[i-1].x, currentPolygon[i-1].y, 0.0)
		glVertex3f(currentPolygon[i].x, currentPolygon[i].y, 0.0)
	glEnd()
	glLineWidth(3.0)
	glBegin(GL_LINES)
	glColor3f(0, 255.0, 255.0)
	glVertex3f(tempLine.startPoint.x, tempLine.startPoint.y, 0.0)
	glVertex3f(tempLine.endPoint.x, tempLine.endPoint.y, 0.0)
	glEnd()
	for polygon in polygons:
		glBegin(GL_POLYGON)	
		for polygonPoint in polygon.points:
			glColor3f(0, 0, 255)
			glVertex3f(polygonPoint.x, polygonPoint.y, 0)
		glEnd()
	



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
	glMatrixMode(GL_PROJECTION)
	gluOrtho2D(0.0, width, height, 0.0)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glutSwapBuffers()
	glutMouseFunc(myMouse)
	glutPassiveMotionFunc(mouseDrag)
	glutReshapeFunc(changeSize)
	glutDisplayFunc(renderScene)
	glutIdleFunc(renderScene)
	glutMainLoop()

if __name__=="__main__":
	main()