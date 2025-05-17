'''
    设置
        1、数据库信息  set{}
        2、用户信息（ 当前登录 ） user{}
        3、设置数据库：
            （1）未设置， 设置；
            （2）已设置， 跳过。
        4、连接数据库  mysql_conn
        5、利润设置    profit
'''

import pymysql

# -*- coding: UTF-8 -*-

# 利润设置
profit = 0.1

# 数据库设置
set = dict()
set = {"init": "true",
       "host": "localhost",
       "user": "root",
       "password": "Tt87094938",
       "database": "warehouse"
       }

# 当前登录用户
user = {
    "name": "tang",
    "id": "1001"
}

# 管理员是否登录
manger_signing = True


def read_con():
    with open("option.config", "r") as f:
        ret = eval(f.read())

    for item in ret:
        set[item] = ret[item]


def init_database():
    conn = pymysql.connect(host='localhost', user='root', password='Tt87094938')
    cursor = conn.cursor()
    # 创建数据库
    try:
        cursor.execute("create  database warehouse")
        set["database"] = "warehouse"
    except Exception as e:
        print("数据库:", e)
    cursor.close()
    conn.close()

    # 重新连接数据库
    conn = pymysql.connect(host='localhost', user='root', password='Tt87094938')
    cursor = conn.cursor()

    # 创建用户表
    # # 用户：        user: {user_name,id, password, reg_time}
    try:
        cursor.execute("""
                     create table users ( 
                     name varchar(20), 
                     id varchar(20) primary key,
                     pw varchar(20), 
                     grade varchar(20) check( grade in ('管理员','普通操作员')),
                     seg timestamp )
                    """)
    except Exception as e:
        print("用户表：", e)

    # 添加管理员账号
    # # 账号： root ， 密码： toor
    try:
        code = "insert into  users(name,id,pw,grade) values('终极Boss','root','toor','管理员')"
        cursor.execute(code)
    except Exception as e:
        print("操作员: ", e)

    # 创建购货表
    #  # 采购--进货：   purchase: {id,  name, price,  num, statu(定、收、退), shop，phone ，user_id}
    try:
        cursor.execute("""
            create table purchase(
                id      varchar(20) primary key,
                name    varchar(20),
                price   double,
                num     int,
                state   varchar(15) check( state in('定货','收货','退货') ),
                shop    varchar(20),
                phone   varchar(20),
                user_id varchar(20) )
            """)
    except  Exception as e:
        print("购货表： ", e)

    # 库存：
    #  # stock： {id, sum,  price, name, }
    try:
        cursor.execute("""
                    create  table stock(
                        id      varchar(20)  primary key,
                        sum     int,
                        price   double,
                        name    varchar(20)
                    )
                    """)
    except  Exception as e:
        print("库存表: ", e)

    # 账目表
    #  # 流水账--卖出：  runuing: {id, stock_id, num, account, time,  user}

    try:
        cursor.execute("""
                    create  table running(
                        id  varchar(20)  primary key,
                        stock_id varchar(20),
                        num  int,
                        account  double,
                        time timestamp,
                        user_id varchar(20) 
                    )
                    """)
    except Exception as e:
        print("账目表： ", e)

    cursor.close()
    conn.close()


def main():
    read_con()
    if set["init"] == "False":
        init_database()
        set["init"] = "true"
        with  open("option.config", "w") as f:
            f.write(str(set))

    return pymysql.connect(host='localhost', user='root', password='Tt87094938')


# 数据库连接
mysql_conn = main()


if __name__ == "__main__":
    conn = main().cursor()
    conn.close()
