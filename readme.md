## 2-3 新建入口文件

关于flask核心对象操作都会注册到app.py中

app.py 

    from flask import Flask


    def create_app():
        app = Flask(__name__)
        app.config.from_object('app.config.setting')
        app.config.from_object('app.config.setting')
        return app
        
ginger.py

    from app.app import create_app
    
    
    app = create_app()
    
    
    if __name__ == '__main__':
        app.run(debug=True)

## 2-4 蓝图分离视图函数的缺陷

如果把视图函数写在入口文件是不可取的

创建一个 v1 项目目录

user.by

    from flask import Blueprint
    
    user = Blueprint('user', __name__)
    
    @user.route('/v1/user/get')
    def get_user():
        return "i am qiye"
        
我们已经把视图注册到了蓝图上，下面将蓝图注册到flask的核心对象上

app.py

    from flask import Flask
    
    def register_blueprints(app):
        from app.api.v1.user import user
        from app.api.v1.book import book
        app.register_blueprint(user)
        app.register_blueprint(book)
    
    
    def create_app():
        app = Flask(__name__)
        app.config.from_object('app.config.setting')
        app.config.from_object('app.config.setting')
        register_blueprints(app)
        return app

但是蓝图的作用是模块级别的拆分，不是视图函数级别的拆分

## 2-5 打开思维，创建自己的Redprint——红图

user.py

    from app.libs.redprint import Redprint
    
    api = Redprint('book')
    
    
    @api.route('/v1/user/get')
    def get_user():
        return "i am qiye"
        
将红图注册到蓝图上

__init__.py

    from flask import Blueprint
    from app.api.v1 import user, book
    
    
    def create_blueprint():
        bp_v1 = Blueprint('v1', __name__)
        
        user.api.register(bp_v1)
        book.api.register(bp_v1)
        
        return bp_v1

将蓝图注册的核心对象上

app.py

    from flask import Flask
    
    
    def register_blueprints(app):
        from app.api.v1 import create_blueprint_v1
        app.register_blueprint(create_blueprint_v1())    
    
    def create_app():
        app = Flask(__name__)
        app.config.from_object('app.config.setting')
        app.config.from_object('app.config.setting')
        register_blueprints(app)
        return app
        
在试图路由上每次都要重复写入 v1/xxx flask 给我们提供了一个参数 url_prefix

    def register_blueprints(app):
        from app.api.v1 import create_blueprint_v1
        app.register_blueprint(create_blueprint_v1(), url_prefix='/v1')
        
    from flask import Blueprint
    from app.api.v1 import user, book
    
    
    def create_blueprint_v1():
        bp_v1 = Blueprint('v1', __name__)
    
        user.api.register(bp_v1, url_prefix='/user')
        book.api.register(bp_v1, url_prefix='/book')
    
        return bp_v1

## 2-6 实现Redprint

将红图注册到蓝图上

redprint.py

    class Redprint(object):
        
        def __init__(self, name):
            self.name = name
            self.mound = []
            
        def route(self, rule, **options):
            
            def decorator(f):
                self.mound.append((f, rule, options))
                return f
            
            return decorator
        
        def register(self, bp, url_prefix=None):
            for f, rule, options in self.mound:
                endpoint = options.pop("endpoint", f.__name__)
                bp.add_url_rule(url_prefix + rule, endpoint, f, **options)

## 2-7 优化Redprint

将红图注册蓝图的时候需要 url_prefix 优化一下成默认的

redprint.py

	def register(self, bp, url_prefix=None):
		if url_prefix is None:
			url_prefix = '/' + self.name
		for f, rule, options in self.mound:
			endpoint = options.pop("endpoint", f.__name__)
			bp.add_url_rule(url_prefix + rule, endpoint, f, **options)
			
# 第4章 自定义异常对象

## 4-1 关于“用户”的思考

客户端注册 client 

## 4-2 构建Client验证器

client.py

    from app.libs.redprint import Redprint
    
    api = Redprint('client')
    
    
    @api.route('/register')
    def create_client():
        pass
        
