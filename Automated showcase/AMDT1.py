import socket 
import random
import hashlib
import time
import json
from Crypto.Cipher import AES
from tinyec.ec import Point
import secrets
from tinyec import registry 
import os





PORT=5050
HEADER=64
FORMAT='utf-8'
SERVER=socket.gethostbyname(socket.gethostname())
#print(socket.gethostbyname(socket.gethostname()))
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


def xor_encrypt( plaintext, key):
        ciphertext = bytearray()
        for i, c in enumerate(plaintext):
            ciphertext.append(c ^ key[i % len(key)])
        return bytes(ciphertext)

def hash_data(*args):
    string=''.join(str(arg) for arg in args)
    return hashlib.sha512(string.encode()).hexdigest()

def receive_file(conn, hashed_sesskey):
    file_start_time=time.perf_counter()

    msg_len = int.from_bytes(conn.recv(4), 'big')  # Receive the message length
    msg_json = bytearray()
    while len(msg_json) < msg_len:
        chunk = conn.recv(min(msg_len - len(msg_json), 1024))
        if not chunk:
            break
        msg_json.extend(chunk)
    msg_json = msg_json.decode()
    msg = json.loads(msg_json)

    extension = msg['extension']
    iv = bytes.fromhex(msg['iv'])  # Convert IV hex string back to bytes
    encrypted_file_data = bytes.fromhex(msg['encrypted_file_data'])  # Convert encrypted data hex string back to bytes

    cipher = AES.new(hashed_sesskey, AES.MODE_OFB, iv)
    decrypted_file_data = cipher.decrypt(encrypted_file_data)

    with open(f'DT1received_file{extension}', 'wb') as f:
        f.write(decrypted_file_data)
        f.close()

    file_end_time=time.perf_counter()
    print(f'{extension} file recieved from AM1')
    print(f'Recieving time for {extension} file from AM1: ',round((file_end_time-file_start_time)*1000, 5), 'milliseconds\n')


    return decrypted_file_data, extension

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


def step1(conn,name):
    if name=='AMA':
        STEP_PHRASE='AMA'
    else:
        STEP_PHRASE='ADT'

    randomvalue1=random.randint(0,q-1)
    t1=time.time()
    R1W1=pow(g,randomvalue1,p)
    L1A1=(pow(R1W1,Pr,p))
    V1=hash_data(TID,L1A1,R1W1)
    #print("V2",V2)
    #print('V1 pre str converison:', V1)
    MSG1_DICT={'TID':TID,
                'L1A1': L1A1,
                'R1W1':R1W1,
                'V1': str(V1),
                't1':t1,
    }



    MSG1=json.dumps(MSG1_DICT).encode('utf-8')
    conn.sendall(MSG1)
    #print(f'-----{STEP_PHRASE}1 MSG SENT-----\n')
    #print(t1)
    return R1W1,L1A1, randomvalue1


def step3(conn,R1W1,name):
    if name=='AMA':
        STEP_PHRASE='AMA'
    else:
        STEP_PHRASE='ADT'
    MSG2_string=conn.recv(1024)
    #print('recieing')
    #print(MSG2_string)
    MSG2=json.loads(MSG2_string)
    t2_2=time.time()
   # print(f'-----{STEP_PHRASE}2 MSG RECEIVED-----')
    '''
    for key, value in MSG2.items():
        print(f"{key}: {value}")
    '''
    if abs(t2_2-MSG2['t2'])<=delta_T:
        #print('t2 time cheks')

        comparison=hash_data(MSG2['L2_A2'],MSG2['t2'])
        if MSG2['V2']==comparison:
            #print('V2 value checks')

            z_e=random.randint(1,p-1)
            t3=time.time()

            S_AD_AM_a=pow(MSG2['L2_A2'],1,p)*pow(g,z_e,p) % p 
            S_AD_AM_b=pow(S_AD_AM_a,Pr,p)
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
            #print(f'-----{STEP_PHRASE}3 MSG SENT-----\n\n')


        else:
            print('V2 failed')
    else:
        print('t2 failed')

#value_dict is our json dictionary of this machine's values 
#to be used in authentication 

