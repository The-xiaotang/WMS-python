"""
    程序入口 ：  界面调用其他模块
        （1）option.config : 配置文件
             ·init： False（默认）， 未初始化数据库；  true，数据库已经建立。  程序自己完成。
             ·host:  主机；
             ·user:  数据库用户
             ·password：数据库密码
             ·database: 用户数据库（ warehouse ）
        （2）settings.py: 基础设置。
        （3）mysql_connect.py: 实现对数据库的各种操作
        （4）gui.py:  程序UI设计， 程序入口
"""
import tkinter as tk
import tkinter.messagebox
from tkinter import Menu
from tkinter import ttk
import time
import settings
import mysql_conn as sql
import re

# 购货管理
class purchase_frame(tk.Frame):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tk.Label(self, text="购货管理", width=10, height=2, font=("黑体", 15), bg="cyan").place(x=250, y=10)
        self.place(x=160, y=40)

        # 实现订货
        tk.Label(self, text="订货", width=10, height=2, font=("黑体", 13), bg="palegreen").place(x=100, y=70)
        tk.Label(self, text="商品名：", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                                y=90)
        self.name = tk.Entry(self, width=18)
        self.name.place(x=100, y=100)
        tk.Label(self, text="数量 ：", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                               y=120)
        self.num = tk.Entry(self, width=18)
        self.num.place(x=100, y=130)
        tk.Label(self, text="单价:", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                              y=150)
        self.price = tk.Entry(self, width=18)
        self.price.place(x=100, y=160)
        tk.Label(self, text="供货商:", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                                y=180)
        self.shop = tk.Entry(self, width=18)
        self.shop.place(x=100, y=190)
        tk.Label(self, text="联系方式:", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                                  y=210)
        self.phone = tk.Entry(self, width=18)
        self.phone.place(x=100, y=220)
        tk.Button(self, text="确认订货", width=10, height=1, command=self.order_goods).place(x=10, y=270)
        tk.Button(self, text="重置", width=10, height=1, command=self.set_entry).place(x=150, y=270)

        # 实现收货和退货
        tk.Label(self, text="订货清单", width=10, height=2, font=("黑体", 13), bg="palegreen").place(x=300, y=70)
        self.info_list = tk.Listbox(self, width=40, height=13, font=("宋体", 12))
        self.info_list.place(x=250, y=100)
        self.add_inof_list()

        menu = Menu(root, tearoff=0)
        menu.add_command(label="收货", command=self.get_goods)
        menu.add_command(label="查看信息", command=self.show_info_selected)
        # menu.add_separator()
        menu.add_command(label="退货", command=self.return_goods)
        self.menu = menu
        # 鼠标右键弹出菜单
        self.info_list.bind("<Button-3>", self.popupmenu)

    # 收货
    def get_goods(self):
        loc = self.info_list.curselection()[0]
        data = str(self.info_list.get(loc)).split(" ")
        title = ['订单编号：', '商品名：', '供货商：', '联系方式：']
        format_data = ""
        for index in range(len(title)):
            format_data += str(title[index]) + str(data[index]) + "\n"

        if tk.messagebox.askyesno(title="确认收货", message=format_data):
            self.info_list.delete(loc)
            # done 数据库修改
            sql.change_goods_state_receving(data[0], data[1])

    # 退货处理
    def return_goods(self):
        loc = self.info_list.curselection()[0]
        data = str(self.info_list.get(loc)).split(" ")
        title = ['订单编号：', '商品名：', '供货商：', '联系方式：']
        format_data = ""
        for index in range(len(title)):
            format_data += str(title[index]) + str(data[index]) + "\n"

        if tk.messagebox.askyesno(title="确认退货", message=format_data):
            self.info_list.delete(loc)
            # done 数据库修改
            sql.change_goods_state_back(data[0])

    # 订货清单打开菜单
    def popupmenu(self, event):
        if len(self.info_list.curselection()):
            self.menu.post(event.x_root, event.y_root)

    # 添加订货清单信息
    def add_inof_list(self):
        # done 获取数据库信息
        data = sql.get_goods_info_order()
        for item in data:
            self.info_list.insert('end', item)

    # 订货
    def order_goods(self):
        id = self.get_id()
        name = self.name.get()
        num = self.num.get()
        price = "%5.2f" % float(self.price.get())
        state = "订货"
        shop = self.shop.get()
        phone = self.phone.get()
        user_id = settings.user["id"]
        show_data = "{} {} {} {}".format(id, name, shop, phone)
        self.info_list.insert('end', show_data)
        # done 写入数据库
        sql.order_goods(id=id, name=name, num=num, price=price, shop=shop, phone=phone, user_id=user_id)

    # 计算订单编号
    def get_id(self):
        id_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # DOne 读取数据库今日订单数量
        id_num = int(sql.get_purchase_day_sum(id_time))
        return str(id_time) + ("_{:0>4d}".format(id_num))

    # 清空订货信息（订货）
    def set_entry(self):
        self.name.delete(0, 'end')
        self.num.delete(0, 'end')
        self.price.delete(0, 'end')
        self.shop.delete(0, 'end')
        self.phone.delete(0, 'end')

    # 显示订单详情（ 状态 = ‘订货’）
    def show_info_selected(self):
        data = self.info_list.get(self.info_list.curselection()[0])
        id = data.split(" ")[0]
        #  done 查询订单的详细信息
        data = sql.get_goods_detailed_info(id)
        format_data = ""
        for item in data:
            format_data += str(item) + "\n"
        tk.messagebox.showinfo(title="提示", message=format_data)


