import socket 
import random
import hashlib
import time
import json
from Crypto.Cipher import AES
import os
import requests


PORT=5050
HEADER=64
FORMAT='utf-8'
SERVER=socket.gethostbyname(socket.gethostname())
ADDR=(SERVER,PORT)




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

def send_file(conn,data,extension,hashedkey,iv,cipher):
    
    encrypted_file_data = cipher.encrypt(data)
   # print('data:',data,'\n')
    #print('iv:',iv)
    #rint('encrypted data:',encrypted_file_data,"\n")
    msg = {
        'extension': extension,
        'iv': iv.hex(),  # Convert IV to hex string for transmission
        'encrypted_file_data': encrypted_file_data.hex()  # Convert encrypted data to hex string
    }
    msg_json = json.dumps(msg).encode('utf-8')
    msg_len = len(msg_json).to_bytes(4, 'big')  # Prefix the message with its length
    conn.sendall(msg_len + msg_json)
    return




machine=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
machine.connect(ADDR)
delta_T=3
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
print("-----REGISTRATION PHASE COMPLETE----- ")
registry_end_time=time.perf_counter()
print('Registration time for AM1: ',round((registry_end_time-registry_start_time)*1000,5), 'milliseconds\n')

#connect to AMDT1
AMDT1_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR=socket.gethostbyname(socket.gethostname()),7070
AMDT1_socket.connect(ADDR)
Stage_2_start_time=time.perf_counter()

AMDT1_socket.sendall(str(Pub).encode())
PUBA1=AMDT1_socket.recv(1024).decode(FORMAT) 
#print('A1 public key is: ',PUBA1)
print('-----DTSMAKA-2 AMDT1-AM1-----')



#step AMA2

MSG1_string=AMDT1_socket.recv(1024).decode(FORMAT) 
MSG1=json.loads(MSG1_string)
t1_2=time.time()
#print(f'-----AMA1 MSG RECIEVED-----')
'''
for key, value in MSG1.items():
        print(f"{key}: {value}")
'''
if abs(t1_2-MSG1['t1'])<=delta_T:
    #print('t1 time cheks')
    
    comparison=hash_data(MSG1['TID'],MSG1['L1A1'],MSG1['R1W1'])
    if MSG1['V1']==comparison:
        #print("V1 equivalent ")
        c1=random.randint(1,q-1)
        d1=random.randint(1,q-1)
        
        t2=time.time()
        #A2=pow(MSG1['R1W1'],c1,p)*pow(g,d1,p) % p 
        A2=mod_xp(p,MSG1['R1W1'],c1) * mod_xp(p,g,d1)  %p
        V2=hash_data(A2,t2)
        MSG2_DICT={'L2_A2':A2,
                   'V2': V2,
                   't2':t2
                    }
        #print('V1 as str: ',MSG1_DICT['V1'])
        MSG2=json.dumps(MSG2_DICT).encode('utf-8')
        #print('senidng')
        AMDT1_socket.sendall(MSG2)
        #print(f'-----AMA2 MSG SENT-----\n\n')


    else:
        print('value failed')
else:
    print("Failed time check")



#step AMA4
MSG3_string=AMDT1_socket.recv(1024).decode(FORMAT) 

MSG3=json.loads(MSG3_string)
t3_2=time.time()
#print(f'-----AMA3 MSG RECIEVED-----')
'''
for key, value in MSG3.items():
        print(f"{key}: {value}")
'''
if abs(t3_2-MSG3['t3'])<=delta_T:
    #print('Pass time 3')
    comparison=hash_data(MSG3['AD_AM_a'],MSG3['AD_AM_b'],MSG3['z_e'],MSG1['R1W1'])
    if MSG3['V3']==comparison:
        #print('V3 value checks')
        SAM_a_comparison=pow(A2,1,p)*pow(g,int(MSG3['z_e']),p) % p 
        if MSG3['AD_AM_a']==SAM_a_comparison:
            d1_e1=d1+MSG3['z_e']
           # part1=pow(int(PUBA1),d1_e1,p)
            part1=mod_xp(p,int(PUBA1),d1_e1)
           # part2=pow(MSG1['L1A1'],c1,p)
            part2=mod_xp(p,MSG1['L1A1'],c1)

            #print("L1:", MSG1['L1'])
            #print('x1: ',x1)
            #print('p:', p)
            SAM_b_comparison=part1*part2 % p 

            #print(SAD_b_comparison,"\n")
            #print(MSG3['AD_b'])
            if MSG3['AD_AM_b']==SAM_b_comparison:

                w2=random.randint(1,q-1)
                t4=time.time()
                #W2=pow(g,w2,p)
                W2=mod_xp(p,g,w2)

                #W1w=pow(MSG1['R1W1'],w2,p)
                W1w=mod_xp(p,MSG1['R1W1'],w2)
                #W1Pr=pow(MSG1['R1W1'],Pr,p)
                W1Pr=mod_xp(p,MSG1['R1W1'],Pr)
                #Pubw2=pow(int(PUBA1),w2,p)
                Pubw2=mod_xp(p,int(PUBA1),w2)


                SessionkeyAMAD=hash_data(W1w,W1Pr,Pubw2)
                #B1=(pow(W2,Pr,p))
                B1=mod_xp(p,W2,Pr)
                V4=hash_data(TID,B1,W2)
                V5=hash_data(SessionkeyAMAD,t4)
                MSG4_DICT={'TIDA2AM':TID,
                   'R2W2': W2,
                   'K1B1': B1,
                   'V4': str(V4),
                   'V5': str(V5),
                   't4': t4
                    }
                MSG4=json.dumps(MSG4_DICT).encode('utf-8')
                #print('senidng MGS4')
                AMDT1_socket.sendall(MSG4)
               # print(f'-----AMA4 MSG SENT-----\n\n')

            else:
                print('SAM_b failed')
        else:
            print('SAM_a failed')
    else:
        print('V3 failed')
