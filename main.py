from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
from typing import List, Dict, Union
import os
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse


from symptom_processing.symptom import hybrid_symptom_extraction
from Followup_Generation.followup import get_followup_for_diagnosis
from symptom_mapping.mapping import get_disease_symptom_mapping
from diagnosis_report.report import final_report
from helper_functions.helper import convert_to_pdf

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


session_store = {}

class PatientInfo(BaseModel):
    name: str
    age: int
    gender: str
    symptoms: str
    # Add session_id to the model if you intend to use it from the client
    # If session_id is generated server-side, you'll handle it differently
    # session_id: str # Uncomment if session_id comes from the client


@app.post("/symptom")
async def submit_symptom(patient: PatientInfo):
    try:
        symptoms = hybrid_symptom_extraction(patient.symptoms)

        # Generate a simple session ID for demonstration if not provided by client
        # In a real application, you'd use a more robust session management
        import uuid
        session_id = str(uuid.uuid4()) # Generate a unique ID

        # Store patient data in session
        session_store[session_id] = {
            "name": patient.name, 
            "age": patient.age,
            "gender": patient.gender,
            "symptoms": symptoms,
            "chat_history": []
        }

        return {"message": "Symptoms received", "status": "symptom_submitted", "session_id": session_id}
    except Exception as e:
        print(f"Error processing symptom submission: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# You might want to add an endpoint to retrieve session data for testing
@app.get("/session/{session_id}")
async def get_session_data(session_id: str):
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_store[session_id]



@app.websocket("/followup/{session_id}")
async def followup_question(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        if session_id not in session_store:
            await websocket.send_json({"error": "Invalid session_id"})
            await websocket.close()
            return

        session = session_store[session_id]
        age, gender, symptoms = session["age"], session["gender"], session["symptoms"]
        chat_history = session["chat_history"]
        question_count = session.get("question_count", 0)

        # Send first question immediately
        if question_count == 0:
            response = get_followup_for_diagnosis(age, gender, symptoms, chat_history)
            if isinstance(response, dict) and "Question" in response:
                session["question_count"] = 1
                session["last_options"] = response  # Save last options for later
                chat_history.append({"bot": response["Question"]})
                await websocket.send_json({
                    "question": response["Question"],
                    "options": [
                        {"key": k, "value": v}
                        for k, v in response.items() if k in ["A", "B", "C", "D"]
                    ],
                    "status": "waiting_for_answer"
                })
            else:
                await websocket.send_json({"error": "Unable to generate initial question."})
                await websocket.close()
                return

        # Handle answers and continue loop
        while True:
            client_msg = await websocket.receive_text()
            client_msg = client_msg.strip().upper()

            last_response = session.get("last_options", {})
            user_answer = last_response.get(client_msg, client_msg)

            # Append actual option value if valid key
            chat_history.append({"user": user_answer})

            response = get_followup_for_diagnosis(age, gender, symptoms, chat_history)

            if isinstance(response, str) and "ready for diagnosis" in response.lower():
                await websocket.send_json({
                    "message": "Diagnosis is ready",
                    "status": "ready_for_diagnosis"
                })
                await websocket.close()
                break

            elif isinstance(response, dict) and "Question" in response:
                session["question_count"] += 1
                session["last_options"] = response  # Update last options

                if session["question_count"] > 10:
                    await websocket.send_json({
                        "message": "Reached max questions, moving to diagnosis.",
                        "status": "ready_for_diagnosis"
                    })
                    await websocket.close()
                    break

                chat_history.append({"bot": response["Question"]})
                await websocket.send_json({
                    "question": response["Question"],
                    "options": [
                        {"key": k, "value": v}
                        for k, v in response.items() if k in ["A", "B", "C", "D"]
                    ],
                    "status": "waiting_for_answer"
                })

            elif isinstance(response, str) and "error" in response.lower():
                await websocket.send_json({"error": response})
            else:
                await websocket.send_json({"error": "Unexpected response format"})

    except WebSocketDisconnect:
        print(f"Session {session_id} disconnected.")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()



@app.get("/generate_report/{session_id}")
async def generate_report(session_id: str):
    try:
        if session_id not in session_store:
            raise HTTPException(status_code=404, detail="Session not found")

        session = session_store[session_id]
        name = session.get("name", "Unknown")
        age = session["age"]
        gender = session["gender"]
        symptoms = session["symptoms"]
        chat_history = session["chat_history"]

        # Get mapped diseases and final report
        mapped_diseases = get_disease_symptom_mapping(age, gender, symptoms, chat_history)
        report = final_report(age, gender, symptoms, chat_history, mapped_diseases)

        # Generate the PDF
        output_pdf_path = "medical_report.pdf"
        success = convert_to_pdf(report, output_pdf_path)

        if success:
            return FileResponse(output_pdf_path, filename="medical_report.pdf", media_type='application/pdf')
        else:
            raise HTTPException(status_code=500, detail="Failed to generate PDF")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

