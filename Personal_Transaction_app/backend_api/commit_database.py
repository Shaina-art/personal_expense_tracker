from database import Base , engine
from models import Transaction
Base.metadata.create_all(bind=engine)