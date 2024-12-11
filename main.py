

import os
import io
from dotenv import load_dotenv
import streamlit as st
import logging
from groq import Groq

# Configure logging
log_stream = io.StringIO()
logging.basicConfig(stream=log_stream, level=logging.INFO)
logger = logging.getLogger()

# Load environment variables from .env file
dotenv_path = '.env'
if not os.path.exists(dotenv_path):
    raise FileNotFoundError(f".env file not found at {dotenv_path}")
load_dotenv(dotenv_path)

# Initialize Groq API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable not found.")

class ExamPrepCoach:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def ask_question(self, question):
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": question,
                    }
                ],
                model="llama3-8b-8192",
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in Groq API call: {e}")
            return "Sorry, an error occurred while fetching the answer."

# Caching function outside the class
@st.cache_data(ttl=3600)
def cached_ask_question(api_key, question):
    try:
        coach = ExamPrepCoach(api_key=api_key)
        response = coach.ask_question(question)
        return response
    except Exception as e:
        logger.error(f"Error in asking question: {e}")
        return "Sorry, an error occurred while fetching the answer."

# Streamlit interface
st.title("Exam Preparation Coach")
st.write("Ask any question to prepare for your exams.")

question = st.text_input("Enter your exam question:")
subject = st.selectbox("Select subject", ["Math", "Science", "History", "Language Arts", "Other"])

if question:
    with st.spinner("Fetching the answer..."):
        answer = cached_ask_question(api_key, question)
    st.write("Answer:", answer)
    
    # Feedback section
    st.write("Was this answer helpful?")
    if st.button("Yes"):
        st.write("Thank you for your feedback!")
    if st.button("No"):
        st.write("Sorry about that. We'll try to improve.")
        
# Help Section
st.sidebar.title("Help")
st.sidebar.write("""
## How to Use
1. Enter your exam question in the text box.
2. Select the relevant subject from the dropdown.
3. Click 'Enter' to get the answer.

## Feedback
Your feedback is valuable. Please let us know if the answers are helpful.
""")

# Display logs for debugging (optional)
st.sidebar.title("Logs")
if st.sidebar.checkbox("Show logs"):
    # Get log contents from StringIO
    log_contents = log_stream.getvalue()
    st.sidebar.text_area("Logs", height=200, value=log_contents, max_chars=2000)
