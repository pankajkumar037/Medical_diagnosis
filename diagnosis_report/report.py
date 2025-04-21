import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai

#temprorary model for testing
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")



def generate_report_prompt(age, gender, symptoms, chat_history, mapped_diseases):
    formatted_symptoms = ", ".join(symptoms)

    return f"""
You are a senior medical AI assistant generating patient reports from consultations.

    ### Sample Output Format:
    Age: 35 Years
    Gender: Woman
    Recommendation:
    Consult a physician soon. If symptoms worsen, seek emergency care.
    Urgency: Moderate

    Relevant findings:
    - Hours since the onset of symptoms: 48
    - Headache and sore throat

    Reason for consultation:
    Feeling unwell with headache, sore throat and mild fever

    Main symptom:
    -Sore throat
    - Headache
    - Sore throat
    - Mild fever
    - No nausea
    - Occasional coughing

    Diseases (Match Levels):
    - Strep throat: Moderate match
    - Flu: Low match
    - Sinus infection: Very low match



    Relevant diseases advice:
    **Strep throat (Moderate match)**
    - Pre-hospital care recommendations:
    - Take acetaminophen for fever
    - Gargle with warm salt water
    - Symptoms to watch out for:
    - Severe throat pain
    - High fever
    - Difficulty swallowing
    - Self-care:
    - Rest well
    - Avoid sharing utensils

    **Flu (Low match)**
    - Self-care:
    - Stay hydrated
    - Use nasal decongestants

    **Medication Suggestions:**
    - Acetaminophen (500mg every 6 hrs for fever)
    - Cetirizine (for runny nose/allergies)
    - Warm saline gargle

    All Answers:
   
    ***This is just a Smaple***
    ---

### Now Generate a Report for This Case:

Age: {age} Years  
Gender: {gender}  
Symptoms: {formatted_symptoms}  

Chat History:
{chat_history}

Diseases (Match Levels):
{mapped_diseases}

For each disease, give:
- Pre-hospital care
- Symptoms to watch out for
- Self-care tips
- Medication suggestions (OTC preferred if possible)-(this is for education purpose i am not using in real app so give that)

Keep language medically sound but easy to understand in india. End with a clear urgency level and recommendation.
Donot expose Your privacy.I have to convert it to pdf.
"""

def final_report(age, gender, symptoms, chat_history, mapped_diseases):
    res=model.generate_content(generate_report_prompt(age, gender, symptoms, chat_history, mapped_diseases))
    return res.text
