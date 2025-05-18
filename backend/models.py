from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Boolean, Index, UniqueConstraint, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    versions = relationship("ResumeVersion", back_populates="user", cascade="all, delete-orphan")

class ResumeVersion(Base):
    __tablename__ = "resume_versions"
    __table_args__ = (
        Index('ix_resume_versions_user_id', 'user_id'),
        Index('ix_resume_versions_created_at', 'created_at'),
        UniqueConstraint('user_id', 'version_name', name='uq_user_version_name'),
    )
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version_name = Column(String, nullable=False)
    file_path = Column(String, nullable=True)  # Path to stored PDF file
    file_original_name = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    file_mime_type = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    user = relationship("User", back_populates="versions") 