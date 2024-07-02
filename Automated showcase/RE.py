import socket
import threading
import random
import time
import hashlib
import secrets
import json
from Crypto.Util.number import getPrime
from Crypto.Random import get_random_bytes
from tinyec import registry 
from tinyec.ec import Point

class AMDT:
    def __init__(self, p, q, g, PubRE):
        self.p = p
        self.q = q
        self.g = g
        self.PubRE = PubRE
        self.ID = random.randint(1, q-1)
        self.s = random.randint(1, q-1)
        self.RT = time.time()
        self.RID=self.hash_data(self.ID,self.s,self.RT)
        self.TID=self.hash_data(self.RID,self.PubRE,self.s,self.RT)
        self.Pr = random.randint(0, q-1)
        self.Pub = pow(self.g, self.Pr, self.p)
        self.curve = registry.get_curve('secp256r1')
        self.KaPr = secrets.randbelow(self.curve.field.n)
        self.X = self.KaPr * self.curve.g
        self.ECCPubKeyBytes = self.X.x.to_bytes((self.X.x.bit_length() + 7) // 8, 'big') + self.X.y.to_bytes((self.X.y.bit_length() + 7) // 8, 'big')

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
    
    def hash_data(*args):
        string=''.join(str(arg) for arg in args)
        return hashlib.sha512(string.encode()).hexdigest()

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
        PubRE = pow(g, random.randint(1, q-1), p)
        PrRE = random.randint(1, q-1)
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.client_handler, args=(conn, addr,p,q,g,PubRE))
            thread.start()
            print("Current num of threads: ", threading.active_count() - 1)

    def client_handler(self, conn, addr,p,q,g,PubRE):
        print(addr, "connected")
        amdt = AMDT(p, q, g, PubRE)
        self.machine_data.append(amdt)
        conn.sendall(amdt.ECCPubKeyBytes)
        ECCmachinePubKey = conn.recv(1024)
        x, y = self.decompress(ECCmachinePubKey)
        machinedecompressed = Point(amdt.curve, x, y)
        sharedkey = amdt.KaPr * machinedecompressed
        shared_key_bytes = sharedkey.x.to_bytes((sharedkey.x.bit_length() + 7) // 8, 'big')
        json_values = json.dumps(amdt.get_values()).encode('utf-8')
        encrypted_json = self.xor_encrypt(json_values, shared_key_bytes)
        conn.sendall(encrypted_json)

    def decompress(self, pubKeyBytes):
        x = int.from_bytes(pubKeyBytes[:32], 'big')
        y = int.from_bytes(pubKeyBytes[32:], 'big')
        return x, y

    def xor_encrypt(self, plaintext, key):
        ciphertext = bytearray()
        for i, c in enumerate(plaintext):
            ciphertext.append(c ^ key[i % len(key)])
        return bytes(ciphertext)

if __name__ == "__main__":
    server = Server(5050)
    server.start()