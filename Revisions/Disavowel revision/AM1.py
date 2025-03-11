import socket 
import random
import hashlib
import time
import json
from tinyec import registry 
from tinyec.ec import Point
import secrets



PORT=5050
HEADER=64
FORMAT='utf-8'
ADDR=socket.gethostbyname(socket.gethostname()),PORT

machine=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
machine.connect(ADDR)
delta_T=0.01
#5-10 miliseconds 


#value_dict is our json dictionary of this machine's values 
#to be used in authentication 


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
ADDR='127.0.0.1',7070
AMDT2_socket.connect(ADDR)

disavowel_start_time=time.perf_counter()

AMDT2_socket.sendall(str(Pub).encode())

PUBA1=AMDT2_socket.recv(1024).decode(FORMAT) 
#print('A1 public key is: ',PUBA1)
#when we bring it over its as a string so we must remforat the json back to a python dict    randomvalue1=random.randint(0,q-1)
DISMSG1_string=AMDT2_socket.recv(1024).decode(FORMAT) 
DISMSG1=json.loads(DISMSG1_string)
x1=random.randint(1,q-1)
s1=random.randint(0,1024)
#print('s1: ',s1)
VAL1=mod_xp(p,DISMSG1['R1W1'],s1)*mod_xp(p,g,x1) % p 
VAL2=mod_xp(p,DISMSG1['L1A1'],s1)*mod_xp(p,int(PUBA1),x1)%p
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
        disavowel_end_time=time.perf_counter()

        print('-----DV for DTSMAKA-2 AMDT1-AM1-----')
        print(f'Time AMDT1 took to prove: ',round((disavowel_end_time-disavowel_start_time)*1000,5), 'milliseconds')

        print('AMDT1 is proved to know s1\n')
else:
    print('false')
    with open('output.txt', 'w') as file:
            file.write("TEST FAILED")




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
    #ask anusha about this RIGHT HERE
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
        else:
            print('false check two')
else:
        print('false check1')



#commit h1
#print('h1:',h1)

#h=pubkey
#s=i1/si
#m=the value we are commiting
#g=g
'''
h1_int=int.from_bytes(h1.encode(),'big')
commitment_r=random.randint(0,q-1)
commitment_c=pow(g,h1_int,p)*pow(Pub,commitment_r,p) % p 
AMDT2_socket.sendall((str(commitment_c)).encode())
'''
#print('commited h:',commitment_c)


'''
#INSTEAD OF S1, I1?
if DISMSG1['VAL1']==(pow(DISMSG1['R1W1'],i1,p)*pow(g,x1,p) % p):
    #print('pass')
    if DISMSG1['VAL2']==(pow(DISMSG1['L1A1'],i1,p)*pow(int(PUBA1),x1,p)%p):
        #print('pass2')
        byte_commit_DICT={'j1':j1,
                'h1_int': h1_int,
                'commit_r':commitment_r               
    }
    #print('V1 as str: ',DISMSG1_DICT['V1'])
        byte_commit_DICT=json.dumps( byte_commit_DICT).encode('utf-8')
        AMDT2_socket.sendall(byte_commit_DICT)
      
r2=random.randint(1,q-1)
R2=pow(g,r2,p)
K1=(pow(R2,Pr,p))


x2=int(AMDT2_socket.recv(1024).decode(FORMAT) )

s2=random.randint(0,1024)
VAL3=pow(R2,s2,p)*pow(g,x2,p) % p 
VAL4=pow(VAL3,Pr,p)
DISMSG2_DICT={'VAL3':VAL3,
                'VAL4': VAL4,
                 'R2W2': R2,
                   'K1B1': K1
         
    }
DISMSG2_DICT=json.dumps(DISMSG2_DICT).encode('utf-8')
              #print('senidng MGS4')
AMDT2_socket.sendall(DISMSG2_DICT)
commitment_c=int((AMDT2_socket.recv(1024).decode(FORMAT)))
    #print(commitment_c)

BYTE_COMMIT_DICT=AMDT2_socket.recv(1024).decode(FORMAT) 
BYTE_COMMIT_DICT=json.loads(BYTE_COMMIT_DICT)
    #print("right: ",(pow(g,h1_int,p)*pow(Pub,commitment_r,p) % p))
    #print('commit_c:',commitment_c)

    
if commitment_c==(pow(g,BYTE_COMMIT_DICT['h1_int'],p)*pow(int(PUBA1),BYTE_COMMIT_DICT['commit_r'],p) % p):
        h1=BYTE_COMMIT_DICT['h1_int'].to_bytes((BYTE_COMMIT_DICT['h1_int'].bit_length() + 7) // 8, 'big').decode()
        #print(h1)
        #print('pass1')
        if(h1==hash_data(BYTE_COMMIT_DICT['j1'],s2)):
            print('AMDT1 is proved to know s1')



        
   #     print(j1)
'''