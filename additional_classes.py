## @package additional_classes
# Extra classes created to extend or complement the other modules
#
# @author Lucas Rodrigues
#
from geometry import *

## Class that extends the Polygon class from the geometry module.
#
# Added color and the data structures necessary to implement the transformation hierarchy.
# 
class ColoredPolygon(Polygon):
	## The constructor
	def __init__(self,points, r, g, b):
		super(ColoredPolygon, self ).__init__(points)
		self.r = r
		self.g = g
		self.b = b
		self.parents = []
		self.children = []
		self.nails = []

	## Sets the polygon color
	# @param self The ColoredPolygon object
	# @param r The red parameter of RGB
	# @param g The green parameter of RGB
	# @param b The blue parameter of RGB
	#
	def setColor(self, r, g, b):
		self.r = r
		self.g = g
		self.b = b
	## Defines the center point of the polygon using a bounding box
	# @param self The ColoredPolygon object
	# @return Returns the center of the polygon
	#
	def centerPoint(self):
		box = Box()
		for p in self.points:
			box.add(p)
		return box.centre()

## Class that implements the double click logic, used to place the nails.
#
class DoubleClick(object):
	## The constructor
	def __init__(self, time):
		self.time = time
	## Checks if the clicks are single or double clicks
	def isDoubleClicked(self, finalTime):
		return finalTime - self.time < 0.2
## Class that defines a temporary line (used to draw the temporary lines representing the polygon edges)
#
class TemporaryLine:
	## The constructor
	def __init__(self, point):
		self.startPoint = point
		self.endPoint = Point(self.startPoint.x, self.startPoint.y)