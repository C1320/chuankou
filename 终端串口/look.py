#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2020/12/23 19:50
# @Author : 十三
# @Email : 2429120006@qq.com
# @Site : 
# @File : look.py
# @Software: PyCharm
import pygame

from main import my_Serial
import tkinter
# import tkinter as tk
import random
import tkinter.messagebox
from tkinter import *
from tkinter.ttk import Combobox

from gevent import monkey, event
import pymysql
from tkinter import Menu
import tkinter.filedialog
from PIL import ImageTk, Image

import datetime as dt
import os.path
from datetime import datetime
path = os.getenv('tmp')
filecode = os.path.join(path, 'info.txt')
class LOOk():
    def __init__(self):
        self.look_Gui()
        self.login_flag = False


    def login_sql(self):
        # 打开数据库连接
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='mysql', charset='utf8')
        # 使用cursor()方法获取操作游标
        self.cur = self.conn.cursor()
        try:
            self.cur.execute("select*from users")
            # 返回所有数据
            self.res = self.cur.fetchall()
            for rows in self.res:
                self.uid = rows[0]
                self.name = rows[1]
                self.upwd = rows[2]
                if self.uid == self.login_text1.get() and self.upwd == self.login_text2.get():
                    self.login_flag = True
                    #     登录成功，把账号密码信息写入临时文件
                    with open(filecode, 'w') as fp:
                        fp.write(','.join((self.login_text1.get(), self.login_text2.get())))
                    break
                else:
                    self.login_flag = False

        except Exception as e:
            print("异常", e)
        finally:
            self.cur.close()
            self.conn.close()

    def login_go(self):
        self.login_sql()
        if self.login_flag:
            self.login.destroy()
            my_Serial()
        else:
            self.login_msg.set("登录失败")

    # 记住账号密码，尝试填入
    def rememcode(self):
        try:
            with open(filecode) as fp:
                self.c, self.p = fp.read().strip().split(',')
                self.varaccount.set(self.c)
                self.varpasswd.set(self.p)
        except:
            pass

    def look_Gui(self):
        self.login = Tk()
        self.login.title("欢迎使用南瓜不朽门禁管理系统")
        self.login.geometry("380x300+500+250")
        self.login.iconbitmap("title.ico")

        # # 创建背景画布
        # 参考https://blog.csdn.net/qq_41620823/article/details/99616160?utm_medium=distribute.pc_relevant_t0.none-task-blog-BlogCommendFromMachineLearnPai2-1.channel_param&depth_1-utm_source=distribute.pc_relevant_t0.none-task-blog-BlogCommendFromMachineLearnPai2-1.channel_param
        self.canvas = Canvas(self.login, width=1200, height=600, bd=0, highlightthickness=0)
        # 图片路径
        self.imagepath = 'bg2.jpg'
        self.img = Image.open(self.imagepath)
        self.photo = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(500, 500, image=self.photo)
        self.canvas.pack()
        self.canvas.create_window(100, 50, width=100, height=20)
        self.login_msg = StringVar()
        self.login_msg_label = Label(self.login, textvariable=self.login_msg, font=('宋体', 16), foreground='blue',
                                     bg='LightSteelBlue')
        self.login_label1 = Label(self.login, text='账号:', font=('宋体', 16))
        self.login_label2 = Label(self.login, text='密码:', font=('宋体', 16))
        # 账号文本框
        self.varaccount = StringVar(self.login)
        self.login_text1 = Entry(self.login, font=('宋体', 16), textvariable=self.varaccount)
        # 密码输入以“*”显示
        self.varpasswd = StringVar(self.login)
        self.login_text2 = Entry(self.login, show='*', font=('宋体', 16), textvariable=self.varpasswd)
        self.login_button = Button(self.login, text='立即登录', font=('宋体', 16), cursor='hand2', command=self.login_go)
        self.remember_ch = Checkbutton(self.login, text='上次登录', font=('微软雅黑', 10), bg="lightskyblue", cursor='hand2',
                                       command=self.rememcode)
        self.login_label1.place(x=50, y=73, h=20, w=80)
        self.login_label2.place(x=50, y=123, h=20, w=80)
        self.login_text1.place(x=150, y=70, h=25, w=150)
        self.login_text2.place(x=150, y=120, h=25, w=150)
        self.login_button.place(x=150, y=220, h=50, w=150)
        self.login_msg_label.place(x=20, y=260, h=20, w=80)
        self.remember_ch.place(x=150, y=160, h=25, w=150)
        self.login.resizable(False, False)
        self.login.mainloop()


if __name__ == '__main__':
    LOOk()
