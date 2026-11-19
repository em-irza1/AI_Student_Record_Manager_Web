"""Groq-powered academic feedback. Student identity is never sent to Groq."""
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def get_api_key():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key or key == "your_actual_api_key":
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add your Groq API key to the .env file, then restart the app."
        )
    return key


def choose_model(client):
    """Use GROQ_MODEL when configured; otherwise find an available text model."""
    configured = os.getenv("GROQ_MODEL", "").strip()
    if configured:
        return configured

    try:
        available = client.models.list()
        model_ids = [getattr(model, "id", "") for model in available.data]
        # Avoid speech, moderation, embedding, and image-only models.
        excluded = ("whisper", "guard", "embed", "vision", "audio", "tts")
        candidates = [name for name in model_ids
                      if name and not any(word in name.lower() for word in excluded)]
        if candidates:
            return candidates[0]
    except Exception as exc:
        raise RuntimeError(
            "Could not discover an available Groq model. Set GROQ_MODEL in .env to a model "
            f"available to your account. Details: {exc}"
        ) from exc

    raise RuntimeError(
        "No suitable text-generation model was found. Set GROQ_MODEL in .env to a supported model."
    )


def ask_ai(prompt):
    client = Groq(api_key=get_api_key())
    model = choose_model(client)
    try:
        result = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a supportive academic study assistant. Be specific, practical, "
                        "age-appropriate, encouraging, and concise. Do not make assumptions "
                        "about a student's identity or personal life."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=900,
        )
        answer = result.choices[0].message.content
        if not answer:
            raise RuntimeError("The AI returned an empty response. Please try again.")
        return answer.strip()
    except Exception as exc:
        message = str(exc)
        lower = message.lower()
        if "model" in lower and ("not found" in lower or "does not exist" in lower):
            raise RuntimeError(
                f"The configured model '{model}' is unavailable. Update GROQ_MODEL in .env "
                "to a model enabled for your Groq account."
            ) from exc
        if "connection" in lower or "timeout" in lower or "network" in lower:
            raise RuntimeError("Could not connect to Groq. Check your internet connection and try again.") from exc
        raise RuntimeError(f"Groq API error: {message}") from exc


def describe_student(student):
    """Create a privacy-safe academic summary containing only approved fields."""
    academic_data = {
        "class_or_semester": student.get("class", ""),
        "subjects_and_marks": student.get("marks", {}),
        "total_marks": student.get("total", 0),
        "average_percentage": student.get("average", 0),
        "grade": student.get("grade", ""),
    }
    return academic_data


def analyze_performance(student):
    academic_data = describe_student(student)
    prompt = (
        "Analyze this student's academic performance using only the data below.\n"
        f"Academic data: {academic_data}\n\n"
        "Respond with clear headings: Overall Summary, Strong Subjects, Subjects to Improve, "
        "Practical Improvement Steps. Identify strengths and weaker subjects from the marks. "
        "Keep the advice realistic and supportive. Do not invent missing information."
    )
    return ask_ai(prompt)


def generate_study_tips(student):
    academic_data = describe_student(student)
    prompt = (
        "Create personalized study guidance based only on this academic data:\n"
        f"{academic_data}\n\n"
        "Include: (1) a simple Monday-to-Sunday weekly study plan, (2) targeted suggestions "
        "for weaker subjects, (3) short daily study tips, (4) practical learning methods, "
        "and (5) one brief encouraging closing message. Keep the plan balanced and realistic."
    )
    return ask_ai(prompt)
