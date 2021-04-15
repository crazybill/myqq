import socket
import os,sys
import threading
from threading import Lock,Thread
import json,time
import chat_robot as robot

# 1 创建套接字
server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
# socket.AF_INET 表示使用 IPv4，socket.SOCK_DGRAM 表示使用 UDP 协议

# 2 获取本机地址
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
address = (host_ip,5678)

# 3 绑定 ip 地址和端口
server.bind(address)
print(f'{address} 服务启动，等待客户连接...')

clients = {}
broadcast_msg = []

def get_time():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def get_name(client_addr):
    if client_addr in clients:
        return clients[client_addr].get('name','未知')
    else:
        return ''

# 检查 msg 是否特殊指令
def is_cmd(msg):
    r = False
    if msg in ['ls','list','users','exit']:
        r = True
    if msg.startswith(':') or msg.startswith('：'):
        r = True
    if msg.startswith('name:'):
        r = True
    if msg.startswith('bongbong,'):
        r = True 
    return r

# 广播用户列表
def send_userlist():
    for client in clients.values():
        server.sendto(json.dumps(clients).encode('utf-8'),client['addr'])

def recieve():
    while True:
        #  接收信息
        msg,client_addr = server.recvfrom(1024) 
        msg = msg.decode('utf-8')
        if not is_cmd(msg):   # 跳过心跳信息 和指令信息
            print_msg = f'{client_addr}:' +msg
            print(f'{get_name(str(client_addr))}'+print_msg)
            broadcast_msg.append({'addr':str(client_addr),'msg':print_msg})  #广播
            
        # 对第一次登陆进来的用户，加入用户列表，发送欢迎信息，并群发用户列表信息
        if str(client_addr) not in clients:
            clients[str(client_addr)] = {'addr':client_addr,'time':time.time(),'login_time':get_time()}
            client_name = ''
            if msg.startswith('name:'):
                client_name = msg.split(':')[1]
                clients[str(client_addr)]['name'] = client_name

            first_msg = f'welcome {client_addr}'
            server.sendto(first_msg.encode('utf-8'),client_addr)    # 发送欢迎信息

            send_userlist() # 广播

            online_msg = f'{client_addr} 上线了'
            print(client_name + online_msg)
            broadcast_msg.append({'addr':str(client_addr),'msg':online_msg})    # 广播

            msg = ''

        if msg.startswith('name:'):
            clients[str(client_addr)]['name'] = msg.split(':')[1]
            msg = ''

        if msg.startswith('bongbong'):
            clients[str(client_addr)].update({'time':time.time(),'name':msg.split(',')[1]})
            msg = ''

        if msg == 'list':
            print(clients)
            clist = json.dumps(clients)
            server.sendto(clist.encode('utf-8'),client_addr)
            msg = ''

        if msg == 'users':
            clist = [get_name(c) for c in clients]
            users_msg = f'当前在线 {len(clist)} 人：'+','.join(clist)
            server.sendto(users_msg.encode('utf-8'),client_addr)
            msg = ''

        # 模仿木马，操控电脑
        if msg == 'ls':
            os.system('ls -al')
            msg = ''
        
        if msg.startswith(':') or msg.startswith('：') or len(clients) == 1:
            if msg != '':
                q = msg
                if msg.startswith(':') or msg.startswith('：'):
                    q = q[1:]
                robot.questions.append([client_addr,q])
        
            

def send():
    while True:
        # 发送信息
        msg = input()
        for c in clients:
            server.sendto(msg.encode('utf-8'),clients[c]['addr'])

        if msg == 'exit':
            server.close()
            os._exit(0)

# 心跳检测，客户端每秒发一次 bongbong，超过2秒没收到，就视同断开了
def check_heartbeat():
    global clients
    while True:
        all_addr = list(clients.keys())
        for addr in all_addr:
            last_beat = clients[addr]['time']
            diff_time = time.time() - last_beat
            if diff_time > 2:
                try:
                    # guest_name = clients[addr]['name']
                    guest_name = get_name(addr)
                    print(f'{guest_name}{addr} 超时无心跳，断开连接')
                    clients.pop(addr)
                    broadcast_msg.append({'addr':addr,'msg':f'{guest_name} 下线了'})    # 广播
                    send_userlist() # 广播
                except Exception as e:
                    print(e)
        time.sleep(1)

# server 广播客户端发来的消息
def broad_cast():
    global broadcast_msg
    
    while True:
        while len(broadcast_msg) > 0:
            bm = broadcast_msg.pop(0)   # FIFO
            client_addr = bm['addr']
            msg = bm['msg']
            sender_name = ''
            if client_addr in clients:
                sender_name = clients[client_addr].get('name','')

            if sender_name != '':
                msg = msg.replace(client_addr,sender_name)
            send_msg = json.dumps({'addr':client_addr,'from':sender_name,'msg':msg})
            for c in clients:
                addr = clients[c]['addr']
                if c != client_addr:
                    server.sendto(send_msg.encode('utf-8'),addr)
        time.sleep(0.03)

def main():
    listener = threading.Thread(target = recieve)
    sender = threading.Thread(target = send)
    heartbeat = threading.Thread(target = check_heartbeat)
    broadcast = threading.Thread(target = broad_cast)
    
    listener.start()
    sender.start()
    heartbeat.start()
    broadcast.start()

    robot.start_robot(server)

if __name__ == '__main__':
    main()