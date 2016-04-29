# -*- coding: utf-8 -*-
"""


@author: Vidyadhar
"""

#References
#1.	https://docs.python.org/3.4/howto/sockets.html
#2.	http://stackoverflow.com/questions/12454675/whats-the-return-value-of-socket-accept-in-python
#3.	https://docs.python.org/3.1/library/_thread.html


import socket
from _thread import start_new_thread
import re
import sys
import time

#Dictionary for caching web page information
cache={}

#thread function for creating 
def new_proxy_thread(client_conn):   
    start_time=time.time()
    original_request=client_conn.recv(4096);
    
    
    #If not GET method then decline request and terminate thread
    if str.encode('GET') not in original_request:
        client_conn.send(str.encode("Unsupported method has been received and will not be processed"));
        client_conn.close();
        return;
    
    #logging HTTP requets
    logging = open('log.txt', 'a');
    logging.writelines(original_request.decode('utf-8'))
    
    
    
    #parsing to get host etc.
    req = (original_request).decode('utf-8');
    req = req.split('\n');
    firstline=req[0].split(' ');
    print (firstline[1])
    
    
    if(firstline[0]=='GET'):
        secondline=re.split(' |\r',req[1]);
        host=secondline[1];
        if 'www.' not in host:
            host='www.'+host
        print ("Connecting to ",host);
        
        #Check if host name exists in cache if true then send data from cache
        #else create new entry in cache and insert data
        if firstline[1] in cache:
            print ("from cache")
            client_conn.send(cache[firstline[1]]);
            client_conn.close; 
        else:
            try:                
                new_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
                new_socket.connect((host,80));
                new_socket.send(original_request);
                from_web_server = new_socket.recv(4096);
                if str.encode('400') in from_web_server:
                    client_conn.send(str.encode("Error handling : Unable to process data because of 400"))
                    logging.writelines("Error handling : Unable to process data because of 400");
                    logging.writelines("\n-------------------------\n");
                    logging.close();
                    new_socket.close();
                    client_conn.close();                   
                    return
                if str.encode('404') in from_web_server:
                    client_conn.send(str.encode("Error handling : Unable to process data because of 404"))
                    new_socket.close();
                    client_conn.close(); 
                    logging.writelines("Error handling : Unable to process data because of 405");
                    logging.writelines("\n-------------------------\n");
                    logging.close();
                    return
                if str.encode('405') in from_web_server:
                    client_conn.send(str.encode("Error handling : Unable to process data because of 405"))
                    new_socket.close();
                    client_conn.close();  
                    logging.writelines("Error handling : Unable to process data because of 405")
                    logging.writelines("\n-------------------------\n");
                    logging.close();
                    return
                if(len(from_web_server)>0):
                    client_conn.send(from_web_server);                
                    cache[firstline[1]]=from_web_server
                    new_socket.close();
                    client_conn.close();
                    logging.writelines("Time taken : "+str(time.time()-start_time));
                    logging.writelines("\n-------------------------\n");
                    logging.close();                
            except socket.error as message:
                print ("Runtime error : ",message)
                sys.exit(1)
    else:
        client_conn.send(str.encode("Unsupported method has been received and will not be processed"));
        client_conn.close();

    
   
#Creating socket and listening on port 6 and also binding on port 8081
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM);
server_socket.bind(('',8081));
server_socket.listen(6);
while 1:
        (client_conn,client_address)=server_socket.accept();
        start_new_thread(new_proxy_thread,(client_conn,))
  
server_socket.close();
    
     