import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_full_feedback_success(client):
    payload = {
        "username": "Jean Dupont",
        "company_name": "TechStore",
        "category": "Produit",
        "content": "Mon colis est arrivé cassé, je suis très déçus.",
        "rating": 1,
    }

    with patch(
        "app.services.feedback_services.FeedbackServices.create_feedback",
        new_callable=AsyncMock,
    ) as mock_create, patch(
        "app.services.feedback_services.FeedbackServices.get_all_feedbacks",
        new_callable=AsyncMock,
    ) as mock_get_all, patch(
        "app.services.feedback_services.FeedbackServices.update_feedback",
        new_callable=AsyncMock,
    ) as mock_update, patch(
        "app.services.feedback_services.FeedbackServices.delete_feedback",
        new_callable=AsyncMock,
    ) as mock_delete, patch(
        "app.services.feedback_services.FeedbackServices.get_one_feedback",
        new_callable=AsyncMock,
    ) as mock_get_one:

        mock_create.return_value = {**payload, "id": "id_123", "status": "analyzed"}
        response = await client.post("/feedbacks/", json=payload)
        assert response.status_code == 201

        mock_get_all.return_value = [{**payload, "id": "id_123"}]
        response = await client.get("/feedbacks/")
        assert response.status_code == 200
        assert len(response.json()) == 1

        updated_data = {
            **payload,
            "id": "id_123",
            "content": "Le contenu a été modifié pour le test.",
        }
        mock_update.return_value = updated_data
        response = await client.put("/feedbacks/id_123", json=updated_data)
        assert response.status_code == 200
        assert response.json()["content"] == "Le contenu a été modifié pour le test."

        mock_get_one.return_value = {**payload, "id": "id_123"}
        response = await client.get("/feedbacks/id_123")
        assert response.status_code == 200

        mock_delete.return_value = True
        response = await client.delete("/feedbacks/id_123")
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_one_feedback_not_found(client):

    with patch(
        "app.services.feedback_services.FeedbackServices.get_one_feedback",
        new_callable=AsyncMock,
    ) as mock_get_one:
        mock_get_one.return_value = None
        response = await client.get("/feedbacks/id_inexistant")
        assert response.status_code == 404
        assert response.json()["detail"] == "Feedback non trouvé"


@pytest.mark.asyncio
async def test_update_feedback_not_found(client):

    payload = {
        "username": "Jean",
        "company_name": "Test",
        "category": "Produit",
        "content": "Un contenu de test bien assez long",
        "rating": 5,
    }
    with patch(
        "app.services.feedback_services.FeedbackServices.update_feedback",
        new_callable=AsyncMock,
    ) as mock_update:
        mock_update.return_value = None
        response = await client.put("/feedbacks/id_inexistant", json=payload)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_feedback_not_found(client):

    with patch(
        "app.services.feedback_services.FeedbackServices.delete_feedback",
        new_callable=AsyncMock,
    ) as mock_delete:
        mock_delete.return_value = False
        response = await client.delete("/feedbacks/id_inexistant")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_feedbacks_invalid_content_value_error(client):

    with patch(
        "app.services.feedback_services.FeedbackServices.create_feedback",
        new_callable=AsyncMock,
    ) as mock_create:
        mock_create.side_effect = ValueError("Contenu invalide")
        payload = {
            "username": "Jean",
            "company_name": "Test",
            "category": "Support",
            "content": "Texte valide pour Pydantic mais rejeté par le service",
            "rating": 3,
        }
        response = await client.post("/feedbacks/", json=payload)
        assert response.status_code == 422
        assert "Contenu invalide" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_feedback_missing_field_pydantic(client):
    invalid_payload = {"username": "Jean", "rating": 5}
    response = await client.post("/feedbacks/", json=invalid_payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_feedbacks_count(client):
    with patch(
        "app.services.feedback_services.FeedbackServices.count_feedbacks",
        new_callable=AsyncMock,
    ) as mock_count:
        mock_count.return_value = 11
        response = await client.get("feedbacks/count")
        assert response.status_code == 200
        assert response.json()["total"] == 11


@pytest.mark.asyncio
async def test_get_feedbacks_pagination(client):
    with patch(
        "app.services.feedback_services.FeedbackServices.get_all_feedbacks",
        new_callable=AsyncMock,
    ) as mock_get_all:
        mock_get_all.return_value = [
            {
                "username": f"user{i}",
                "company_name": "test",
                "category": "test",
                "content": "test_content",
                "rating": 3,
            }
            for i in range(10)
        ]
        response = await client.get("/feedbacks/?limit=10&skip=0")
        assert response.status_code == 200
        assert len(response.json()) == 10

        response = await client.get("/feedbacks/?limit=10&skip=10")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_feedbacks(client):
    with patch(
        "app.repositories.feedback_repo.FeedbackRepository.search",
        new_callable=AsyncMock,
    ) as mock_search:
        mock_search.return_value = [
            {
                "username": "medsfire",
                "company_name": "test",
                "category": "test",
                "content": "test_content",
                "rating": 3,
            }
        ]
        response = await client.get("/feedbacks/?search=meds")
        assert response.status_code == 200
        assert len(response.json()) == 1
