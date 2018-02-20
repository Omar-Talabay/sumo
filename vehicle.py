# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 18:04:56 2018

@author: otalabay
"""
     
import traci
import socket
import numpy as np
import msg_types
import struct
import math
import re

import threading

lock = threading.Lock()

class Vehicle(object):
    def __init__(self, car_id, conn, ip):
        self.v_id = car_id
        self.conn = conn
        self.ip = ip

connections_number = 1000

vehicles_list = []
        
BUFFER_SIZE = 1024

def start_tcp_server():
    print 'tcp server has started'
    
    TCP_IP = '127.0.0.1'
    TCP_PORT = 6666
    
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    s.bind((TCP_IP, TCP_PORT))
    s.listen(10)
    
    counter = 0
    while True:
        
        
        conn, ip = s.accept()
        
        print str(ip[0])+' has joined'
        
        #car_id = conn.recv(BUFFER_SIZE)
        #car_id = struct.unpack(b'>i', car_id)[0]
        #print car_id
        
        vehicle = Vehicle(counter, conn, ip[0])
        vehicles_list.append(vehicle)
        
        counter +=1
        
        thread.start_new_thread(handle_received_msgs, (vehicle,))
        
        
  
def broadcast_local_info(vehicle_ids, positions, angles, speeds):
    for vehicle in vehicles_list:
        for v_id, pos, angle, speed in zip(vehicle_ids, positions, angles, speeds):
            # to ensure a vehicle doesn't send to itself
            #if vehicle.v_id == v_id:
            x,y = pos
            x = int(x*10000000)
            y = int(y*10000000)
            
            angle = int(angle*math.pi/180)
            speed = int(speed)
            
            msg = struct.pack(b'>6i', msg_types.LOCAL_INFO, v_id, x, y, angle, speed)
            
            vehicle.conn.send(msg)
            print vehicle.v_id,vehicle.conn
            


def broadcast_specialized_msgs():
    msgs_pool = append_del_read_msg_pool(None, 'copy')
    for vehicle in vehicles_list:
        for v_id, msg in msgs_pool:
            if vehicle.v_id != v_id:
                msg = struct.pack(b'>'+str(len(msg))+'i', *msg)
                vehicle.conn.send(msg)


# this should not be used directly
# of shape [ [v_id, tuple of the message] ]
msgs_pool = []

def append_del_read_msg_pool(msg, mode):
    lock.acquire()
    msg_pool_new = []
    try:
        if mode == 'append':
            add_msg_2_pool(msg)
        elif mode == 'del':
            del_from_msg_pool(msg)
        else:
            msg_pool_new = msgs_pool[:]
        
    finally:
        lock.release()
    if mode == 'copy':
        return msg_pool_new

# it deletes associated messages before adding a new one
#input shape: [v_id, tuple of the msg]
def add_msg_2_pool(msg):
    # if there is a preveous msg for the same vehicle and the same msg type
    del_from_msg_pool(msg)
    msgs_pool.append(msg)
    
# delete messages from msg_pool by v_id and msg_type
#input shape: [v_id, tuple of the msg]
def del_from_msg_pool(msg):
    idxs = [i for i in range(len(msgs_pool)) if msg[0] == msgs_pool[i][0]]
    
    for idx in idxs:
        del msgs_pool[idx]

def handle_received_msgs(vehicle):
    
    while True:
        raw_msg = vehicle.conn.recv(BUFFER_SIZE)
        
        if raw_msg is None:
            return
        
        # multiple messages can be sent by a vehicle
        for msg in raw_msg.split('\\r'):
            if len(msg)/4 != 0 or len(msg) == 0:
                continue
            msg = list(struct.unpack(b'>'+str(len(msg)/4)+'i', msg))
            msg_type = msg[0]
            
            if msg_type == msg_types.LSM or msg_type == msg_types.TLS or \
            msg_type == msg_types.PM or msg_types.DANGER:
                
                if msg_type != msg_types.PM:
                    
                    idx = 2 if msg_type == msg_types.TLS else 1
                    
                    msg.insert(idx, vehicle.v_id)
                    
                append_del_read_msg_pool([vehicle.v_id, msg], 'append')
                    
            elif msg_type == msg_types.STOP_DANGER or \
            msg_type == msg_types.TLS_STOP or \
            msg_type == msg_types.PM_STOP:
                
                append_del_read_msg_pool([vehicle.v_id, msg], 'del')
        
            
    
import time    
def start_sumo_server():
    print 'sumo server has started'
    sumoCmd = ['sumo-gui', '-c', 'sumoTestCode.sumocfg', '--step-length', '0.25']
    traci.start(sumoCmd)
    while True:
        traci.simulationStep()
        sumo_vehicles_list =  set(traci.vehicle.getIDList())
        sumo_vehicles_list = [int(re.findall('\d+', i)[0]) for i in sumo_vehicles_list]
        
        # for debuging
        if 3 in sumo_vehicles_list:
            print sumo_vehicles_list
        
        obu_vehicle_list = set([i.v_id for i in vehicles_list])
        
        vehicles_capable = \
            list(obu_vehicle_list.intersection(sumo_vehicles_list))
        if len(vehicles_capable) > 0:
            print vehicles_capable
            
            vehicles_capable_2 = ['veh'+str(i) for i in vehicles_capable]
            
            positions = [traci.vehicle.getPosition(i) for i in vehicles_capable_2]
            positions = [traci.simulation.convertGeo(i[0], i[1]) for i in positions]
            
            angles = [traci.vehicle.getAngle(i) for i in vehicles_capable_2]
            speeds = [traci.vehicle.getSpeed(i) for i in vehicles_capable_2]
        
            broadcast_local_info(vehicles_capable, positions, angles, speeds)
            
            #handle_received_msgs()
            
            broadcast_specialized_msgs()
            
        #time.sleep(.5)
      
        
        
    traci.stop()
    
    
import thread
if __name__ == "__main__": 
    
    
    
    thread.start_new_thread(start_tcp_server, ())
    # this just to wait until all clients are ready, then press enter
    raw_input()
    thread.start_new_thread(start_sumo_server, ())
    
    raw_input()
        
        