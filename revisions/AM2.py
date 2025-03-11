import socket 
import random
import hashlib
import time
import json
from Crypto.Cipher import AES
import select

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

def receive_file(conn, hashed_sesskey):
    # Record the start time for the file receiving process
   

    # Wait for the socket to be ready to receive data (first 4 bytes for the message length)
    rlist, _, _ = select.select([conn], [], [], 2)  # 1-second timeout
    if rlist:
        # Capture the time when the first byte is received
        start_recv_time = time.perf_counter()
        print('First byte received at:', start_recv_time)

        # Receive the message length (first 4 bytes)
        msg_len_bytes = conn.recv(4)
        #a = time.perf_counter()
       # print('post rcv len', a)
       # print('Time from first byte to receiving length:', (a - start_recv_time) * 1000, 'milliseconds')

        # Convert the 4-byte message length to an integer
        msg_len = int.from_bytes(msg_len_bytes, 'big')

        # Now receive the full message based on the length we got
        msg_json_bytes = conn.recv(msg_len)
        msg_json = msg_json_bytes.decode()
        msg = json.loads(msg_json)

        # Extract the necessary data from the message
        extension = msg['extension']
        iv = bytes.fromhex(msg['iv'])  # Convert IV hex string back to bytes
        encrypted_file_data = bytes.fromhex(msg['encrypted_file_data'])  # Convert encrypted data hex string back to bytes
        
        # Decrypt the file data using AES
        cipher = AES.new(hashed_sesskey, AES.MODE_OFB, iv)
        decrypted_file_data = cipher.decrypt(encrypted_file_data)

        # Write the decrypted data to a file
        with open(f'AM2received_file{extension}', 'wb') as f:
            f.write(decrypted_file_data)

        # Record the end time for receiving the file
        receive_file_end_time = time.perf_counter()
        print(f'{extension} file received from AMDT2')
        print(f'Receiving time for {extension} file from AMDT2: ', round((receive_file_end_time - start_recv_time) * 1000,5), 'milliseconds\n')

        return decrypted_file_data, extension
    else:
        print('Timeout waiting for data to be available')
        return None, None
    
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

AM2=json.loads(decrypted_json)

RID=AM2['RID']
TID=AM2['TID']
Pr,Pub=AM2['Pr and Pub']
g=AM2['g']
p=AM2['p']
q=AM2['q']
print("-----REGISTRATION PHASE COMPLETE----- ")
registry_end_time=time.perf_counter()
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
        A2=mod_xp(p,MSG1['R1W1'],c1)*mod_xp(p,g,d1) % p 
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
        SAM_a_comparison=mod_xp(p,A2,1)*mod_xp(p,g,int(MSG3['z_e'])) % p 
        if MSG3['AD_AM_a']==SAM_a_comparison:
            d1_e1=d1+MSG3['z_e']
            part1=mod_xp(p,int(PUBDT2),d1_e1)
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
                W2=mod_xp(p,g,w2)

                W1w=mod_xp(p,MSG1['R1W1'],w2)
                W1Pr=mod_xp(p,MSG1['R1W1'],Pr)
                Pubw2=mod_xp(p,int(PUBDT2),w2)

                SessionkeyAM2DT2=hash_data(W1w,W1Pr,Pubw2)
                B1=(mod_xp(p,W2,Pr))
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

        SAM2a=mod_xp(p,int(MSG5['K2B2']),1)*mod_xp(p,g,e2) % p 
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
#print("TEST TEST:",end_auth_time, ":::::",Stage_2_start_time)
#we do *1000, 5 to display the time in milliseconds not seconds
print('Authentication time for AMDT2: ',round((end_auth_time-Stage_2_start_time)*1000,5), 'milliseconds')
print('Overall time for DTSMAKA-2: ',round((Stage_2_end_time-Stage_2_start_time)*1000,5), 'milliseconds')
print('Session key AMDT2-AM2: ',SessionkeyAM2DT2,'\n\n')


hashed_sessAM2DT2key=hashlib.sha256(SessionkeyAM2DT2.encode()).digest()


print('-----Receiving gcode file TO AMDT2-----')
receive_file(AMDT2_socket,hashed_sessAM2DT2key)


print('-----Receiving ngc file TO AMDT2-----')
receive_file(AMDT2_socket,hashed_sessAM2DT2key)




