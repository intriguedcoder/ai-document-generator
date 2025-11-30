from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import (
    RefineContentRequest, RefineContentResponse,
    FeedbackRequest, RevertVersionRequest
)
from app.core.dependencies import get_current_user
from app.services.refinement_service import RefinementService

router = APIRouter()
refinement_service = RefinementService()

@router.post("/refine", response_model=RefineContentResponse)
async def refine_content(
    request: RefineContentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Refine section content based on user prompt
    - Applies AI-powered refinements
    - Saves as new version with history
    - Returns diff for visualization
    """
    try:
        result = await refinement_service.refine_section(
            project_id=request.project_id,
            section_id=request.section_id,
            refinement_prompt=request.refinement_prompt,
            user_id=current_user['sub']
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Refinement failed: {str(e)}"
        )

@router.post("/feedback")
async def add_feedback(
    request: FeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Add like/dislike feedback and comment to version
    Stores user satisfaction data
    """
    try:
        result = await refinement_service.add_feedback(
            project_id=request.project_id,
            section_id=request.section_id,
            version=request.version,
            feedback=request.feedback,
            comment=request.comment or "",
            user_id=current_user['sub']
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save feedback: {str(e)}"
        )

@router.post("/revert")
async def revert_version(
    request: RevertVersionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Revert section to previous version
    Allows users to undo unwanted refinements
    """
    try:
        result = await refinement_service.revert_to_version(
            project_id=request.project_id,
            section_id=request.section_id,
            target_version=request.target_version,
            user_id=current_user['sub']
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Revert failed: {str(e)}"
        )
