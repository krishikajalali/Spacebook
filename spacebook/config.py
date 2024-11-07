import os

class Config:
    SECRET_KEY = os.urandom(24)  # Secret key for session management
    MYSQL_HOST = 'localhost'  # Update with your MySQL host if needed
    MYSQL_USER = 'root'       # Update with your MySQL username
    MYSQL_PASSWORD = 'Satyavan12@'  # Update with your MySQL password
    MYSQL_DB = 'spacebook'
