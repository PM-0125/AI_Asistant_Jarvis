import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow INFO and WARNING messages

from modules.nlp import NLPManager

def main():
    nlp_manager = NLPManager()

    # Example Questions
    questions = [
        {"question": "What is AI?", "language": "en"},
        {"question": "धृतराष्ट्र उवाच | धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः | मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय ", "language": "sa"},
        {"question": "What is the weather in Warsaw Poland?", "language": "en"},
        {"question": "What is the news about Elon Musk?", "language": "en"}
    ]

    for q in questions:
        print(f"Question: {q['question']}")
        print(f"Answer: {nlp_manager.answer_question(q['question'], q['language'])}")
        print("-" * 50)

    # Example Conversation
    conversation_starters = [
        "Tell me about Trading.",
        "What do you think about Machine Learning?",
        "How can I improve accuracy of machine learning model?"
    ]

    for starter in conversation_starters:
        print(f"Conversation: {starter}")
        print(f"Response: {nlp_manager.have_conversation(starter)}")
        print("-" * 50)

if __name__ == "__main__":
    main()
