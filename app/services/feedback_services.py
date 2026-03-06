from app.repositories.feedback_repo import FeedbackRepository
from app.models.feedback import Feedback, FeedbackDB

class FeedbackServices:
    def __init__(self):
        self.repo = FeedbackRepository()

    async def create_feedback(self, feedback_in: Feedback) -> FeedbackDB:


        feedback_dict = feedback_in.model_dump()

        feedback_db = FeedbackDB(**feedback_dict)

        data_to_save = feedback_db.model_dump(by_alias=True, exclude={"id"})

        feedback_id = await self.repo.create(data_to_save)

        return await self.repo.get_by_id(feedback_id)
    

    async def get_all_feedbacks(self, limit: int = 50):

        return await self.repo.get_all(limit=limit)
    
    async def get_one_feedback(self, feedback_id: str):

        return await self.repo.get_by_id(feedback_id)
    
    async def update_feedback(self, feedback_id: str, update_data: Feedback):
         
        data = update_data.model_dump()
        success = await self.repo.update(feedback_id, data)
        if success:
            return await self.repo.get_by_id(feedback_id)
        return None
    
    async def delete_feedback(self, feedback_id: str):
        
        return await self.repo.delete(feedback_id)