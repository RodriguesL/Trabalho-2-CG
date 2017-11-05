from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
from geometry import *
from random import uniform
from triangulate import *

width = 800
height = 600

polygons = []
vertices = []
clicked = False

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
	currentPoint = (point, point)
	if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
		print(point.x, point.y)
		vertices.append(point)

def mouseDrag (x, y):

	glutPostRedisplay();


def renderScene ():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glPushMatrix()
	glMatrixMode (GL_PROJECTION)
	gluOrtho2D (0.0, width, height, 0.0)
	polygon = Polygon([Point(0, 0), Point(550, 0), Point(550, 400), Point(275, 200), Point(0, 400)])
	vertices = triangulate(polygon)
	glBegin(GL_TRIANGLES)
	glColor3f(255.0, 255.0, 0.0)
	for point in vertices:
		glVertex3f(point[0], point[1], 0.0)
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
	#glutPassiveMotionFunc(mouseDrag)
	glutReshapeFunc(changeSize)
	glutDisplayFunc(renderScene)
	glutMainLoop()

if __name__=="__main__":
	main()