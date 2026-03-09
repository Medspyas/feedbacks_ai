import os
import json
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

class AIServices:
    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel("gemini-1.5-flash")

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

            response = self.model.generate_content(prompt)

            text_response = response.text.replace('```json', '').replace('```', '').strip()

            return json.loads(text_response)
        except Exception as e:
            print(f"Erreur IA : {e}")
            return {
                "sentiment": "Analyse indisponible",
                "reply": "Merci pour votre retour, nous reviendrons vers vous rapidement."
            }
