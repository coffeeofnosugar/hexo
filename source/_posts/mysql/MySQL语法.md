---
title: 【MySQL】MySQL语法
date: 2023-08-29 20:50:06
tags: MySQL
---

### MySQL客户端

- 如果安装了MySQL-Shell可以直接使用`mysqlsh`进入MySQL-Shell客户端
- 也可以使用`mysql -u root -p`来进入MySQL客户端

#### 数据库语法

| 语法                               | 解释           |
| ---------------------------------- | -------------- |
| `SHOW DATABASES;`                  | 展示所有数据库 |
| `CREATE DATABASE <database_name>;` | 创建数据库     |
| `DROP DATABASE <database_name>;`   | 删除数据库     |
| `USE <database_name>;`             | 选择数据库     |

#### 表语法

| 语法                                        | 解释       |
| ------------------------------------------- | ---------- |
| `SHOW TABLES;`                              | 展示所有表 |
| `CREATE TABLE <table_name> <表的结构定义>;` | 创建表     |
| `DROP TABLE <table_name>;`                  | 删除表     |

##### `<表的结构定义>`语法

在创建表的时候可以，定义列名和列的格式

```mysql
CREATE TABLE player (
	id INT,					-- 列名为id，格式为INT
    name VARCHAR(100),		-- 长度为100的变长字符串
    level INT,
    exp INT,
    gold DECIMAL(10,2)		-- 长度为10，并且保留两位小数的十进制数
);
```







#### 数据的增删改

#### 增

```mysql
INSERT INTO <table_name> (<col1>, <col2>, <col3>) VALUES (<value1>, <value2>, <value3>);
```

当`VALUES`后面的数据与列的个数对应，则可以不用写列，e.g. `INSERT INTO <table_name> VALUES (v1, v2, v3);`

也可以只使用部分列，没有使用的列使用默认值，e.g. `INSERT INTO <table_name> (col1, col2) VALUES (v1, v2);`



---

### 查询语句

| 语法                                                | 解释                                 |
| --------------------------------------------------- | ------------------------------------ |
| `SELECT <col> FROM <table>;`                        | 显示`<table>`表中的`<col>`列中的数据 |
| `SELECT <col> FROM <table> WHERE <condition>;`      | 显示`<col>`中符合`<condition>`的数据 |
| `SELECT <col> FROM <table> ORDER BY <col> ASC\|DESC;` | 按照排序显示查询数据                 |

#### `WHERE <condition>`限制查询目标语法

- 可以使用<,>,=
- 多个条件可以使用`AND`和`OR`连接(需要注意优先级`AND`优先于`OR`，还可以使用括号改变优先顺序)
- 使用`IN`限制范围，e.g. `WHERE level IN (1, 3, 5)`限制条件为：等级等于1,3,5
- 使用`WHERE BETWEEN <num1> AND <num2>`限制范围，e.g. `WHERE level BETWEEN 1 AND 10`：等级在1到10之间(包括1和10)，等价于`WHERE level >= 1 AND level <= 10`
- 使用`NOT`取反
- 使用`LINK`关键字(简化版的正则表达式)：`WHERE name LINK '王%'`，查找所有姓王的玩家，`%`可以代替多个字符，`_`代替一个字符
- 使用`REGEXP`关键字(正则表达式)

> **注意事项**
>
> 数据库中`null` "空"不等于`""` "空字符串"
>
> - 查找`null` ''空''：`WHERE email is null`
> - 查找`""` "空字符串"：`WHERE email = ''`

#### `ORDER BY <col> ASC|DESC`排序语法

- `ASC`升序，默认就是升序，可省略不写
- `DESC`降序

e.g. `ORDER BY level DES, exp ASC`等级降序，经验升序

### 聚合函数

聚合函数对某列执行一些计算，比如返回项目`COUNT()`，求和`SUN()`、平均`AVG()`、最大值`MAX()`、最小值`MIN()`等

```mysql
-- 返回所有玩家的总人数
SELECT COUNT(*) FROM player
-- 返回等级的平均值
SELECT AVG(level) FROM player
```

`GROUP BY`分组语法

待续
