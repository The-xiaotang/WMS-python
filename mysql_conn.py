# -*- coding: UTF-8 -*-
import pymysql
import settings
import re
import time

sql = pymysql.connect(
    host='localhost',
    port=3306, user='root',
    password='Tt87094938',
    db='warehouse')
cur = sql.cursor()

"""
    登录界面
"""

# 验证登录: 成功，返回True，用户姓名；  失败， 返回False，""
def check_sign(id, pw):
    code = "select  name from users where id='{}'and pw='{}' ".format(id, pw)
    if cur.execute(code):
        return True, cur.fetchall()[0][0]
    else:
        return False, ""


"""
    购货管理
"""


# 获取订单信息（ 状态 =“订货”）， id name shop phone
def get_goods_info_order():
    code = "select id, name, shop,phone from purchase where state='订货'"
    data = []
    if cur.execute(code):
        cur_data = cur.fetchall()
        for item in cur_data:
            tmp = ""
            for i in item:
                tmp += str(i) + " "
            data.append(tmp)
    return data


# 获取某订单的详细信息（ 状态 =“订货”）
def get_goods_detailed_info(id):  # 订单id
    code = "SELECT  purchase.*, users.name FROM purchase,users  WHERE purchase.id='{}' AND purchase.user_id=users.id ".format(
        id)
    data = []
    title = ['订单号：', '名字：', '价格：', '数量：', '状态：', '店铺名称：', '联系方式：', '操作员id：', '操作员：']
    if cur.execute(code):
        cur_data = cur.fetchall()[0]
        for index in range(len(cur_data)):
            # print( cur_data, index, len( cur_data))
            data.append(str(title[index]) + str(cur_data[index]))
    return data


# 订单收货- （1）状态修改为收货； （2）库存修改
def change_goods_state_receving(id, name):
    #  （1）修改状态
    code = "update purchase set  state='收货' where id='{}'".format(id)
    cur.execute(code)
    #  （2）库存修改
    code = "select id from stock where name='{}'".format(name)
    if cur.execute(code):
        code = "update stock  set sum= sum+( select num from purchase where id='{}') where  id='{}' ".format(id,
                                                                                                             cur.fetchall()[
                                                                                                                 0][0])
    else:
        cur.execute("select count(*) from  stock")
        s_id = "%06d" % cur.fetchall()[0][0]
        name = name
        cur.execute("select num,  price  from  purchase where id='{}'".format(id))
        num, price = cur.fetchall()[0]
        code = "insert into stock(id,name,sum,price) values('{}','{}','{}','{}')".format(s_id, name, num, price)
    print(code)
    cur.execute(code)


# 订单退货- （1）状态修改为 退货 ；
def change_goods_state_back(id):
    code = "update purchase set  state='退货' where id='{}'".format(id)
    cur.execute(code)


# 订货
def order_goods(id, name, num, price, shop, phone, user_id):
    code = "insert into purchase(id,name,num,price,shop,phone,user_id,state) values('{}','{}','{}',{},'{}','{}','{}','订货')".format(
        id, name, num, price, shop, phone, user_id)
    cur.execute(code)
    print(code)


#  获取当天订单数量
def get_purchase_day_sum(id_time):
    code = "select count(*) from purchase where id like '{}%'".format(id_time)
    cur.execute(code)
    return cur.fetchall()[0][0] + 1


"""
    零售管理
"""


#   获取库存商品的name id
def get_stock_goods_name_id():
    code = "select name, id  from  stock"
    cur.execute(code)
    data = []
    tmp_data = cur.fetchall()
    for item in tmp_data:
        data_str = ""
        for i in item:
            data_str += str(i) + "  "
        data.append(data_str)
    return data


#  获取库存商品价格---利润值相加
def get_stock_goods_price(id):
    code = "select  price  from stock where id='{}'".format(id)
    cur.execute(code)
    return "%.2f" % (float(cur.fetchall()[0][0]) * (1 + settings.profit))


#  流水账写入数据库
def write_running(user_id, data):
    id_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    for item in data:
        cur.execute("select count(*) from running where id like '{}%'".format(id_time))
        id_num = cur.fetchall()[0][0]
        id = str(id_time) + "_" + "{:0>4d}".format(int(id_num))

        item = re.sub(r" +", " ", str(item)).split(" ")
        name = item[0]
        stock_id = item[1]
        price = item[2][:-2]
        num = item[3][:-2]

        # 添加流水账
        code = "insert into running(id, stock_id, num, account, user_id)  values('{}','{}','{}','{}','{}')".format(id,
                                                                                                                   stock_id,
                                                                                                                   num,
                                                                                                                   price,
                                                                                                                   user_id)
        cur.execute(code)
        # 修改库存
        code = "update stock set sum=sum-{}  where id='{}'".format(num, stock_id)
        cur.execute(code)


