import spacy
import scispacy
from spacy import displacy
import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai

#temprorary model for testing
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")


def extract_medical_terms(text):
    nlp = spacy.load("en_core_sci_sm")
    doc = nlp(text)
    medical_entities = [ent.text.lower() for ent in doc.ents]
    return list(set(medical_entities))  


def clarify_symptoms(text):
    prompt = f"""You are a medical expert. Extract only medical symptoms from this sentence:
    "{text}".
    Just return a list of symptoms like ['headache', 'fever']
    """
    response = model.generate_content(prompt)
    return response.text


def hybrid_symptom_extraction(text):
    sci_terms = extract_medical_terms(text)
    print(sci_terms)
    try:
        llm_terms = eval(clarify_symptoms(text))  
        print(llm_terms)
    except:
        llm_terms = []
    
    return list(set(sci_terms + llm_terms))  

