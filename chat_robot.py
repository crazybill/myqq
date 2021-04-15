import requests
import json,time
import socket,threading

url = 'https://api.ownthink.com/bot?appid=xiaosi&userid=user&spoken='

headers={
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}
questions = []
conn = None
def robot():
    while True:
        if len(questions)>0:
            q = questions.pop(0)
            try:
                r = requests.get(url+q[1],headers = headers)
                # print(r.text)
                answer = r.json()
                if answer['message'] == 'success':
                    rtxt = answer['data']['info']['text']
                    conn.sendto(rtxt.encode('utf-8'),q[0])
                    print(f'{q[0]},{rtxt}')
            except Exception as e:
                print(e)
        time.sleep(0.02)

def start_robot(connection):
    global conn
    conn = connection
    rt = threading.Thread(target= robot)
    rt.start()