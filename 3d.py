from tkinter import *
from math import copysign, sin, cos, pi
from time import sleep, time

def sign(x):
    return int(copysign(1, x))


tk=Tk()

size=500
if size % 2 != 0:
    raise ValueError("Size must be even")

tk.resizable(0, 0)
canvas=Canvas(tk, width=size, height=size, highlightthickness=0)
canvas.pack()
tk.update()

class Canvas:
    def __init__(self, canvas):
        self.canvas=canvas

    ## Converts from (0,0)=center to (0,0)=top_left
    def cx(self, x):
        return (canvas.winfo_width()/2)-x
    
    def cy(self, y):
        return (canvas.winfo_height()/2)-y
    
    def draw_point(self, x, y):
        c="black"
        canvas.create_oval(self.cx(x-1), self.cy(y-1), self.cx(x+1), self.cy(y+1), fill=c, outline=c)

    def draw_poly(self, lxy, c):
        for i in range(0, len(lxy)):
            if i%2==0:
                lxy[i] = self.cx(lxy[i])
            else:
                lxy[i] = self.cy(lxy[i])
                
        canvas.create_polygon(lxy, fill=c, outline="")
        
    def draw_line(self, x1, y1, x2, y2):
        canvas.create_line(self.cx(x1), self.cy(y1), self.cx(x2), self.cy(y2))

    def draw_pixel(self, x, y, color):
        canvas.create_rectangle(self.cx(x), self.cy(y), self.cx(x+1), self.cy(y+1), fill=color, outline="")


class Vector:
    ## 3d vector
    def __init__(self, t):
        if len(t) != 3:
            raise ValueError("Vector must be 3-dimensional")
        self.v=tuple(t)
        self.sign_map=[sign(v) for v in t]
        self.abs_map=[abs(v) for v in t]

    def get_v(self):
        return self.v

    def set_v(self, new_t):
        self.v=new_t
        self.sign_map=[sign(v) for v in new_t]
        self.abs_map=[abs(v) for v in new_t]

    def get_abs(self):
        return self.abs_map

    def get_signs(self):
        return self.sign_map

    ## Essentially does job of matrix:
    ## (sign_x, 0, 0)
    ## (0, sign_y, 0)
    ## (0, 0, sign_z)
    def combine_sign(self, absolute):
        if len(absolute) != 3:
            raise ValueError("Input must be 3-dimensional")
        o=[]
        for x in range(0, len(absolute)):
            o.append(absolute[x]*self.sign_map[x])
        return o
    
    ## Calculates self-v1
    def subtract(self, v1):
        if type(v1) != type(self):
            raise TypeError("Argument must be of type `Vector\'")
        v1=v1.get_v()
        v2=self.get_v()
        out=[]
        for i, x in enumerate(v1):
            out.append(v2[i]-x)
        return tuple(out)
    def add(self, v1):
        if type(v1) != type(self):
            raise TypeError("Argument must be of type `Vector\'")
        v1=v1.get_v()
        v2=self.get_v()
        out=[]
        for i, x in enumerate(v1):
            out.append(v2[i]+x)
        return tuple(out)
    
    def invert(self):
        return [-1*v for v in self.v]
    def magnitude(self):
        return ( self.v[0]**2 + self.v[1]**2 + self.v[2]**2 )**0.5
        
    
    def dot_product(self, v1):
        if type(v1) != type(self):
            raise TypeError("Argument must be of type `Vector\'")

        # Unpacks
        v1=v1.get_v()
        v2=self.get_v()
        out=0
        
        for x in range(0, len(v1)):
            out+=v1[x]*v2[x]
        return out

    def cross_product(self, v1):
        if type(v1) != type(self):
            raise TypeError("Argument must be of type `Vector\'")
        # Unpacks
        a=v1.get_v()
        b=self.get_v()

        ## a2*b3 - a3*b2
        ## a3*b1 - a1*b3
        ## a1*b2 - b1*a2
        out=( a[1]*b[2] - a[2]*b[1], a[2]*b[0] - b[2]*a[0], a[0]*b[1] - b[0]*a[1])
        return Vector(out)

class Line:
    def __init__(self, point_1: Vector, point_2: Vector):
        self.p1=point_1
        self.p2=point_2
    def get_start(self):
        return self.p1
    def get_end(self):
        return self.p2
    def get_vector(self):
        out=[]
        for i, x in enumerate(self.p1.get_v()):
            
            out.append(self.p2.get_v()[i]-x)

        return Vector(out)

class Plane:
    ## point_1 is corner/basis vector, i.e.
    ## p2
    ## |
    ## p1--p3
    ## Prioritize up then right
    ## (base, up, right)
    def __init__(self, point_1: Vector, point_2: Vector, point_3: Vector, color):
        self.p1=point_1
        self.p2=point_2
        self.p3=point_3
        self.color=color
    def get_color(self):
        return self.color
    def set_color(self, new_color):
        self.color=new_color
    
    def get_p1(self):
        return self.p1
    def get_p2(self):
        return self.p2
    def get_p3(self):
        return self.p3
    
    def get_normal(self):
        return Vector(self.p2.subtract(self.p1)).cross_product( Vector(self.p3.subtract(self.p1)) )
        

