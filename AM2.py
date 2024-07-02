import socket 
import random
import hashlib
import time
import json
from tinyec import registry 
from tinyec.ec import Point
import secrets
from Crypto.Cipher import AES


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


def receive_file(conn, hashed_sesskey):
    file_start_time=time.perf_counter()

    msg_len_bytes = conn.recv(4)  # Receive the message length
    msg_len = int.from_bytes(msg_len_bytes, 'big')
    msg_json = bytearray()

    while len(msg_json) < msg_len:
        chunk = conn.recv(min(msg_len - len(msg_json), 1024))  # Receive the message in chunks
        msg_json.extend(chunk)

    msg_json = msg_json.decode()
    msg = json.loads(msg_json)

    extension = msg['extension']
    iv = bytes.fromhex(msg['iv'])  # Convert IV hex string back to bytes
    encrypted_file_data = bytes.fromhex(msg['encrypted_file_data'])  # Convert encrypted data hex string back to bytes

    cipher = AES.new(hashed_sesskey, AES.MODE_OFB, iv)
    decrypted_file_data = cipher.decrypt(encrypted_file_data)

    with open(f'AM2received_file{extension}', 'wb') as f:
        f.write(decrypted_file_data)
    file_end_time=time.perf_counter()
    print(f'{extension} file recieved from AMDT2')
    print(f'Recieving time for {extension} file from AMDT2: ',round((file_end_time-file_start_time)*1000, 5), 'milliseconds\n')

machine=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
machine.connect(ADDR)
delta_T=4
registry_start_time=time.time()

