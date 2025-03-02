from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Base class for models
Base = declarative_base()

class CallInfo(Base):
    __tablename__ = 'call_info'  # Adjusted to use lowercase naming convention
    id = Column(Integer, primary_key=True, index=True)
    call_time = Column(DateTime, default=datetime.utcnow)
    full_name = Column(String(100))
    date_of_birth = Column(DateTime)
    last_four_cc_digits = Column(String(4))
    contact_number = Column(String(20))
    action_to_do = Column(String(100))

    def __repr__(self):
        return f'<CallInfo {self.full_name}>'

# Set up the database session and engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"  # You can change this to your actual database URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)
