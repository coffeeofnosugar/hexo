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

##### 定义表结构

在创建表的时候可以，定义列名、列的<a href="./#数据类型">数据类型</a>和<a href="./#默认值">默认值</a>

```mysql
CREATE TABLE player (
	id INT NOT NULL,			-- 列名为id，数据类型为INT，并且不能为NULL
    name VARCHAR(100) UNIQUE,	-- 长度为100的变长字符串这个字段必须为唯一值
    level INT DEFAULT 1,  		-- 列名为level，数据类型为INT，默认值为1
    exp INT,
    gold DECIMAL(10,2)			-- 长度为10，并且保留两位小数的十进制数
);
```

##### 修改表结构

```mysql
-- 添加列
ALTER TABLE <table_name> ADD <col> <value_type>;
-- 删除列
ALTER TABLE <table_name> DROP <col>;
```

```mysql
-- 将player表的level列的数据类型设置为INT，默认值设置为1
ALTER TABLE player MODIFY level INT DEFAULT 1;
```

| 语法                                                         | 解释                           |
| ------------------------------------------------------------ | ------------------------------ |
| `ALTER TABLE <table_name> MODIFY <col> <value_type> DEFAULT <value>;` | 设置默认值为\<value>           |
| `ALTER TABLE <table_name> MODIFY <col> <value_type> [NOT] NULL;` | 设置[不]可以为NULL             |
| `ALTER TABLE <table_name> ADD UNIQUE (<col>);`               | 设置为唯一性，**需要使用括号** |
| `ALTER TABLE <table_name> MODIFT <col> <value_type> PRIMARY KEY;` | 设置为主键，唯一且不为空       |
| `ALTER TABLE <child_table> ADD FOREIGN KEY (<child_col>) REFERENCES <parent_table> (parent_col);` | 设置从键                       |

`<child_table>`是从表

`<child_col>`是从表中的外键列

`<parent_table>`是主表

`<parent_col>`是主表中的主键列

#### 数据的增删改

##### 增

```mysql
-- 在<table_name>表中插入<col1>为<value1>,<col2>为<value2>,<col3>为<value3>的数据
INSERT INTO <table_name> (<col1>, <col2>, <col3>) VALUES (<value1>, <value2>, <value3>);
```

当`VALUES`后面的数据与列的个数对应，则可以不用写列

e.g. `INSERT INTO player (id, name, level) VALUES (1, '张三', 10);`可以写成 `INSERT INTO player VALUES (1, '张三', 10);`

也可以只使用部分列，没有使用的列将使用默认值

e.g. `INSERT INTO player (id, name) VALUES (2, '李四');`没有被定义的`level`将以默认值代替

也可以同时插入多条数据

e.g. `INSERT INTO player (id, name) VALUES (3, '王五'), (4, '赵六');`

##### 删

```mysql
-- 删除<table_name>表中所有<col>列为<value>的数据
DELETE FROM <table_name> WHERE <col>=<value>;
```

e.g. `DELETE FROM test;`删除test表中所有的数据

##### 改

```mysql
-- 将<tablue_name>表的<col2>列为<value2>数据的<col1>赋值为<value1>
UPDATE <table_name> SET <col1> = <value1> WHERE <col2> = <value2>;
```

e.g. `UPDATE player SET level = 1 WHERE name = '李四';`将李四的等级修改为1

不加`WHERE`限制范围就是对所有的数据修改，多个设置可以使用`,`隔开

e.g. `UPDATE player SET level=1, exp=0;`将所有玩家的等级修改为1，经验修改为0



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

#### 聚合函数

聚合函数对某列执行一些计算，比如返回项目`COUNT()`，求和`SUN()`、平均`AVG()`、最大值`MAX()`、最小值`MIN()`等

```mysql
-- 返回所有玩家的总人数
SELECT COUNT(*) FROM player
-- 返回等级的平均值
SELECT AVG(level) FROM player
```

`GROUP BY`分组语法

待续

---



### 数据导入和导出

#### 导出

在MySQL-Shell中使用命令

```mysql
# -u指定用户，-p后续输入密码，game > game.sql将数据库game导出到game.sql文件中
mysqldump -u root -p game > game.sql
# 将game数据库的player表导出到player.sql中
mysqldump -u root -o game player > player.sql
```

#### 导入

在Shell中使用命令

```shell
# 将game.sql的数据导入到game数据库中
mysql -u root -p game < game.sql
```







---

### 数据类型

#### 数值类型

| 数据类型     | 大小                                     | 范围(有符号)                                                 | 范围(无符号)                                                 | 用途            |
| ------------ | ---------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | --------------- |
| TINYINT      | 1 Bytes                                  | (-128，127)                                                  | (0，255)                                                     | 小整数值        |
| SMALLINT     | 2 Bytes                                  | (-32,768，32,767)                                            | (0，65 535)                                                  | 大整数值        |
| MEDIUMINT    | 3 Bytes                                  | (-8,388,608，8 388,607)                                      | (0，16 777 215)                                              | 大整数值        |
| INT或INTEGER | 4 Bytes                                  | (-2,147,483,648，2,147,483,647)                              | (0，4 294 967 295)                                           | 大整数值        |
| BIGINT       | 8 Bytes                                  | (-9,223,372,036,854,775,808，9,223,372,036,854,775,807)      | (0，18 446 744 073 709 551 615)                              | 极大整数值      |
| FLOAT        | 4 Bytes                                  | (-3.402 823 466 E+38，-1.175 494 351 E-38)，0，(1.175 494 351 E-38，3.402 823 466 351 E+38) | 0，(1.175 494 351 E-38，3.402 823 466 E+38)                  | 单精度 浮点数值 |
| DOUBLE       | 8 Bytes                                  | (-1.797 693 134 862 315 7 E+308，-2.225 073 858 507 201 4 E-308)，0，(2.225 073 858 507 201 4 E-308，1.797 693 134 862 315 7 E+308) | 0，(2.225 073 858 507 201 4 E-308，1.797 693 134 862 315 7 E+308) | 双精度 浮点数值 |
| DECIMAL      | 对DECIMAL(M,D) ，如果M>D，为M+2否则为D+2 | 依赖于M和D的值                                               | 依赖于M和D的值                                               | 小数值          |





