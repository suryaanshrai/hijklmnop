from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .todo import Todo
from .user import User