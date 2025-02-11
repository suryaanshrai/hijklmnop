import os

SECRET_KEY = "wobot-todolist-app"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
DATABASE_URL = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:root@localhost:3306/todo-db')