def step5(conn,name):
    if name=='AMA':
        STEP_PHRASE='AMA'
    else:
        STEP_PHRASE='ADT'
    #STEP ADT5
    MSG4_string=conn.recv(1024)
    MSG4=json.loads(MSG4_string)
    #print('recieing MGS4')
    t4_2=time.time()
    #print(f'-----{STEP_PHRASE}4 MSG RECEIVED-----')
    '''
    for key, value in MSG4.items():
        print(f"{key}: {value}")
    '''
    if abs(t4_2-MSG4['t4'])<=delta_T:
        #print('t4 time checks')
        comparison=hash_data(MSG4['TIDA2AM'],MSG4['K1B1'],MSG4['R2W2'])
        if MSG4['V4']==comparison:
            #print('V4 check')
            t5=time.time()
            x2_c2=random.randint(1,q-1)
            y2_d2=random.randint(1,q-1)
            K2B2=pow(MSG4['R2W2'],x2_c2,p)*pow(g,y2_d2,p) % p 
            V6=hash_data(K2B2,t5)
            MSG5_DICT={
                'K2B2':K2B2,
                'V6':str(V6),
                't5':t5
                    }
            MSG5=json.dumps(MSG5_DICT).encode('utf-8')
            conn.sendall(MSG5)
            #print(f'-----{STEP_PHRASE}5 MSG SENT-----\n\n')

            return MSG4,K2B2,x2_c2,y2_d2
        else:
            print("V4 failed")

    else:
        print('t5 failed')

def step7(conn,MSG4,K2B2,x2_c2,y2_d2,r1_w1,publickey,name):
    if name=='AMA':
        STEP_PHRASE='AMA'
    else:
        STEP_PHRASE='ADT'
    #step ADT7
    MSG6_string=conn.recv(1024)
    sessionkeyR=conn.recv(1024).decode()
    MSG6=json.loads(MSG6_string)   #print('recieing MGS6')
    t6_2=time.time()
    #print(f'-----{STEP_PHRASE}6 MSG RECEIVED-----')
    '''
    for key, value in MSG6.items():
        print(f"{key}: {value}") 
    '''
    if abs(t6_2-MSG6['t6'])<=delta_T:
        #print('t6 time cheks')   
        comparison=hash_data(MSG6['SAD_AM2a'],MSG6['SAD_AM2b'],MSG6['z2_e2'],MSG4['R2W2'])
        if MSG6['V7']==comparison:
            SAD_AM2a_comparison=pow(K2B2,1,p)*pow(g,int(MSG6['z2_e2']),p) % p 
            if MSG6['SAD_AM2a']==SAD_AM2a_comparison:
                y2z2_d2e2=y2_d2+MSG6['z2_e2']
                part1=pow(int(publickey),y2z2_d2e2,p)
                part2=pow(MSG4['K1B1'],x2_c2,p)
                SAD_AM2b_comparison=part1*part2 % p 
                if MSG6['SAD_AM2b']==SAD_AM2b_comparison:
                    R2r=pow(MSG4['R2W2'],r1_w1,p)
                    PubA2r1=pow(int(publickey),r1_w1,p)
                    R2Pr=pow(MSG4['R2W2'],Pr,p)
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


#SECP256k1

