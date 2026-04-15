import os
import json
import asyncio
from groq import AsyncClient
from dotenv import load_dotenv


load_dotenv()

class AIServices:
    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")
        self.client = AsyncClient(api_key=api_key)
        self.model_id = "llama-3.3-70b-versatile"

        self.fallback_model_id = "llama-3.1-8b-instant"

        self.max_retries = 3

    def _fallback_response(self):
        return {
            "sentiment": "Analyse indisponible",
            "priority": "medium",
            "keyword": [],
            "language": "fr",
            "satisfaction_score": 5.0,
            "reply": "Merci pour votre retour, nous reviendrons vers vous rapidement.",
            "suggested_action": "Traitement manuel requis"
        }
    


    async def analysis_feedback(self, content: str, company:str, category:str):

        prompt = f"""
        Tu es un expert en relation client pour l'entreprise "{company}".

        Voici un feedback client dans la catégorie "{category}" :
        "{content}"

        Raisonne étape par étape avant de répondre :
        1. Identifie la langue du message
        2. Évalue le niveau de satisfaction du client (1 à 10)
        3. Identifie les mots-clés importants (problèmes, besoins, émotions)
        4. Détermine la priorité de traitement
        5. Rédige une réponse professionnelle adaptée

        Exemple de priorité :
        - "high" : client très insatisfait, problème bloquant, risque de perte de client
        - "medium" : insatisfaction modérée, amélioration souhaitée
        - "low" : feedback positif ou suggestion mineure

        Format attendu pour chaque champ :
        - "sentiment": une phrase décrivant l'émotion du client (ex: "Contacter le client frustré mais constructif")
        - "keywords": liste de 3 à 5 mots-clés
        - "suggested_action": une action concrète (ex: "Contacter le client sous 24h avec un geste commercial")

        Réponds UNIQUEMENT sous format JSON avec ces clés :

         {{"sentiment": "Analyse indisponible",
            "priority": "medium",
            "keywords": [],
            "language": "fr",
            "satisfaction_score": 5.0,
            "reply": "Merci pour votre retour, nous reviendrons vers vous rapidement.",
            "suggested_action": "Traitement manuel requis"
            }}
            """
        for attempt in range(self.max_retries):
            try:

                response = await self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    timeout=15
                    )
                        
            
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"Tentative {attempt + 1}/{self.max_retries} échouée : {e}")

                if attempt < self.max_retries -1:
                    await asyncio.sleep(attempt + 1)
            
        print(f"Modèle principal indisponible, tentative sur {self.fallback_model_id} ...")

        try:
            response = await self.client.chat.completions.create(
            model=self.fallback_model_id,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=40
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Modèle fallback également indisponible : {e}")
            return self._fallback_response()
        
                
