from sqlalchemy import text

from chess_coach.database.connection import engine


with engine.connect() as connection:
    result = connection.execute(text("SELECT version();"))
    print(result.fetchone())