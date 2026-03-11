import os
import json
from groq import AsyncClient
from dotenv import load_dotenv


load_dotenv()

class AIServices:
    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")
        self.client = AsyncClient(api_key=api_key)
        self.model_id = "llama-3.3-70b-versatile"

    async def analysis_feedback(self, content: str, company:str, category:str):

        prompt = f"""
        Tu es un expert en relation client pour l'entreprise "{company}".
        Analyse ce feedback concernant la catégorie "{category}" :
        "{content}"

        Réponds UNIQUEMENT sous format JSON avec ces clés :
        1. "sentiment" : un résumé court de l'humeur et du problème.
        2. "reply" : une réponse polie et professionnelle destinée au client.       
        """

        try:

            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
                )
                      
        
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Erreur IA : {e}")
            return {
                "sentiment": "Analyse indisponible",
                "reply": "Merci pour votre retour, nous reviendrons vers vous rapidement."
            }
