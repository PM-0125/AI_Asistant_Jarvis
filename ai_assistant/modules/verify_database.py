from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_database import JsonKnowledge, BookKnowledge, ResearchPaperKnowledge
import json
import urllib.parse

# Database connection setup
username = 'your username'
password = 'password'
encoded_password = urllib.parse.quote_plus(password)
connection_string = f'postgresql://{username}:{encoded_password}@localhost/knowledge_db'
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
session = Session()

# Query to fetch JSON knowledge entries
json_knowledge_entries = session.query(JsonKnowledge).limit(10).all()
print("JSON Knowledge Entries:")
for entry in json_knowledge_entries:
    print(f"Question: {entry.question}\nAnswer: {entry.answer}\n")

# Query to fetch book knowledge entries
book_knowledge_entries = session.query(BookKnowledge).limit(10).all()
print("Book Knowledge Entries:")
for entry in book_knowledge_entries:
    print(f"Document Title: {entry.document_title}\nSentence: {entry.sentence}\n")

# Query to fetch research paper knowledge entries
research_paper_knowledge_entries = session.query(ResearchPaperKnowledge).limit(10).all()
print("Research Paper Knowledge Entries:")
for entry in research_paper_knowledge_entries:
    print(f"Document Title: {entry.document_title}\nSentence: {entry.sentence}\n")

# Function to count JSON entries
def count_json_entries(json_path):
    with open(json_path, 'r') as file:
        knowledge_base = json.load(file)
        return len(knowledge_base)

# Path to the JSON knowledge base
json_path = r"D:\Voice Assistants\ai_assistant\modules\knowledge_base.json"
num_entries_json = count_json_entries(json_path)
print(f"Number of entries in JSON: {num_entries_json}")

# Count entries in the new tables
num_entries_json_knowledge = session.query(JsonKnowledge).count()
num_entries_book_knowledge = session.query(BookKnowledge).count()
num_entries_research_paper_knowledge = session.query(ResearchPaperKnowledge).count()

print(f"Number of entries in JSON Knowledge Table: {num_entries_json_knowledge}")
print(f"Number of entries in Book Knowledge Table: {num_entries_book_knowledge}")
print(f"Number of entries in Research Paper Knowledge Table: {num_entries_research_paper_knowledge}")

total_entries = num_entries_json_knowledge + num_entries_book_knowledge + num_entries_research_paper_knowledge
print(f"Total number of entries in the database: {total_entries}")
