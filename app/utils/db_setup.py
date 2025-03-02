from sqlalchemy import Column, Integer, String, Date, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# Base class for models
Base = declarative_base()

class CallInfo(Base):
    __tablename__ = 'call_info'  # Using lowercase naming convention

    id = Column(Integer, primary_key=True, index=True)
    call_time = Column(DateTime, default=datetime.utcnow)  # Defaults to current time
    full_name = Column(String(100), nullable=False)  # Ensure full_name is required
    date_of_birth = Column(Date)  # Use Date instead of DateTime if time isn't needed
    last_four_cc_digits = Column(String(4), nullable=False)  # Ensure it's always 4 digits
    contact_number = Column(String(20), nullable=False)
    action_to_do = Column(String(100), nullable=False)

    def __repr__(self):
        return f'<CallInfo(full_name={self.full_name}, call_time={self.call_time})>'

# Set up the database engine and session
DATABASE_URL = "sqlite:///./test.db"  # Change this to your actual database URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create database tables
def init_db():
    """Initialize the database and create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

# Call this function once when the application starts
init_db()