# 零售管理
class running_frame(tk.Frame):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tk.Label(self, text="零售管理", width=10, height=2, font=("黑体", 15), bg="cyan").place(x=250, y=10)
        self.place(x=160, y=40)

        # 添加商品
        tk.Label(self, text="商品名-编号", width=20, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(
            x=20, y=70)
        tk.Label(self, text="单价", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=250,
                                                                                                             y=70)
        tk.Label(self, text="数量", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=350,
                                                                                                             y=70)
        tk.Label(self, text="合计", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=450,
                                                                                                             y=70)
        self.name_id = ttk.Combobox(self, width=28)
        self.name_id.bind("<<ComboboxSelected>>", self.update_goods_info)
        self.name_id.place(x=20, y=100)
        self.set_value()
        self.price = tk.Spinbox(self, width=7, from_=0, to=100000, increment=1, command=self.change_num)
        self.price.place(x=250, y=100)
        self.num = tk.Spinbox(self, width=7, from_=0, to=100000, increment=1)
        self.num.place(x=350, y=100)
        self.account = tk.Label(self, text="-----", width=10, height=1, font=("楷体", 12), bg="palegreen", anchor="w")
        self.account.place(x=450, y=100)
        tk.Button(self, text="单品合计", width=10, height=1, command=self.add_goods).place(x=510, y=90)

        # 商品展示
        self.goods_info = tk.Listbox(self, width=71, height=9, font=("宋体", 12))
        self.goods_info.place(x=20, y=140)

        # 商品清除
        menu = Menu(root, tearoff=0)
        menu.add_command(label="删除", command=self.del_goods)
        self.menu = menu
        # 鼠标右键弹出菜单
        self.goods_info.bind("<Button-3>", self.popupmenu)
        # 总额计算
        tk.Button(self, text="计算总和", width=10, height=1, command=self.all_account).place(x=20, y=310)
        tk.Button(self, text="清空商品", width=10, height=1, command=self.del_goods_info).place(x=510, y=310)
        self.money = tk.Label(self, text="-----", width=10, height=1, font=("楷体", 12), bg="palegreen", anchor="w")
        self.money.place(x=200, y=310)

    # 设置商品信息
    def set_value(self):
        #  done 获取库存商品name id
        data = sql.get_stock_goods_name_id()
        self.name_id['value'] = data

    # 选择商品后修改对应数据
    def update_goods_info(self, event):
        name_id = str(self.name_id.get()).split("  ")
        id = name_id[1]
        # done 读取商品的库存价格
        price = sql.get_stock_goods_price(id)
        self.price.delete(0, 'end')
        self.price.insert(0, price)

    # 修改价格整数为小数
    def change_num(self):
        data = self.price.get()
        self.price.insert('end', ".00")

    # 计算商品价格 加入购物车
    def add_goods(self):
        name_id = self.name_id.get()
        price = self.price.get()
        num = self.num.get()

        account = eval(price) * eval(num)
        self.account['text'] = format(account, '>5.2f')

        data = "{}  {}/元  {}/个  {}元".format(name_id, str(price), str(num), format(account, '>5.2f'))
        self.goods_info.insert(0, data)

    # 商品清单打开菜单
    def popupmenu(self, event):
        if len(self.goods_info.curselection()):
            self.menu.post(event.x_root, event.y_root)

    # 删除商品--商品栏中清除
    def del_goods(self):
        loc = self.goods_info.curselection()[0]
        data = str(self.goods_info.get(loc)).replace("  ", "\n")
        if tk.messagebox.askyesno(title="确认删除", message=data):
            self.goods_info.delete(loc)

    # 计算商品总和
    def all_account(self):
        data = self.goods_info.get(0, 'end')
        money = float(0)
        for item in data:
            money += float(str(item).split(" ")[-1][:-1])
        self.money['text'] = format(money, '<8.2f')
        # DOne 流水账 输入数据库
        sql.write_running(settings.user["id"], data)

    # 清空商品
    def del_goods_info(self):
        if tk.messagebox.askyesno(title="确认删除", message="清空商品栏？"):
            self.goods_info.delete(0, 'end')
            self.money['text'] = "-----"


# 仓库管理
class warehouse_frame(tk.Frame):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tk.Label(self, text="仓库管理", width=10, height=2, font=("黑体", 15), bg="cyan").place(x=250, y=10)
        self.place(x=160, y=40)

        # 查看存货
        tk.Label(self, text="商品名", width=20, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=20,
                                                                                                               y=70)
        self.name = ttk.Combobox(self, width=20)
        self.name.place(x=20, y=100)
        self.set_name()

        tk.Label(self, text="数量", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=250,
                                                                                                             y=70)
        self.num_type = ttk.Combobox(self, width=1)
        self.num_type['value'] = ['>', '=', "<"]
        self.num_type.current(0)
        self.num_type.place(x=250, y=100)
        self.num_value = tk.Spinbox(self, width=4, from_=0, to=9999999, increment=1)
        self.num_value.place(x=280, y=100)

        tk.Label(self, text="价格", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=350,
                                                                                                             y=70)
        self.price_type = ttk.Combobox(self, width=1)
        self.price_type['value'] = ['>', '=', "<"]
        self.price_type.current(0)
        self.price_type.place(x=350, y=100)
        self.price_value = tk.Spinbox(self, width=4, from_=0, to=9999999, increment=1, command=self.set_price_value)
        self.price_value.place(x=380, y=100)

        tk.Button(self, text="条件查询", font=("楷体", 12), command=self.find_stock).place(x=430, y=95)
        tk.Button(self, text="查询全部", bg="gold", font=("楷体", 12), command=self.find_all_stock).place(x=510, y=95)

        # 库存显示
        self.stock_info = tk.Listbox(self, width=80, height=10)
        self.stock_info.place(x=20, y=150)

    # 读取库存商品名
    def set_name(self):
        #  done 读取数据库库存商品名
        data = sql.get_stock_goods_name_id()
        self.name['value'] = data

    # 按条件查询库存
    def find_stock(self):
        name = str(self.name.get()).split(" ")[0]
        num = self.num_type.get() + self.num_value.get()
        price = self.price_type.get() + self.price_value.get()
        # done 按条件查询库存
        data = sql.get_stock_goods_price_and_num(name, num, price)
        self.stock_info.delete(0, 'end')
        for item in data:
            self.stock_info.insert('end', item)

    # 查询所有库存
    def find_all_stock(self):
        # done  查询全部库存
        data = sql.get_all_stock_info()
        self.stock_info.delete(0, 'end')
        for item in data:
            self.stock_info.insert('end', item)

    #   格式化价格设置
    def set_price_value(self):
        self.price_value.insert('end', '.00')


# 结算管理
class acount_frame(tk.Frame):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tk.Label(self, text="结算管理", width=10, height=2, font=("黑体", 15), bg="cyan").place(x=250, y=10)
        self.place(x=160, y=40)

        # 查询条件
        tk.Label(self, text="查询类型：", width=20, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                                  y=70)
        self.type = ttk.Combobox(self, width=15, height=2)
        self.type['value'] = ['购货账目', '零售账目']
        self.type.place(x=90, y=75)
        self.type.current(0)

        tk.Label(self, text="开始时间：", width=20, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                                  y=100)
        self.y1 = tk.Spinbox(self, width=6, from_=0, to=2050, increment=1, command=self.set_y1)
        self.y1.place(x=90, y=107)
        self.y1.delete(0, 'end')
        self.y1.insert(0, '2020年')
        self.m1 = tk.Spinbox(self, width=3, from_=1, to=12, increment=1, command=self.set_m1)
        self.m1.place(x=145, y=107)
        self.m1.delete(0, 'end')
        self.m1.insert(0, '1月')
        self.d1 = tk.Spinbox(self, width=3, from_=1, to=31, increment=1, command=self.set_d1)
        self.d1.place(x=180, y=107)
        self.d1.delete(0, 'end')
        self.d1.insert(0, '1日')

        tmp_time = time.strftime('%Y-%m-%d', time.localtime(time.time())).split("-")
        tk.Label(self, text="结束时间：", width=20, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                                  y=130)
        self.y2 = tk.Spinbox(self, width=6, from_=0, to=2050, increment=1, command=self.set_y2)
        self.y2.place(x=90, y=137)
        self.y2.delete(0, 'end')
        self.y2.insert(0, '{}年'.format(tmp_time[0]))
        self.m2 = tk.Spinbox(self, width=3, from_=1, to=12, increment=1, command=self.set_m2)
        self.m2.place(x=145, y=137)
        self.m2.delete(0, 'end')
        self.m2.insert(0, '{}月'.format(tmp_time[1]))
        self.d2 = tk.Spinbox(self, width=3, from_=1, to=31, increment=1, command=self.set_d2)
        self.d2.place(x=180, y=137)
        self.d2.delete(0, 'end')
        self.d2.insert(0, '{}日'.format(tmp_time[2]))

        tk.Label(self, text="操作员：", width=20, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                                y=160)
        self.user = ttk.Combobox(self, width=15, height=2)
        self.user.place(x=90, y=165)
        self.set_user_val()

        tk.Button(self, text="查询", width=28, height=1, command=self.find_info).place(x=10, y=240)

        # 查询结果显示
        self.ans_info = tk.Listbox(self, width=45, height=15, font=('宋体', 12))
        self.ans_info.place(x=220, y=70)
        self.ans_info.bind("<Double-Button-1>", self.show_detailed_ans_info)

    # 显示详细信息
    def show_detailed_ans_info(self, event):
        type = self.ans_info.curselection()
        if type and type[0] > 0:
            id = self.ans_info.get(type[0])
            # todo 获取详细信息
            data = sql.get_detailed_info(str(self.ans_info.get(0)).strip(), str(id).split(" ")[0])
            tk.messagebox.showinfo(title=str(self.ans_info.get(0)).strip(), message=data)

    # 设置查询条件--操作员
    def set_user_val(self):
        # DOne 获取操作员id_name
        data = sql.get_user_name_id()
        self.user['value'] = data

    # 查询信息
    def find_info(self):
        type = self.type.get()
        start_time = re.sub(r"[年月日]", "",
                            "%s-%03s-%03s" % (str(self.y1.get()), str(self.m1.get()), str(self.d1.get())))
        end_time = re.sub(r"[年月日]", "",
                          "%s-%03s-%03s" % (str(self.y2.get()), str(self.m2.get()), str(self.d2.get())))
        start_time.replace(" ", '0')
        end_time.replace(" ", '0')
        try:
            user_id = str(self.user.get()).split("__")[1]
        except Exception as e:
            user_id = ""
        # done  读取数据库
        data = sql.find_running_or_purchase(type, start_time, end_time, user_id)
        self.ans_info.delete(0, 'end')
        for item in data:
            self.ans_info.insert('end', item)

    # 设置伪日历
    def set_y1(self):
        self.y1.insert('end', '年')

    def set_m1(self):
        self.m1.insert('end', '月')

    def set_d1(self):
        self.d1.insert('end', '日')

    def set_y2(self):
        self.y2.insert('end', '年')

    def set_m2(self):
        self.m2.insert('end', '月')

    def set_d2(self):
        self.d2.insert('end', '日')


# 管理员
class manger_frame(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tk.Label(self, text="管理员", width=10, height=2, font=("黑体", 15), bg="cyan").place(x=250, y=10)
        self.place(x=160,y=40)

        # 实现 添加账号
        tk.Label(self, text="添加账号", width=10, height=2, font=("黑体", 13), bg="palegreen").place(x=90, y=60)
        tk.Label(self, text="昵称：", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                              y=90)
        self.name = tk.Entry(self, width=18)
        self.name.place(x=120, y=100)
        tk.Label(self, text="账号 ：", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                               y=120)
        self.id = tk.Entry(self, width=18)
        self.id.place(x=120, y=130)
        tk.Label(self, text="密码:", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                              y=150)
        self.pw = tk.Entry(self, width=18)
        self.pw.place(x=120, y=160)
        tk.Label(self, text="再次输入密码：", width=13, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(
            x=10, y=180)
        self.pw2 = tk.Entry(self, width=18)
        self.pw2.place(x=120, y=190)
        tk.Label(self, text="等级:", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                              y=210)
        self.grade = ttk.Combobox(self, width=16)
        self.grade.place(x=120, y=220)
        self.grade['value'] = ['管理员', '普通操作员']
        self.grade.current(1)
        tk.Button(self, text="添加账号", width=10, height=1, command=self.add_account).place(x=10, y=270)
        tk.Button(self, text="重置", width=10, height=1, command=self.reset_entry).place(x=170, y=270)

        # 实现删除和修改信息
        tk.Label(self, text="账号", width=10, height=2, font=("黑体", 13), bg="palegreen").place(x=300, y=60)
        self.account_list = tk.Listbox(self, width=35, height=13, font=("宋体", 12))
        self.account_list.place(x=280, y=100)
        self.add_account_list()

        menu = Menu(root, tearoff=0)
        menu.add_command(label="修改信息", command=self.change_pw)
        menu.add_command(label="删除账号", command=self.del_account)

        self.menu = menu
        # 鼠标右键弹出菜单
        self.account_list.bind("<Button-3>", self.popupmenu)

    # 商品清单打开菜单
    def popupmenu(self, event):
        if len(self.account_list.curselection()):
            self.menu.post(event.x_root, event.y_root)

    # 添加账号
    def add_account(self):
        name = self.name.get()
        id = self.id.get()
        pw = self.pw.get()
        pw2 = self.pw2.get()
        grade = self.grade.get()

        # done 添加账号，写入数据库
        if name == "" or id == "" or grade == "":
            tk.messagebox.showwarning(title="添加账号", message="请填入正确的数据！")
        else:
            if not pw == pw2:
                tk.messagebox.showwarning(title="密码", message="密码不一致！")

            else:
                if sql.add_user(name, id, pw, grade):
                    tk.messagebox.showinfo(title="添加账号", message="添加成功！")
                    info = "{}  {}  {}  {}".format(name, id, pw, grade)
                    self.account_list.insert('end', info)
                else:
                    tk.messagebox.showerror(title="添加账号", message="账号已存在，请修改账号！")

    # 修改信息界面
    def change_pw(self):
        # 获取数据
        data = str(self.account_list.get(self.account_list.curselection()[0]))
        data = data.split("  ")
        print(data)
        # 界面
        child = tk.Toplevel()
        child.geometry("280x210+100+100")
        child.config(bg="palegreen")
        child.title("修改账号信息")

        tk.Label(child, text="昵称：", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                               y=20)
        name = tk.Entry(child, width=18)
        name.place(x=120, y=30)
        name.insert(0, data[0])

        tk.Label(child, text="账号 ：", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                                y=50)
        id = tk.Label(child, width=18, text=str(data[1]), anchor="w")
        id.place(x=120, y=60)

        tk.Label(child, text="密码:", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                               y=80)
        pw = tk.Entry(child, width=18)
        pw.insert(0, data[2][2:])
        pw.place(x=120, y=90)

        tk.Label(child, text="等级:", width=10, height=2, font=("楷体", 12), bg="palegreen", anchor="w").place(x=10,
                                                                                                               y=110)
        grade = ttk.Combobox(child, width=16)
        grade.place(x=120, y=120)
        grade['value'] = ['管理员', '普通操作员']
        grade.current(1)
        if data[3] == "管理员":
            grade.current(0)

        tk.Button(child, text="修改信息", width=10, height=1,
                  command=lambda: self.change_account(str(data[1]), name, pw, grade)).place(x=10, y=170)
        tk.Button(child, text="退出", width=10, height=1, command=child.destroy).place(x=170, y=170)
        child.mainloop()

    # 修改信息
    def change_account(self, id, name, pw, grade):
        name = name.get()
        pw = pw.get()
        grade = grade.get()

        if name == "" or pw == "" or grade == "":
            tk.messagebox.showwarning(title="修改用户信息", message="请正确填写相关数据！")
        else:
            #  done 修改用户信息
            sql.update_user_info(id, name, pw, grade)
            self.account_list.delete(0, 'end')
            self.add_account_list()

    # 删除账号
    def del_account(self):
        loc = self.account_list.curselection()[0]
        data = str(self.account_list.get(loc)).split("  ")
        title = ['昵称：', '账号：', '密码：', '登记：']
        format_data = ""
        for index in range(len(data)):
            format_data += title[index] + data[index] + "\n"
        if tk.messagebox.askyesno(title="确认删除", message=data):
            self.account_list.delete(loc)
            # done 数据库修改
            sql.del_user(data[1])

    # 获取已存在账号信息
    def add_account_list(self):
        # done 获取管理员信息
        data = sql.get_user_info()
        self.account_list.delete(0, 'end')
        for item in data:
            self.account_list.insert('end', item)

    # 重置输入框
    def reset_entry(self):
        self.name.delete(0, 'end')
        self.id.delete(0, 'end')
        self.pw.delete(0, 'end')
        self.pw2.delete(0, 'end')
        self.grade.current(0)


# 管理员登录 - settings.manger_signing( False/ True)
def manger_sign(frame, tmp_frame):
    child = tk.Toplevel()
    child.geometry("300x230+100+100")
    child.config(bg="palegreen")
    child.title("管理员登录")

    #  管理员登录信息
    tk.Label(child, width=10, height=2, text="账号： ", anchor="w", bg="palegreen", font=("黑体", 12)).place(x=20, y=20)
    user_id = tk.Entry(child, width=20)
    user_id.place(x=130, y=25)

    tk.Label(child, width=10, height=2, text="密码： ", anchor="w", bg="palegreen", font=("黑体", 12)).place(x=20, y=60)
    user_pw = tk.Entry(child, width=20)
    user_pw.place(x=130, y=65)

    tk.Label(child, width=13, height=2, text="再次输入密码： ", anchor="w", bg="palegreen", font=("黑体", 12)).place(
        x=20, y=100)
    user_pw2 = tk.Entry(child, width=20)
    user_pw2.place(x=130, y=105)

    # 操作
    tk.Button(child, width=10, height=1, text="登录",
              command=lambda: manger_sign_check(frame, tmp_frame, child, user_id.get(), user_pw.get(),
                                                user_pw2.get())).place(x=20, y=165)
    tk.Button(child, width=10, height=1, text="重置",
              command=lambda: reset_manger_sign_info(user_id, user_pw, user_pw2)).place(x=190, y=165)
    child.mainloop()

#  管理员登录
# 修改管理员登录回调函数
def manger_sign_check(frame, tmp_frame, child, user_id, user_pw, user_pw2):
    if not user_pw == user_pw2:
        tk.messagebox.showwarning(title="管理员登录", message="密码不一致！")
    else:
        data, name = sql.manger_sign(user_id, user_pw)
        if data:
            tk.messagebox.showinfo(title="提示", message=f"管理员:{name}\n\t\t登录成功！")
            child.destroy()
            settings.manger_signing = True
            # 直接返回管理员框架实例
            return manger_frame(master=function_frame, width=600, heigt=350, bg='palegreen')
#  重置管理员登录信息
def reset_manger_sign_info(user_id, user_pw, user_pw2):
    user_id.delete(0, 'end')
    user_pw.delete(0, 'end')
    user_pw2.delete(0, 'end')


#  实现页面切换
# 修改change_frame函数
def change_frame(frame, tmp_frame):
    if tmp_frame == "manger_frame":  # 管理员登录
        if not settings.manger_signing:  # 添加权限验证
            manger_sign(frame, tmp_frame)
        return manger_frame(master=function_frame, width=600, height=350, bg='palegreen')
    else:
        if frame:
            frame.destroy()
        return eval(tmp_frame + "(master=function_frame, width=600, height=350, bg='palegreen')")

# 在登录成功后显示其他功能按钮
def show_function_buttons():
    purchase_button.place(x=50, y=60)
    running_button.place(x=50, y=120)
    warehouse_button.place(x=50, y=180)
    acount_button.place(x=50, y=240)
    manger_button.place(x=50, y=300)

# 在登录失败或未登录时隐藏其他功能按钮
def hide_function_buttons():
    purchase_button.place_forget()
    running_button.place_forget()
    warehouse_button.place_forget()
    acount_button.place_forget()
    manger_button.place_forget()

# 登录类
class sign_frame(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tk.Label(self, text="登录/注册", width=10, height=2, font=("黑体", 15), bg="cyan").place(x=250, y=10)
        self.place(x=160, y=40)

        tk.Label(self, text="账号: ", width=14, height=2, font=("楷体", 12), bg="palegreen", anchor="w") \
            .place(x=150, y=100)
        self.user_id = tk.Entry(self, width=20)
        self.user_id.place(x=300, y=110)

        tk.Label(self, text="密码: ", width=14, height=2, font=("楷体", 12), bg="palegreen", anchor="w") \
            .place(x=150, y=150)
        self.user_pw = tk.Entry(self, width=20, show="*")
        self.user_pw.place(x=300, y=160)

        tk.Label(self, text="重新输入密码: ", width=14, height=2, font=("楷体", 12), bg="palegreen", anchor="w") \
            .place(x=150, y=200)
        self.user_pw2 = tk.Entry(self, width=20, show="*")
        self.user_pw2.place(x=300, y=210)

        tk.Button(self, text="登录", width=10, height=1, command=self.check).place(x=150, y=270)
        tk.Button(self, text="注册", width=10, height=1, command=self.register).place(x=365, y=270)

    def check(self):
        user_id = self.user_id.get()
        user_pw = self.user_pw.get()
        user_pw2 = self.user_pw2.get()

        if user_pw != user_pw2:
            tk.messagebox.showwarning(title='提示', message='密码不一致！')
        else:
            # 登录验证
            ans = sql.check_sign(user_id, user_pw)
            if ans[0]:
                tk.messagebox.showinfo(title="提示", message="登陆成功！")
                settings.user["name"] = ans[1]
                settings.user["id"] = user_id

                # 隐藏登录界面
                self.place_forget()

                # 显示功能界面
                function_frame.place(x=0, y=0, width=800, height=400)
                show_function_buttons()

            else:
                tk.messagebox.showwarning(title='提示', message='密码错误！')
    def register(self):
        user_id = self.user_id.get()
        user_pw = self.user_pw.get()
        user_pw2 = self.user_pw2.get()

        if user_pw != user_pw2:
            tk.messagebox.showwarning(title='提示', message='密码不一致！')
        else:
            # 注册新用户
            if sql.add_user("新用户", user_id, user_pw, "普通操作员"):
                tk.messagebox.showinfo(title="提示", message="注册成功！")
            else:
                tk.messagebox.showwarning(title='提示', message='账号已存在！')


# 主程序
if __name__ == '__main__':
    root = tk.Tk()
    root.title("仓库售货管理系统")
    root.geometry("800x400")

    # 先显示登录界面
    login_frame = sign_frame(master=root, width=600, height=350, bg="palegreen")
    login_frame.place(x=100, y=20)  # 居中显示登录界面

    # 初始化功能按钮（但保持隐藏）
    function_frame = tk.Frame(root)  # 用于容纳功能按钮的容器
    function_frame.place(x=0, y=0, width=800, height=400)

    tk.Label(master=function_frame, text="昵称：{}\t账号：{}".format(settings.user["name"], settings.user["id"])) \
        .place(x=50, y=10)

    purchase_button = tk.Button(master=function_frame, text="购货管理", width=10, height=2,
                                command=lambda: change_frame(None, "purchase_frame"))
    running_button = tk.Button(master=function_frame, text="零售管理", width=10, height=2,
                               command=lambda: change_frame(None, "running_frame"))
    warehouse_button = tk.Button(master=function_frame, text="仓库管理", width=10, height=2,
                                 command=lambda: change_frame(None, "warehouse_frame"))
    acount_button = tk.Button(master=function_frame, text="结算管理", width=10, height=2,
                              command=lambda: change_frame(None, "acount_frame"))
    manger_button = tk.Button(master=function_frame, text="管理员", width=10, height=2,
                              command=lambda: change_frame(None, "manger_frame"))

    # 初始隐藏功能界面
    function_frame.place_forget()

    root.mainloop()