enums.py

    from enum import Enum
    
    class ClientTypeEnum(Enum):
        USER_EMAIL = 100
        USER_MOBILE = 101
        
        USER_MINA = 200
        USER_WX = 201

forms.py

    from wtforms import Form, StringField, IntegerField
    from wtforms.validators import DataRequired, length
    from app.libs.enums import ClientTypeEnum
    
    
    class ClientForm(Form):
        account = StringField(validators=[DataRequired(),
                                          length(max=32, min=5)])
        secret = StringField(validators=[DataRequired()])
        type = IntegerField(validators=[DataRequired()])
        
        def validate_type(self, value):
            try:
                client = ClientTypeEnum(value.data)
            except ValueError as e:
                raise e

## 4-3 处理不同客户端注册的方案

上面构建了验证器,这里使用验证器

client.py

    from app.libs.redprint import Redprint
    from app.validators.forms import ClientForm
    from flask import request, json
    from app.libs.enums import ClientTypeEnum
    
    api = Redprint('client')
    
    
    @api.route('/register', methods=['POST'])
    def create_client():
        data = request.json
        form = ClientForm(data=data)
        if form.validate():
            promise = {
                ClientTypeEnum.USER_EMAIL: __register_by_email,
            }
            
    
    def __register_by_email():
        pass
        
## 4-4 创建User模型

创建 models 文件夹 user.py 模型类

    from sqlalchemy import Column, Integer, String, SmallInteger
    from werkzeug.security import generate_password_hash
    from app.models.base import Base, db
    
    
    class User(Base):
        id = Column(Integer, primary_key=True)
        email = Column(String(24), unique=True, nullable=False)
        nickname = CValidationError()olumn(String(24), unique=True)
        auth = Column(SmallInteger, default=1)
        _password = Column('password', String(128))
    
        @property
        def password(self):
            return self._password
    
        @password.setter
        def password(self, raw):
            self._password = generate_password_hash(raw)
    
        @staticmethod
        def register_by_email(nickname, account, secret):
            with db.auto_commit():
                user = User()
                user.nickname = nickname
                user.email = account
                user.password = secret
                db.session.add(user)

base.py 模型基类

    from datetime import datetime
    from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
    from sqlalchemy import Column, Integer, SmallInteger
    from contextlib import contextmanager
    
    
    class SQLAlchemy(_SQLAlchemy):
        @contextmanager
        def auto_commit(self):
            try:
                yield
                self.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
    
    
    class Query(BaseQuery):
        def filter_by(self, **kwargs):
            if 'status' not in kwargs.keys():
                kwargs['status'] = 1
            return super(Query, self).filter_by(**kwargs)
    
    
    db = SQLAlchemy(query_class=Query)
    
    
    class Base(db.Model):
        __abstract__ = True
        create_time = Column(Integer)
        status = Column(SmallInteger, default=1)
    
        def __init__(self):
            self.create_time = int(datetime.now().timestamp())
    
        @property
        def create_datetime(self):
            if self.create_time:
                return datetime.fromtimestamp(self.create_time)
            else:
                return None
    
        def set_attrs(self, attrs_dict):
            for key, value in attrs_dict.items():
                if hasattr(self, key) and key != 'id':
                    setattr(self, key, value)
    
        def delete(self):
            self.status = 0

给模型添加一个注册的功能

	@staticmethod
	def register_by_email(nickname, account, secret):
		with db.auto_commit():
			user = User()
			user.nickname = nickname
			user.email = account
			user.password = secret
			db.session.add(user)
		
这里 User() 是类本身,在对象里面创建一个对象本身是不合理的,如果是静态方法就没有问题.

    @staticmethod
    
要让 flask_sqlalchemy 生效就必须注册插件 app.py

    def register_plugin(app):
        from app.models.base import db
        db.init_app(app)
        with app.app_context():
            db.create_all()
    
    
    def create_app():
        app = Flask(__name__)
        app.config.from_object('app.config.setting')
        app.config.from_object('app.config.setting')
        register_blueprints(app)
        register_plugin(app)
        return app
        
