import traci
import socket

from enum import Enum

class RadioMessageType(Enum):
    LOCAL_INFO = 1
    LSM = 2
    TLS = 3
    TLS_STOP = 4
    DANGER = 5
    STOP_DANGER = 6
    PM = 7
    PM_STOP = 8


import thread

TCP_IP = '127.0.0.1'
TCP_PORT = 6666
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()


sumoCmd = ['sumo', '-c', 'sumoTestCode.sumocfg', '--step-length', '0.25']

traci.start(sumoCmd)

step = 0 
while step < 10000:
    step += 1
    traci.simulationStep()
    
    
    v_list =  traci.vehicle.getIDList()
    
    positions = [traci.vehicle.getPosition(i) for i in v_list]
    positions = [traci.simulation.convertGeo(i[0], i[1]) for i in positions]
    
    angles = [traci.vehicle.getAngle(i) for i in v_list]
    
    v_list = [i for i in v_list if 'type1' in i]
    if len(v_list) > 0:
        for v_id in v_list:
            print v_id
            x,y =  traci.vehicle.getPosition(v_id)
            x,y =  traci.simulation.convertGeo(x,y)
            
            angle = traci.vehicle.getAngle(v_id)
            
            data = conn.recv(BUFFER_SIZE)
            if data is not None and data == 'end':
                break
            else:
                msg = [x,y,angle, addr[0] ]
                #msg = socket.htonl(msg[0])
                #print msg
                conn.send(msg)
            
        print

traci.stop()
conn.close()