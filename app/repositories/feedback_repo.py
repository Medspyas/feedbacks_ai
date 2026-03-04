from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId, errors
from typing import List, Optional, Dict, Any
from app.database import db_connection


class FeedbackRepository:
    def __init__(self):

        self.collection:AsyncIOMotorCollection = db_connection.db.get_collection("feedbacks")

    async def create(self, data:Dict[str, Any]) -> str:

        result = await self.collection.insert_one(data)
        return str(result.inserted_id)
    
    async def get_all(self, limit:int = 50) -> List[Dict[str, Any]]:

        cursor = self.collection.find().limit(limit)
        feedbacks = await cursor.to_list(length=limit)
        for f in feedbacks:
            f["_id"] = str(f["_id"])
        return feedbacks
    
    async def get_by_id(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        try:
            document = await self.collection.find_one({"_id": ObjectId(feedback_id)})
            if document:
                document["_id"] = str(document["_id"])        
            return document
        except errors.InvalidId:
            return None
    

    async def update(self, feedback_id:str, update_data:Dict[str, Any]) -> bool:

        result = await self.collection.update_one(
            {"_id": ObjectId(feedback_id)},
            {"$set": update_data}
            )
        return result.modified_count > 0
    

    async def delete(self, feedback_id:str) -> bool :
        result = await self.collection.delete_one({"_id": ObjectId(feedback_id)})
        return result.deleted_count > 0