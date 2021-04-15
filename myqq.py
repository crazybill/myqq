import tkinter as tk
import tkinter.font as tkFont
import tkinter.scrolledtext as ScrolledText
from tkinter.simpledialog import askstring

import time,threading,os
import chat_client as net

window = tk.Tk()
user_name = ''
window.geometry('800x600')

window.title('聊天窗口')

window.rowconfigure(0,weight=1)
window.columnconfigure(1,weight=1)

txtfont = tkFont.Font(family="YAHEI", size=14)

user_list = []
ul = tk.StringVar()
ul.set(user_list)
wg_UserList = tk.Listbox(window,listvariable = ul)
wg_UserList.grid(rowspan = 2,padx = 5,pady = 5,sticky = 'NS')

wg_msgtext = ScrolledText.ScrolledText(window,state = tk.DISABLED,spacing2 = 1)
wg_msgtext.grid(row = 0,column = 1,columnspan =2 ,padx= 5,pady = 5,sticky ='NSEW') 
wg_msgtext.configure(font=('microsoft yahei',11))
wg_msgtext.tag_config('others',font = ('microsoft yahei',10,'bold'),foreground = 'green')
wg_msgtext.tag_config('linespace',font=('microsoft yahei',3))

wg_inputtext = tk.Text(window,height = 6)
wg_inputtext.configure(font = txtfont)
wg_inputtext.grid(row = 1,column = 1,padx = 5,pady = 5,sticky ='EW') 


def add_msg(msg,ms = 0):
    wg_msgtext.configure(state='normal')
    if ms == 0:
        wg_msgtext.insert(tk.END,msg)
    else:
        wg_msgtext.insert(tk.END,msg,'others')
    wg_msgtext.insert(tk.END,' \n','linespace')    # 加间距
    wg_msgtext.configure(state='disabled')
    wg_msgtext.see(tk.END)

def send_msg(event):
    msg = wg_inputtext.get(1.0, "end")
    add_msg(user_name+':'+msg)
    wg_inputtext.delete(1.0, "end")
    msg = msg[:-1]  # 去掉末尾换行
    net.send_queue.append(msg)

bt_send = tk.Button(window,text = 'Send',command = lambda:send_msg(None))
bt_send.grid(row = 1,column = 2,padx = 5)

wg_inputtext.bind('<Alt-s>',send_msg)

while user_name == '' or user_name is None:
    window.withdraw()
    user_name = askstring('用户名','请输入用户名')
    print('user_name:',user_name)
window.wm_deiconify()

net.login(user_name)
net.start()

def check_msg():
    while True:
        # 检查消息
        while len(net.msg_queue)>0:
            msg = net.msg_queue.pop(0)
            add_msg(msg+'\n',1)

        # 检查在线用户
        if len(net.clients)>0:
            # print(net.clients,type(net.clients))
            user_list.clear()
            for client in net.clients.values():
                # print(client,type(client))
                if "name" in client:
                    user_list.append(client['name'])
            ul.set(user_list)
            net.clients.clear()
        time.sleep(0.03)

rt = threading.Thread(target= check_msg)
rt.start()

tk.mainloop()
os._exit(0)