## Add after 3d.py while loop for multiprocess calculation. 
## Also requires draw_faces_2 to write to queue rather than list or direct draw.
q1=Queue()
q2=Queue()
q3=Queue()
q4=Queue()

p1=Process(target=draw_faces_2, args=( backfaces(planes), planes, 1, size**2/4+1, q1 ))
p2=Process(target=draw_faces_2, args=( backfaces(planes), planes, size**2/4+1, size**2/2+1, q2 ))
p3=Process(target=draw_faces_2, args=( backfaces(planes), planes, size**2/2+1, 3*size**2/4+1, q3 ))
p4=Process(target=draw_faces_2, args=( backfaces(planes), planes, 3*size**2/4+1, size**2+1, q4 ))

ti=time()

p1.start()
p2.start()
p3.start()
p4.start()

while (q1.qsize()+q2.qsize()+q3.qsize()+q4.qsize()) != 250000:
    pass

final1=[]
final2=[]
final3=[]
final4=[]

for x in range(0, int(size**2/4)):
    final1.append(q1.get())
    final2.append(q2.get())
    final3.append(q3.get())
    final4.append(q4.get())

p1.join()
p2.join()
p3.join()
p4.join()

final=final1+final2+final3+final4

print(len(final))

draw_from_array(final)
tk.update()

tf=time()

print(tf-ti)
sleep(5)
