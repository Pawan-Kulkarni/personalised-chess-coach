from chess_coach.database.connection import engine
from chess_coach.database.models import Base

Base.metadata.create_all(engine)

print("Tables created successfully.")