else:
    print('t3 failed')

end_auth_time=time.perf_counter()

#step AMA6
MSG5_string=AMDT1_socket.recv(1024).decode(FORMAT) 

MSG5=json.loads(MSG5_string)
t5_2=time.time()
#print(f'-----AMA5 MSG RECIEVED-----')
'''
for key, value in MSG5.items():
        print(f"{key}: {value}")
'''
if abs(t5_2-MSG5['t5'])<=delta_T:
    #print('Pass time 5')
    comparison=hash_data(MSG5['K2B2'],MSG5['t5'])
    if MSG5['V6']==comparison:
        #print('V6 value checks')
        t6=time.time()
        e2=random.randint(1,q-1)

        #SAM2a=pow(int(MSG5['K2B2']),1,p)*pow(g,e2,p) % p 
        SAM2a=mod_xp(p,int(MSG5['K2B2']),1)*mod_xp(p,g,e2) % p 
        
       # SAM2b=pow(SAM2a,Pr,p)
        SAM2b=mod_xp(p,SAM2a,Pr)
        V7=hash_data(SAM2a,SAM2b,e2,W2)
        MSG6_DICT={'SAD_AM2a':SAM2a,
                   'SAD_AM2b': SAM2b,
                   'z2_e2':e2,
                   'V7': str(V7),
                   't6': t6
                    }
        MSG6=json.dumps(MSG6_DICT).encode('utf-8')
        #print('senidng MGS6')
        AMDT1_socket.sendall(MSG6)
        AMDT1_socket.sendall(SessionkeyAMAD.encode())
        #print(f'-----AMA6 MSG SENT-----\n\n')

    else:
        print("V6 check failed")
else:
    print('time 5 failed')  

answer=AMDT1_socket.recv(1024).decode(FORMAT) 
if answer=='create new TID':
    TIDnew=hash_data(TID,Pub,w2,MSG5['t5'])
Stage_2_end_time=time.perf_counter()
#print('\n-----Phase 2 Summary------------')

print('Authentication time for AMDT1: ',round((end_auth_time-Stage_2_start_time)*1000,5), 'milliseconds')

print('Overall time of DTSMAKA-2: ',round((Stage_2_end_time-Stage_2_start_time)*1000,5), 'milliseconds')

print('Session key AMDT1-AM1: ',SessionkeyAMAD,'\n\n')

iv = os.urandom(16)  # Generate a random 16-byte IV


hashed_sesskey=hashlib.sha256(SessionkeyAMAD.encode()).digest()




print('-----Sending gcode file to AMDT1-----')
#print(hashed_sessAMkey)
gcode_permalink = 'https://raw.github.com/jwwyeth/REU-Data-Transfer-in-Smart-Environment/a697fe33f43893aadc6b876c61253096f296ff89/Duet_Saeid_thin_wall.gcode'  # replace with the permalink

response = requests.get(gcode_permalink)
gcode_file_data = response.content
gcode_file_name, gcode_file_extension = os.path.splitext('Duet_Saeid_thin_wall.gcode')

file_start_time=time.perf_counter()
cipherAM1gcode = AES.new(hashed_sesskey, AES.MODE_OFB,iv)
send_file(AMDT1_socket,gcode_file_data,gcode_file_extension,hashed_sesskey,iv,cipherAM1gcode)
file_end_time=time.perf_counter()
print('.gcode file sent to AMDT1')
print('Sending time for gcode file to AMDT1: ',round((file_end_time-file_start_time)*1000, 5), 'milliseconds\n')


print('-----Sending ngc file to AMDT1-----')
#conn,data,extension,hashedkey,iv
ngc_permalink = 'https://raw.github.com/jwwyeth/REU-Data-Transfer-in-Smart-Environment/a697fe33f43893aadc6b876c61253096f296ff89/new2_Praneeth_Trial.ngc'  # replace with the permalink

response = requests.get(ngc_permalink)
ngc_file_data = response.content
ngc_file_name, ngc_file_extension = os.path.splitext('new2_Praneeth_Trial.ngc')
file_start_time=time.perf_counter()

cipherAM1ngc = AES.new(hashed_sesskey, AES.MODE_OFB,iv)
send_file(AMDT1_socket,ngc_file_data,ngc_file_extension,hashed_sesskey,iv,cipherAM1ngc)
file_end_time=time.perf_counter()
print('.ngc file sent to AMDT1')
print('Sending time for ngc file to AMDT1: ',round((file_end_time-file_start_time)*1000, 5), 'milliseconds\n')




