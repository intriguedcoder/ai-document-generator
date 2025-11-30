from app.utils.firebase_client import get_firestore_client
from typing import List, Dict, Any
from datetime import datetime

class ProjectsService:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = get_firestore_client()
        self.collection = self.db.collection("projects")
    
    async def list_projects(self) -> List[Dict]:
        docs = self.collection.where("user_id", "==", self.user_id).stream()
        projects = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            projects.append(data)
        return projects
    
    async def create_project(self, project_data: Dict) -> Dict:
        doc_ref = self.collection.document()
        doc_ref.set(project_data)
        project_data["id"] = doc_ref.id
        return project_data
    
    async def get_project(self, project_id: str) -> Dict:
        doc = self.collection.document(project_id).get()
        if doc.exists and doc.to_dict().get("user_id") == self.user_id:
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        return None
    
    async def update_project(self, project_id: str, update_data: Dict) -> Dict:
        doc_ref = self.collection.document(project_id)
        doc = doc_ref.get()
        if doc.exists and doc.to_dict().get("user_id") == self.user_id:
            update_data["updated_at"] = datetime.utcnow()
            doc_ref.update(update_data)
            data = doc.to_dict()
            data["id"] = doc.id
            data.update(update_data)
            return data
        return None
    
    async def delete_project(self, project_id: str) -> bool:
        doc = self.collection.document(project_id).get()
        if doc.exists and doc.to_dict().get("user_id") == self.user_id:
            self.collection.document(project_id).delete()
            return True
        return False
