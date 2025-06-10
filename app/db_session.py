from app.database import Database

db_instance = Database()

def get_db():
    return db_instance