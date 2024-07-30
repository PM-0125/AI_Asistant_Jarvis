import os
import json
import requests
from transformers import BertTokenizer, BertForMaskedLM, Trainer, TrainingArguments
from googletrans import Translator
from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader
import urllib.parse

# Database setup
Base = declarative_base()

class Knowledge(Base):
    __tablename__ = 'knowledge'
    id = Column(Integer, primary_key=True)
    question = Column(String, unique=True)
    answer = Column(Text)

username = 'amit'
password = 'Pym_0125'
encoded_password = urllib.parse.quote_plus(password)
connection_string = f'postgresql://{username}:{encoded_password}@localhost/knowledge_db'
engine = create_engine(connection_string)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

class NLPManager:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertForMaskedLM.from_pretrained('bert-base-uncased')
        self.translator = Translator()
        self.memory = []
        self.weather_api_key = 'your actual weather api key' #your actual weather api key from weather api 
        self.news_api_key = 'your api key from news api'  #your api key from news api 
        self.load_knowledge_base()

    def load_knowledge_base(self):
        self.knowledge_base = {}
        results = session.query(Knowledge).all()
        for result in results:
            self.knowledge_base[result.question] = result.answer

    def translate_text(self, text, dest_language):
        try:
            translated = self.translator.translate(text, dest=dest_language)
            return translated.text
        except Exception as e:
            print(f"Error in translation: {e}")
            return text

    def answer_question(self, question, language='en'):
        translated_question = self.translate_text(question, 'en')
        if "weather" in translated_question.lower():
            location = translated_question.split("in")[-1].strip() if "in" in translated_question else "Warsaw"
            return self.get_weather(location, language)
        elif "news" in translated_question.lower():
            topic = translated_question.split("about")[-1].strip() if "about" in translated_question else "technology"
            return self.get_news(topic, language)
        else:
            db_answer = self.knowledge_base.get(translated_question)
            if db_answer:
                answer = self.translate_text(db_answer, language)
                self.learn_from_interaction(translated_question, db_answer)
                return answer
            else:
                return "Sorry, I don't know the answer to that question."

    def get_weather(self, location, language):
        api_key = self.weather_api_key
        base_url = "http://api.weatherapi.com/v1/current.json"
        complete_url = f"{base_url}?key={api_key}&q={location}&aqi=no"
        response = requests.get(complete_url)
        data = response.json()
        if "current" in data:
            weather = data["current"]
            weather_info = f"The current weather in {location} is {weather['condition']['text']} with a temperature of {weather['temp_c']}°C."
            return self.translate_text(weather_info, language)
        else:
            return "City not found."

    def get_news(self, topic, language):
        api_key = self.news_api_key
        base_url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={api_key}&language=en"
        response = requests.get(base_url)
        articles = response.json().get('articles', [])
        summaries = [article['description'] for article in articles if article['description']]
        news_summary = " ".join(summaries[:5])
        return self.translate_text(news_summary, language)

    def learn_from_interaction(self, question, answer):
        self.memory.append({'question': question, 'answer': answer})
        if len(self.memory) > 5:
            self.continuous_learning()

    def continuous_learning(self):
        class CustomDataset(Dataset):
            def __init__(self, tokenizer, data, max_len=512):
                self.tokenizer = tokenizer
                self.data = data
                self.max_len = max_len

            def __len__(self):
                return len(self.data)

            def __getitem__(self, index):
                item = self.data[index]
                encoding = self.tokenizer(
                    item['question'],
                    add_special_tokens=True,
                    max_length=self.max_len,
                    return_token_type_ids=False,
                    padding='max_length',
                    truncation=True,
                    return_attention_mask=True,
                    return_tensors='pt',
                )
                labels = self.tokenizer(
                    item['answer'],
                    add_special_tokens=True,
                    max_length=self.max_len,
                    padding='max_length',
                    truncation=True,
                    return_tensors='pt',
                )
                labels = labels['input_ids']
                labels[labels == self.tokenizer.pad_token_id] = -100
                return {
                    'input_ids': encoding['input_ids'].flatten(),
                    'attention_mask': encoding['attention_mask'].flatten(),
                    'labels': labels.flatten(),
                }

        def data_loader(data, batch_size=2):
            dataset = CustomDataset(self.tokenizer, data)
            return DataLoader(dataset, batch_size=batch_size)

        train_data, val_data = train_test_split(self.memory, test_size=0.1)
        train_dataloader = data_loader(train_data)
        val_dataloader = data_loader(val_data)

        training_args = TrainingArguments(
            output_dir='./results',
            num_train_epochs=1,
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            warmup_steps=10,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=10,
            save_total_limit=1,
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataloader.dataset,
            eval_dataset=val_dataloader.dataset,
        )

        trainer.train()

    def have_conversation(self, input_text, language='en'):
        translated_input = self.translate_text(input_text, 'en')
        response = self.generate_response(translated_input)
        translated_response = self.translate_text(response, language)
        self.learn_from_interaction(translated_input, translated_response)
        return translated_response

    def generate_response(self, input_text):
        inputs = self.tokenizer(input_text, return_tensors='pt')
        outputs = self.model.generate(**inputs, max_new_tokens=50, num_beams=5, early_stopping=True)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
