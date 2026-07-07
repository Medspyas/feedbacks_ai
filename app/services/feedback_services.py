from app.models.feedback import Feedback, FeedbackDB
from app.repositories.feedback_repo import FeedbackRepository
from app.services.ai_service import AIServices
from app.utils import clean_text, is_valid_content


class FeedbackServices:
    def __init__(self):
        self.repo = FeedbackRepository()
        self.ai = AIServices()

    # On nettoie le texte, on l'envoie à l'IA, puis on sauvegarde le résultat
    async def create_feedback(self, feedback_in: Feedback) -> FeedbackDB:

        cleaned = clean_text(feedback_in.content)
        if not is_valid_content(cleaned):
            raise ValueError("Contenu invalide")

        ai_data = await self.ai.analysis_feedback(
            content=cleaned,
            company=feedback_in.company_name,
            category=feedback_in.category,
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

    # Renvoie les feedbacks page par page, du plus récent au plus ancien
    async def get_all_feedbacks(self, limit: int = 10, skip: int = 0):

        return await self.repo.get_all(limit=limit, skip=skip)

    async def get_one_feedback(self, feedback_id: str):

        return await self.repo.get_by_id(feedback_id)

    # Modifie un feedback, ou renvoie None si l'id ne correspond à rien
    async def update_feedback(self, feedback_id: str, update_data: Feedback):

        data = update_data.model_dump()
        success = await self.repo.update(feedback_id, data)
        if success:
            return await self.repo.get_by_id(feedback_id)
        return None

    async def delete_feedback(self, feedback_id: str):

        return await self.repo.delete(feedback_id)

    async def count_feedbacks(self) -> int:
        return await self.repo.count()

    # Recherche libre parmi les feedbacks (contenu, entreprise, mots-clés...)
    async def search_feedbacks(self, query: str, limit: int = 10) -> list:
        return await self.repo.search(query, limit)
