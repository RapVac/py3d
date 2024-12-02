from tkinter import *
from math import copysign, sin, cos, pi
from time import sleep
from random import choice

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

        # Unpacks
        v1=v1.get_v()
        v2=self.get_v()
        out=[]
        for i, x in enumerate(v1):
            out.append(v2[i]-x)
        return tuple(out)
        
    
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
 
s=0.03
c=Canvas(canvas)
## DOCUMENTING VIEW ORIENTATION!
## viewing zy plane (?), x is depth, disregard as 0
## greater x = further from view
lproject=((0, 0, 0),
           (-s, 1, 0),
           (-s, 0, 1))

project=Matrix(lproject)

vCamera=Vector((-1, 0, 0))

## Cube
v1=Vector((-100, 100, 100))
v2=Vector((-100, -100, 100))
v3=Vector((-100, 100, -100))
v4=Vector((-100, -100, -100))

v5=Vector((100, 100, 100))
v6=Vector((100, -100, 100))
v7=Vector((100, 100, -100))
v8=Vector((100, -100, -100))


t1=Line(v7, v8)
t2=Line(v7, v5)
t3=Line(v6, v5)
t4=Line(v8, v6)

t5=Line(v4, v3)
t6=Line(v4, v2)
t7=Line(v2, v1)
t8=Line(v3, v1)

t9=Line(v3, v7)
t10=Line(v5, v1)
t11=Line(v8, v4)
t12=Line(v6, v2)


p1=Plane(v4, v2, v3, "red")
p2=Plane(v7, v5, v8, "green")
p3=Plane(v1, v3, v2, "red")
p4=Plane(v6, v8, v5, "green")

p5=Plane(v8, v6, v4, "cyan")
p6=Plane(v2, v4, v6, "cyan")
p7=Plane(v3, v1, v7, "purple")
p8=Plane(v5, v7, v1, "purple")

p9=Plane(v5, v1, v6, "pink")
p10=Plane(v2, v6, v1, "pink")
p11=Plane(v3, v7, v4, "brown")
p12=Plane(v8, v4, v7, "brown")

points2=[v1, v2, v3, v4, v5, v6, v7, v8]
lines2=[t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12]
planes2=[p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12]

## Pyramid
n=100
w1=Vector((0+n,0+n,0+n))
w2=Vector((50+n,0+n,50+n))
w3=Vector((0+n, 50+n, 50+n))
w4=Vector((50+n,50+n,0+n))

u1=Line(w1, w2)
u2=Line(w2, w3)
u3=Line(w3, w4)
u4=Line(w1, w4)
u5=Line(w1, w3)
u6=Line(w2, w4)

q1=Plane(w1, w3, w4, "cyan")
q2=Plane(w1, w4, w2, "magenta")
q3=Plane(w4, w3, w2, "yellow")
q4=Plane(w2, w3, w1, "black")

points=[w1, w2, w3, w4]+points2
lines=[u1, u2, u3, u4, u5, u6]+lines2
planes=[q1, q2, q3, q4]+planes2

## This block generally renders out the points
def draw(lrender):
    for x in lrender:
        p1=project.project(x)
        c.draw_point(p1[1], p1[2])
#############
## This block renders out lines
def draw_lines(llines):
    for x in llines:
        p1=project.project(x.get_start())
        p2=project.project(x.get_end())
        c.draw_line( p1[1], p1[2], p2[1], p2[2] )
#############
## This function renders planes
def draw_faces(lfaces):
    for x in lfaces:
        if x.get_normal().dot_product(vCamera) >= 0:
            p1=project.project(x.get_p1())
            p2=project.project(x.get_p2())
            p3=project.project(x.get_p3())
            c.draw_poly([p1[1], p1[2], p2[1], p2[2], p3[1], p3[2]], x.get_color())
#############        
        


d=0.5
lrotatez=((cos(d*pi/180), -sin(d*pi/180), 0),
          (sin(d*pi/180), cos(d*pi/180), 0),
          (0, 0, 1))

lrotatex=((1, 0, 0),
          (0, cos(d*pi/180), -sin(d*pi/180)),
          (0, sin(d*pi/180), cos(d*pi/180)))

lrotatey=((cos(d*pi/180), 0, sin(d*pi/180)),
          (0, 1, 0),
          (-sin(d*pi/180), 0, cos(d*pi/180)))

rotatey=Matrix(lrotatey)

rotatez=Matrix(lrotatez)

rotatex=Matrix(lrotatex)

lshrink=((0.999, 0, 0),
         (0, 0.999, 0),
         (0, 0, 0.999))

shrink=Matrix(lshrink)

delay=0.001
while True:
    draw(points)
    draw_lines(lines)
    draw_faces(planes)
    tk.update()
    tk.update_idletasks()
    sleep(delay)
    canvas.delete("all")

    ## Transformations in loop
    for i, x in enumerate(points):
        p1=rotatey.product(x)
        temp=Vector(p1)
        p2=rotatez.product(temp)
        temp=Vector(p2)
        p3=shrink.product(temp)
        x.set_v(p3)

    draw(points)
    draw_lines(lines)
    draw_faces(planes)
    tk.update()
    tk.update_idletasks()
    sleep(delay)
    canvas.delete("all")
    
    
