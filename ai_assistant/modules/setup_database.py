# setup_database.py

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

# Configure pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

Base = declarative_base()

class Knowledge(Base):
    __tablename__ = 'knowledge'
    id = Column(Integer, primary_key=True)
    question = Column(String, unique=True)
    answer = Column(Text)

# Encode the password
username = 'your username'
password = 'yourpassword'
encoded_password = urllib.parse.quote_plus(password)

# Construct the connection string with the encoded password
connection_string = f'postgresql://{username}:{encoded_password}@localhost/knowledge_db'

# Update the engine to use PostgreSQL
engine = create_engine(connection_string)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

@retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
def add_knowledge(session, question, answer):
    try:
        # Sanitize the question and answer to remove null characters
        question = question.replace('\x00', '')
        answer = answer.replace('\x00', '')
        if not session.query(Knowledge).filter_by(question=question).first():
            new_entry = Knowledge(question=question, answer=answer)
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
                add_knowledge(session, question, answer)
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
    sentences = text.split(". ")
    return sentences

def move_processed_file(file_path, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    shutil.move(file_path, os.path.join(destination_folder, os.path.basename(file_path)))

def add_document_to_knowledge_base(document_path, document_type='pdf'):
    session = Session()
    try:
        sentences = process_document(document_path, document_type)
        for i, sentence in enumerate(sentences):
            question = f"Information from {os.path.basename(document_path)} - sentence {i+1}"
            add_knowledge(session, question, sentence.strip())
        # Move the file to the processed folder after successful processing
        move_processed_file(document_path, os.path.join(os.path.dirname(document_path), 'processed'))
    except Exception as e:
        session.rollback()
        logging.error(f"Error adding document to knowledge base: {e}")
    finally:
        session.close()

def process_documents_in_folder(folder, document_type):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if filename.endswith(".pdf") and document_type == 'pdf':
                logging.info(f"Submitting PDF for processing: {file_path}")
                futures.append(executor.submit(add_document_to_knowledge_base, file_path, 'pdf'))
            elif filename.endswith((".png", ".jpg", ".jpeg")) and document_type == 'image':
                logging.info(f"Submitting Image for processing: {file_path}")
                futures.append(executor.submit(add_document_to_knowledge_base, file_path, 'image'))
        for future in futures:
            future.result()

# Process documents in batches
folders = [r"D:\Voice Assistants\ai_assistant\modules\books", r"D:\Voice Assistants\ai_assistant\modules\research_papers"]

for folder in folders:
    process_documents_in_folder(folder, 'pdf')
    process_documents_in_folder(folder, 'image')
