from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Boolean, Index, UniqueConstraint, Integer, Table, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    
    versions = relationship("ResumeVersion", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("Skill", secondary="user_skills", back_populates="users")

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, index=True)
    users = relationship("User", secondary="user_skills", back_populates="skills")

user_skills = Table(
    "user_skills",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id", ondelete="CASCADE")),
    Column("skill_id", String, ForeignKey("skills.id", ondelete="CASCADE")),
    Index("ix_user_skills_user_id", "user_id"),
    Index("ix_user_skills_skill_id", "skill_id")
)

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
    file_path = Column(String, nullable=True)
    file_original_name = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    file_mime_type = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # New fields
    summary = Column(Text)
    skills = Column(ARRAY(String))
    experience = Column(ARRAY(Text))  # Store as JSON array of experience entries
    education = Column(ARRAY(Text))   # Store as JSON array of education entries
    certifications = Column(ARRAY(Text))
    languages = Column(ARRAY(String))
    projects = Column(ARRAY(Text))
    
    user = relationship("User", back_populates="versions") 