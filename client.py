import socket
import pickle
import time

class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "localhost"
        self.port = 5555
        self.addr = (self.host, self.port)
        self.board = self.connect()
        self.board = pickle.loads(self.board)
    #connnexion au serveur
    def connect(self):
        self.client.connect(self.addr)
        return self.client.recv(4096*8)
    #deconnexion
    def disconnect(self):
        self.client.close()
    #Envoi des data
    def send(self, data, pick=False):
        start_time = time.time()
        while time.time() - start_time < 5:
            try:
                if pick:
                    self.client.send(pickle.dumps(data))
                else:
                    self.client.send(str.encode(data))
                reply = self.client.recv(4096*8)
                try:
                    reply = pickle.loads(reply)
                    break
                except Exception as e:
                    print(e)

            except socket.error as e:
                print(e)


        return reply