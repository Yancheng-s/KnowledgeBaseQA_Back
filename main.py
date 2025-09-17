from flask import Flask
from flask_cors import CORS
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
from database.database import db
from src.route import module

app = Flask(__name__)
CORS(app)  # 全局启用 CORS，允许所有来源的请求

# 配置 MySQL 数据库 URI（格式：mysql://用户名:密码@主机地址/数据库名）
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3307/chainflow'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化 SQLAlchemy
db.init_app(app)

# 注册路由
module.register_routes(app)

# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # 调用 module 中的函数
    app.run(debug=True, host='0.0.0.0', port=5000)