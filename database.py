import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
import enum
from config import DATABASE_URL

# Define an enum for the status
class JobStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the model for storing analysis results
class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, index=True, default="default_user") # Example user field
    file_path = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    status = Column(SQLAlchemyEnum(JobStatus), default=JobStatus.PENDING)
    final_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, task_id='{self.task_id}', status='{self.status}')>"

# Function to create the table
def init_db():
    print("Initializing the database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")

# Run this once to create your database table
if __name__ == "__main__":
    init_db()