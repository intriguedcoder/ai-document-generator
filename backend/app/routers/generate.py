from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import (
    AIOutlineRequest, AIOutlineResponse,
    GenerateContentRequest, GenerateContentResponse
)
from app.core.dependencies import get_current_user
from app.services.gemini_service import GeminiService
from app.utils.firebase_client import db
from datetime import datetime
import uuid

router = APIRouter()
gemini_service = GeminiService()

@router.post("/outline", response_model=AIOutlineResponse)
async def generate_outline(
    request: AIOutlineRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    AI-Generated Template (BONUS FEATURE)
    - Generates section headers for Word documents
    - Generates slide titles for PowerPoint presentations
    - User can accept, edit, or discard suggestions
    """
    try:
        outline = await gemini_service.suggest_outline(
            topic=request.topic,
            doc_type=request.doc_type,
            num_sections=request.num_sections
        )
        
        return outline
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Outline generation failed: {str(e)}"
        )

@router.post("/content", response_model=GenerateContentResponse)
async def generate_content(
    request: GenerateContentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate content for a specific section/slide
    - Context-aware generation based on project topic
    - Stores generated content with version tracking
    """
    try:
        # Get project for context
        project_ref = db.collection('projects').document(request.project_id)
        project_doc = project_ref.get()
        
        if not project_doc.exists:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = project_doc.to_dict()
        
        # Verify ownership
        if project_data['user_id'] != current_user['sub']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Find section
        section = None
        section_index = None
        for idx, sec in enumerate(project_data['sections']):
            if sec['id'] == request.section_id:
                section = sec
                section_index = idx
                break
        
        if section is None:
            raise HTTPException(status_code=404, detail="Section not found")
        
        # Generate content using AI with doc_type awareness
        content = await gemini_service.generate_section_content(
            section_title=section['title'],
            project_topic=project_data['topic'],
            context=request.context or "",
            tone=request.tone,
            doc_type=project_data.get('doc_type', 'docx')  # ✅ ADDED THIS LINE
        )
        
        # Create initial version
        version = {
            'version': 1,
            'content': content,
            'prompt': f"Initial generation with {request.tone} tone",
            'timestamp': datetime.utcnow(),
            'feedback': None,
            'comment': ''
        }
        
        # Update section
        section['content'] = content
        section['versions'] = [version]
        
        # Update Firestore
        project_data['sections'][section_index] = section
        project_data['updated_at'] = datetime.utcnow()
        project_ref.update({
            'sections': project_data['sections'],
            'updated_at': project_data['updated_at']
        })
        
        return {
            'section_id': request.section_id,
            'content': content,
            'version': 1
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/add-section/{project_id}")
async def add_section(
    project_id: str,
    section_title: str,
    order: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a new section/slide to project
    Used when user manually adds sections to outline
    """
    try:
        project_ref = db.collection('projects').document(project_id)
        project_doc = project_ref.get()
        
        if not project_doc.exists:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = project_doc.to_dict()
        
        if project_data['user_id'] != current_user['sub']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Create new section
        new_section = {
            'id': str(uuid.uuid4()),
            'title': section_title,
            'content': '',
            'order': order,
            'versions': []
        }
        
        # Add to sections
        project_data['sections'].append(new_section)
        project_data['updated_at'] = datetime.utcnow()
        
        project_ref.update({
            'sections': project_data['sections'],
            'updated_at': project_data['updated_at']
        })
        
        return new_section
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
