from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.core.dependencies import get_current_user
from app.utils.firebase_client import db
from google.cloud import firestore
from datetime import datetime
import uuid
from typing import List

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(current_user: dict = Depends(get_current_user)):
    """
    Get all projects for current user
    Returns list of projects with metadata
    """
    try:
        user_id = current_user['sub']
        projects_ref = db.collection('projects').where('user_id', '==', user_id)
        projects = projects_ref.stream()
        
        result = []
        for project in projects:
            project_data = project.to_dict()
            project_data['id'] = project.id
            result.append(project_data)
        
        # Sort by updated_at descending
        result.sort(key=lambda x: x.get('updated_at', datetime.min), reverse=True)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new project
    - Stores initial sections from configuration
    """
    try:
        user_id = current_user['sub']
        project_id = str(uuid.uuid4())

        # Build sections with ids and empty versions
        sections_data = [
            {
                "id": str(uuid.uuid4()),
                "title": s.title,
                "content": s.content,
                "order": s.order,
                "versions": []
            }
            for s in project.sections
        ]

        project_data = {
            'user_id': user_id,
            'title': project.title,
            'doc_type': project.doc_type,
            'topic': project.topic,
            'description': project.description,
            'sections': sections_data,  # use sections from request
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        db.collection('projects').document(project_id).set(project_data)
        
        # Update user project count
        user_ref = db.collection('users').document(user_id)
        user_ref.update({'total_projects': firestore.Increment(1)})
        
        project_data['id'] = project_id
        return project_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get specific project by ID
    Verifies user ownership
    """
    try:
        project_ref = db.collection('projects').document(project_id)
        project = project_ref.get()
        
        if not project.exists:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = project.to_dict()
        
        # Verify ownership
        if project_data['user_id'] != current_user['sub']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        project_data['id'] = project_id
        return project_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{project_id}")
async def update_project(
    project_id: str,
    updates: ProjectUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update project details or sections
    - Updates title, description, or sections
    - Tracks update timestamp
    """
    try:
        project_ref = db.collection('projects').document(project_id)
        project = project_ref.get()
        
        if not project.exists:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = project.to_dict()
        if project_data['user_id'] != current_user['sub']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Prepare update data
        update_data = updates.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        
        project_ref.update(update_data)
        
        return {"message": "Project updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete project
    Verifies ownership before deletion
    """
    try:
        project_ref = db.collection('projects').document(project_id)
        project = project_ref.get()
        
        if not project.exists:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = project.to_dict()
        if project_data['user_id'] != current_user['sub']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        project_ref.delete()
        
        # Update user project count
        user_ref = db.collection('users').document(current_user['sub'])
        user_ref.update({'total_projects': firestore.Increment(-1)})
        
        return {"message": "Project deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
