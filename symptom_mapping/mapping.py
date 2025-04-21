import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai

#temprorary model for testing
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")



def generate_llm_prompt(age,gender,symptoms, chat_history):
    formatted_symptoms = ", ".join(symptoms)

    return f"""
        You are a highly experienced medical diagnosis doctor.

        Patient:
        - Age: {age}
        - Gender: {gender}

        Symptoms: {formatted_symptoms}

        Chat History:
        {chat_history}

        Based on all the above, list the top 3 most likely medical conditions or diseases this patient may have. For each, provide:
        - Condition name
        - One-line reasoning (based on symptoms + answers)
        - Urgency level: (Low / Moderate / High)

        Make sure your answer is formatted clearly.
    """



def get_disease_symptom_mapping(age,gender,symptoms, chat_history):
    prompt = generate_llm_prompt(age,gender,symptoms, chat_history)
    response = model.generate_content(prompt)
    return response.text