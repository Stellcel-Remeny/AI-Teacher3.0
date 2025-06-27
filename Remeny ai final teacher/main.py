from flask import Flask, render_template, request, jsonify
import json
import re
import difflib

app = Flask(__name__)

# Helper function to clean and normalize text


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text


# Load your prewritten answers
with open("data/answers.json", "r", encoding="utf-8") as f:
    knowledge_base = json.load(f)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    question = clean_text(request.json.get("message", "").strip())
    all_qna = {}

    # Flatten all Q&A pairs into one dictionary
    for class_data in knowledge_base.values():
        for subject_data in class_data.values():
            for key, answer in subject_data.items():
                all_qna[key] = answer

    # Step 1: Try exact match
    for key in all_qna:
        if clean_text(key) in question:
            return jsonify({"response": all_qna[key]})

    # Step 2: Fuzzy match using similarity score
    best_match = difflib.get_close_matches(
        question, [clean_text(k) for k in all_qna.keys()], n=1, cutoff=0.5)

    if best_match:
        matched_key = next(
            k for k in all_qna if clean_text(k) == best_match[0])
        return jsonify({"response": all_qna[matched_key]})

    return jsonify({"response": "❗ Sorry, I don't know that yet. Renemy AI is still learning."})


app.run(debug=True, port=5000)
