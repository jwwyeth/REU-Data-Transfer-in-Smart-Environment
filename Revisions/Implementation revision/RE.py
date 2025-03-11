import socket
import threading
import random
import time
import hashlib
import secrets
import json
from Crypto.Util.number import getPrime
from Crypto.Random import get_random_bytes

class AMDT:
    def __init__(self, p, q, g, PubRE):
        self.p = p
        self.q = q
        self.g = g
        self.PubRE = PubRE
        self.ID = random.randint(1, q-1)
        self.s = random.randint(1, q-1)
        self.RT = time.time()
        self.RID = self.hash_data(self.ID, self.s, self.RT)
        self.TID = self.hash_data(self.RID, self.PubRE, self.s, self.RT)
        self.Pr = random.randint(0, q-1)
        self.Pub = self.mod_xp(self.p,self.g, self.Pr)
        self.shared_key = secrets.token_bytes(16)  # Generate a symmetric key

    def get_values(self):
        value_dict = {
            'RID': str(self.RID),
            'TID': str(self.TID),
            'Pr and Pub': (self.Pr, self.Pub),
            'g': self.g,
            'p': self.p,
            'q': self.q
        }
        return value_dict
    
    def hash_data(self, *args):
        string = ''.join(str(arg) for arg in args)
        return hashlib.sha512(string.encode()).hexdigest()
    
    def mod_xp(self,modulus_n, base_a, integer_b):
    
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

class Server:
    def __init__(self, port):
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((socket.gethostbyname(socket.gethostname()), self.port))
        self.machine_data = []

    def start(self):
        print('-----REGISTRY ENROLLER INITIATED-----')
        self.server.listen()
        p = getPrime(160, randfunc=get_random_bytes)
        q = (p - 1) // 2
        g = random.randint(1, q-1)
        PubRE = self.mod_xp(p,g,(random.randint(1, q-1)))
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.client_handler, args=(conn, addr, p, q, g, PubRE))
            thread.start()
            print("Current num of threads: ", threading.active_count() - 1)

    def client_handler(self, conn, addr, p, q, g, PubRE):
        print(addr, "connected")
        amdt = AMDT(p, q, g, PubRE)
        self.machine_data.append(amdt)
        conn.sendall(amdt.shared_key)  # Send the symmetric key
        json_values = json.dumps(amdt.get_values()).encode('utf-8')
        #print( self.xor_encrypt(json_values, amdt.shared_key))
        encrypted_json = self.xor_encrypt(json_values, amdt.shared_key)
        conn.sendall(encrypted_json)

    def xor_encrypt(self, plaintext, key):
        ciphertext = bytearray()
        for i, c in enumerate(plaintext):
            ciphertext.append(c ^ key[i % len(key)])
        return bytes(ciphertext)
    
    def mod_xp(self,modulus_n, base_a, integer_b):
    
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

if __name__ == "__main__":
    server = Server(5050)
    server.start()