"""
    仓库管理
"""


#  获取符合条件的库存信息
def get_stock_goods_price_and_num(name, num, price):
    code = "select name, id, price,sum from stock where  name like '%{}%' and  sum{} and  price{} order by id asc".format(
        name, num, price)
    cur.execute(code)
    data = []
    title = ['商品名', '编号', '价格/元', '数量/个']
    data.append("%-25s%-25s%-25s%-25s" % (title[0], title[1], title[2], title[3]))
    ans = cur.fetchall()
    for item in ans:
        tmp_item = ""
        for i in item:
            tmp_item += str(i) + " " * (25 - len(str(i)))
        data.append(tmp_item)
    return data


# 获取所有库存信息
def get_all_stock_info():
    code = "select name, id, price,sum from  stock order by id asc "
    cur.execute(code)
    data = []
    title = ['商品名', '编号', '价格/元', '数量/个']
    data.append("%-25s%-25s%-25s%-25s" % (title[0], title[1], title[2], title[3]))
    ans = cur.fetchall()
    for item in ans:
        tmp_item = ""
        for i in item:
            tmp_item += str(i) + " " * (25 - len(str(i)))
        data.append(tmp_item)
    return data


"""
    结算管理
"""


# 获取管理员name_id
def get_user_name_id():
    code = "select name, id  from users"
    cur.execute(code)
    data = []
    cur_data = cur.fetchall()
    for item in cur_data:
        data.append(str(item[0]) + "__" + str(item[1]))
    return data


# 获取流水账单或者购货账单
def find_running_or_purchase(type, start_time, end_time, user_id):
    data = []
    if type == "购货账目":
        data.append(" " * 10 + "购货账目")
        code = "select id, name, shop ,state from purchase where id>='{}_0000' and  id<='{}_9999' and user_id like '%{}%' ".format(
            start_time, end_time, user_id)
    else:
        data.append(" " * 10 + "零售账目")
        code = "select running.id, stock.name, running.num, running.time from running, stock where  running.stock_id=stock.id and running.id>='{}_0000' and  running.id<='{}_9999' and running.user_id like '%{}%'  ".format(
            start_time, end_time, user_id)

    # print(code)
    if cur.execute(code):
        cur_data = cur.fetchall()
        for item in cur_data:
            tmp = ""
            for i in item:
                tmp += str(i) + "  "
            data.append(tmp)
    return data


# 查看查询数据的详细信息
def get_detailed_info(type, id):
    print(type, id)
    data = ""
    if type == "购货账目":
        title = ['购物编号：', '商品名：', '订单数量：', '单价：', '状态：', '供货商：', '联系方式：', '操作员：']
        code = "select p.id, p.name,p.num, p.price,p.state, p.shop,p.phone,u.name  from purchase p,users u where p.id='{}' and  p.user_id=u.id ".format(
            id)

    else:
        title = ['流水编号：', '商品名：', '销售数量：', '价格：', '结单时间：', '操作员：']
        code = "select r.id, s.name, r.num,r.account, r.time, u.name from running r, stock s, users u where r.id='{}' and s.id=r.stock_id and u.id=r.user_id".format(
            id)
    cur.execute(code)
    cur_data = cur.fetchall()[0]
    for index in range(len(title)):
        data += str(title[index]) + str(cur_data[index]) + "\n"
    return data


"""
    管理员
"""


# 添加账号
def add_user(name, id, pw, grade):
    code = " insert into users(name, id, pw, grade) values('{}','{}','{}','{}')".format(name, id, pw, grade)
    try:
        cur.execute(code)
        return True
    except Exception:
        return False


# 删除账号
def del_user(id):
    code = "delete from  users where id='{}'".format(id)
    cur.execute(code)


# 获取管理员信息
def get_user_info():
    code = "select name,id,pw,grade from users "
    cur.execute(code)
    data = []
    cur_data = cur.fetchall()

    for item in cur_data:
        tmp_code = "{}  {}  p:{}  {}".format(str(item[0]), str(item[1]), str(item[2]), str(item[3]))
        data.append(tmp_code)
    return data


# 修改用户信息
def update_user_info(id, name, pw, grade):
    code = "update users set name='{}',pw='{}',grade='{}'  where id='{}' ".format(name, pw, grade, id)
    cur.execute(code)


# 管理员登录
def manger_sign(user_id, user_pw):
    code = "select name from users where id='{}' and pw='{}' and grade='管理员'".format( user_id, user_pw)
    if cur.execute(code):
        return True, cur.fetchall()[0][0]
    return False, ""