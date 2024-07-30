from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import json
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, stop_after_attempt, wait_fixed
import urllib.parse  # Importing urllib.parse for URL encoding
import shutil
import re
from nltk.tokenize import sent_tokenize

# Configure pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

Base = declarative_base()

class JsonKnowledge(Base):
    __tablename__ = 'json_knowledge'
    id = Column(Integer, primary_key=True)
    question = Column(String, unique=True)
    answer = Column(Text)
    source = Column(String)

class BookKnowledge(Base):
    __tablename__ = 'book_knowledge'
    id = Column(Integer, primary_key=True)
    document_title = Column(String)
    author = Column(String)
    sentence = Column(Text)
    source = Column(String)

class ResearchPaperKnowledge(Base):
    __tablename__ = 'research_paper_knowledge'
    id = Column(Integer, primary_key=True)
    document_title = Column(String)
    author = Column(String)
    sentence = Column(Text)
    source = Column(String)

# Encode the password
username = 'your username'
password = 'password'
encoded_password = urllib.parse.quote_plus(password)

# Construct the connection string with the encoded password
connection_string = f'postgresql://{username}:{encoded_password}@localhost/knowledge_db'

# Update the engine to use PostgreSQL
engine = create_engine(connection_string)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

@retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
def add_json_knowledge(session, question, answer, source):
    try:
        # Sanitize the question and answer to remove null characters
        question = question.replace('\x00', '')
        answer = answer.replace('\x00', '')
        if not session.query(JsonKnowledge).filter_by(question=question).first():
            new_entry = JsonKnowledge(question=question, answer=answer, source=source)
            session.add(new_entry)
            session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Error adding knowledge: {e}")
        raise

def load_knowledge_base(json_path):
    session = Session()
    try:
        with open(json_path, 'r') as file:
            knowledge_base = json.load(file)
            for question, answer in knowledge_base.items():
                add_json_knowledge(session, question, answer, 'json')
    except Exception as e:
        session.rollback()
        logging.error(f"Error loading knowledge base: {e}")
    finally:
        session.close()

# Load existing knowledge base
logging.info("Loading knowledge base from JSON")
json_path = r"D:\Voice Assistants\ai_assistant\modules\knowledge_base.json"
load_knowledge_base(json_path)

def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

def extract_text_from_image(image_path):
    return pytesseract.image_to_string(Image.open(image_path))

def process_document(document_path, document_type='pdf'):
    if document_type == 'pdf':
        text = extract_text_from_pdf(document_path)
    elif document_type == 'image':
        text = extract_text_from_image(document_path)
    
    # Sanitize the text to remove null characters
    text = text.replace('\x00', '')
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    sentences = sent_tokenize(text)  # Use NLTK's sentence tokenizer
    return sentences

def move_processed_file(file_path, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    shutil.move(file_path, os.path.join(destination_folder, os.path.basename(file_path)))

def add_book_knowledge(session, document_title, author, sentence, source):
    try:
        # Sanitize the sentence to remove null characters
        sentence = sentence.replace('\x00', '')
        new_entry = BookKnowledge(document_title=document_title, author=author, sentence=sentence, source=source)
        session.add(new_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Error adding book knowledge: {e}")
        raise

def add_research_paper_knowledge(session, document_title, author, sentence, source):
    try:
        # Sanitize the sentence to remove null characters
        sentence = sentence.replace('\x00', '')
        new_entry = ResearchPaperKnowledge(document_title=document_title, author=author, sentence=sentence, source=source)
        session.add(new_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Error adding research paper knowledge: {e}")
        raise

def process_documents_in_folder(folder, document_type, target_table):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if filename.endswith(".pdf") and document_type == 'pdf':
                logging.info(f"Submitting PDF for processing: {file_path}")
                futures.append(executor.submit(add_document_to_knowledge_base, file_path, 'pdf', target_table))
            elif filename.endswith((".png", ".jpg", ".jpeg")) and document_type == 'image':
                logging.info(f"Submitting Image for processing: {file_path}")
                futures.append(executor.submit(add_document_to_knowledge_base, file_path, 'image', target_table))
        for future in futures:
            future.result()

def add_document_to_knowledge_base(document_path, document_type='pdf', target_table='book'):
    session = Session()
    try:
        sentences = process_document(document_path, document_type)
        document_title = os.path.basename(document_path)
        author = "Unknown"  # You can extract author information if available
        if target_table == 'book':
            for i, sentence in enumerate(sentences):
                add_book_knowledge(session, document_title, author, sentence.strip(), 'book')
        elif target_table == 'research_paper':
            for i, sentence in enumerate(sentences):
                add_research_paper_knowledge(session, document_title, author, sentence.strip(), 'research_paper')
        # Move the file to the processed folder after successful processing
        move_processed_file(document_path, os.path.join(os.path.dirname(document_path), 'processed'))
    except Exception as e:
        session.rollback()
        logging.error(f"Error adding document to knowledge base: {e}")
    finally:
        session.close()

# Process documents in batches
book_folders = [r"D:\Voice Assistants\ai_assistant\modules\books"]
research_paper_folders = [r"D:\Voice Assistants\ai_assistant\modules\research_papers"]

for folder in book_folders:
    process_documents_in_folder(folder, 'pdf', 'book')
    process_documents_in_folder(folder, 'image', 'book')

for folder in research_paper_folders:
    process_documents_in_folder(folder, 'pdf', 'research_paper')
    process_documents_in_folder(folder, 'image', 'research_paper')
