from app.utils.firebase_client import db
from app.services.gemini_service import GeminiService
from app.utils.logger import get_logger
from fastapi import HTTPException
from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Dict

logger = get_logger(__name__)
gemini_service = GeminiService()

class RefinementService:
    @staticmethod
    async def refine_section(
        project_id: str,
        section_id: str,
        refinement_prompt: str,
        user_id: str
    ) -> dict:
        """
        Refine section content and save as new version
        Stores refinement history for tracking
        """
        try:
            # Get project from Firestore
            project_ref = db.collection('projects').document(project_id)
            project_doc = project_ref.get()
            
            if not project_doc.exists:
                raise HTTPException(status_code=404, detail="Project not found")
            
            project_data = project_doc.to_dict()
            
            # Verify ownership
            if project_data['user_id'] != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Find section
            section_index = None
            for idx, section in enumerate(project_data['sections']):
                if section['id'] == section_id:
                    section_index = idx
                    break
            
            if section_index is None:
                raise HTTPException(status_code=404, detail="Section not found")
            
            section = project_data['sections'][section_index]
            current_content = section['content']
            section_title = section['title']
            
            # Generate refined content using AI
            refined_content = await gemini_service.refine_content(
                original_content=current_content,
                refinement_prompt=refinement_prompt,
                section_title=section_title
            )
            
            # Create new version
            new_version = {
                'version': len(section.get('versions', [])) + 1,
                'content': refined_content,
                'prompt': refinement_prompt,
                'timestamp': datetime.utcnow(),
                'feedback': None,
                'comment': ''
            }
            
            # Update section
            if 'versions' not in section:
                section['versions'] = []
            section['versions'].append(new_version)
            section['content'] = refined_content  # Update current content
            
            # Update Firestore
            project_data['sections'][section_index] = section
            project_data['updated_at'] = datetime.utcnow()
            project_ref.update({
                'sections': project_data['sections'],
                'updated_at': project_data['updated_at']
            })
            
            # Generate diff for visualization
            diff = RefinementService._generate_diff(current_content, refined_content)
            
            logger.info(f"Section refined: {section_id}, version: {new_version['version']}")
            
            return {
                'section_id': section_id,
                'content': refined_content,
                'version': new_version['version'],
                'diff': diff
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Refinement error: {str(e)}")
            raise HTTPException(status_code=500, detail="Refinement failed")
    
    @staticmethod
    def _generate_diff(original: str, refined: str) -> List[Dict]:
        """
        Generate word-level diff for frontend visualization
        Returns list of changes with type and text
        """
        matcher = SequenceMatcher(None, original.split(), refined.split())
        changes = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                changes.append({
                    'type': 'replace',
                    'old': ' '.join(original.split()[i1:i2]),
                    'new': ' '.join(refined.split()[j1:j2])
                })
            elif tag == 'delete':
                changes.append({
                    'type': 'delete',
                    'text': ' '.join(original.split()[i1:i2])
                })
            elif tag == 'insert':
                changes.append({
                    'type': 'insert',
                    'text': ' '.join(refined.split()[j1:j2])
                })
        
        return changes
    
    @staticmethod
    async def add_feedback(
        project_id: str,
        section_id: str,
        version: int,
        feedback: str,
        comment: str,
        user_id: str
    ) -> dict:
        """
        Add like/dislike feedback and comment to specific version
        """
        try:
            project_ref = db.collection('projects').document(project_id)
            project_doc = project_ref.get()
            
            if not project_doc.exists:
                raise HTTPException(status_code=404, detail="Project not found")
            
            project_data = project_doc.to_dict()
            
            if project_data['user_id'] != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Find section and version
            for section in project_data['sections']:
                if section['id'] == section_id:
                    if 'versions' in section and len(section['versions']) >= version:
                        section['versions'][version - 1]['feedback'] = feedback
                        section['versions'][version - 1]['comment'] = comment
                        
                        # Update Firestore
                        project_ref.update({'sections': project_data['sections']})
                        
                        logger.info(f"Feedback added: {section_id}, version: {version}")
                        return {"message": "Feedback saved successfully"}
            
            raise HTTPException(status_code=404, detail="Section or version not found")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Feedback error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save feedback")
    
    @staticmethod
    async def revert_to_version(
        project_id: str,
        section_id: str,
        target_version: int,
        user_id: str
    ) -> dict:
        """
        Revert section content to a previous version
        """
        try:
            project_ref = db.collection('projects').document(project_id)
            project_doc = project_ref.get()
            
            if not project_doc.exists:
                raise HTTPException(status_code=404, detail="Project not found")
            
            project_data = project_doc.to_dict()
            
            if project_data['user_id'] != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Find section
            for section in project_data['sections']:
                if section['id'] == section_id:
                    if 'versions' in section and len(section['versions']) >= target_version:
                        # Get target version content
                        target_content = section['versions'][target_version - 1]['content']
                        
                        # Update current content
                        section['content'] = target_content
                        
                        # Update Firestore
                        project_ref.update({
                            'sections': project_data['sections'],
                            'updated_at': datetime.utcnow()
                        })
                        
                        logger.info(f"Reverted to version: {target_version}, section: {section_id}")
                        return {
                            "message": f"Reverted to version {target_version}",
                            "content": target_content
                        }
            
            raise HTTPException(status_code=404, detail="Section or version not found")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Revert error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to revert version")
