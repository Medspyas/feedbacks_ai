from typing import Any, Dict, List, Optional

from bson import ObjectId, errors
from motor.motor_asyncio import AsyncIOMotorCollection

from app.database import db_connection


class FeedbackRepository:
    def __init__(self):

        self.collection: AsyncIOMotorCollection = db_connection.db.get_collection(
            "feedbacks"
        )

    async def create(self, data: Dict[str, Any]) -> str:

        result = await self.collection.insert_one(data)
        return str(result.inserted_id)

    # On affiche d'abord les feedbacks les plus récents
    async def get_all(self, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:

        cursor = self.collection.find().sort("created_at", -1).skip(skip).limit(limit)
        feedbacks = await cursor.to_list(length=limit)
        for f in feedbacks:
            f["_id"] = str(f["_id"])
        return feedbacks

    # Si l'id est mal formé, on renvoie None plutôt que de faire planter l'appli
    async def get_by_id(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        try:
            document = await self.collection.find_one({"_id": ObjectId(feedback_id)})
            if document:
                document["_id"] = str(document["_id"])
            return document
        except errors.InvalidId:
            return None

    async def update(self, feedback_id: str, update_data: Dict[str, Any]) -> bool:

        result = await self.collection.update_one(
            {"_id": ObjectId(feedback_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete(self, feedback_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(feedback_id)})
        return result.deleted_count > 0

    # Cherche le mot-clé un peu partout (nom, entreprise, contenu...), sans tenir compte de la casse
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        regex = {"$regex": query, "$options": "i"}

        cursor = self.collection.find(
            {
                "$or": [
                    {"username": regex},
                    {"company_name": regex},
                    {"content": regex},
                    {"keywords": regex},
                    {"category": regex},
                ]
            }
        ).limit(limit)

        feedbacks = await cursor.to_list(length=limit)
        for f in feedbacks:
            f["_id"] = str(f["_id"])
        return feedbacks

    async def count(self) -> int:
        return await self.collection.count_documents({})
