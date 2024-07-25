# main.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow INFO and WARNING messages

from modules.nlp import NLPManager

def main():
    nlp_manager = NLPManager()

    # Example of questions in the expanded knowledge base and external data queries
    questions = [
        "What is AI?",
        "What is the capital of France?",
        "Who developed the theory of relativity?",
        "What is the largest ocean on Earth?",
        "What is the speed of light?",
        "Who wrote '1984'?",
        "What is the highest waterfall in the world?",
        "What is the weather in Sultanpur Uttar Pradesh India?",
        "What is the news about technology?"
    ]

    for question in questions:
        answer = nlp_manager.manage_dialogue(question, context=None)
        print(f"Question: {question}\nAnswer: {answer}\n")

if __name__ == "__main__":
    main()