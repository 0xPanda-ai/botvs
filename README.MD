# 机器人

---
### 安装
- 创建虚拟环境 `python3 -m venv venv`
- 进入虚拟环境 `source venv/bin/activate`
- 安装包 `pip install -r requirements.txt`
- 复制配置文件 `cp .env.env_exp .env`
- 编辑env文件
- 数据库迁移 `flask db upgrade`

###启动网格策略
- 复制策略配置文件 `cp robot/qipan_exp.py robot/qipan.py`
- 编辑qipan.py文件
- flask qipan

