from extention import db

# 创建中间表
user_role = db.Table(
    "rt_user_role",  # 中间表名称
    db.Column("id", db.Integer, primary_key=True, autoincrement=True, comment='标识'),  # 主键
    db.Column("user_id", db.Integer, db.ForeignKey("cp_user.id"), comment='用户编号'),  # 属性 外键
    db.Column("role_id", db.Integer, db.ForeignKey("rt_role.id"), comment='角色编号'),  # 属性 外键
)

# 创建中间表
role_power = db.Table(
    "rt_role_power",  # 中间表名称
    db.Column("id", db.Integer, primary_key=True, autoincrement=True, comment='标识'),  # 主键
    db.Column("power_id", db.Integer, db.ForeignKey("rt_power.id"), comment='用户编号'),  # 属性 外键
    db.Column("role_id", db.Integer, db.ForeignKey("rt_role.id"), comment='角色编号'),  # 属性 外键
)


class UserModel(db.Model):
    __tablename__ = 'cp_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120))
    password = db.Column(db.String(128))

    role = db.relationship('RoleModel',
                           secondary="rt_user_role",
                           backref=db.backref('user'),
                           lazy='dynamic')


class RoleModel(db.Model):
    __tablename__ = 'rt_role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, comment='角色名称')
    code = db.Column(db.String(64), unique=True, comment='角色标识')

    power = db.relationship('PowerModel', secondary="rt_role_power", backref=db.backref('role'))


class PowerModel(db.Model):
    __tablename__ = 'rt_power'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(64), unique=True, comment='权限路径')
    code = db.Column(db.String(64), comment='权限标识')

    parent_id = db.Column(db.Integer, db.ForeignKey("rt_power.id"), comment='父类编号')
    parent = db.relationship("PowerModel", remote_side=[id])  # 自关联
