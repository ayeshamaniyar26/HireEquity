import os
import logging
from groq import Groq
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def generate_job_description(role, level, domain):
    """
    Generates a job description using Groq Llama3 based on inputs.
    """
    client = get_groq_client()
    if not client:
        raise ValueError("Groq API Key not found. Please add GROQ_API_KEY to your .env file or Streamlit Secrets.")

    prompt = f"""Generate a professional, inclusive job description for {role} at {level} level in {domain} industry. Include:
- Job Summary (3 lines)
- Key Responsibilities (6 bullet points)
- Required Skills (6 bullet points)
- Nice to Have (3 bullet points)
- What We Offer (4 bullet points)
Use gender neutral language only.
Do not use any masculine or feminine coded words."""

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional HR copywriter specialized in writing inclusive, biased-free, and engaging job descriptions."
                },
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=1024
        )
        
        jd_text = response.choices[0].message.content
        return jd_text.strip()

    except Exception as e:
        logger.error(f"Error calling Groq JD Generator API: {e}")
        raise e
