import json
import os
import threading
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from ai_helper import analyze_performance, generate_study_tips

load_dotenv()
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
DATA_FILE = Path(__file__).with_name("students.json")
DATA_LOCK = threading.Lock()


def load_students():
    """Read saved records. A missing file starts with an empty list."""
    if not DATA_FILE.exists():
        save_students([])
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("The JSON file must contain a list of students.")
        return data
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        raise RuntimeError(
            f"Could not read students.json: {exc}. Fix or restore the JSON file."
        ) from exc


def save_students(students):
    """Save records with readable indentation."""
    temporary_file = DATA_FILE.with_suffix(".tmp")
    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(students, file, indent=2, ensure_ascii=False)
    temporary_file.replace(DATA_FILE)


def calculate_result(marks):
    total = sum(marks.values())
    average = total / len(marks) if marks else 0
    if average >= 85:
        grade = "A"
    elif average >= 70:
        grade = "B"
    elif average >= 60:
        grade = "C"
    elif average >= 50:
        grade = "D"
    else:
        grade = "F"
    return total, round(average, 2), grade


def validate_student(data, existing_id=None):
    if not isinstance(data, dict):
        raise ValueError("Please send student information in the correct format.")

    student_id = str(data.get("id", "")).strip()
    name = str(data.get("name", "")).strip()
    student_class = str(data.get("class", "")).strip()

    if not student_id or not name or not student_class:
        raise ValueError("Student ID, student name, and class/semester are required.")

    subjects = data.get("subjects")
    marks_input = data.get("marks")

    # Also accept a marks dictionary from clients that send the stored format.
    if isinstance(marks_input, dict):
        pairs = list(marks_input.items())
    else:
        if isinstance(subjects, str):
            subjects = subjects.split(",")
        if isinstance(marks_input, str):
            marks_input = marks_input.split(",")
        if not isinstance(subjects, list) or not isinstance(marks_input, list):
            raise ValueError("Enter subjects and marks as comma-separated values.")
        if len(subjects) != len(marks_input):
            raise ValueError("The number of subjects must match the number of marks.")
        pairs = list(zip(subjects, marks_input))

    if not pairs:
        raise ValueError("Add at least one subject and its marks.")

    clean_marks = {}
    for subject, mark in pairs:
        subject_name = str(subject).strip()
        if not subject_name:
            raise ValueError("Subject names cannot be empty.")
        if subject_name.casefold() in {item.casefold() for item in clean_marks}:
            raise ValueError(f"Duplicate subject name: {subject_name}.")
        try:
            numeric_mark = float(mark)
        except (TypeError, ValueError):
            raise ValueError(f"Marks for {subject_name} must be numeric.")
        if not 0 <= numeric_mark <= 100:
            raise ValueError(f"Marks for {subject_name} must be between 0 and 100.")
        clean_marks[subject_name] = int(numeric_mark) if numeric_mark.is_integer() else numeric_mark

    total, average, grade = calculate_result(clean_marks)
    return {
        "id": student_id,
        "name": name,
        "class": student_class,
        "marks": clean_marks,
        "total": total,
        "average": average,
        "grade": grade,
    }


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/students")
def get_students():
    try:
        with DATA_LOCK:
            return jsonify(load_students())
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/api/students")
def add_student():
    try:
        student = validate_student(request.get_json(silent=True))
        with DATA_LOCK:
            students = load_students()
            if any(item.get("id") == student["id"] for item in students):
                return jsonify({"error": "That Student ID already exists."}), 409
            students.append(student)
            save_students(students)
        return jsonify({"message": "Student added successfully.", "student": student}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except (RuntimeError, OSError) as exc:
        return jsonify({"error": str(exc)}), 500


@app.put("/api/students/<student_id>")
def update_student(student_id):
    try:
        data = request.get_json(silent=True) or {}
        data["id"] = student_id  # The original ID is always retained.
        student = validate_student(data)
        with DATA_LOCK:
            students = load_students()
            index = next((i for i, item in enumerate(students)
                          if item.get("id") == student_id), None)
            if index is None:
                return jsonify({"error": "Student not found."}), 404
            students[index] = student
            save_students(students)
        return jsonify({"message": "Student updated successfully.", "student": student})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except (RuntimeError, OSError) as exc:
        return jsonify({"error": str(exc)}), 500


@app.delete("/api/students/<student_id>")
def delete_student(student_id):
    try:
        with DATA_LOCK:
            students = load_students()
            updated = [item for item in students if item.get("id") != student_id]
            if len(updated) == len(students):
                return jsonify({"error": "Student not found."}), 404
            save_students(updated)
        return jsonify({"message": "Student deleted successfully."})
    except (RuntimeError, OSError) as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/api/ai/<kind>/<student_id>")
def student_ai(kind, student_id):
    if kind not in ("analyze", "tips"):
        return jsonify({"error": "Unknown AI request. Use 'analyze' or 'tips'."}), 400
    try:
        with DATA_LOCK:
            students = load_students()
            student = next((item for item in students if item.get("id") == student_id), None)
        if student is None:
            return jsonify({"error": "Student not found."}), 404

        # ai_helper deliberately sends academic details only, never name or ID.
        response = (analyze_performance(student) if kind == "analyze"
                    else generate_study_tips(student))
        return jsonify({"response": response})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception as exc:
        app.logger.exception("AI request failed")
        return jsonify({"error": f"AI request failed: {exc}"}), 502


def open_browser():
    url = "http://127.0.0.1:5000"
    try:
        browser = webbrowser.get("chrome")
        browser.open(url)
    except webbrowser.Error:
        webbrowser.open(url)


if __name__ == "__main__":
    try:
        load_students()
    except RuntimeError as error:
        print(error)
    threading.Timer(1.2, open_browser).start()
    print("AI Student Record Manager is running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
