import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.ai_service import AIServices


@pytest.mark.asyncio
async def test_ai_service_success():
    ai = AIServices()

    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(
        {
            "sentiment": "Positif",
            "priority": "low",
            "keywords": ["excellent"],
            "language": "fr",
            "satisfaction_score": 9.0,
            "reply": "Merci !",
            "suggested_action": "Aucune",
        }
    )
    mock_response.choices = [mock_choice]

    with patch.object(
        ai.client.chat.completions, "create", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = mock_response
        res = await ai.analysis_feedback("Super service", "Comp", "Cat")

        assert res["sentiment"] == "Positif"
        assert mock_create.call_count == 1


@pytest.mark.asyncio
async def test_ai_service_retry_then_success():
    ai = AIServices()
    ai.max_retries = 2

    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({"sentiment": "Réussi après échec"})
    mock_response.choices = [mock_choice]

    with patch.object(
        ai.client.chat.completions, "create", new_callable=AsyncMock
    ) as mock_create, patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        mock_create.side_effect = [Exception("Erreur Réseau"), mock_response]

        res = await ai.analysis_feedback("Test", "Comp", "Cat")
        assert res["sentiment"] == "Réussi après échec"
        assert mock_create.call_count == 2
        mock_sleep.assert_called_once()


@pytest.mark.asyncio
async def test_ai_service_fallback_model_success():
    ai = AIServices()
    ai.max_retries = 1

    mock_response_fallback = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(
        {"sentiment": "Réponse du modèle de secours"}
    )
    mock_response_fallback.choices = [mock_choice]

    with patch.object(
        ai.client.chat.completions, "create", new_callable=AsyncMock
    ) as mock_create:
        mock_create.side_effect = [Exception("Main model down"), mock_response_fallback]

        res = await ai.analysis_feedback("Test", "Comp", "Cat")
        assert res["sentiment"] == "Réponse du modèle de secours"
        assert mock_create.call_count == 2


@pytest.mark.asyncio
async def test_ai_service_total_failure_fallback_response():
    ai = AIServices()
    ai.max_retries = 1

    with patch.object(
        ai.client.chat.completions, "create", new_callable=AsyncMock
    ) as mock_create:
        mock_create.side_effect = [Exception("Main down"), Exception("Fallback down")]

        res = await ai.analysis_feedback("Test", "Comp", "Cat")
        assert res["sentiment"] == "Analyse indisponible"
