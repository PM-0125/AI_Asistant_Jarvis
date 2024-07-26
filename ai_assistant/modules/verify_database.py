# verify_database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_database import Knowledge
import json

engine = create_engine('sqlite:///knowledge.db')
Session = sessionmaker(bind=engine)
session = Session()

knowledge_entries = session.query(Knowledge).limit(10).all()

for entry in knowledge_entries:
    print(f"Question: {entry.question}\nAnswer: {entry.answer}\n")


def count_json_entries(json_path):
    with open(json_path, 'r') as file:
        knowledge_base = json.load(file)
        return len(knowledge_base)

json_path = r"D:\Voice Assistants\ai_assistant\modules\knowledge_base.json"
num_entries_json = count_json_entries(json_path)
print(f"Number of entries in JSON: {num_entries_json}")