machine=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
machine.connect(ADDR)
delta_T=3
registry_start_time=time.time()
curve=(registry.get_curve('secp256r1'))
#using secrets module(random crypto number generator) 
#generate random number in th ecurve's finite field
KbPr=secrets.randbelow(curve.field.n)
#calc public key
Y=KbPr *curve.g
#convert Y into a byte representation
ECCPubkeybytes=Y.x.to_bytes((Y.x.bit_length() + 7) // 8, 'big') + Y.y.to_bytes((Y.y.bit_length() + 7) // 8, 'big')
#receive RE's pub key
ECCREpubkey=machine.recv(1024)
#send its pub key
machine.sendall(ECCPubkeybytes)
x,y=decompress(ECCREpubkey)
#restore the point on the elliptic curve
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
print('Registration time for AMDT1: ',round((registry_end_time-registry_start_time)*1000,5), 'milliseconds\n')

#step ADT1
AMDT1_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR=socket.gethostbyname(socket.gethostname()),8080
AMDT1_socket.bind(ADDR)
AMDT1_socket.listen()
connection,address=AMDT1_socket.accept()
#used for authentication half time and overall
Stage_1_start_time=time.perf_counter()
print('-----DTSMAKA-1 AMDT1-AMDT2------------')

PUBA2=connection.recv(1024).decode()
connection.sendall(str(Pub).encode())
R1,L1,r1=step1(connection,'ADT')
#STEP ADT3
step3(connection,R1,'ADT')
#step ADT4
Auth_start_time=time.perf_counter()

MSG4DT,K2,x2,y2=step5(connection,'ADT')

#step ADT7
sessionkeyDT=step7(connection,MSG4DT,K2,x2,y2,r1,PUBA2,'ADT')
Stage_1_end_time=time.perf_counter()

#print('\n-----Phase 1 Summary------------')
print('Authentication time for AMDT2: ',round((Stage_1_end_time-Auth_start_time)*1000,5), 'milliseconds')
print('Overall time of DTSMAKA-1: ',round((Stage_1_end_time-Stage_1_start_time)*1000,5), 'milliseconds')
print('session key AMDT1-AMDT2:\n',sessionkeyDT,'\n\n')





#STAGe 2 DT_AM
AM1_AM_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR=socket.gethostbyname(socket.gethostname()),7070
AM1_AM_socket.bind(ADDR)
AM1_AM_socket.listen()
AM1,address=AM1_AM_socket.accept()
Stage_2_start_time=time.perf_counter()
print('-----DTSMAKA-2 AMDT1-AM1------------')
PUBAM=AM1.recv(1024).decode()
AM1.sendall(str(Pub).encode())
#step AMA1
W1,A1,w1=step1(AM1,'AMA')
#step AMA3
step3(AM1,W1,'AMA')
#step AMA5
Auth_start_time=time.perf_counter()

MSG4AM,B2,c2,d2=step5(AM1,'AMA')
#step AMA7
sessionkeyAM=step7(AM1,MSG4AM,B2,c2,d2,w1,PUBAM,'AMA')
Stage_2_end_time=time.perf_counter()

#print('\n-----Phase 2 Summary------------')
print('Authentication time for AM1: ',round((Stage_2_end_time-Auth_start_time)*1000,5), 'milliseconds')
print('Overall time of DTSMAKA-2: ',round((Stage_2_end_time-Stage_2_start_time)*1000, 5), 'milliseconds')
print('Session key AMDT1-AM1:\n',sessionkeyAM,'\n\n')


#after initalizeiton no RE Involved


hashed_sesskey=hashlib.sha256(sessionkeyDT.encode()).digest()

hashed_sessAMkey=hashlib.sha256(sessionkeyAM.encode()).digest()

iv = os.urandom(16)  # Generate a random 16-byte IV

print('-----Recieving gcode file from AM1-----')

gcode_file_data,gcode_extension=receive_file(AM1,hashed_sessAMkey)

print('-----Recieving ngc file from AM1-----')

ngc_file_data,ngc_extension=receive_file(AM1,hashed_sessAMkey)


print('-----Sending gcode file TO AMDT2-----')

file_start_time=time.perf_counter()
cipherDT2gcode = AES.new(hashed_sesskey, AES.MODE_OFB,iv)
send_file(connection,gcode_file_data,gcode_extension,hashed_sesskey,iv,cipherDT2gcode)
file_end_time=time.perf_counter()
print('gcode file sent to AMDT2')
print('Sending time for gcode file to AMDT2: ',round((file_end_time-file_start_time)*1000, 5), 'milliseconds\n')





print('-----Sending ngc file TO AMDT2-----')
#conn,data,extension,hashedkey,iv



file_start_time=time.perf_counter()
cipherDT2ngc = AES.new(hashed_sesskey, AES.MODE_OFB,iv)
send_file(connection, ngc_file_data, ngc_extension, hashed_sessAMkey,iv,cipherDT2ngc)
file_end_time=time.perf_counter()
print('ngc file sent to AMDT2')
print('Sending time for ngc file to AMDT2: ',round((file_end_time-file_start_time)*1000, 5), 'milliseconds\n')






#print('done')


#print(hashed_sesskey)

#after initalizeiton no RE Involved





#any entity that wants to make private an d public key class?