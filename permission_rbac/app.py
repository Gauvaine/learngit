from flask import Flask, request, redirect, url_for
from flask import render_template, session
from auth_decorator import permission_required, login_required, role_required, admin_required
from utils import permission

from extention import migrate
from extention import db
from models import UserModel, RoleModel


class Config:
    # 数据库链接配置参数
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask('permission_acl')
app.secret_key = '123456'
app.config.from_object(Config)

db.init_app(app)
# 挂在登录与退出管理
migrate.init_app(app, db)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.json.get('username')
        password = request.json.get('password')
        print(username, password)
        user = UserModel()
        user.username = username
        user.password = password
        db.session.add(user)
        user.role.append(RoleModel.query.get(1))
        db.session.commit()
        return {'status': 'success', 'message': '注册成功,接下来就可以去登录了', 'next': '/login'}
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.json.get('username')
        password = request.json.get('password')
        user = UserModel.query.filter(UserModel.username == username).first()
        session['_user_id'] = user.id
        session['permission'] = ':'.join([power.code for role in user.role for power in role.power])
        return {'status': 'success', 'next': '/home', 'message': '登录账号成功'}
    return render_template('login.html')


@app.route("/logout")
def logout():
    session['_user_id'] = ''
    session['permission'] = ''
    return redirect('/')


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/auth/read')
@login_required
@permission_required('read')
def read():
    return render_template('auth/read.html')


@app.route('/auth/commit')
@login_required
@permission_required('commit')
def commit():
    return render_template('auth/commit.html')


@app.route('/auth/write')
@login_required
@permission_required('write')
def write():
    return render_template('auth/write.html')


@app.route("/admin")
@login_required
@role_required('level3')
# @admin_required
def admin():
    return render_template('admin.html')


@app.cli.command()
def create():
    db.drop_all()
    db.create_all()
    import models

    user = models.UserModel()
    user.username = 'zhengxin'
    user.password = '123456'
    db.session.add(user)
    roles = [
        {'name': '普通用户', 'code': 'level1'},
        {'name': '会员用户', 'code': 'level2'},
        {'name': '管理员用户', 'code': 'level3'},
    ]
    role1 = models.RoleModel(name=roles[0]['name'], code=roles[0]['code'])
    role2 = models.RoleModel(name=roles[1]['name'], code=roles[1]['code'])
    role3 = models.RoleModel(name=roles[2]['name'], code=roles[2]['code'])
    db.session.add(role1)
    db.session.add(role2)
    db.session.add(role3)
    _permission = {
        'read': '/auth/read',
        'commit': '/auth/comment',
        'write': '/auth/write',
        'admin': '/admin',
    }
    power1 = models.PowerModel(code='read', url=_permission['read'])
    power2 = models.PowerModel(code='commit', url=_permission['commit'])
    power3 = models.PowerModel(code='write', url=_permission['write'])
    power4 = models.PowerModel(code='admin', url=_permission['admin'])
    db.session.add(power1)
    db.session.add(power2)
    db.session.add(power3)
    db.session.add(power4)

    role1.power.append(power1)
    role1.power.append(power2)

    role2.power.append(power1)
    role2.power.append(power2)
    role2.power.append(power3)

    role3.power.append(power4)

    user.role.append(role1)
    print(user)

    print([power.code for role in user.role for power in role.power])
    db.session.commit()
