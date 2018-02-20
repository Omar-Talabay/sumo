# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 23:06:34 2018

@author: otalabay
"""

import socket
import random
import struct

TCP_IP = '127.0.0.1'
TCP_PORT = 6667
BUFFER_SIZE = 1024
MESSAGE = "!"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(struct.pack('>i', 3))
while True: 
    
    data = s.recv(BUFFER_SIZE)
    print data
    
    
   
s.close()


