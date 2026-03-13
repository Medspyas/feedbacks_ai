import pytest
from unittest.mock import AsyncMock, patch
from app.services.ai_service import AIServices



@pytest.mark.asyncio
async def test_ai_service_format():

    ai = AIServices()

    mock_ai_json = {
        "sentiment": "Positif",
        "reply": "Merci pour votre retour excellent !"
    }

    with patch.object(ai, 'analysis_feedback', new_callable=AsyncMock) as mocked_ai:
        mocked_ai.return_value = mock_ai_json

        result = await ai.analysis_feedback(
            content="Le service était excellent, merci !",
            company="TestCorp",
            category="Service Client"
        )

        assert isinstance(result, dict)
        assert "sentiment" in result
        assert "reply" in result
        assert len(result["reply"]) > 0

@pytest.mark.asyncio
async def test_full_feedback_success(client):

    payload = {
        "username": "Jean Dupont",
        "company_name": "TechStore",
        "category": "Produit",
        "content": "Mon colis est arrivé cassé, je suis très déçus.",
        "rating" : 1
    }

    with patch("app.services.feedback_services.FeedbackServices.create_feedback", new_callable=AsyncMock) as mock_create, \
         patch("app.services.feedback_services.FeedbackServices.get_all_feedbacks", new_callable=AsyncMock) as mock_get_all, \
         patch("app.services.feedback_services.FeedbackServices.update_feedback", new_callable=AsyncMock) as mock_update, \
         patch("app.services.feedback_services.FeedbackServices.delete_feedback", new_callable=AsyncMock) as mock_delete, \
         patch("app.services.feedback_services.FeedbackServices.get_one_feedback", new_callable=AsyncMock) as mock_get_one:




        mock_create.return_value = {**payload, "id": "id_123", "status": "analyzed"}
        response = await client.post("/feedbacks/", json=payload)
        assert response.status_code == 201
        assert response.json()["_id"] == "id_123"

        mock_get_all.return_value = [{**payload, "id": "id_123"}]
        response = await client.get("/feedbacks/")
        assert response.status_code == 200
        assert len(response.json()) == 1

        updated_data = {**payload, "id": "id_123", "content": "Le contenu à été modifié pour le test."}
        mock_update.return_value = updated_data
        response = await client.put("/feedbacks/id_123", json=updated_data)
        assert response.status_code == 200 
        assert response.json()["content"] == "Le contenu à été modifié pour le test."

        mock_delete.return_value = True
        response = await client.delete("/feedbacks/id_123")
        assert response.status_code == 204


        mock_get_one.return_value = None
        response = await client.get(f"/feedbacks/id_123")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_feedback_missing_field(client):
    invalid_payload = {
        "username" : "Jean",
        "rating": 5
    }

    response = await client.post("/feedbacks/", json=invalid_payload)
    assert response.status_code == 422