class Matrix:
    ## n x n list -> n x n matrix
    def __init__(self, l):
        self.l=l

    def get_l(self):
        return self.l
    
    def product(self, v: Vector):
        if isinstance(v, Vector) != True:
            raise TypeError("Argument must be of type `Vector\'")
        if len(v.get_v()) != len(self.l):
            raise ValueError("Matrix and Vector must be of same size")

        out=[]

        for x in range(0, len(self.l)):
            temp=Vector(self.l[x])
            out.append(v.dot_product(temp))
        del temp
        return out            

    def project(self, v: Vector):
        p=self.product(Vector(v.get_abs()))
        return v.combine_sign(p)

    def transform(self, points_list):
        for x in points_list:
            x.set_v(self.product(x))
        return points_list

class Ray_Source:
    def __init__(self, origin: Vector):
        self.o=origin

    def set_origin(self, new_o):
        self.o=new_o

    ## I cannot claim to have done the linear algebra myself.
    ## https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection
    ## Convenient solutions were acquired here.
    def is_in_plane(self, ray, plane):
        if isinstance(ray, Vector) != True:
            raise TypeError("`ray\' (arg 1) must be of type `Vector\'")
        elif isinstance(plane, Plane) != True:
            raise TypeError("`plane\' (arg 2) must be of type `Plane\'")

        p0=plane.get_p1()
        p01=Vector(plane.get_p2().subtract(p0))
        p02=Vector(plane.get_p3().subtract(p0))
        denom=Vector(ray.invert()).dot_product( plane.get_normal() )

        u = p02.cross_product( Vector(ray.invert()) ).dot_product( Vector(self.o.subtract( p0 )) )/denom
        
        v = Vector( ray.invert() ).cross_product( p01 ).dot_product( Vector(self.o.subtract( p0 )) )/denom

        if (u+v)<=1 and 0<=v<=1 and 0<=u<=1:
            t = p01.cross_product(p02).dot_product( Vector(self.o.subtract(p0)) ) / denom
            return (t, plane)
        else:
            return (10000000000000, plane)

class Bound_Box:
    def __init__(self, points, planes, cam):
        ## List of Vector objects
        self.points=points
        self.planes=planes
        self.center=Vector((0,0,0))
        self.radius=0
        self.cam=cam
        
    def get_radius(self):
        return self.radius

    def get_center(self):
        return self.center

    def get_planes(self):
        return self.planes

    def update(self):
        self.center = Vector( (sum([points.get_v()[0] for points in points])/len(points),
                        sum([points.get_v()[1] for points in points])/len(points),
                        sum([points.get_v()[2] for points in points])/len(points) ) )
        best=Vector(self.center.subtract(points[0]))
        for p in points[1:]:
            if Vector(self.center.subtract(p)).magnitude() > best.magnitude():
                best=Vector(self.center.subtract(p))
        self.radius=best

    def is_hit(self, ray: Vector):
        return Vector(self.center.subtract( ray )).cross_product(self.cam).magnitude() /  self.cam.magnitude() < self.radius.magnitude()

class Obj_Reader:
    def __init__(self, filename):
        self.loc="/".join(__file__.split("/")[:-1])+"/"
        self.file=self.loc+filename

    def set_file(self, new_file):
        self.file=self.loc+new_file

    ## Arbitrarily decided format:
    ## points lines planes
    ## x y z
    ## x y z...
    ## line_num1 line_num2
    ## line_num1 line_num2 line_num3
    def read(self):
        vectors=[]
        lines=[]
        planes=[]
        
        with open(self.file, "r") as f:
            f=f.read().split(sep="\n")
            for i, x in enumerate(f):
                if x == '' or x[0] == "#":
                    del f[i]
            lnum=0
            
            while lnum<len(f):
                line=f[lnum].split(sep=" ")
                if len(line)<4:
                    line=[int(line) for line in line]
                    color=""
                else:
                    color=line[-1]
                    line=[int(line) for line in line[:-1]]
    
                if len(line) == 3 and color == "":
                    vectors.append( Vector( (line[0], line[1], line[2]) ))
                elif len(line) == 3:
                    planes.append( Plane(vectors[line[0]-1], vectors[line[1]-1], vectors[line[2]-1], color) )
                    
                elif len(line) == 2:
                    lines.append( Line( vectors[line[0]-1], vectors[line[1]-1]) )
                lnum+=1

        return vectors, lines, planes


s=0.003
c=Canvas(canvas)
## DOCUMENTING VIEW ORIENTATION!
## viewing zy plane (?), x is depth, disregard as 0
## greater x = further from view
lproject=((0, 0, 0),
           (-s, 1, 0),
           (-s, 0, 1))

project=Matrix(lproject)
vCamera=Vector((-1, 0, 0))
r=Ray_Source( Vector( (200, -20, 20) ) )

read=Obj_Reader("cube.vec")
r=read.read()
points=r[0]
lines=r[1]
planes=r[2]


