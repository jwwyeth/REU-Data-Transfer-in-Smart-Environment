import socket 
import random
import time
import json
import hashlib
from Crypto.Cipher import AES
import os
import select




PORT=5050
HEADER=64
FORMAT='utf-8'
SERVER=socket.gethostbyname(socket.gethostname())
ADDR=(SERVER,PORT)

#print("AMDT2")

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


def receive_file(conn, hashed_sesskey):
    # Record the start time for the file receiving process
   

    # Wait for the socket to be ready to receive data (first 4 bytes for the message length)
    rlist, _, _ = select.select([conn], [], [], 2)  # 1-second timeout
    if rlist:
        # Capture the time when the first byte is received
        start_recv_time = time.perf_counter()

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
        with open(f'DT2eceived_file{extension}', 'wb') as f:
            f.write(decrypted_file_data)

        # Record the end time for receiving the file
        receive_file_end_time = time.perf_counter()
        print(f'{extension} file received from AMDT1')
        print(f'Receiving time for {extension} file from AMDT1: ', round((receive_file_end_time - start_recv_time) * 1000,5), 'milliseconds\n')

        return decrypted_file_data, extension
    else:
        print('Timeout waiting for data to be available')
        return None, None

def send_file(conn,data,extension,hashedkey):
    file_start_time=time.perf_counter()

    iv = os.urandom(16)  # Generate a random 16-byte IV
    cipher = AES.new(hashedkey, AES.MODE_OFB, iv)
    encrypted_file_data = cipher.encrypt(data)

    msg = {
        'extension': extension,
        'iv': iv.hex(),  # Convert IV to hex string for transmission
        'encrypted_file_data': encrypted_file_data.hex()  # Convert encrypted data to hex string
    }
    msg_json = json.dumps(msg).encode('utf-8')
    msg_len = len(msg_json).to_bytes(4, 'big')  # Prefix the message with its length
    conn.sendall(msg_len + msg_json)
    file_end_time=time.perf_counter()
    print(f'{extension} file sent to AM2')
    print(f'Sending time for {extension} file to AM2: ',round((file_end_time-file_start_time)*1000, 5), 'milliseconds\n')

    return


    
def step1(conn):
    randomvalue1=random.randint(0,q-1)
    t1=time.time()
    R1W1=mod_xp(p,g,randomvalue1)
    L1A1=(mod_xp(p,R1W1,Pr))
    V1=hash_data(TID,L1A1,R1W1)
    #print("V2",V2)
    #print('V1 pre str converison:', V1)
    MSG1_DICT={'TID':TID,
                'L1A1': L1A1,
                'R1W1':R1W1,
                'V1': str(V1),
                't1':t1,
    }
    #print('V1 as str: ',MSG1_DICT['V1'])
    MSG1=json.dumps(MSG1_DICT).encode('utf-8')
    conn.sendall(MSG1)
    #print(f'-----AMA1 MSG SENT-----\n')

    return R1W1,L1A1, randomvalue1


def step3(conn,R1W1):
    #step ADT3
    MSG2_string=conn.recv(1024)
    #print('recieing')
    #print(MSG2_string)
    MSG2=json.loads(MSG2_string)
    t2_2=time.time()
    #print(f'-----AMA2 MSG RECIEVED-----')

    if abs(t2_2-MSG2['t2'])<=delta_T:
        #print('t2 time cheks')

        comparison=hash_data(MSG2['L2_A2'],MSG2['t2'])
        if MSG2['V2']==comparison:
            #print('V2 value checks')

            z_e=random.randint(1,p-1)
            t3=time.time()

            S_AD_AM_a=mod_xp(p,MSG2['L2_A2'],1)*mod_xp(p,g,z_e) % p 
            S_AD_AM_b=mod_xp(p,S_AD_AM_a,Pr)
            V3=hash_data(S_AD_AM_a,S_AD_AM_b,z_e,R1W1)
            MSG3_DICT={
                'AD_AM_a':S_AD_AM_a,
                'AD_AM_b': S_AD_AM_b,
                'z_e':z_e,
                'V3': str(V3),
                't3':t3,
                    }
            MSG3=json.dumps(MSG3_DICT).encode('utf-8')
            conn.sendall(MSG3)
            #print(f'-----AMA3 MSG SENT-----\n\n')
    

        else:
            print('V2 failed')
    else:
        print('t2 failed')

