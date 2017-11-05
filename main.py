from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
from geometry import *
from random import uniform

width = 800
height = 600

polygons = []
vertices = []
tempLine = Line(Point(0,0))
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
	glPointSize(5.0)
	vertices = tess.tessellate([Point(1,0,0), Point(0,1,0), Point(1./3,1./3,1./3), Point(0,0,1)])
	glBegin(GL_POLYGON)
	glColor3f(255.0, 0.0, 0.0)
	for vertex in vertices:
		glVertex3f(vertex.x, vertex.y, vertex.z)
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