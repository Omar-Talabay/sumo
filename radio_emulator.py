# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 16:21:49 2018

@author: otalabay
"""

import traci
import socket
import numpy as np

import cPickle as pickle

import multiprocessing as mp

import msg_types

connections_number = 1000


# this should be used via add_msgs_2_pool only
msgs_pool = []

RUNNING_FLAG = True

def add_msgs_2_pool(msgs):
    for msg in msgs:
        msgs_pool.append(msg)
        
def del_msgs_from_pool(addrs):
    delete_list = []
    for idx, msg in enumerate(msgs_pool):
        addr, msg = msg
        
        if addr in addrs:
            delete_list.append(idx)
            
    for i in reversed(delete_list):
        del msgs_pool[i]
    
            



BUFFER_SIZE = 1024

def tcp_server(connections_list):
    print 'tcp server has started'
    
    TCP_IP = '127.0.0.1'
    TCP_PORT = 6667
    
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    s.bind((TCP_IP, TCP_PORT))
    s.listen(10)
    
    
    while RUNNING_FLAG:
        
        
        conn, addr = s.accept()
        
        print str(addr[0])+' has joined'
        
        connections_list.append((conn, addr[0]))
        
import math
import struct
def broadcast_local_info(vehicle_ids, positions, angles, speeds, connections_list):
    for conn, addr in connections_list:
        for v_id, pos, angle, speed in zip(vehicle_ids, positions, angles, speeds):
            x,y = pos
            
            angle *= math.pi/180
            
            x *= 10000000
            y *= 10000000
            
            msg = np.array([1, 1, x, y, angle, speed]).\
            astype(np.int32)
            
            msg = struct.pack(b'>6i', 1, 1, int(x), int(y), \
                              int(angle), int(speed))
            
          
            conn.send(msg)

def broadcast_pool_msgs(connections_list):
    for conn in connections_list:
        for addr, msg in msgs_pool:
            pass

def decode_msg(msg):
    pass

def encode(msg):
    return socket.htonl(msg[2])

def get_msg_type(msg):
    msg_decoded = decode_msg(msg)
    return msg_decoded[0]

BUFFER_SIZE=1024
def handle_received_msgs(connections_list):
    # new non-local messages recieved
    temp_msgs = []
    # deleted messages indecies from the pool
    # step number 4 from "General instructions for the radio"
    msgs_2_b_deleted = []
    
    for conn, addr in connections_list:
        data = conn.recv(BUFFER_SIZE)
        
        if data is None:
            continue
        else:
            # one connection may send multiple messages
            # each message should append end of message char
            msgs = data.split('\n')
            for msg in msgs:
                
                msg_type = get_msg_type(msg)
                if msg_type == msg_types.LSM or msg_type == msg_types.TLS or \
                msg_type == msg_types.PM:
                    
                    temp_msgs.append([addr,msg])
                    
                elif msg_type == msg_types.STOP_DANGER or \
                msg_type == msg_types.TLS_STOP or \
                msg_type == msg_types.PM_STOP:
                    
                    msgs_2_b_deleted.append(addr)
                    
                else:
                    # un handled msg type
                    pass
                    
                    
    del_msgs_from_pool(msgs_2_b_deleted)
    add_msgs_2_pool(temp_msgs)
                    
                    
            

import time     
def sumo_server(connections_list):
    print 'sumo server has started'
    sumoCmd = ['sumo', '-c', 'sumoTestCode.sumocfg', '--step-length', '0.25']
    traci.start(sumoCmd)
    while RUNNING_FLAG:
  
        
        traci.simulationStep()
        vehicle_list =  traci.vehicle.getIDList()
        
        positions = [traci.vehicle.getPosition(i) for i in vehicle_list]
        positions = [traci.simulation.convertGeo(i[0], i[1]) for i in positions]
        
        angles = [traci.vehicle.getAngle(i) for i in vehicle_list]
        speeds = [traci.vehicle.getSpeed(i) for i in vehicle_list]
        
        broadcast_local_info(vehicle_list, positions, angles, speeds, connections_list)
        
        #handle_received_msgs(connections_list)
        
        #broadcast_pool_msgs(connections_list)
        
        
    traci.stop()
        
        
def main(p, connections_list):
    print '-----------------------------' 
    global RUNNING_FLAG
    if p == 0:
        
        tcp_server(connections_list)
    elif p == 1:
        sumo_server(connections_list)
    else:
        while RUNNING_FLAG:
            break
            flag = input('type 0 to exit: ')
            if flag == 0:
                RUNNING_FLAG = False

#connections_list = []
#manager = mp.Manager()
#connections_list = manager.list([])  
                
global connections_list
connections_list = []

import thread
if __name__ == "__main__": 
    
    
    thread.start_new_thread(main, (0,connections_list))
    thread.start_new_thread(main, (1,connections_list))
    
#    processes = [mp.Process(target=main, args=(i,connections_list,))\
#                 for i in range(2)]
#    
#    
#    
#    for p in processes:
#        p.start()
#        
#    for p in processes:
#        p.join()    