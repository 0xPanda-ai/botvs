from app import create_app
from flask.cli import load_dotenv
from strategies.qipan import main
import os
from flask_migrate import Migrate
from app.extensions import db
from services import transaction_log_serv

load_dotenv()

app = create_app(os.getenv("FLASK_ENV"))
migrate = Migrate(app, db)


@app.cli.command()
def qipan():
    #棋盘策略
    main()
