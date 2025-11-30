from fastapi import APIRouter, Depends, HTTPException, Response
from app.models.schemas import ExportRequest
from app.core.dependencies import get_current_user
from app.services.document_service import DocumentService
from app.utils.firebase_client import db
from datetime import datetime

router = APIRouter()
document_service = DocumentService()

@router.post("/docx")
async def export_word(
    request: ExportRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Export project as Word document (.docx)
    - Fetches latest refined content
    - Generates professionally formatted document
    - Returns file for download
    """
    try:
        # Get project
        project_ref = db.collection('projects').document(request.project_id)
        project_doc = project_ref.get()
        
        if not project_doc.exists:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = project_doc.to_dict()
        
        # Verify ownership
        if project_data['user_id'] != current_user['sub']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Verify document type
        if project_data['doc_type'] != 'docx':
            raise HTTPException(
                status_code=400,
                detail="Project is not a Word document"
            )
        
        # Add formatted date for document
        project_data['created_date'] = project_data['created_at'].strftime('%B %d, %Y')
        
        # Generate Word document
        doc_bytes = document_service.create_word_document(project_data)
        
        # Return as downloadable file
        filename = f"{project_data['title'].replace(' ', '_')}.docx"
        
        return Response(
            content=doc_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document export failed: {str(e)}"
        )

@router.post("/pptx")
async def export_powerpoint(
    request: ExportRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Export project as PowerPoint presentation (.pptx)
    - Fetches latest refined content
    - Generates professionally formatted slides
    - Returns file for download
    """
    try:
        # Get project
        project_ref = db.collection('projects').document(request.project_id)
        project_doc = project_ref.get()
        
        if not project_doc.exists:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = project_doc.to_dict()
        
        # Verify ownership
        if project_data['user_id'] != current_user['sub']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Verify document type
        if project_data['doc_type'] != 'pptx':
            raise HTTPException(
                status_code=400,
                detail="Project is not a PowerPoint presentation"
            )
        
        # Add formatted date
        project_data['created_date'] = project_data['created_at'].strftime('%B %d, %Y')
        
        # Generate PowerPoint
        pptx_bytes = document_service.create_powerpoint(project_data)
        
        # Return as downloadable file
        filename = f"{project_data['title'].replace(' ', '_')}.pptx"
        
        return Response(
            content=pptx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Presentation export failed: {str(e)}"
        )
