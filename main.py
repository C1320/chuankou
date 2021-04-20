import serial
import serial.tools.list_ports
import threading
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox
import time
from gevent import monkey, event
import pymysql
import pymysql
from PIL import ImageTk, Image
import datetime

"pip install pyserial"
DATA = ""  # 读取的数据
NOEND = True  # 是否读取结束


class my_Serial():
    def __init__(self):
        self.fg = 0
        self.n = 0
        self.shibai = 0
        self.dj = 0
        self.bdj = True
        self.ser = serial.Serial()
        self.show_face()

    def on_closing(self):
        global NOEND
        NOEND = False
        if self.ser.isOpen():
            self.ser.close()
        self.root.destroy()

    # 读数据的本体
    def read_data(self, ser):
        global DATA, NOEND
        # 循环接收数据（线程实现）
        # 空列表存数据
        self.data_list = []
        # 空列表存在读取过的卡
        self.per_list = [0]
        self.flag_list = []
        self.f = True
        # 创建字典
        self.flag_dct = {}
        self.dct_list = []
        self.del_zc = 0
        # 考勤
        self.Attendance = False
        # 统计次数
        count = 0
        self.time_flag = 0
        while NOEND:
            if self.ser.in_waiting:
                # DATA = ser.read(ser.in_waiting).decode("gbk")
                DATA = self.ser.read(self.ser.in_waiting)
                # self.data_list.append(int(DATA.hex(), 16))

                print(DATA)
                if DATA == b'a':
                    print("cbh a")
                self.flag_list.append(DATA.hex().upper())
                if self.f:
                    self.admin_sql()
                    # flag = self.admin_sql()
                    # self.data_list.append(DATA.hex().upper())
                    """
                    此处用字典
                    """
                    # if DATA.hex().upper() == self.per_list[-1]:
                    #     count += 1
                    # else:
                    #     count = count
                    # self.data_list.append(count)
                    print(self.data_list)
                    if self.time_flag == 1:
                        self.dct = self.card_2
                        self.List = list(self.flag_dct.keys())
                        if self.dct in self.List:
                            self.flag_dct[self.dct] = self.flag_dct[self.dct] + 1
                        else:
                            self.flag_dct[self.dct] = 1
                        count = self.flag_dct[self.dct]
                        self.data_list.append(count)
                        self.btn_sendcmd()
                        self.data_list.append("成功")
                        #     调用数据库
                        self.mysql()
                        self.insert_data()
                        self.info.set("刷卡成功，欢迎您！")
                        # 延时5s
                        time.sleep(1.5)
                        self.info.set('')

                    elif self.time_flag == 2:
                        self.fail_sendcmd()
                        self.info.set("刷卡失败，剩余{}次机会".format(2 - self.shibai))
                        time.sleep(2)
                        self.info.set('')
                        self.shibai += 1
                        if self.shibai == 3:
                            self.shibai = 0
                        print("失败")
                        # tkinter.messagebox.showerror('失败', "刷卡失败或未注册")
                        # self.data_list.append("失败")
                if not self.f:
                    if self.del_zc == 1:
                        self.zc_IC_var.set(self.flag_list[-1])
                    elif self.del_zc == 2:
                        self.del_var.set(self.flag_list[-1])
                    # self.sendcmd.insert(0, self.flag_list[-1])
                    elif self.del_zc == 3:
                        self.fi_var.set(self.flag_list[-1])
                self.flag_list = []
                self.data_list = []

    def open_seri(self, portx, bps, timeout):
        ret = False
        try:
            # 打开串口，并得到串口对象
            self.ser = serial.Serial(portx, bps, timeout=timeout)
            # 判断是否成功打开
            if (self.ser.is_open):
                ret = True
                th = threading.Thread(target=self.read_data, args=(self.ser,))  # 创建一个子线程去等待读数据
                th.start()
        except Exception as e:
            print("error!", e)
        return self.ser, ret

    def btn_hit(self):
        global NOEND
        if self.ser.isOpen():
            NOEND = False
            self.ser.close()
            # print("已关闭，接下来打开串口")
            self.comopenflagstr.set("系统未开启")
            self.comopenbtnstr.set("系统启动")
        else:
            print("等待打开")
            # self.ser, ret = self.open_seri("COM12", 9600, None) # 串口com12、bps为9600，等待时间为永久
            self.ser, ret = self.open_seri(self.cbcomportvar.get(), self.cbcombpsvar.get(),
                                           None)  # 串口com3、bps为115200，等待时间为永久
            if (ret == True):  # 判断串口是否成功打开
                # print("打开串口成功")
                self.comopenflagstr.set("已开启")
                self.comopenbtnstr.set("关闭")
        #         通行数据库

    # 删除
    def dele_func(self):
        self.del_GUI = Tk()
        self.del_GUI.title("查找")
        self.del_GUI.geometry("250x100+600+500")

        # self.fi_msg = Label(self.look, text='姓名/学号')
        self.del_msgsvar = StringVar()
        self.del_msg = Combobox(self.del_GUI, textvariable=self.del_msgsvar)
        self.del_msg["value"] = ("姓名", "卡号")
        # 默认波特率
        self.del_msg.current(0)
        self.del_var = StringVar(self.del_GUI)
        self.del_text = Entry(self.del_GUI, textvariable=self.del_var)
        self.del_button = Button(self.del_GUI, text='确定', command=self.del_select)
        self.del_msg.place(x=5, y=30, h=30, w=50)
        self.del_text.place(x=60, y=30, h=30, w=100)
        self.del_button.place(x=170, y=30, h=30, w=50)
        self.del_GUI.resizable(False, False)
        self.del_GUI.mainloop()

    def del_fun(self):
        #     打开数据库连接
        self.db7 = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='mysql', charset='utf8')
        # 获取游标
        self.cur7 = self.db7.cursor()
        self.del_count = 0
        self.del_list = []
        self.del_flag = False
        try:
            self.cur7.execute("select*from admin")
            # 获取数据库数据
            self.res_7 = self.cur7.fetchall()
            for self.rows_7 in self.res_7:
                self.name_7 = self.rows_7[0]
                self.card_7 = self.rows_7[3]
                self.del_count += 1
                self.del_list.append(self.name_7)
                if self.del_msg.get() == '姓名':
                    if self.name_7 == self.del_text.get():
                        self.del_flag = True
                        self.del_sql = "delete from admin where name='%s'" % (self.del_text.get())
                elif self.del_msg.get() == '卡号':
                    if self.card_7 == self.del_text.get():
                        self.del_flag = True
                        self.del_sql = "delete from admin where card2='%s'" % (self.del_text.get())
            if self.del_flag:
                self.cur7.execute(self.del_sql)
                self.db7.commit()
                tkinter.messagebox.showinfo('提示', "删除成功")
            else:
                tkinter.messagebox.showinfo('提示', "无此用户")
            self.del_flag = False
        except Exception as e:
            # 抛出异常
            print("异常", e)
        finally:
            self.cur7.close()
            self.db7.close()

    def admin_sql(self):

        #     打开数据库连接
        self.db2 = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='mysql', charset='utf8')
        # 获取游标
        self.cur2 = self.db2.cursor()
        self.find_list = []
        self.len = 0
        # 获取时间
        self.now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            self.cur2.execute("select*from admin")
            # 获取数据库数据
            self.result = self.cur2.fetchall()
            for self.row in self.result:
                # 姓名
                self.name = self.row[0]
                self.ID = self.row[1]
                self.PRO = self.row[2]
                self.card_2 = self.row[3]
                self.find_list.append(self.ID)
                self.len += 1
                if not self.Attendance:
                    if self.flag_list[0] == self.card_2:
                        self.per_list.append(DATA.hex().upper())
                        self.data_list.append(self.name)
                        self.data_list.append(self.ID)
                        self.data_list.append(self.PRO)
                        self.data_list.append(self.card_2)
                        self.data_list.append(self.now_time)
                        print("验证成功")
                        self.time_flag = 1
                        break
                    # 遍历完成，不存在匹配项，失败
                    elif self.len >= len(self.result) and self.flag_list[0] != self.card_2:
                        # self.data_list = []
                        self.time_flag = 2
                else:
                    # 范围时间
                    d_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + self.up_time.get(),
                                                        '%Y-%m-%d%H:%M')
                    d_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + self.ov_time.get(),
                                                         '%Y-%m-%d%H:%M')
                    # 当前时间
                    n_time = datetime.datetime.now()
                    if d_time <= n_time <= d_time1:
                        self.time_flag = True
                        if self.flag_list[0] == self.card_2:
                            self.per_list.append(DATA.hex().upper())
                            self.data_list.append(self.name)
                            self.data_list.append(self.ID)
                            self.data_list.append(self.PRO)
                            self.data_list.append(self.card_2)
                            self.data_list.append(self.now_time)
                            print("验证成功")
                            self.time_flag = 1
                            break
                        # 遍历完成，不存在匹配项，失败
                        elif self.len >= len(self.result) and self.flag_list[0] != self.card_2:
                            # self.data_list = []
                            self.time_flag = 2
                    else:
                        self.time_flag = 3
                        tkinter.messagebox.showinfo("提示", '当前不在服务时间范围，请稍后再试！')

        except Exception as e:
            # 抛出异常
            print("异常", e)
        finally:
            self.db2.close()

    # 数据库记录
    def mysql(self):
        #     打开数据库连接
        self.db = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='mysql', charset='utf8')
        # 获取游标
        self.cur = self.db.cursor()
        # 写入数据
        self.sql_insert = "insert into Attendance(name, ID, PRO,card,time,number,stas)values ('%s', '%s', '%s','%s','%s','%s','%s')" % (
            self.data_list[0], self.data_list[1], self.data_list[2], self.data_list[3],
            self.data_list[4], self.data_list[5], self.data_list[6])
        try:
            self.cur.execute(self.sql_insert)
            # 提交
            self.db.commit()
            print("数据写入成功")
        except Exception as e:
            # 回滚
            self.db.rollback()
            print("错误", e)
        finally:
            self.db.cursor().close()
            self.db.close()

    def record_sql(self):
        self.m = 0
        #     打开数据库连接
        self.db3 = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='mysql', charset='utf8')
        # 获取游标
        self.cur3 = self.db3.cursor()
        # 空列表
        self.record_list = []
        try:
            self.cur3.execute("select*from Attendance")
            # 获取数据库数据
            self.res = self.cur3.fetchall()
            for self.rows in self.res:
                self.name_2 = self.rows[0]
                self.ID_2 = self.rows[1]
                self.PRO_2 = self.rows[2]
                self.card = self.rows[3]
                self.time_2 = self.rows[4]
                self.num_2 = self.rows[5]
                self.stas_2 = self.rows[6]
                # 判断卡号是否正常
                if 6 <= len(self.card) <= 10:
                    self.record_list.append(self.name_2)
                    self.record_list.append(self.ID_2)
                    self.record_list.append(self.PRO_2)
                    self.record_list.append(self.card)
                    self.record_list.append(self.time_2)
                    self.record_list.append(self.num_2)
                    self.record_list.append(self.stas_2)
                #     判断列表是否为空
                if len(self.record_list) > 0:
                    self.record_listbox.insert("", self.m, text=self.m + 1, values=self.record_list)
                    self.m += 1
                #     清空列表
                self.record_list = []
        except Exception as e:
            # 抛出异常
            print("异常", e)
        finally:
            self.db3.close()

    # 显示数据
    def insert_data(self):
        self.recvlistbox.insert("", self.n, text=self.n + 1, values=self.data_list)
        self.n += 1

    def ID_count(self):
        self.per_record_listbox.delete(0, 'end')
        #     打开数据库连接
        self.db4 = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='mysql', charset='utf8')
        # 获取游标
        self.cur4 = self.db4.cursor()
        # 空列表
        self.num_list = []
        self.num_list1 = []
        self.jishu = 0
        try:
            self.cur4.execute("select*from Attendance")
            # 获取数据库数据
            self.res_4 = self.cur4.fetchall()
            for self.rows_4 in self.res_4:
                self.ID_4 = self.rows_4[0]
                self.ID_5 = self.rows_4[1]
                self.time_4 = self.rows_4[2]
                self.num_4 = self.rows_4[3]
                # 判断卡号是否正常且不存在
                if 6 <= len(self.ID_4) <= 10 and self.ID_4 not in self.num_list:
                    self.num_list.append(self.ID_4)
                    self.num_list.append(self.ID_5)
                    self.num_list.append(self.time_4)
                    # self.num_list.append(self.num_4)
                    self.num_list1.append(self.num_list)
                    self.num_list = []
            self.num_list4 = []
            for i in self.num_list1:
                self.num_list4.append(i[:2])
            self.num_list2 = []
            self.num_list3 = []
            self.flag = 0
            for i in self.num_list1:
                if i[:2] not in self.num_list2:
                    self.total = self.num_list4.count(i[:2])
                    self.num_list3.append(self.total)
                    self.num_list2.append(i[:2])
            for i in range(len(self.num_list2)):
                self.num_list2[i] += str(self.num_list3[i])
            # #     排序
            # self.num_list2.sort(key=lambda x: x[i][-1], reverse=True)
            for i in self.num_list2:
                self.per_record_listbox.insert(END, i)
            # for i in
            # if self.ID_4 in self.num_list:
            #     #     计数加1
            #     self.jishu += 1
            #
            # if self.jishu > 0 and len(self.num_list) > 0:
            #     self.num_list.append(self.jishu)
            #     self.per_record_listbox.insert(END, self.num_list)
            # #     清空列表
            # self.num_list = []
        except Exception as e:
            # 抛出异常
            print("异常", e)
        finally:
            self.db4.close()

    def zc_sql(self):
        #     打开数据库连接
        self.db5 = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='mysql', charset='utf8')
        # 获取游标
        self.cur5 = self.db5.cursor()
        self.zc_list = []
        try:
            self.cur5.execute("select*from admin")
            # 获取数据库数据
            self.res_5 = self.cur5.fetchall()
            for self.rows_5 in self.res_5:
                self.ID_6 = self.rows_5[3]
                self.zc_list.append(self.ID_6)
            # 判断卡号是否已注册
            if self.zc_text4.get() in self.zc_list:
                tkinter.messagebox.showinfo("提示", "该卡号已被注册")
            else:
                self.zc_insert = "insert into admin(name, ID, pro,card2)values ('%s', '%s','%s','%s')" % (
                    self.zc_text1.get(), self.zc_text2.get(), self.zc_text3.get(), self.zc_text4.get())
                self.cur5.execute(self.zc_insert)
                self.db5.commit()
                tkinter.messagebox.showinfo('提示', '登记成功')
                # self.sendcmd.delete(0, END)
                print("ok")
                # self.show_face()
        except Exception as e:
            # 抛出异常
            print("异常", e)
        finally:
            self.db5.close()

    def up_func(self):
        self.per_record_listbox.delete(0, END)
        self.num_list2.sort(key=lambda x: x[-1], reverse=True)
        #     排序
        for i in self.num_list2:
            self.per_record_listbox.insert(0, i)

    def low_func(self):
        #     排序
        self.per_record_listbox.delete(0, END)
        self.num_list2.sort(key=lambda x: x[-1], reverse=False)
        for i in self.num_list2:
            self.per_record_listbox.insert(0, i)

    # 统计界面
    def statistics(self):
        self.look.withdraw()
        self.statist_view = Tk()
        self.statist_view.title("门禁查询统计系统")
        self.statist_view.iconbitmap("title.ico")
        self.statist_view.geometry("560x500+500+250")
        self.per_button = Button(self.statist_view, text='返回', command=self.per_push)
        self.per_button.place(x=30, y=10, h=30, w=60)
        self.per_c1_label = Label(self.statist_view, text='卡号1', font=('宋体', 12))
        self.per_c2_label = Label(self.statist_view, text='卡号2', font=('宋体', 12))
        self.per_t_label = Label(self.statist_view, text='刷卡时间', font=('宋体', 12))
        self.per_num_label = Label(self.statist_view, text='刷卡总数', font=('宋体', 12))
        self.per_back_button = Button(self.statist_view, text='返回', command=self.per_push)
        self.per_push_button = Button(self.statist_view, text='刷新')
        self.per_stat_button = Button(self.statist_view, text='查询')
        self.up_button = Button(self.statist_view, text='升序', command=self.up_func)
        self.low_button = Button(self.statist_view, text='降序', command=self.low_func)
        self.per_record_listbox = Listbox(self.statist_view, font=('宋体', 16))
        self.per_button.place(x=30, y=10, h=30, w=60)
        self.per_push_button.place(x=470, y=10, h=30, w=60)
        self.per_stat_button.place(x=230, y=10, h=30, w=60)
        self.up_button.place(x=310, y=10, h=30, w=60)
        self.low_button.place(x=390, y=10, h=30, w=60)
        self.per_c1_label.place(x=40, y=50, h=20, w=50)
        self.per_c2_label.place(x=190, y=50, h=20, w=50)
        self.per_t_label.place(x=320, y=50, h=20, w=100)
        self.per_num_label.place(x=460, y=50, h=20, w=100)
        self.per_record_listbox.place(x=3, y=70, h=426, w=555)
        #     调用数据库统计数据
        self.ID_count()
        # 固定窗口大小，设置窗口不可拉伸
        self.statist_view.resizable(False, False)
        self.statist_view.mainloop()

    #     查找
    def find(self):
        #     打开数据库连接
        self.db6 = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='mysql', charset='utf8')
        # 获取游标
        self.cur6 = self.db6.cursor()
        self.find_total = []
        self.fi_count = 0
        self.fi_flag = 0
        try:
            self.cur6.execute("select*from attendance")
            # 获取数据库数据
            self.res_6 = self.cur6.fetchall()
            for self.rows_6 in self.res_6:
                self.name_6 = self.rows_6[0]
                self.ID_6 = self.rows_6[1]
                self.PRO_6 = self.rows_6[2]
                self.card_6 = self.rows_6[3]
                self.time_6 = self.rows_6[4]
                self.num_6 = self.rows_6[5]
                self.stas_6 = self.rows_6[6]
                self.fi_count += 1
                if self.fi_msg.get() == '姓名':
                    if self.name_6 == self.fi_text.get():
                        self.find_total.append(self.rows_6)
                elif self.fi_msg.get() == '卡号':
                    if self.card_6 == self.fi_text.get():
                        self.find_total.append(self.rows_6)
            if len(self.find_total) != 0:
                self.items = self.record_listbox.get_children()
                [self.record_listbox.delete(item) for item in self.items]
                for i in self.find_total:
                    self.record_listbox.insert("", self.fi_flag, text=self.fi_flag + 1, values=i)
                    self.fi_flag += 1
                # print(self.find_total)
                # self.record_listbox.delete(0, END)
            if len(self.res_6) >= self.fi_count and len(self.find_total) == 0:
                tkinter.messagebox.showinfo('提示', "抱歉，未找到结果")
                # print("ok")
        except Exception as e:
            # 抛出异常
            print("异常", e)
        finally:
            self.db6.close()

    def fi_select(self):
        if len(self.fi_text.get()) != 0:
            self.find()
            self.f_GUI.destroy()
        else:
            tkinter.messagebox.showinfo('提示', '输入为空')

    def del_select(self):
        if len(self.del_text.get()) != 0:
            self.del_fun()
            self.f = True
            self.del_GUI.destroy()
        else:
            tkinter.messagebox.showinfo('提示', '输入为空')

    # 查找
    def find_GUI(self):
        self.f = False
        self.del_zc = 3
        self.f_GUI = Tk()
        self.f_GUI.title("查找")
        self.f_GUI.geometry("250x100+600+500")

        # self.fi_msg = Label(self.look, text='姓名/学号')
        self.fi_msgsvar = StringVar()
        self.fi_msg = Combobox(self.f_GUI, textvariable=self.fi_msgsvar)
        self.fi_msg["value"] = ("姓名", "卡号")
        # 默认波特率
        self.fi_msg.current(0)
        self.fi_var = StringVar(self.f_GUI)
        self.fi_text = Entry(self.f_GUI, textvariable=self.fi_var)
        self.fi_button = Button(self.f_GUI, text='确定', command=self.fi_select)
        self.fi_msg.place(x=5, y=30, h=30, w=50)
        self.fi_text.place(x=60, y=30, h=30, w=100)
        self.fi_button.place(x=170, y=30, h=30, w=50)
        self.f_GUI.resizable(False, False)
        self.f_GUI.mainloop()

    # 查询记录界面
    def record(self):
        # 隐藏组窗口
        self.root.withdraw()
        self.look = Tk()
        self.look.title("门禁查询系统")
        self.look.iconbitmap("title.ico")
        self.look.geometry("560x500+500+250")
        # self.c1_label = Label(self.look, text='卡号1', font=('宋体', 12))
        # self.c2_label = Label(self.look, text='卡号2', font=('宋体', 12))
        # self.t_label = Label(self.look, text='刷卡时间', font=('宋体', 12))
        # self.num_label = Label(self.look, text='次数', font=('宋体', 12))

        self.record_listbox = Treeview(self.look)
        self.record_listbox["columns"] = ("姓名", "学号", "专业", "卡号", "时间", "次数", "状态")  # #定义列
        self.record_listbox.column("姓名", width=50)  # #设置列
        self.record_listbox.column("学号", width=50)
        self.record_listbox.column("卡号", width=50)  # #设置列
        self.record_listbox.column("专业", width=50)
        self.record_listbox.column("时间", width=150)
        self.record_listbox.column("次数", width=50)
        self.record_listbox.column("状态", width=50)
        self.record_listbox.heading("姓名", text="姓名")  # #设置显示的表头名
        self.record_listbox.heading("学号", text="学号")
        self.record_listbox.heading("专业", text="专业")
        self.record_listbox.heading("卡号", text="卡号")  # #设置显示的表头名
        self.record_listbox.heading("时间", text="时间")
        self.record_listbox.heading("次数", text="次数")
        self.record_listbox.heading("状态", text="状态")
        # self.record_listbox.insert("", 0, text='1', values=['6E9C39', '7248953', '2020-12-24 14:46:11', '1', '成功'])

        self.back_button = Button(self.look, text='返回', command=self.push)
        self.push_button = Button(self.look, text='刷新')
        self.stat_button = Button(self.look, text='统计', command=self.statistics)
        self.find_button = Button(self.look, text='查找', command=self.find_GUI)
        # self.record_listbox = Listbox(self.look, font=('宋体', 16))
        self.back_button.place(x=30, y=10, h=30, w=60)
        self.push_button.place(x=470, y=10, h=30, w=60)
        self.stat_button.place(x=390, y=10, h=30, w=60)
        self.find_button.place(x=320, y=10, h=30, w=60)
        # self.c1_label.place(x=40, y=50, h=20, w=50)
        # self.c2_label.place(x=190, y=50, h=20, w=50)
        # self.t_label.place(x=340, y=50, h=20, w=100)
        # self.num_label.place(x=480, y=50, h=20, w=50)
        self.record_listbox.place(x=3, y=70, h=426, w=555)
        # 调用数据库
        self.record_sql()
        # 固定窗口大小，设置窗口不可拉伸
        self.look.resizable(False, False)
        self.look.mainloop()

    def per_push(self):
        # 销毁子界面
        self.statist_view.destroy()
        # 将隐藏的上一个界面显示
        self.look.update()
        self.look.deiconify()

    # 返回上一个界面
    def push(self):
        # 销毁子界面
        self.f = True
        self.look.destroy()
        # self.look.withdraw()
        # 将隐藏的主界面显示
        self.root.update()
        self.root.deiconify()
        # self.show_face()

    # 登记界面退出
    def back(self):
        self.bdj = False
        self.zc.destroy()

        # # 重启界面
        # my_Serial()

    def ok_zc(self):
        self.f = True
        self.zc.withdraw()
        self.ok_list = []
        # 获取内容
        self.text1 = self.zc_text1.get()
        # 获取内容
        self.text2 = self.zc_text2.get()
        # 获取内容
        self.text3 = self.zc_text3.get()
        self.text4 = self.zc_text4.get()
        self.ok_list.append(self.text1)
        self.ok_list.append(self.text2)
        self.ok_list.append(self.text3)
        if len(self.text1) == 0 or len(self.text2) == 0 or len(self.text3) == 0 or len(self.text4) == 0:
            tkinter.messagebox.showinfo("提示", "信息不完整")
        else:
            # for i in self.ok_list:
            #     self.sendcmd.insert(0, i)
            self.zc_sql()

    # 登记
    def zc_func(self):
        if tkinter.messagebox.askokcancel('提示', '是否进行卡号登记？'):
            self.fg += 1
            self.zc = Tk()
            self.zc.title("门禁卡号登记")
            self.zc.iconbitmap("title.ico")
            self.zc.geometry("300x300+650+300")
            self.zc_label1 = Label(self.zc, text='姓名', font=('宋体', 12))
            self.zc_label2 = Label(self.zc, text='学号', font=('宋体', 12))
            self.zc_label3 = Label(self.zc, text='专业', font=('宋体', 12))
            self.zc_label4 = Label(self.zc, text='IC', font=('宋体', 12))
            self.zc_flag = StringVar(self.zc)
            self.zc_IC_var = StringVar(self.zc)
            # self.zc_IC_var.set("123")
            self.zc_f = Label(self.zc, textvariable=self.zc_flag, font=('宋体', 10))
            self.zc_text1 = Entry(self.zc)
            self.zc_text2 = Entry(self.zc)
            self.zc_text3 = Entry(self.zc)
            self.zc_text4 = Entry(self.zc, textvariable=self.zc_IC_var)
            self.zc_button = Button(self.zc, text='返回', command=self.back)
            self.ok_button = Button(self.zc, text='确定', command=self.ok_zc)
            self.zc_label1.place(x=30, y=10, h=30, w=80)
            self.zc_label2.place(x=30, y=60, h=30, w=80)
            self.zc_label3.place(x=30, y=110, h=30, w=80)
            self.zc_label4.place(x=30, y=160, h=30, w=80)
            self.zc_text1.place(x=80, y=10, h=30, w=200)
            self.zc_text2.place(x=80, y=60, h=30, w=200)
            self.zc_text3.place(x=80, y=110, h=30, w=200)
            self.zc_text4.place(x=80, y=160, h=30, w=200)
            self.zc_button.place(x=50, y=220, h=30, w=80)
            self.zc_f.place(x=120, y=160, h=30, w=100)
            self.ok_button.place(x=180, y=220, h=30, w=80)
            # 固定窗口大小，设置窗口不可拉伸
            self.zc.resizable(False, False)
            self.zc.mainloop()

    def zc_select(self, event):
        self.select = zc_button.get()
        if self.select in "用户登记":
            self.f = False
            self.dj = 1
            self.del_zc = 1
            self.zc_func()
        elif self.select in "考勤管理":
            # 考勤
            self.Attendance = True
            self.up_time['state'] = 'normal'
            self.ov_time['state'] = 'normal'
            self.cel_time_button['state'] = 'normal'
            # self.f = True
            # # 判断信息是否已填写
            # if self.dj == 0 or not self.bdj:
            #     tkinter.messagebox.showinfo('提示', "未登记")
            # else:
            #     self.zc_sql()
        elif self.select in "删除用户":
            self.f = False
            self.dj = 1
            self.del_zc = 2
            self.dele_func()

    # 界面重启
    def rebt(self):
        self.root.destroy()
        my_Serial()

    # 实时显示时间
    def gettime(self):
        self.now = datetime.datetime.now()
        self.time_text = '%s-%s-%s %s:%s:%s' % \
                         (self.now.year,
                          '{:0>2d}'.format(self.now.month),
                          '{:0>2d}'.format(self.now.day),
                          '{:0>2d}'.format(self.now.hour),
                          '{:0>2d}'.format(self.now.minute),
                          '{:0>2d}'.format(self.now.second))
        return self.time_text

    def update(self):
        self.nowtime.set(self.gettime())
        self.nowtime_label.after(1000, self.update)

    def cel_func(self):
        # 考勤
        self.Attendance = False
        self.up_time['state'] = 'disabled'
        self.ov_time['state'] = 'disabled'
        self.cel_time_button['state'] = 'disabled'

    def show_face(self):
        global zc_button
        self.root = Tk()
        self.root.title("南瓜不朽门禁管理系统")
        self.root.iconbitmap("title.ico")
        self.root.geometry("560x500+500+250")
        # # 创建背景画布
        # 参考https://blog.csdn.net/qq_41620823/article/details/99616160?utm_medium=distribute.pc_relevant_t0.none-task-blog-BlogCommendFromMachineLearnPai2-1.channel_param&depth_1-utm_source=distribute.pc_relevant_t0.none-task-blog-BlogCommendFromMachineLearnPai2-1.channel_param
        # self.canvas = Canvas(self.root, width=1200, height=600, bd=0, highlightthickness=0)
        # # 图片路径
        # self.imagepath = 'bg2.jpg'
        # self.img = Image.open(self.imagepath)
        # self.photo = ImageTk.PhotoImage(self.img)
        # self.canvas.create_image(500, 500, image=self.photo)
        # self.canvas.pack()
        # self.canvas.create_window(100, 50, width=100, height=20)

        # （1）打开串口按钮
        self.comopenflagstr = StringVar()
        self.comopenflagstr.set("系统未开启")
        self.labelname = Label(self.root, textvariable=self.comopenflagstr, font=('宋体', 10))
        self.comopenbtnstr = StringVar()
        self.comopenbtnstr.set("系统启动")
        self.btnopencom = Button(self.root, textvariable=self.comopenbtnstr, command=self.btn_hit)

        self.comlist = []
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) == 0:
            # print('无可用串口')
            self.comlist.append("无串口")
            self.btnopencom['state'] = 'disabled'
        else:
            for i in range(0, len(port_list)):
                plist_com = list(port_list[i])
                self.comlist.append(plist_com[i])

        self.labelport = Label(self.root, text="端口号：")
        self.cbcomportvar = StringVar()
        self.cbport = Combobox(self.root, textvariable=self.cbcomportvar)
        self.cbport["value"] = tuple(self.comlist)
        self.cbport.current(0)
        self.labelbps = Label(self.root, text="波特率:")
        self.cbcombpsvar = StringVar()
        self.cbbps = Combobox(self.root, textvariable=self.cbcombpsvar)
        self.cbbps["value"] = ("9600", "19200", "38400", "57600", "115200")
        # 默认波特率
        self.cbbps.current(4)
        # 显示时间
        self.nowtime = StringVar()
        self.nowtime.set(self.gettime())
        self.nowtime_label = Label(self.root, textvariable=self.nowtime, font=("宋体", 13), foreground='blue')
        self.zc_svar = StringVar()
        zc_button = Combobox(self.root, textvariable=self.zc_svar, font=('宋体', 12))
        zc_button["value"] = ("请选择", "用户登记", "删除用户", "考勤管理")
        # 默认波特率
        zc_button.current(0)
        # t提示
        self.info = StringVar()
        self.info_label = Label(self.root, textvariable=self.info, font=("宋体", 13), foreground='red')
        zc_button.bind("<<ComboboxSelected>>", self.zc_select)  # 绑定事件,(下拉列表框被选中时，绑定go()函数)
        # self.zc_button = Button(self.root, text="卡号登记", command=self.zc_func)
        # self.sendx = StringVar()
        self.up_time_label = Label(self.root, text='始：')
        self.ov_time_label = Label(self.root, text='终：')
        self.cel_time_button = Button(self.root, text='取消', command=self.cel_func)
        self.cel_time_button['state'] = 'disabled'
        self.up_time_var = StringVar()
        self.up_time = Combobox(self.root, textvariable=self.up_time_var)
        self.up_time["value"] = (
            "1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00",
            "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00", "00:00")
        self.up_time.current(0)
        self.up_time['state'] = 'disabled'
        self.ov_time_var = StringVar()
        self.ov_time = Combobox(self.root, textvariable=self.ov_time_var)
        self.ov_time["value"] = ("1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00", "9:00", "10:00",
                                 "11"                                                                                                             ":00",
                                 "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
                                 "21:00", "22:00", "23:00", "00:00")
        self.ov_time.current(0)
        self.ov_time['state'] = 'disabled'
        # self.card1_Label = Label(self.root, text="卡号1")
        # self.card2_Label = Label(self.root, text="卡号2")
        # self.time_Label = Label(self.root, text="时间")
        # self.count_Label = Label(self.root, text="次数")
        # self.status_Label = Label(self.root, text="状态")
        self.look_button = Button(self.root, text="查看记录", command=self.record)
        self.Reboot_button = Button(self.root, text="重启", command=self.rebt)
        # self.recvlistbox = Listbox(self.root, width=40, font=('宋体', 18))
        self.recvlistbox = Treeview(self.root)
        self.recvlistbox["columns"] = ("姓名", "学号", "专业", "卡号", "时间", "次数", "状态")  # #定义列
        self.recvlistbox.column("姓名", width=50)
        self.recvlistbox.column("学号", width=50)
        self.recvlistbox.column("专业", width=50)
        self.recvlistbox.column("卡号", width=50)  # #设置列
        self.recvlistbox.column("时间", width=150)
        self.recvlistbox.column("次数", width=50)
        self.recvlistbox.column("状态", width=50)
        self.recvlistbox.heading("姓名", text="姓名")  # #设置显示的表头名
        self.recvlistbox.heading("学号", text="学号")
        self.recvlistbox.heading("专业", text="专业")
        self.recvlistbox.heading("卡号", text="卡号")  # #设置显示的表头名
        self.recvlistbox.heading("时间", text="时间")
        self.recvlistbox.heading("次数", text="次数")
        self.recvlistbox.heading("状态", text="状态")
        # self.recvlistbox.insert("", 0, text='1', values=['6E9C39', '7248953', '2020-12-24 14:46:11', '1', '成功'])

        self.labelname.place(x=20, y=10, h=30, w=80)
        self.btnopencom.place(x=100, y=10, h=30, w=80)

        self.labelport.place(x=50, y=50, h=20, w=80)
        self.cbport.place(x=50, y=80, h=20, w=80)
        self.nowtime_label.place(x=300, y=110, h=25, w=180)
        self.nowtime_label.after(1000, self.update)
        self.labelbps.place(x=180, y=50, h=20, w=80)
        self.cbbps.place(x=180, y=80, h=20, w=80)
        self.info_label.place(x=300, y=140, h=25, w=180)
        zc_button.place(x=50, y=120, h=50, w=100)
        self.look_button.place(x=180, y=120, h=50, w=100)
        self.Reboot_button.place(x=180, y=10, h=30, w=80)
        self.up_time_label.place(x=300, y=10, h=80, w=20)
        self.up_time.place(x=320, y=40, h=20, w=60)
        self.ov_time_label.place(x=420, y=10, h=80, w=20)
        self.ov_time.place(x=440, y=40, h=20, w=60)
        self.cel_time_button.place(x=510, y=40, h=20, w=50)
        # self.card1_Label.place(x=20, y=160, h=50, w=100)
        # self.card2_Label.place(x=150, y=160, h=50, w=100)
        # self.time_Label.place(x=310, y=160, h=50, w=100)
        # self.count_Label.place(x=460, y=160, h=50, w=100)
        # self.status_Label.place(x=510, y=160, h=50, w=100)
        # self.recvlistbox.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=W)
        self.recvlistbox.place(x=5, y=180, h=315, w=550)
        self.root.resizable(0, 0)  # 阻止Python GUI的大小调整
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    # 验证成功
    def btn_sendcmd(self):
        if self.ser.isOpen():
            # text = b'c'
            text = 't'
            self.ser.write(text.encode('utf-8'))  # 写
            print("发送成功")

    # 验证失败
    def fail_sendcmd(self):
        if self.ser.isOpen():
            # text = b'c'
            text = 'b'
            self.ser.write(text.encode('utf-8'))  # 写
            print("发送成功")

# if __name__ == "__main__":
#     myserial = my_Serial()