## 4-5 完成客户端注册

我们定义的 ClientForm 是通用的form,需要满足个性化就继承 ClientForm.

    class UserEmailForm(ClientForm):
        account = StringField(validators=[
            Email(message='invalidate email')
        ])
        secret = StringField(validators=[
            DataRequired(),
            # 密码只能包含字母，数字和“ _”
            Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}$')
        ])
        nickname = StringField(validators=[DataRequired(),
                                           length(min=2, max=22)])
    
        def validate_account(self, value):
            if User.query.filter_by(email=value.data).first():
                raise ValidationError()
                
这里做一次 validate_account 数据库验证,如果email已经存在就抛出异常 

    ValidationError()
    
wtforms 内置异常 ValidationError

回到 api 中去实现 UserEmail 注册

    def __register_user_by_email():
        form = UserEmailForm(data=request.json)
        User.register_by_email(form.nickname.data,
                               form.account.data,
                               form.secret.data)

通过 create_client 调用 UserEmail 注册, ClientTypeEnum.USER_EMAIL 是健(枚举类型)

    promise = {
        ClientTypeEnum.USER_EMAIL: __register_user_by_email,
    }

form 中返回 type

	def validate_type(self, value):
		try:
			client = ClientTypeEnum(value.data)
		except ValueError as e:
			raise e

		self.type.data = client
	
实现 api 层调用

        promise[form.type.data]()
    return 'success'
    
## 4-6 生成用户数据

配置信息 secure.py

    SQLALCHEMY_DATABASE_URI = 'mysql+cymysql://root:123456@localhost/ginger'
    SECRET_KEY = '\x88D\xf09\x6\xa0A\x7\xc5V\xbe\x8b\xef\xd7\xd8\xd3\xe6\x98*4'

## 4-7 自定义异常对象

如果用 wtforms 出现异常会返回 False

自定义异常继承 HTTPException 类

    from werkzeug.exceptions import HTTPException
    
    class ClientTypeError(HTTPException):
        code = 400
        msg = 'client is invalid'
        error_code = 1006

api 返回
    
    @api.route('/register', methods=['POST'])
    def create_client():
        data = request.json
        form = ClientForm(data=data)
        if form.validate():
            promise = {
                ClientTypeEnum.USER_EMAIL: __register_user_by_email,
            }
            promise[form.type.data]()
        else:
            ClientTypeError()
        return 'success'
        
## 4-9 自定义 APIException
 
需要返回 json 数据

error.py

get_body() 返回主题信息

msg 重写了 description

get_headers() 定义了返回类型是json


    from flask import request, json
    from werkzeug.exceptions import HTTPException
    
    
    class APIException(HTTPException):
        code = 500
        msg = 'sorry, we made a mistake (*￣︶￣)!'
        error_code = 999
    
        def __init__(self, msg=None, code=None, error_code=None, headers=None):
            if code:
                self.code = code
            if error_code:
                self.error_code = error_code
            if msg:
                self.msg = msg
            super(APIException, self).__init__(msg, None)
    
        def get_body(self, environ=None):
            body = dict(
                msg=self.msg,
                error_code=self.error_code,
                request=request.method + ' ' + self.get_url_no_param()
            )
            text = json.dumps(body)
            return text
    
        def get_headers(self, environ=None):
            """Get a list of headers."""
            return [('Content-Type', 'application/json')]
    
        @staticmethod
        def get_url_no_param():
            full_path = str(request.full_path)
            main_path = full_path.split('?')
            return main_path[0]
    
# 第5章 理解WTForms并灵活改造她

WTForms其实是非常强大的验证插件。但很多同学对WTForms的理解仅仅停留在“验证表单”上。那WTForms可以用来做API的参数验证码？完全可以，但这需要你灵活的使用它，对它做出一些“改变”

## 5-1 重写WTForms 一