curve=registry.get_curve('secp256r1')
KbPr=secrets.randbelow(curve.field.n)
Y=KbPr *curve.g
ECCPubkeybytes=Y.x.to_bytes((Y.x.bit_length() + 7) // 8, 'big') + Y.y.to_bytes((Y.y.bit_length() + 7) // 8, 'big')

ECCREpubkey=machine.recv(1024)
machine.sendall(ECCPubkeybytes)
x,y=decompress(ECCREpubkey)
REdecompressed=Point(curve,x,y)
sharedkey=KbPr*REdecompressed
shared_key_bytes = sharedkey.x.to_bytes((sharedkey.x.bit_length() + 7) // 8, 'big')

encrypted_json = machine.recv(1024)

decrypted_json = xor_decrypt(encrypted_json, shared_key_bytes)


AMDT1=json.loads(decrypted_json)

RID=AMDT1['RID']
TID=AMDT1['TID']
Pr,Pub=AMDT1['Pr and Pub']
g=AMDT1['g']
p=AMDT1['p']
q=AMDT1['q']
print("-----REGISTRATION PHASE COMPLETE----- ")
registry_end_time=time.time()
print('Registration time for AM2: ',round((registry_end_time-registry_start_time)*1000,5), 'milliseconds\n')
#'10.106.95.180'
#connect to AMDT2
AMDT2_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR=socket.gethostbyname(socket.gethostname()),9090
AMDT2_socket.connect(ADDR)
Stage_2_start_time=time.perf_counter()

AMDT2_socket.sendall(str(Pub).encode())
PUBDT2=AMDT2_socket.recv(1024).decode(FORMAT) 
print('-----DTSMAKA 2 AMDT2-AM2-----')

#print('A1 public key is: ',PUBA1)



#step AMA2

MSG1_string=AMDT2_socket.recv(1024).decode(FORMAT) 
MSG1=json.loads(MSG1_string)
t1_2=time.time()
#print(f'-----AMA1 MSG RECEIVED-----')
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
        A2=pow(MSG1['R1W1'],c1,p)*pow(g,d1,p) % p 
        V2=hash_data(A2,t2)
        MSG2_DICT={'L2_A2':A2,
                   'V2': V2,
                   't2':t2
                    }
        #print('V1 as str: ',MSG1_DICT['V1'])
        MSG2=json.dumps(MSG2_DICT).encode('utf-8')
        #print('senidng')
        AMDT2_socket.sendall(MSG2)
        #print(f'-----AMA2 MSG SENT-----\n\n')


    else:
        print('value failed')
else:
    print("Failed time check")



#step AMA4
MSG3_string=AMDT2_socket.recv(1024).decode(FORMAT) 

MSG3=json.loads(MSG3_string)
t3_2=time.time()
#print(f'-----AMA3 MSG RECEIVED-----')
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
            part1=pow(int(PUBDT2),d1_e1,p)
            part2=pow(MSG1['L1A1'],c1,p)

            #print("L1:", MSG1['L1'])
            #print('x1: ',x1)
            #print('p:', p)
            SAM_b_comparison=part1*part2 % p 

            #print(SAD_b_comparison,"\n")
            #print(MSG3['AD_b'])
            if MSG3['AD_AM_b']==SAM_b_comparison:

                w2=random.randint(1,q-1)
                t4=time.time()
                W2=pow(g,w2,p)

                W1w=pow(MSG1['R1W1'],w2,p)
                W1Pr=pow(MSG1['R1W1'],Pr,p)
                Pubw2=pow(int(PUBDT2),w2,p)

                SessionkeyAM2DT2=hash_data(W1w,W1Pr,Pubw2)
                B1=(pow(W2,Pr,p))
                V4=hash_data(TID,B1,W2)
                V5=hash_data(SessionkeyAM2DT2,t4)
                MSG4_DICT={'TIDA2AM':TID,
                   'R2W2': W2,
                   'K1B1': B1,
                   'V4': str(V4),
                   'V5': str(V5),
                   't4': t4
                    }
                MSG4=json.dumps(MSG4_DICT).encode('utf-8')
                #print('senidng MGS4')
                AMDT2_socket.sendall(MSG4)
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
MSG5_string=AMDT2_socket.recv(1024).decode(FORMAT) 

MSG5=json.loads(MSG5_string)
t5_2=time.time()
#print(f'-----AMA5 MSG RECEIVED-----')
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

        SAM2a=pow(int(MSG5['K2B2']),1,p)*pow(g,e2,p) % p 
        SAM2b=pow(SAM2a,Pr,p)
        V7=hash_data(SAM2a,SAM2b,e2,W2)
        MSG6_DICT={'SAD_AM2a':SAM2a,
                   'SAD_AM2b': SAM2b,
                   'z2_e2':e2,
                   'V7': str(V7),
                   't6': t6
                    }
        MSG6=json.dumps(MSG6_DICT).encode('utf-8')
        #print('senidng MGS6')
        AMDT2_socket.sendall(MSG6)
        AMDT2_socket.sendall(SessionkeyAM2DT2.encode())
        #print(f'-----AMA6 MSG SENT-----\n\n')
    else:
        print("V6 check failed")
else:
    print('time 5 failed')  

answer=AMDT2_socket.recv(1024).decode(FORMAT) 
if answer=='create new TID':
    TIDnew=hash_data(TID,Pub,w2,MSG5['t5'])

Stage_2_end_time=time.perf_counter()

#print('-----Phase 2 Summary-----')
print('Authentication time for AMDT2: ',round((end_auth_time-Stage_2_start_time)*1000,5), 'milliseconds')
print('Overall time for DTSMAKA-2: ',round((Stage_2_end_time-Stage_2_start_time)*1000,5), 'milliseconds')
print('Session key AMDT2-AM2: ',SessionkeyAM2DT2,'\n\n')


hashed_sessAM2DT2key=hashlib.sha256(SessionkeyAM2DT2.encode()).digest()


print('-----Recieving gcode file TO AMDT2-----')
receive_file(AMDT2_socket,hashed_sessAM2DT2key)


print('-----Recieving ngc file TO AMDT2-----')
receive_file(AMDT2_socket,hashed_sessAM2DT2key)





