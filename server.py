import datetime
import json
import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 2000))
server.listen(0)

rooms = [] # [{'room_name': 'foo', 'room_password': 'bar', 'users': [{'username': 'foo', 'usr': usr}]}]

class User:
    def __init__(self, usr):
        self.usr = usr
        self.start()
    
    def start(self):
        try:
            while True:
                temp = self.usr.recv(1024).decode()
                if temp == 'disconnect':
                    self.disconnect()
                    break
                self.msg = json.loads(temp.replace("'", '"'))
                match self.msg[0]:
                    case 'create': self.create()
                    case 'connect': self.connect()
                    case 'send': self.send()
                    case 'disconnect': self.disconnect()
                    case 'rooms': self.rooms()
                    case 'get_users': self.get_users()
        except:
            self.disconnect()

    def create(self):
        for i in rooms:
            if self.msg[2] == i['room_name']:
                self.usr.send(str(['NC']).encode())
                return
        rooms.append({'room_name': self.msg[2], 'room_password': self.msg[3], 'users': [{'username': self.msg[1],'usr': self.usr}]})
        self.login = self.msg[1]
        self.room_name = self.msg[2]
        self.room_password = self.msg[3]
        self.usr.send(str(['OK']).encode())

    def connect(self):
        for j, i in enumerate(rooms):
            if self.msg[2] == i['room_name'] and self.msg[3] == i['room_password']:
                self.login = self.msg[1]
                self.room_name = self.msg[2]
                self.room_password = self.msg[3]
                rooms[j]['users'].append({'username': self.msg[1], 'usr': self.usr})
                self.usr.send(str(['OK']).encode())
                return
        self.usr.send(str(['ER']).encode())
    
    def send(self):
        today = datetime.datetime.today()
        for i in rooms:
            if i['room_name'] == self.room_name and i['room_password'] == self.room_password:
                for j in i['users']:
                    j['usr'].send(str([today.strftime('%H:%M:%S'), self.login, self.msg[1]]).encode())

    def disconnect(self):
        try:
            for i, item in enumerate(rooms):
                if item['room_name'] == self.room_name and item['room_password'] == self.room_password:
                    rooms[i]['users'].remove({'username': self.login, 'usr': self.usr})
                    try:
                        self.usr.send('Disconnect'.encode())
                    except:
                        pass
                    if len(rooms[i]['users']) == 0:
                        rooms.pop(i)
                    return
        except:
            pass
    
    def rooms(self):
        temp = []
        for i in rooms:
            temp.append(i['room_name'])
        self.usr.send(str(temp).encode())
    
    def get_users(self):
        temp = []
        for i, j in enumerate(rooms):
            if j['room_name'] == self.room_name:
                for users in rooms[i]['users']:
                    temp.append(users['username'])
        self.usr.send(str(['Users list', temp]).encode())

    


def main():
	while True:
		user, _ = server.accept()
		t = threading.Thread(target=User, args=(user, ))
		t.start()

if __name__ == '__main__':
	main()