read.set_file("tetrahedron.vec")
r=read.read()
points=r[0]
lines=r[1]
planes=r[2]


##bTetr=Bound_Box(points2, planes2, vCamera)
##bCube=Bound_Box(points, planes, vCamera)
##bCube.update()
##bTetr.update()


## !! Bound boxes for ray tracing
b=Bound_Box(points, planes, vCamera)
b.update()


## This block generally renders out the points
def draw(lrender):
    for x in lrender:
        p1=project.project(x)
        c.draw_point(p1[1], p1[2])

## This block renders out lines
def draw_lines(llines):
    for x in llines:
        p1=project.project(x.get_start())
        p2=project.project(x.get_end())
        c.draw_line( p1[1], p1[2], p2[1], p2[2] )

## Backface culling; should be done before rendering and depth checks
def backfaces(lfaces):
    visible=[]
    for x in lfaces:
        if x.get_normal().dot_product(vCamera) >= 0:
            visible.append(x)
    return visible

## This function renders planes
def draw_faces(lfaces):
    for x in lfaces:
        p1=project.project(x.get_p1())
        p2=project.project(x.get_p2())
        p3=project.project(x.get_p3())
        c.draw_poly([p1[1], p1[2], p2[1], p2[2], p3[1], p3[2]], x.get_color())

## This does the same as the previous function, but implements ray tracing
def draw_faces_2(lfaces):
  
    for y in range(int(-size/2), int(size/2)):

        for x in range(int(-size/2), int(size/2)):
            ## Hard-code bounding box conditions here
            current_ray=Vector( (500, x, y) )
            if b.is_hit( current_ray ):
                l={}

                if bTetr.is_hit( current_ray ):
                    
                    for f in bTetr.get_planes():
                        r.set_origin( Vector( (500, x, y) ) )
                        res=r.is_in_plane(vCamera, f)
                        l[res[0]] = res[1]
                    
                    mn = min(l.keys())
                    if mn != 10000000000000:
                        c.draw_pixel(x, y, l[mn].get_color() )
                        continue
                    
                if bCube.is_hit( current_ray ):
                    
                    for f in bCube.get_planes():
                        r.set_origin( Vector( (500, x, y) ) )
                        res=r.is_in_plane(vCamera, f)
                        l[res[0]] = res[1]
                    
                    mn = min(l.keys())
                    if mn != 10000000000000:
                        c.draw_pixel(x, y, l[mn].get_color() )
                        continue
                    
            c.draw_pixel(x, y, "black")

def draw_faces_3(lfaces):

    for y in range(int(-size/2), int(size/2)):

        for x in range(int(-size/2), int(size/2)):
            ## Hard-code bounding box conditions here
            if b.is_hit(Vector( (500, x, y) )):

                l={}
                for f in lfaces:
                    r.set_origin( Vector( (500, x, y) ) )
                    res=r.is_in_plane(vCamera, f)
                    l[res[0]] = res[1]

                mn = min(l.keys())
                if mn != 10000000000000:
                    c.draw_pixel(x, y, l[mn].get_color() )
                    continue
            c.draw_pixel(x, y, "black")

def get_rotation_matrix(degrees, axis):
    if axis.lower() == "z":
        return ((cos(degrees*pi/180), -sin(degrees*pi/180), 0),
          (sin(degrees*pi/180), cos(degrees*pi/180), 0),
            (0, 0, 1))
    elif axis.lower() == "y":
        return ((cos(degrees*pi/180), 0, sin(degrees*pi/180)),
          (0, 1, 0),
          (-sin(degrees*pi/180), 0, cos(degrees*pi/180)))
    elif axis.lower() == "x":
        return ((1, 0, 0),
          (0, cos(degrees*pi/180), -sin(degrees*pi/180)),
          (0, sin(degrees*pi/180), cos(degrees*pi/180)))
##

def test():
    ti=time()
    canvas.delete("all")
    draw_faces_2(backfaces(planes))
    print(time()-ti)


d=0.25

lrotatez=get_rotation_matrix(d, "z")
lrotatez90=get_rotation_matrix(-90, "z")
lrotatey45=get_rotation_matrix(-45, "y")

lrotatex=get_rotation_matrix(d, "x")
lrotatey=get_rotation_matrix(d, "y")

rotatey=Matrix(lrotatey)
rotatey45=Matrix(lrotatey45)
rotatez=Matrix(lrotatez)
rotatez90=Matrix(lrotatez90)
rotatex=Matrix(lrotatex)

points=rotatez90.transform(points)

delay=0.001

while True:
    draw(points)
    draw_lines(lines)
    draw_faces(backfaces(planes))
    
    tk.update()
    tk.update_idletasks()
    sleep(delay)
    canvas.delete("all")

    ## Transformations
    points=rotatez.transform(points)
    points=rotatey.transform(points)
    
    b.update()


    draw(points)
    draw_lines(lines)
    draw_faces(backfaces(planes))
    
    tk.update()
    tk.update_idletasks()
    sleep(delay)
    canvas.delete("all")
