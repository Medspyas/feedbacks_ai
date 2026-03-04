from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.models.feedback import Feedback, FeedbackDB
from app.repositories.feedback_repo import FeedbackRepository




router = APIRouter(prefix="/feedbacks", tags=["Feedbacks"])


def get_feedback_repo():

    return FeedbackRepository()


@router.post("/", response_model=FeedbackDB, status_code=status.HTTP_201_CREATED)
async def create_new_feedback(
    feedback: Feedback,
    repo: FeedbackRepository = Depends(get_feedback_repo)
):
    
    new_feedback_data = feedback.model_dump()

    full_data = FeedbackDB(**new_feedback_data).model_dump(by_alias=True)

    feedback_id = await repo.create(full_data)

    created_feedback = await repo.get_by_id(feedback_id)
    return created_feedback

@router.get("/", response_model=List[FeedbackDB])
async def read_all_feedbacks(
    limit: int = 50,
    repo: FeedbackRepository = Depends(get_feedback_repo)    
):
    return await repo.get_all(limit=limit)

@router.get("/{feedback_id}", response_model=FeedbackDB)
async def get_one_feed_back(
    feedback_id: str,
    repo: FeedbackRepository = Depends(get_feedback_repo)    
):
    feedback = await repo.get_by_id(feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback non trouvé")
    return feedback

@router.put("/{feedback_id}", response_model=FeedbackDB)
async def update_feedback_content(
    feedback_id: str,
    update_data: Feedback,
    repo: FeedbackRepository = Depends(get_feedback_repo)
):
    
    data = update_data.model_dump()

    success = await repo.update(feedback_id, data)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Feedback non trouvé ou aucune modification apportée"
        )
    
    updated_feedback = await repo.get_by_id(feedback_id)
    return updated_feedback

@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_feeedback(
    feedback_id: str,
    repo: FeedbackRepository = Depends(get_feedback_repo)

):
    
    deleted = await repo.delete(feedback_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Feedback non trouvé")
    return None