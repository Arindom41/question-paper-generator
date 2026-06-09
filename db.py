from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:root@localhost:5432/Question_bank"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

session = Session()