#value_dict is our json dictionary of this machine's values 
#to be used in authentication 

def step4(conn):
    #STEP ADT5
    MSG4_string=conn.recv(1024)
    MSG4=json.loads(MSG4_string)
    #print('recieing MGS4')
    t4_2=time.time()
   # print(f'-----AMA4 MSG RECIEVED-----')

    if abs(t4_2-MSG4['t4'])<=delta_T:
        #print('t4 time checks')
        comparison=hash_data(MSG4['TIDA2AM'],MSG4['K1B1'],MSG4['R2W2'])
        if MSG4['V4']==comparison:
            #print('V4 check')
            t5=time.time()
            x2_c2=random.randint(1,q-1)
            y2_d2=random.randint(1,q-1)
            K2B2=mod_xp(p,MSG4['R2W2'],x2_c2)*mod_xp(p,g,y2_d2) % p 
            V6=hash_data(K2B2,t5)
            MSG5_DICT={
                'K2B2':K2B2,
                'V6':str(V6),
                't5':t5
                    }
            MSG5=json.dumps(MSG5_DICT).encode('utf-8')
            conn.sendall(MSG5)
            #print(f'-----AMA5 MSG SENT-----\n\n')

            return MSG4,K2B2,x2_c2,y2_d2
        else:
            print("V4 failed")

    else:
        print('t5 failed')

def step7(conn,MSG4,K2B2,x2_c2,y2_d2,r1_w1,publickey):
    #step ADT7
    MSG6_string=conn.recv(1024)
    sessionkeyR=conn.recv(1024).decode()
    MSG6=json.loads(MSG6_string)
    #print('recieing MGS6')
    t6_2=time.time()
    #print(f'-----AMA6 MSG RECIEVED-----')
    '''
    for key, value in MSG6.items():
        print(f"{key}: {value}")   
'''
    if abs(t6_2-MSG6['t6'])<=delta_T:
        #print('t6 time cheks')   
        comparison=hash_data(MSG6['SAD_AM2a'],MSG6['SAD_AM2b'],MSG6['z2_e2'],MSG4['R2W2'])
        if MSG6['V7']==comparison:
            SAD_AM2a_comparison=mod_xp(p,K2B2,1)*mod_xp(p,g,int(MSG6['z2_e2'])) % p 
            if MSG6['SAD_AM2a']==SAD_AM2a_comparison:
                y2z2_d2e2=y2_d2+MSG6['z2_e2']
                part1=mod_xp(p,int(publickey),y2z2_d2e2)
                part2=mod_xp(p,MSG4['K1B1'],x2_c2)
                SAD_AM2b_comparison=part1*part2 % p 
                if MSG6['SAD_AM2b']==SAD_AM2b_comparison:
                    R2r=mod_xp(p,MSG4['R2W2'],r1_w1)
                    PubA2r1=mod_xp(p,int(publickey),r1_w1)
                    R2Pr=mod_xp(p,MSG4['R2W2'],Pr)
                    sessionkeyS=hash_data(R2r,PubA2r1,R2Pr)
                    if (MSG4['V5']==hash_data(sessionkeyR,MSG4['t4'])):
                        TIDnew=hash_data(TID,Pub,r1_w1,MSG6['t6'])
                        conn.sendall(b'create new TID')   
                        return sessionkeyS
                else:
                    print('fail')    
        else:
            print("V7 failed")
    else:
        print('t5 failed')



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

AMDT2=json.loads(decrypted_json)

RID=AMDT2['RID']
TID=AMDT2['TID']
Pr,Pub=AMDT2['Pr and Pub']
g=AMDT2['g']
p=AMDT2['p']
q=AMDT2['q']

