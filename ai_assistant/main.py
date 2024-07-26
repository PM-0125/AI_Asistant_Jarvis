# main.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow INFO and WARNING messages

# main.py

from modules.nlp import NLPManager

def main():
    nlp_manager = NLPManager()

    # Example of questions in the expanded knowledge base
    questions = [
        "What is AI?",
        "What is the capital of France?",
        "Who developed the theory of relativity?",
        "What is the largest ocean on Earth?",
        "What is the speed of light?",
        "Who wrote '1984'?",
        "What is the highest waterfall in the world?",
        "Who invented the telephone?",
        "What is the smallest planet in our solar system?",
        "Who wrote 'War and Peace'?",
        "What is a black hole?",
        "Who is the author of 'The Hobbit'?",
        "What is the capital of Brazil?",
        "Who wrote 'The Divine Comedy'?",
        "What is the Great Wall of China?",
        "Who discovered electricity?",
        "What is the capital of Japan?",
        "Who invented the airplane?",
        "What is the national sport of Japan?",
        "Who wrote 'Les Misérables'?",
        "What is the largest organ in the human body?",
        "Who is known as the father of medicine?",
        "What is the smallest unit of life?",
        "Who discovered the law of gravity?",
        "What is the tallest animal in the world?",
        "What is the main ingredient in tofu?",
        "Who wrote 'The Art of War'?",
        "What is the chemical symbol for lead?",
        "What is the capital of Colombia?",
        "What is the longest river in Europe?",
        "What is the weather in Sultanpur Uttar Pradesh India?",
        "What is the news about Elon Musk?"
    ]

    for question in questions:
        answer = nlp_manager.manage_dialogue(question, context=None)
        print(f"Question: {question}\nAnswer: {answer}\n")

if __name__ == "__main__":
    main()




