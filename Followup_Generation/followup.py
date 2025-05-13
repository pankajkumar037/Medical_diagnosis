import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

MODEL_NAME = "gemini-2.0-flash"

model_available = False # Initialize availability flag
model = None # Initialize model object

if google_api_key:
    genai.configure(api_key=google_api_key)
    try:
        # Check if the model is available
        genai.get_model(MODEL_NAME)
        model = genai.GenerativeModel(MODEL_NAME)
        model_available = True
        # Optional: Configure safety settings here if needed for your application
        # model.safety_settings = {
        #     'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
        #     'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
        #     'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
        #     'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
        # }
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
    # Check model availability at the start of the function call
    if not model_available or model is None:
        print("Model is not available. Cannot generate content.")
        return None

    # --- Modified Prompt ---
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
        # Generate content
        response = model.generate_content(prompt)
        raw_response = response.text.strip() # Get the text content and remove leading/trailing whitespace

        # --- Handling Logic (same as before) ---
        # 1. Check for the specific "Ready for diagnosis" string
        if raw_response == "Ready for diagnosis":
            # print("DEBUG: Model returned 'Ready for diagnosis'") # Optional debug print
            return raw_response # Return the specific string directly

        # 2. Attempt to clean up potential markdown wrapping
        cleaned_res = raw_response
        if cleaned_res.startswith("```json"):
             cleaned_res = cleaned_res[len("```json"):].strip()
        if cleaned_res.endswith("```"):
             cleaned_res = cleaned_res[:-len("```")].strip()

        # 3. Attempt to parse the cleaned response as JSON
        try:
            # Add a basic check if it looks like JSON before parsing
            if cleaned_res.startswith('{') and cleaned_res.endswith('}'):
                parsed_json = json.loads(cleaned_res)
                # print("DEBUG: Model returned valid JSON") # Optional debug print
                return parsed_json # Return the parsed dictionary if successful
            else:
                 # It wasn't "Ready for diagnosis" and didn't look like JSON
                 print(f"Warning: Model returned unexpected format (not 'Ready for diagnosis' and not JSON-like): {raw_response}")
                 return None # Indicate unexpected format

        except json.JSONDecodeError as e:
            # Handle cases where it looked like JSON but failed parsing
            print(f"JSONDecodeError: Could not parse response as JSON: {e}")
            print(f"Problematic string was:\n{raw_response}")
            return None # Indicate parsing failure

    except Exception as e:
        # Catch broader exceptions during content generation (e.g., API errors)
        print(f"An API error occurred during content generation: {e}")
        return None

