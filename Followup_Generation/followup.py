import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

MODEL_NAME = "gemini-2.0-flash"

model_available = False 
model = None 

if google_api_key:
    genai.configure(api_key=google_api_key)
    try:
        
        genai.get_model(MODEL_NAME)
        model = genai.GenerativeModel(MODEL_NAME)
        model_available = True
      
    except Exception as e:
        print(f"Error accessing model {MODEL_NAME}: {e}")
        print("Please check your API key and model name.")


def get_followup_for_diagnosis(age, gender, symptoms, chat_history):
    """
    Generates a follow-up question (as a JSON dict) or a diagnosis indicator string,
    with an emphasis on reaching diagnosis efficiently based on history.

    Returns:
        dict: If a JSON question is generated and parsed successfully.
        str: "Ready for diagnosis" if the model indicates diagnosis is ready.
        None: If an API error occurred, the model is not available, or the
              response was an unexpected format that couldn't be parsed.
    """
   
    if not model_available or model is None:
        print("Model is not available. Cannot generate content.")
        return None

    
    prompt = f"""
        You are a top medical diagnosis expert. Your primary goal is to efficiently gather just enough information from the patient to form a likely diagnosis or differential diagnoses. Avoid asking unnecessary or repetitive questions.

        Patient is a {age}-year-old {gender.lower()} with initial symptoms: {symptoms}.
        Here is the complete conversation history so far, showing the progression of information gathering:
        {chat_history}

        Evaluate the conversation history above. Have you gathered sufficient *essential and differentiating* information to reasonably proceed towards a diagnosis? Consider the initial symptoms and the depth of detail provided in the answers.

        IF you have gathered sufficient essential information to proceed towards a diagnosis:
            Reply ONLY with the exact string: "Ready for diagnosis"
        ELSE (you still need ONE more piece of critical information):
            Ask ONE next follow-up question that is:
            - An MCQ (multiple choice) style
            - Highly relevant to the *most recent turn* and the overall goal of diagnosis.
            - Dives deeper medically to gather crucial differentiating information not yet covered.
            - Avoid repeating questions or asking about obvious information.

        Your follow-up question Answer format MUST be valid JSON like this, starting immediately with the JSON object:
        {{
        "Question":"",
        "A":"option a",
        "B":"option b",
        "C":"option c",
        "D":"option d"
        }}

        Do NOT include any extra words, markdown formatting (like ```json), or explanations before or after your response, UNLESS you are returning "Ready for diagnosis".
        """



    try:
        
        response = model.generate_content(prompt)
        raw_response = response.text.strip() 

        
        if raw_response == "Ready for diagnosis":
            return raw_response 

        
        cleaned_res = raw_response
        if cleaned_res.startswith("```json"):
             cleaned_res = cleaned_res[len("```json"):].strip()
        if cleaned_res.endswith("```"):
             cleaned_res = cleaned_res[:-len("```")].strip()

        
        try:
            
            if cleaned_res.startswith('{') and cleaned_res.endswith('}'):
                parsed_json = json.loads(cleaned_res)
                
                return parsed_json
            else:
                 
                 print(f"Warning: Model returned unexpected format (not 'Ready for diagnosis' and not JSON-like): {raw_response}")
                 return None 

        except json.JSONDecodeError as e:
            
            print(f"JSONDecodeError: Could not parse response as JSON: {e}")
            print(f"Problematic string was:\n{raw_response}")
            return None 

    except Exception as e:
        
        print(f"An API error occurred during content generation: {e}")
        return None

