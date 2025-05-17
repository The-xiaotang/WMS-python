-- 创建用户表
CREATE TABLE users (
    name VARCHAR(20), 
    id VARCHAR(20) PRIMARY KEY,
    pw VARCHAR(20), 
    grade VARCHAR(20) CHECK (grade IN ('管理员', '普通操作员')),
    seg TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入管理员用户
INSERT INTO users (name, id, pw, grade) 
VALUES ('终极Boss', 'root', 'toor', '管理员');

-- 创建采购表
CREATE TABLE purchase (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(20),
    price DOUBLE,
    num INT,
    state VARCHAR(15) CHECK (state IN ('定货', '收货', '退货')),
    shop VARCHAR(20),
    phone VARCHAR(20),
    user_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建库存表
CREATE TABLE stock (
    id VARCHAR(20) PRIMARY KEY,
    sum INT,
    price DOUBLE,
    name VARCHAR(20)
);

-- 创建流水表
CREATE TABLE running (
    id VARCHAR(20) PRIMARY KEY,
    stock_id VARCHAR(20) NOT NULL,
    num INT,
    account DOUBLE,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (stock_id) REFERENCES stock(id)
);