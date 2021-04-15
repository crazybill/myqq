import pygame
from pygame.locals import *
import sys
import threading
import tkinter as tk

pygame.init()

screen = pygame.display.set_mode((800,600))
pygame.display.set_caption('tkinter')

cur_title = 'hello world'

def open_window():
    window = tk.Tk()
    window.geometry('800x600+200+100')
    window.title('tkinter window')

    label1 = tk.Label(window,text='请输入：').grid(row=0,padx =10,pady=5)
    entry1 = tk.Entry(window)
    entry1.grid(row =0,column = 1,padx =10,pady=5)

    def text_change(e):
        global cur_title
        txt = entry1.get()
        print(txt)
        cur_title = txt

    entry1.bind('<Return>',text_change)
    window.mainloop()

def show_tkinter():
    tkw = threading.Thread(target=open_window)
    tkw.start()

def draw_text():
    myfont = pygame.font.SysFont('SimHei',30)
    text_image = myfont.render(cur_title,True,(255,255,255))
    screen.blit(text_image,(100,100))

clock = pygame.time.Clock()

while True:
    clock.tick(30)
    events = pygame.event.get()

    for event in events:
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            show_tkinter()

    screen.fill(0)
    draw_text()
    pygame.display.update()