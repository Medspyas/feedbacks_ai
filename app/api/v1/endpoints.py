from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.models.feedback import Feedback, FeedbackDB
from app.services.feedback_services import FeedbackServices




router = APIRouter(prefix="/feedbacks", tags=["Feedbacks"])


def get_feedback_services():

    return FeedbackServices()


@router.post("/", response_model=FeedbackDB, status_code=status.HTTP_201_CREATED)
async def create_new_feedback(
    feedback: Feedback,
    service: FeedbackServices = Depends(get_feedback_services)
):    
    
    return await service.create_feedback(feedback)

@router.get("/", response_model=List[FeedbackDB])
async def read_all_feedbacks(
    limit: int = 50,
    service: FeedbackServices = Depends(get_feedback_services)    
):
    return await service.get_all_feedbacks(limit=limit)

@router.get("/{feedback_id}", response_model=FeedbackDB)
async def get_one_feed_back(
    feedback_id: str,
    service: FeedbackServices = Depends(get_feedback_services)    
):
    feedback = await service.get_one_feedback(feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback non trouvé")
    return feedback

@router.put("/{feedback_id}", response_model=FeedbackDB)
async def update_feedback_content(
    feedback_id: str,
    update_data: Feedback,
    service: FeedbackServices = Depends(get_feedback_services)
):       

    updated_feedback = await service.update_feedback(feedback_id, update_data)

    if not updated_feedback:
        raise HTTPException(
            status_code=404,
            detail="Feedback non trouvé ou aucune modification apportée"
        )    
  
    return updated_feedback

@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_feeedback(
    feedback_id: str,
    service: FeedbackServices = Depends(get_feedback_services)

):
    
    deleted = await service.delete_feedback(feedback_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Feedback non trouvé")
    return None


@router.get("/count")
async def get_feedback_count(services: FeedbackServices = Depends(get_feedback_services)):
    count = await services.count_feedbacks()
    return{"total": count}