print("-----REGISTRATION PHASE COMPLETE----- ")
registry_end_time=time.perf_counter()
print('Registration time for AMDT2: ',round((registry_end_time-registry_start_time)*1000,5), 'milliseconds\n')
print('-----DTSMAKA-1 AMDT1-AMDT2-----')

AMDT2_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR=socket.gethostbyname(socket.gethostname()),8080
AMDT2_socket.connect(ADDR)
Stage_1_start_time=time.perf_counter()

AMDT2_socket.sendall(str(Pub).encode())
PUBA1=AMDT2_socket.recv(1024).decode(FORMAT) 
#print('A1 public key is: ',PUBA1)
#when we bring it over its as a string so we must remforat the json back to a python dict
MSG1_string=AMDT2_socket.recv(1024).decode(FORMAT) 
MSG1=json.loads(MSG1_string)
t1_2=time.time()

if abs(t1_2-MSG1['t1'])<=delta_T:
    comparison = hash_data(MSG1['TID'],MSG1['L1A1'],MSG1['R1W1'])
    if MSG1['V1']==comparison:
        x1=random.randint(1,q-1)
        y1=random.randint(1,q-1)
        t2=time.time()
        L2=mod_xp(p,MSG1['R1W1'],x1)*mod_xp(p,g,y1) % p 
        V2=hash_data(L2,t2)
        MSG2_DICT={'L2_A2':L2,
                   'V2': V2,
                   't2':t2
                    }
        MSG2=json.dumps(MSG2_DICT).encode('utf-8')
        AMDT2_socket.sendall(MSG2)
        #print(f'-----ADT2 MSG SENT-----\n\n')


    else:
        print('value failed')
else:
    print("Failed time check")

#step ADT4
MSG3_string=AMDT2_socket.recv(1024).decode(FORMAT) 

MSG3=json.loads(MSG3_string)
t3_2=time.time()
#print(f'-----ADT3 MSG RECIEVED-----')
'''
for key, value in MSG3.items():
        print(f"{key}: {value}")
'''
if abs(t3_2-MSG3['t3'])<=delta_T:
    #print('Pass time 3')
    comparison=hash_data(MSG3['AD_AM_a'],MSG3['AD_AM_b'],MSG3['z_e'],MSG1['R1W1'])
    if MSG3['V3']==comparison:
        #print('V3 value checks')
        SAD_a_comparison=mod_xp(p,L2,1)*mod_xp(p,g,int(MSG3['z_e'])) % p 
        if MSG3['AD_AM_a']==SAD_a_comparison:
            y1_z1=y1+MSG3['z_e']
            part1=mod_xp(p,int(PUBA1),y1_z1)
            part2=mod_xp(p,MSG1['L1A1'],x1)

            #print("L1:", MSG1['L1'])
            #print('x1: ',x1)
            #print('p:', p)
            SAD_b_comparison=(part1*part2) % p 
            #print("combined:",part1*part2)
            #print(SAD_b_comparison,"\n")
            #print(MSG3['AD_AM_b'])
            #print(MSG3['AD_b'])
            if MSG3['AD_AM_b']==MSG3['AD_AM_b']:
                r2=random.randint(1,q-1)
                t4=time.time()
                R2=mod_xp(p,g,r2)
               # print('R1 value: ', MSG1['R1'])
                #print('r2 value: ', r2)
                R1r=mod_xp(p,MSG1['R1W1'],r2)
                R1Pr=mod_xp(p,MSG1['R1W1'],Pr)
                Pubr2=mod_xp(p,int(PUBA1),r2)

                SessionkeyA2A1=hash_data(R1r,R1Pr,Pubr2) 
                K1=(mod_xp(p,R2,Pr))
                V4=hash_data(TID,K1,R2)
                V5=hash_data(SessionkeyA2A1,t4)
                MSG4_DICT={'TIDA2AM':TID,
                   'R2W2': R2,
                   'K1B1': K1,
                   'V4': str(V4),
                   'V5': str(V5),
                   't4': t4
                    }
                MSG4=json.dumps(MSG4_DICT).encode('utf-8')
                #print('senidng MGS4')
                AMDT2_socket.sendall(MSG4)
                #print(f'-----ADT4 MSG SENT-----\n\n')

            else:
                print('SAD_b failed')
        else:
            print('SAD_a failed')
    else:
        print('V3 failed')
