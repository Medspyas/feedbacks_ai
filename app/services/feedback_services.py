from app.repositories.feedback_repo import FeedbackRepository
from app.models.feedback import Feedback, FeedbackDB
from app.services.ai_service import AIServices

class FeedbackServices:
    def __init__(self):
        self.repo = FeedbackRepository()
        self.ai = AIServices()

    async def create_feedback(self, feedback_in: Feedback) -> FeedbackDB:

        ai_data = await self.ai.analysis_feedback(
            content=feedback_in.content,
            company=feedback_in.company_name,
            category=feedback_in.category
        )


        feedback_dict = feedback_in.model_dump()

        feedback_db = FeedbackDB(
            **feedback_dict,
            ai_analysis=ai_data.get("sentiment"),
            ai_response=ai_data.get("reply"),
            status="analyzed",
            priority=ai_data.get("priority"),
            keywords=ai_data.get("keywords"),
            language=ai_data.get("language"),
            satisfaction_score=ai_data.get("satisfaction_score"),
            suggested_action=ai_data.get("suggested_action"),

        )

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