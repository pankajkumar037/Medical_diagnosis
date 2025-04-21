import streamlit as st
from typing import List, Tuple
import pyarrow.lib as _lib
import os
from dotenv import load_dotenv
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")

import google.generativeai as genai

genai.configure(api_key=google_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

from symptom_processing.symptom import hybrid_symptom_extraction


if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'awaiting_question' not in st.session_state:
    st.session_state.awaiting_question = True


with st.sidebar:
    st.header(" Patient Info")
    symptom_input = st.text_input("Enter symptoms")
    age = st.number_input("Age", min_value=0, max_value=120, value=20)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0)


symptoms = hybrid_symptom_extraction(symptom_input)


def format_history(history):
    formatted = ""
    for i, (q, a) in enumerate(history):
        formatted += f"{i+1}. Q: {q}\n   A: {a}\n"
    return formatted


def ask_followup(symptoms, chat_history):
    prompt = f"""
        You are a top medical diagnosis expert.
        Patient is a {age}-year-old {gender.lower()} with symptoms: {symptoms}.
        Here is the conversation so far:
        {format_history(chat_history)}

        Ask ONE next follow-up question that is:
        - An MCQ (multiple choice) style
        - Highly relevant to last answer and question
        - Should dive deeper medically
        - If enough information is gathered, reply ONLY with: "Ready for diagnosis"

        Format:
        Q: <your question>
        A) <option_a>
        B) <option_b>
        C) <option_c>
        D) <option_d>

        Don't add extra explanation.
            """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating response: {e}"


def diagnosis_loop(symptoms):
    st.title("🩺 AI Medical Diagnosis")

    if st.session_state.chat_history:
        for i, (q, a) in enumerate(st.session_state.chat_history):
            st.markdown(f"**{i+1}. {q}** \n*Answer:* {a}")

    if "Ready for diagnosis" in [q for q, _ in st.session_state.chat_history if "Ready for diagnosis" in q]:
        st.success("Thanks for your answers diagnosis...")
        return

    if len(st.session_state.chat_history) < 10:
        question_response = ask_followup(symptoms, st.session_state.chat_history)
        if "Ready for diagnosis" in question_response:
            st.session_state.chat_history.append((question_response, ""))
            st.rerun()
        else:
            parts = question_response.split("\n")
            question_text = parts[0].replace("Q:", "").strip()
            options = [part.split(") ", 1)[1].strip() for part in parts[1:] if ")" in part and len(part.split(") ", 1)) == 2]

            st.markdown(f"**{question_text}**")
            if options:
                choice = st.radio("Choose your answer:", options, key=f"q{len(st.session_state.chat_history)}")
                if st.button("Submit Answer"):
                    st.session_state.chat_history.append((question_text, choice))
                    st.rerun()
            else:
                st.warning("⚠️please press enter to proceed")
                st.text(f"Raw response: {question_response}") 
    else:
        st.info(" Proceeding to diagnosis...")

diagnosis_loop(symptoms)

from symptom_mapping.mapping import get_disease_symptom_mapping
from diagnosis_report.report import final_report

if len(st.session_state.chat_history) == 10:

    
    formatted_chat = "\n".join([f"{i+1}. Question: {q}\n   Answer: {a}" for i, (q, a) in enumerate(st.session_state.chat_history)])

    mapped_diseases = get_disease_symptom_mapping(age=age,gender=gender,symptoms=symptoms, chat_history=formatted_chat)


    report=final_report(age, gender, symptoms, formatted_chat, mapped_diseases)
    st.write(report)
    from xhtml2pdf import pisa


    def convert_to_pdf(text, output_path):
        html = f"<pre>{text}</pre>"  
        with open(output_path, "w+b") as result_file:
            pisa_status = pisa.CreatePDF(html, dest=result_file)
        return not pisa_status.err



    
    output_pdf_path = "medical_report.pdf"
    success = convert_to_pdf(report, output_pdf_path)

    if success:
        st.success("PDF generated successfully!")
        with open(output_pdf_path, "rb") as file:
            st.download_button(label="Download PDF", data=file, file_name="medical_report.pdf", mime="application/pdf")
    else:
        st.error("Failed to generate PDF.")