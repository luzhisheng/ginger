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