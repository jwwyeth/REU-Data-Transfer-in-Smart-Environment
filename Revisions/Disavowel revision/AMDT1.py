
import socket 
import random
import hashlib
import time
import json
from tinyec import registry 
from tinyec.ec import Point
import secrets
import select


PORT=5050
HEADER=64
FORMAT='utf-8'
ADDR=socket.gethostbyname(socket.gethostname()),PORT

delta_T=0.01

def mod_xp(modulus_n, base_a, integer_b):
    
    #print('working on mod xp')
    x=base_a
    t=1
    #print(t)
    while integer_b>0:
        if ((integer_b%2)!=0):
            t=t*x % modulus_n
            integer_b=integer_b-1
        x=(x**2)%modulus_n
        integer_b=integer_b//2
    return t

def decompress(pubKeyBytes):
    x = int.from_bytes(pubKeyBytes[:32], 'big')
    y = int.from_bytes(pubKeyBytes[32:], 'big')
    return x, y

def xor_decrypt(ciphertext, key):
    plaintext = bytearray()
    for i, c in enumerate(ciphertext):
        plaintext.append(c ^ key[i % len(key)])
    return bytes(plaintext).decode()

def hash_data(*args):
    string=''.join(str(arg) for arg in args)
    return hashlib.sha512(string.encode()).hexdigest()


def disavowe(conn,PUBpartner,name):
    disavowel_start_time=time.perf_counter()

    
    randomvalue1=random.randint(0,q-1)
    R1W1=mod_xp(p,g,randomvalue1)
    #L1A1=random.randint(0,1024)
    L1A1=(mod_xp(p,R1W1,Pr))
    DISMSG1_DICT={
                'L1A1':L1A1,
                'R1W1':R1W1
    }
    DISMSG1=json.dumps(DISMSG1_DICT).encode('utf-8')
    conn.sendall(DISMSG1)
    DISMSG2_string=conn.recv(1024).decode(FORMAT) 
    DISMSG2=json.loads(DISMSG2_string)

    numerator=mod_xp(p,DISMSG2['VAL1'],Pr)
    #print(numerator)
    #DISMSG2['x1']=2
   
    for i1 in range(0,1024):
        #numerator == VAL2
        denominator=mod_xp(p,L1A1,i1)*mod_xp(p,int(Pub),DISMSG2['x1'])%p
        if ((numerator/denominator)==1):
            i1=i1
            break
   
    
    j1=random.randint(0,q-1)
    h1=hash_data(j1,i1)
    if(DISMSG2['VAL1']==(mod_xp(p,R1W1,i1)*mod_xp(p,g,DISMSG2['x1']) % p )):
    
        if(DISMSG2['VAL2']==mod_xp(p,L1A1,i1)*mod_xp(p,int(Pub),DISMSG2['x1'])%p):
               DISMSG3_DICT={
                'h1':h1,
                'j1':j1
                }
               
               DISMSG3=json.dumps(DISMSG3_DICT).encode('utf-8')
               conn.sendall(DISMSG3)
        else:
        
            print('Invalid L1 value given, step DV13 failed')
            #print('Ending Authentication\n')
            with open('output.txt', 'a') as file:
                file.write("TEST FAILED\n")
            return False
    else:
        return False
   

    rlist, _, _ = select.select([conn], [], [], 2)  # 1-second timeout
    if rlist:
        disavowel_start2_time=time.perf_counter()

        DISMSG4=conn.recv(1024).decode(FORMAT) 
        DISMSG4=json.loads(DISMSG4)
        x2=random.randint(1,q-1)
        s2=random.randint(0,1024)
        VAL3=mod_xp(p,DISMSG4['R2W2'],s2)*mod_xp(p,g,x2) % p 
        VAL4=mod_xp(p,DISMSG4['K1B1'],s2)*mod_xp(p,int(PUBpartner),x2)%p
        DISMSG5_DICT={
                    'VAL3':VAL3,
                    'VAL4':VAL4,
                    'x2':x2
                    }
        DISMSG5=json.dumps(DISMSG5_DICT).encode('utf-8')
        conn.sendall(DISMSG5)


        DISMSG6_string=conn.recv(1024).decode(FORMAT) 
        DISMSG6=json.loads(DISMSG6_string)
        if DISMSG6['h2']==hash_data(DISMSG6['j2'],s2):

            disavowel_end_time=time.perf_counter()
            print(f'Time {name} took to prove: ',round((disavowel_end_time-disavowel_start2_time)*1000,5), 'milliseconds')
            print('Overall Disavowel time: ',round((disavowel_end_time-disavowel_start_time)*1000,5), 'milliseconds')

            return  True
    else:
        print("timeout")
 
        return None 




machine=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
machine.connect(ADDR)
registry_start_time=time.perf_counter()
# Receive the symmetric key from the server
shared_key_bytes = machine.recv(1024)
# Receive the encrypted JSON data from the server
encrypted_json = machine.recv(1024)
# Decrypt the JSON data using the shared key
decrypted_json = xor_decrypt(encrypted_json, shared_key_bytes)


AM1=json.loads(decrypted_json)

RID=AM1['RID']
TID=AM1['TID']
Pr,Pub=AM1['Pr and Pub']
g=AM1['g']
p=AM1['p']
q=AM1['q']
machine.close()
#print("-----REGISTRATION PHASE COMPLETE----- ")

print('----- DV for DTSMAKA-1 AMDT1-AMDT2-----')

#step ADT1
AMDT1_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR='127.0.0.1',8080
AMDT1_socket.bind(ADDR)
AMDT1_socket.listen(1)
connection,address=AMDT1_socket.accept()
PUBA2=connection.recv(1024).decode()
connection.sendall(str(Pub).encode())

if disavowe(connection,PUBA2,'AMDT2'):
    print('AMDT2 is proved to know s2\n')
else:
    print('Ending Authentication\n')



'''

print('-----DV for DTSMAKA-2 AMDT1-AM1-----')



#STAGe 2 DT_AM
AM1_AM_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR='127.0.0.1',7070
AM1_AM_socket.bind(ADDR)
AM1_AM_socket.listen(1)
AM1,address=AM1_AM_socket.accept()
PUBAM=AM1.recv(1024).decode()
AM1.sendall(str(Pub).encode())

#step AMA1
if disavowe(AM1,PUBAM,'AM1'):
    print('AM1 is proved to know s2')
else:
    print('Ending Authentication\n')

#step AMA3
#step AMA4
'''
#after initalizeiton no RE Involved
 

#any entity that wants to make private an d public key class?