else:
    print('t3 failed')
end_auth_time=time.perf_counter()

#step ADT6
MSG5_string=AMDT2_socket.recv(1024).decode(FORMAT) 

MSG5=json.loads(MSG5_string)
t5_2=time.time()
#print(f'-----ADT5 MSG RECIEVED-----')
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
        z2=random.randint(1,q-1)
        SAD2a=mod_xp(p,int(MSG5['K2B2']),1)*mod_xp(p,g,z2) % p 
        SAD2b=mod_xp(p,SAD2a,Pr)
        V7=hash_data(SAD2a,SAD2b,z2,R2)
        MSG6_DICT={'SAD_AM2a':SAD2a,
                   'SAD_AM2b': SAD2b,
                   'z2_e2':z2,
                   'V7': str(V7),
                   't6': t6
                    }
        MSG6=json.dumps(MSG6_DICT).encode('utf-8')
        #print('senidng MGS6')
        AMDT2_socket.sendall(MSG6)
        AMDT2_socket.sendall(SessionkeyA2A1.encode())
        #print(f'-----ADT6 MSG SENT-----\n\n')

    else:
        print("V6 check failed")
else:
    print('time 5 failed')  

answer=AMDT2_socket.recv(1024).decode(FORMAT) 
if answer=='create new TID':
    TIDnew=hash_data(TID,Pub,r2,MSG5['t5'])
Stage_1_end_time=time.perf_counter()


#print('\n-----Phase 1 Summary------------')

print('Authentication time for AMDT1: ',round((end_auth_time-Stage_1_start_time)*1000,5), 'milliseconds')
print('Overall time of DTSMAKA-1:',round((Stage_1_end_time-Stage_1_start_time)*1000,5), 'milliseconds')
print('Session key AMDT1-AMDT2: ',SessionkeyA2A1,'\n\n')

hashed_sessA2A1key = hashlib.sha256(SessionkeyA2A1.encode()).digest()



AM2_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR=socket.gethostbyname(socket.gethostname()),9090
AM2_socket.bind(ADDR)
AM2_socket.listen()
AM2,address=AM2_socket.accept()
Stage_2_start_time=time.perf_counter()

PUBAM2=AM2.recv(1024).decode()
AM2.sendall(str(Pub).encode())
print('-----DTSMAKA-2 AMDT2-AM2-----')

W1,A1,w1=step1(AM2)
#step AMA3
step3(AM2,W1)
Auth_start_time=time.perf_counter()

#step AMA4
MSG4AM,B2,c2,d2=step4(AM2)
#step AMA7
sessionkeyAM2=step7(AM2,MSG4AM,B2,c2,d2,w1,PUBAM2)
Stage_2_end_time=time.perf_counter()
#print('\n-----Phase 2 Summary------------')

print('Authentication time for AM2: ',round((Stage_2_end_time-Auth_start_time)*1000,5), 'milliseconds')
print('Overall time for DTSMAKA-2: ',round((Stage_2_end_time-Stage_2_start_time)*1000,5), 'milliseconds')
print('Session key AMDT2-AM2: ',sessionkeyAM2,'\n\n')

hashed_sessAM2key=hashlib.sha256(sessionkeyAM2.encode()).digest()


print('-----Receiving gcode file from AMDT1-----')
gcode_file_data,gcode_extension=receive_file(AMDT2_socket,hashed_sessA2A1key)


print('-----Receiving ngc file from AMDT1-----')
ngc_file_data,ngc_extension=receive_file(AMDT2_socket,hashed_sessA2A1key)




print('-----Sending gcode file TO AM2-----')
send_file(AM2,gcode_file_data,gcode_extension,hashed_sessAM2key)

print('-----Sending ngc file TO AM2-----')
send_file(AM2,ngc_file_data,ngc_extension,hashed_sessAM2key)

#print(hashed_sesskey)

#code goes here

