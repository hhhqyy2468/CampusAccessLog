# @Author   : 胡浩宇
import pymysql

def con_my_sql(sql_code, conn):
    """
    执行传入的 SQL 语句，并确保与 MySQL 数据库的连接正常
    :param sql_code: 要执行的 SQL 语句
    :param conn: 数据库连接对象
    :return: 执行结果或错误信息
    """
    try:
        conn.ping(reconnect=True)  # 保证数据库正常连接
        print(sql_code)
        # 确保游标对象对数据库服务器发送sql语句
        cursor = conn.cursor(pymysql.cursors.DictCursor)  # 返回数据格式位字典
        cursor.execute(sql_code)
        # 提交
        conn.commit()
        # 关闭
        conn.close()
        return cursor  # 普通执行返回1 就是执行成功

    except pymysql.MySQLError as err_massage:

        # 回滚
        conn.rollback()
        # 关闭连接
        return None

def update(table_name, fields, condition):
    """
    UPDATE table_name
    SET column1 = value1, column2 = value2, ...
    WHERE condition;
    :return:
    """
    set_clause = ', '.join(f"{key}='{value}'" for key, value in fields.items())
    return f"UPDATE {table_name} SET {set_clause} WHERE {condition};"

def insert(table_name, **fields):
    """
    生成 MySQL 插入语句
    :param table_name: 表名
    :param fields: 字段名及其对应的值
    :return: MySQL 插入语句
    """
    columns = ', '.join(fields.keys())
    values = ', '.join(f"'{value}'" for value in fields.values())
    return f"INSERT INTO {table_name} ({columns}) VALUES ({values});"

def select(table_name, **conditions):
    """
    生成 MySQL 查询语句
    :param table_name: 表名
    :param conditions: 查询条件
    :return: MySQL 查询语句
    """
    query = f"SELECT * FROM {table_name}"
    if conditions:
        condition_str = ' AND '
        .join(f"{key}='{value}'" for key, value in conditions.items())
        query += f" WHERE {condition_str}"
    return query

def connected_database(database):
    """
    :param database: 数据库名字
    :return:连接对象
    """
    conn = pymysql.connect(host='localhost', port=3306,
                           user='root', passwd='123456',
                           db=database, charset='utf8')
    return conn
