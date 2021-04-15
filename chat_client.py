import socket
import threading
from threading import Lock,Thread
import os,json,random
import time

# 1 创建套接字
connection = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# 2 获取本机地址
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
address = (host_ip,random.randint(10000,60000))

# 3 绑定 ip 地址和端口(可选，不绑定，会自动绑到随机分配的端口号)
connection.bind(address)

server_addr = ('49.232.223.88',5678) # 服务端的地址
# server_addr = ('192.168.3.98',5678) # 服务端的地址
clients = []    # 在线用户
clients_changed = False     # 在线用户发生变化

msg_queue = []  # 消息队列
send_queue = []     # 发送队列
user_name = ''  # 当前用户

# 循环，接收和发送消息
def send():
    while True:
        # 发送信息
        while len(send_queue)>0:
            msg = send_queue.pop(0)
            connection.sendto(msg.encode('utf-8'),server_addr)

        time.sleep(0.03)
   
def recieve():
    global clients, clients_changed
    while True:
        # 接收信息
        msg,server_addr = connection.recvfrom(1024) 
        msg = msg.decode('utf-8')
        r_txt = ''
          
        if msg.startswith('{'):
            msg_dict = json.loads(msg)
            if 'msg' in msg_dict:
                r_txt = msg_dict['msg']
            else:
                clients = json.loads(msg)   # 收到用户列表
                clients_changed = True
        else:
            r_txt = msg
        if r_txt != '':
            # print('\033[1;32m'+r_txt+'\033[0:30m')
            msg_queue.append(r_txt)

def heart_beat():
    while True:
        connection.sendto(f'bongbong,{user_name}'.encode('utf-8'),server_addr)
        time.sleep(1)

def login(username):
    global user_name
    user_name = username
    connection.sendto(f'name:{user_name}'.encode('utf-8'),server_addr)

def start():
    lt = threading.Thread(target = recieve)
    st = threading.Thread(target = send)
    ht = threading.Thread(target = heart_beat)
    lt.start()
    st.start()
    ht.start()

def main():
    global user_name
    user_name = input('请输入名字：')
    login(user_name)
    start()


if __name__ == '__main__':
    main()