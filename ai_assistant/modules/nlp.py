# modules/nlp.py

import spacy
from transformers import pipeline
from langdetect import detect
from googletrans import Translator
import json
import requests
import os

class NLPManager:
    def __init__(self):
        self.nlp_en = spacy.load("en_core_web_sm")
        self.nlp_multi = spacy.load("xx_ent_wiki_sm")  # Multilingual model for Hindi and Sanskrit
        self.qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
        self.summarization_pipeline = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
        self.translator = Translator()
        self.create_knowledge_base()

    def process_text(self, text, lang='en'):
        if lang == 'en':
            doc = self.nlp_en(text)
        else:
            doc = self.nlp_multi(text)
        return [token.text for token in doc]

    def detect_language(self, text):
        return detect(text)

    def translate_text(self, text, target_lang='en'):
        translation = self.translator.translate(text, dest=target_lang)
        return translation.text

    def answer_question(self, question, context):
        result = self.qa_pipeline(question=question, context=context)
        return result['answer']

    def create_knowledge_base(self):
        path = os.path.join(os.path.dirname(__file__), 'knowledge_base.json')
        with open(path, 'r') as f:
            self.knowledge_base = json.load(f)

    def query_knowledge_base(self, question):
        return self.knowledge_base.get(question, "I don't know the answer to that.")

    def handle_query(self, question, context=None):
        # First, try to get an answer from the knowledge base
        answer = self.query_knowledge_base(question)
        if answer:
            return answer
        
        # If no answer is found in the knowledge base, use the QA model
        if context:
            return self.answer_question(question, context)
        
        return "I'm sorry, I don't know the answer to that."

    def fetch_weather(self, location):
        # This method fetches weather information from an external API
        api_key = "YOUR API KEY"  # Replace with your actual API key
        base_url = "http://api.weatherapi.com/v1/current.json"
        complete_url = f"{base_url}?key={api_key}&q={location}"
        response = requests.get(complete_url)
        data = response.json()
        if response.status_code == 200:
            return f"The current weather in {location} is {data['current']['condition']['text']} with a temperature of {data['current']['temp_c']}°C."
        else:
            return "I couldn't retrieve the weather information right now."

    def fetch_news(self, topic):
        # This method fetches news information from NewsAPI
        api_key = "Your API KEY"  # Replace with your actual NewsAPI key
        base_url = "https://newsapi.org/v2/everything"
        complete_url = f"{base_url}?q={topic}&apiKey={api_key}"
        response = requests.get(complete_url)
        data = response.json()
        if response.status_code == 200:
            articles = data['articles'][:5]  # Get top 5 articles
            contents = " ".join([article['content'] for article in articles if article['content']])
            input_length = len(contents.split())
            max_length = min(300, input_length)  # Set max_length based on input length
            min_length = max(100, int(0.4 * input_length))  # Ensure min_length is reasonable
            summary = self.summarization_pipeline(contents, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
            return f"Here is a summary of the top news articles on {topic}:\n{summary}"
        else:
            return "I couldn't retrieve the news information right now."

    def fetch_external_data(self, query):
        # General method to handle different types of external data queries
        if "weather" in query.lower():
            location = query.split("weather in")[-1].strip()
            return self.fetch_weather(location)
        elif "news" in query.lower():
            topic = query.split("news about")[-1].strip()
            return self.fetch_news(topic)
        # Add more external data handling here
        return "I couldn't retrieve the information you requested."

    def manage_dialogue(self, user_input, context):
        # Basic dialogue management implementation
        # This method can be expanded to maintain context and manage multi-turn conversations
        if "weather" in user_input.lower():
            location = user_input.split("weather in")[-1].strip()
            return self.fetch_external_data(f"weather in {location}")
        elif "news" in user_input.lower():
            topic = user_input.split("news about")[-1].strip()
            return self.fetch_external_data(f"news about {topic}")
        
        return self.handle_query(user_input, context)
