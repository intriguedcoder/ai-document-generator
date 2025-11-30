from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Literal
from datetime import datetime

# AUTH SCHEMAS
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    display_name: str = Field(..., min_length=2, description="Display name")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


class UserProfile(BaseModel):
    user_id: str
    email: str
    display_name: str


#  VERSION CONTROL SCHEMAS 
class ContentVersion(BaseModel):
    version: int
    content: str
    prompt: Optional[str] = None
    timestamp: datetime
    feedback: Optional[Literal["like", "dislike"]] = None
    comment: Optional[str] = None


#  SECTION SCHEMAS 
class SectionBase(BaseModel):
    title: str
    content: str = ""
    order: int


class Section(SectionBase):
    id: str
    versions: List[ContentVersion] = []


class SectionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None


class SectionInput(BaseModel):
    """Section shape used when creating a project from the config screen."""
    title: str
    content: str = ""
    order: int


#  PROJECT SCHEMAS 
class ProjectCreate(BaseModel):
    title: str
    doc_type: Literal["docx", "pptx"]
    topic: str
    description: Optional[str] = None
    sections: List[SectionInput] = []   # take sections from frontend


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    sections: Optional[List[Section]] = None
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    title: str
    doc_type: str
    topic: str
    sections: List[Section]
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


#  GENERATION SCHEMAS 
class AIOutlineRequest(BaseModel):
    """Request for AI-generated outline (BONUS FEATURE)"""
    topic: str
    doc_type: Literal["docx", "pptx"]
    num_sections: int = Field(default=5, ge=3, le=10)


class AIOutlineResponse(BaseModel):
    sections: List[dict]  # [{"title": "...", "description": "..."}]


class GenerateContentRequest(BaseModel):
    project_id: str
    section_id: str
    context: Optional[str] = None
    tone: Literal["professional", "casual", "academic"] = "professional"


class GenerateContentResponse(BaseModel):
    section_id: str
    content: str
    version: int


#  REFINEMENT SCHEMAS 
class RefineContentRequest(BaseModel):
    project_id: str
    section_id: str
    refinement_prompt: str


class RefineContentResponse(BaseModel):
    section_id: str
    content: str
    version: int
    diff: List[dict]  # Diff data for frontend visualization


class FeedbackRequest(BaseModel):
    project_id: str
    section_id: str
    version: int
    feedback: Optional[Literal["like", "dislike"]] = None
    comment: Optional[str] = None


class RevertVersionRequest(BaseModel):
    project_id: str
    section_id: str
    target_version: int


#  EXPORT SCHEMAS 
class ExportRequest(BaseModel):
    project_id: str
