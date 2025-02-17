# @Version  : 1.0
# @Author   : 胡浩宇
# 校园出入登记管理系统
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from dao.dao_SQL import *
from math import ceil
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于session加密和flash消息
app.config['JSON_AS_ASCII'] = False  # 支持中文JSON响应
conn = connected_database('campus_access_log')

# 登录检查装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('请先登录后再访问！', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def base():
    return render_template("home.html")

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login_post():
    """处理用户登录请求
    获取表单中的学号和密码，验证用户身份

    Returns:
        验证成功：重定向到用户主页
        验证失败：重定向回登录页面并显示错误信息
    """
    account = request.form['account']  # 获取学号
    password = request.form['password']  # 获取密码

    # 查询用户信息
    query = select('users', account=account, password=password)
    result = con_my_sql(query, conn).fetchone()

    # 验证用户身份
    if result:
        if result['account'] == account and result['password'] == password:
            session['username'] = result['username']  # 保存用户信息到session
            session['account'] = result['account']
            return redirect(url_for('base'))
    flash('用户名或密码错误！')
    return redirect(url_for('login'))


@app.route('/register', methods=['POST'])
def register_post():
    """处理用户注册请求
    获取用户提交的注册信息，存入数据库

    Returns:
        注册成功：重定向到登录页面
        注册失败：显示错误信息并重定向回注册页面
    """
    # 获取注册表单数据
    username = request.form['username']  # 用户名
    password = request.form['password']  # 密码
    account = request.form['account']  # 学号

    # 插入新用户数据
    insert_query = insert('users',
                          username=username, password=password,
                          account=account)
    result = con_my_sql(insert_query, conn)

    # 处理注册结果
    if result is None:
        flash('用户名已存在，注册失败: ')
    else:
        flash('注册成功！请登录。')

    return redirect(url_for('login'))

@app.route('/checkin')
@login_required
def checkin():
    return render_template('checkin.html')

@app.route('/checkin', methods=['POST'])
def checkin_post():
    name = request.form['name']
    college = request.form['college']
    student_id = request.form['student_id']
    phone = request.form['phone']
    counselor_name = request.form['counselor_name']
    remark = request.form['remark']

    insert_query = insert('student_checkin',
                          name=name, college=college,
                          student_id=student_id, phone=phone,
                          counselor_name=counselor_name,
                          remark=remark)
    result = con_my_sql(insert_query, conn)
    if result is None:
        flash('登记失败！')
    else:
        flash('登记成功！')
    return redirect(url_for('checkin'))

@app.route('/statistics')
@login_required
def statistics():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 每页显示10条记录
    
    # 获取总记录数
    count_query = "SELECT COUNT(*) as count FROM student_checkin"
    total_count = con_my_sql(count_query, conn).fetchone()['count']
    
    # 计算总页数
    total_pages = ceil(total_count / per_page)
    
    # 获取分页数据
    offset = (page - 1) * per_page
    query = f"""
        SELECT * FROM student_checkin 
        ORDER BY checkin_time DESC 
        LIMIT {per_page} OFFSET {offset}
    """
    records = con_my_sql(query, conn).fetchall()
    
    return render_template('statistics.html', 
                         records=records,
                         page=page, 
                         per_page=per_page,
                         total_pages=total_pages)

@app.route('/checkin_management')
@login_required
def checkin_management():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 获取总记录数
    count_query = "SELECT COUNT(*) as count FROM student_checkin"
    total_count = con_my_sql(count_query, conn).fetchone()['count']
    
    # 计算总页数
    total_pages = ceil(total_count / per_page)
    
    # 获取分页数据
    offset = (page - 1) * per_page
    query = f"""
        SELECT * FROM student_checkin 
        ORDER BY checkin_time DESC 
        LIMIT {per_page} OFFSET {offset}
    """
    records = con_my_sql(query, conn).fetchall()
    
    return render_template('checkin_management.html', 
                         records=records,
                         page=page, 
                         per_page=per_page,
                         total_pages=total_pages)

@app.route('/checkin/edit', methods=['POST'])
def edit_checkin():
    record_id = request.form['id']
    name = request.form['name']
    college = request.form['college']
    student_id = request.form['student_id']
    phone = request.form['phone']
    counselor_name = request.form['counselor_name']
    remark = request.form['remark']
    
    update_query = f"""
        UPDATE student_checkin 
        SET name = '{name}', 
            college = '{college}',
            student_id = '{student_id}',
            phone = '{phone}',
            counselor_name = '{counselor_name}',
            remark = '{remark}'
        WHERE id = {record_id}
    """
    try:
        con_my_sql(update_query, conn)
        flash('信息更新成功！')
    except Exception as e:
        flash('更新失败：' + str(e))
    
    return redirect(url_for('checkin_management'))

@app.route('/checkin/delete/<int:record_id>', methods=['DELETE'])
def delete_checkin(record_id):
    delete_query = f"DELETE FROM student_checkin WHERE id = {record_id}"
    try:
        con_my_sql(delete_query, conn)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/logout')
def logout():
    session.clear()  # 清除所有session数据
    return redirect(url_for('base'))

if __name__=='__main__':
    app.run(debug=True)