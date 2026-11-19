# AI Student Record Manager

A beginner-friendly Flask web application for managing student marks, calculating results, and generating personalized academic feedback with the Groq API.

## Features

- Add, view, update, search, and delete student records.
- Automatically calculate total marks, average percentage, and grade.
- Save records in `students.json` so they remain after restarting.
- Ask Groq AI to analyze subject performance and create weekly study tips.
- Keep student names and IDs private: the AI receives only class/semester, subjects, marks, total, average, and grade.
- Responsive green-and-white interface.

## Technologies

Python 3, Flask, HTML, CSS, JavaScript Fetch API, JSON, Groq Python SDK, and python-dotenv.

## Folder structure

```text
AI_Student_Record_Manager_Web/
├── app.py
├── ai_helper.py
├── students.json
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
└── templates/
    └── index.html
```

## 1. Install Python

Install Python 3 from the official Python website. During Windows installation, enable **Add Python to PATH**. Open a new VS Code terminal and check:

```powershell
python --version
```

## 2. Open the project

Open the `AI_Student_Record_Manager_Web` folder in VS Code. In its terminal, make sure the current directory is the folder containing `app.py`.

## 3. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

If PowerShell blocks activation, use Command Prompt in the VS Code terminal:

```bat
venv\Scripts\activate.bat
```

## 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 5. Configure the Groq API key

1. Create an API key in your Groq account.
2. In the project root, make a copy of `.env.example` and name the copy `.env`.
3. Open `.env` and replace the example value:

```env
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=
```

Leave `GROQ_MODEL` blank to let the program try to discover a text-generation model available to your account. If discovery is unavailable or you prefer a particular model, enter a model ID currently enabled for your Groq account. Do not share your key or upload `.env` to GitHub. The `.gitignore` file excludes it.

## 6. Run the application

```powershell
python app.py
```

The app runs locally at:

**http://127.0.0.1:5000**

The program attempts to open Chrome automatically. If it does not, open the address above manually. Keep the terminal open while using the app. Press `Ctrl+C` in the terminal to stop the server.

## 7. How to use it

1. **Add:** Enter a unique Student ID, name, class/semester, comma-separated subjects, and matching comma-separated marks. Example subjects: `Python, Mathematics, English`. Example marks: `88, 76, 92`.
2. **Select:** Click a row in the records table. Its information appears in the form.
3. **Update:** Edit the selected student's details and click **Update Selected**. The original Student ID is retained.
4. **Delete:** Select a row and click **Delete Selected**. Confirm the deletion.
5. **Search:** Search by student name or ID. Click **Show All** to restore the full list.
6. **Analyze Performance:** Select a student and click the button for AI-generated strengths, improvement areas, and practical steps.
7. **Generate Study Tips:** Select a student and request a personalized weekly plan and study recommendations.

## Result calculation

The total is the sum of all subject marks. Average percentage is total divided by the number of subjects. Grades are:

- A: 85% or above
- B: 70% to below 85%
- C: 60% to below 70%
- D: 50% to below 60%
- F: below 50%

For the sample marks 88, 76, 92, and 81, the total is 337, average is 84.25%, and grade is B.

## Common errors

- **`GROQ_API_KEY is missing`:** Check that `.env` is in the same folder as `app.py`, the variable is spelled `GROQ_API_KEY`, and you restarted the app after editing it.
- **Model not found / unavailable:** Set `GROQ_MODEL` to a text-generation model currently available to your Groq account. Model availability can change.
- **Could not connect to Groq:** Check your internet connection and try again.
- **ModuleNotFoundError:** Activate `venv` and run `python -m pip install -r requirements.txt`.
- **Port 5000 is already in use:** Close the other local Flask app using port 5000, then run this project again.
- **Could not read students.json:** Check that the file contains valid JSON and begins with `[` and ends with `]`. Restore the sample structure if it was accidentally changed.

## Data and privacy notes

Student records are stored locally in `students.json`. Back up this file if you need to preserve records elsewhere. The AI functions intentionally construct a separate academic-only payload and do not include student names or IDs. Use fictional/sample records for demonstrations unless you have permission to process real student academic information.
