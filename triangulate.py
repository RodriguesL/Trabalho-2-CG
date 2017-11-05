from OpenGL.GL import *
from OpenGL.GLU import *

def triangulate(polygon, holes=[]):
    """
    Returns a list of triangles.
    Uses the GLU Tesselator functions!
    """
    vertices = []
    def edgeFlagCallback(param1, param2): pass
    def beginCallback(param=None):
        vertices = []
    def vertexCallback(vertex, otherData=None):
        vertices.append(vertex[:2])
    def combineCallback(vertex, neighbors, neighborWeights, out=None):
        out = vertex
        return out
    def endCallback(data=None): pass

    tess = gluNewTess()
    gluTessProperty(tess, GLU_TESS_WINDING_RULE, GLU_TESS_WINDING_ODD)
    gluTessCallback(tess, GLU_TESS_EDGE_FLAG_DATA, edgeFlagCallback)#forces triangulation of polygons (i.e. GL_TRIANGLES) rather than returning triangle fans or strips
    gluTessCallback(tess, GLU_TESS_BEGIN, beginCallback)
    gluTessCallback(tess, GLU_TESS_VERTEX, vertexCallback)
    gluTessCallback(tess, GLU_TESS_COMBINE, combineCallback)
    gluTessCallback(tess, GLU_TESS_END, endCallback)
    gluTessBeginPolygon(tess, 0)

    #first handle the main polygon
    gluTessBeginContour(tess)
    for point in polygon:
        point3d = (point[0], point[1], 0)
        gluTessVertex(tess, point3d, point3d)
    gluTessEndContour(tess)

    #then handle each of the holes, if applicable
    if holes != []:
        for hole in holes:
            gluTessBeginContour(tess)
            for point in hole:
                point3d = (point[0], point[1], 0)
                gluTessVertex(tess, point3d, point3d)
            gluTessEndContour(tess)

    gluTessEndPolygon(tess)
    gluDeleteTess(tess)
    return vertices