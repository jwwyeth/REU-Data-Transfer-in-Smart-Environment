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

machine=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
machine.connect(ADDR)
delta_T=0.01
#5-10 miliseconds 

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

#value_dict is our json dictionary of this machine's values 
#to be used in authentication 
def disavowel_AMDT1(AMDT2_socket,PUBA1):
    rlist, _, _ = select.select([AMDT2_socket], [], [], 2)  # 1-second timeout
    if rlist:
        disavowel_start_time=time.time()

            #print('A1 public key is: ',PUBA1)
        #when we bring it over its as a string so we must remforat the json back to a python dict    randomvalue1=random.randint(0,q-1)
        DISMSG1_string=AMDT2_socket.recv(1024).decode(FORMAT) 
        DISMSG1=json.loads(DISMSG1_string)
        x1=random.randint(1,q-1)
        s1=random.randint(0,1024)
        #print('s1: ',s1)
        VAL1=mod_xp(p,DISMSG1['R1W1'],s1)*mod_xp(p,g,x1) % p 
        VAL2=mod_xp(p,4,s1)*mod_xp(p,int(PUBA1),x1)%p

        #VAL2=pow(DISMSG1['L1A1'],s1,p)*pow(int(PUBA1),x1,p)%p
        #print("V2",V2)
            #print('V1 pre str converison:', V1)
            
        DISMSG2_DICT={'VAL1':VAL1,
                        'VAL2': VAL2,
                        'x1':x1
        }
        DISMSG2=json.dumps(DISMSG2_DICT).encode('utf-8')

        AMDT2_socket.sendall(DISMSG2)

        DISMSG3_string=AMDT2_socket.recv(1024).decode(FORMAT) 
        DISMSG3=json.loads(DISMSG3_string)

        #IS s1 an i1 one?

        if DISMSG3['h1']==hash_data(DISMSG3['j1'],s1):
            disavowel_end_time=time.time()

            print('-----DV for DTSMAKA-1 AMDT1-AMDT2-----')
            print('Time AMDT1 took to prove: ',round((disavowel_end_time-disavowel_start_time)*1000,5), 'milliseconds')
            print('AMDT1 is proved to know s1\n')
        else:
            print('false')
            with open('output.txt', 'w') as file:
                file.write("TEST FAILED")
        #=============================================
        r2=random.randint(1,q-1)
        R2W2=mod_xp(p,g,r2)
        K1B1=(mod_xp(p,R2W2,Pr))

        DISMSG4={'R2W2': R2W2,
            'K1B1': K1B1   
            }
        DISMSG4=json.dumps(DISMSG4).encode('utf-8')

        AMDT2_socket.sendall(DISMSG4)

        DISMSG5_string=AMDT2_socket.recv(1024).decode(FORMAT) 
        DISMSG5=json.loads(DISMSG5_string)
        numerator=mod_xp(p,DISMSG5['VAL3'],Pr)
        
        for i2 in range(0,1024):
                #numerator == VAL2
            denominator=mod_xp(p,K1B1,i2)*mod_xp(p,int(Pub),DISMSG5['x2'])%p
            if ((numerator/denominator)==1):
                    i2=i2
                    break
        #print('out of loop:',i2)

        j2=random.randint(0,q-1)
        h2=hash_data(j2,i2)
        if(DISMSG5['VAL3']==(mod_xp(p,R2W2,i2)*mod_xp(p,g,DISMSG5['x2']) % p )):
                if(DISMSG5['VAL4']==mod_xp(p,K1B1,i2)*mod_xp(p,int(Pub),DISMSG5['x2'])%p):
                    DISMSG6_DICT={
                        'h2':h2,
                        'j2':j2
                        
                        }
                    
                    DISMSG6=json.dumps(DISMSG6_DICT).encode('utf-8')
                    AMDT2_socket.sendall(DISMSG6)
                    return True
                else:
                    return False
        else:
                return False
    else:
         return None


def disavowel_AM2(conn,PUBpartner):
    disavowel_start_time=time.perf_counter()

    randomvalue1=random.randint(0,q-1)
    R1W1=mod_xp(p,g,randomvalue1)
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

    
    for i1 in range(0,1024):
        #numerator == VAL2
        denominator=mod_xp(p,L1A1,i1)*mod_xp(p,int(Pub),DISMSG2['x1'])%p
        if ((numerator/denominator)==1):
            i1=i1
            break
    #print('out of loop:',i1)

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
            return False
    else:
        with open('output.txt', 'w') as file:
            file.write("TEST FAILED")
        return False
    
   


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

        print('-----DTSMAKA-2 AMDT2-AM2-----')
        print(f'Time AM2 took to prove: ',round((disavowel_end_time-disavowel_start2_time)*1000,5), 'milliseconds')
        print('Overall Disavowel time: ',round((disavowel_end_time-disavowel_start_time)*1000,5), 'milliseconds')


        print('AM2 is proved to know s2\n')

        return  True
    else:
        print("Failed")
        with open('output.txt', 'w') as file:
            file.write("TEST FAILED")


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


AMDT2_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR='127.0.0.1',8080
AMDT2_socket.connect(ADDR)
AMDT2_socket.sendall(str(Pub).encode())
PUBA1=AMDT2_socket.recv(1024).decode(FORMAT) 
disavowel_AMDT1(AMDT2_socket,PUBA1)

'''
AM2_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR=socket.gethostbyname(socket.gethostname()),9090
AM2_socket.bind(ADDR)
AM2_socket.listen(1)
AM2,address=AM2_socket.accept()
PUBAM2=AM2.recv(1024).decode()
AM2.sendall(str(Pub).encode())
disavowel_AM2(AM2,PUBAM2)

'''