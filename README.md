# Medical Diagnosis

## 🧠 Overview
This project is a medical diagnosis system that takes user symptoms, generates intelligent follow-up questions, and produces a diagnostic report. It uses a FastAPI backend and an HTML frontend interface.

---

## 📥 Clone the Repository

```bash
git clone https://github.com/pankajkumar037/Medical_diagnosis.git
cd Medical_diagnosis
```

---

## 🛠️ Create and Activate Conda Environment

```bash
conda create -n diagnosis
conda activate diagnosis
```

---

## 📦 Install Required Packages

```bash
pip install -r requirements.txt
```

---

## 🚀 Run the Server

```bash
uvicorn main:app --reload
```

The server will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---
##for help see html part>>>

## 💡 Application Flow

### 🔹 Step 1: Input Symptoms
Users input their symptoms via the HTML interface.

### 🔹 Step 2: Follow-Up Questions
Based on the symptoms, the backend generates intelligent follow-up questions.

### 🔹 Step 3: Diagnosis Report
A final medical report is generated summarizing the diagnosis.

---

## 🌐 Frontend Integration

Make sure the HTML files are correctly linked to the FastAPI backend to ensure smooth interaction during:

- Symptom input
- Follow-up Q&A
- Report generation

---



## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---
