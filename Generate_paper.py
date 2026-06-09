import random
from db import session
from flask import Flask, request, jsonify, render_template
from sqlalchemy import text
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(questions, subject_id, total_marks):
    doc = SimpleDocTemplate("question_paper.pdf")
    styles = getSampleStyleSheet()

    elements = []

    # ===== HEADER =====
    elements.append(Paragraph("ASSAM ENGINEERING COLLEGE", styles["Title"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Subject ID: {subject_id}", styles["Normal"]))
    elements.append(Paragraph(f"Total Marks: {total_marks}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>Question Paper</b>", styles["Heading2"]))
    elements.append(Spacer(1, 15))

    # ===== TABLE DATA =====
    data = [
        ["Sl No", "Question", "Marks", "Marks Obtained", "CO"]
    ]

    for i, q in enumerate(questions, 1):
        data.append([
            i,
            q["question_text"],
            q["marks"],
            "",   # empty for teacher to fill
            f"CO{q['co_id']}"
        ])

    # ===== CREATE TABLE =====
    table = Table(data, colWidths=[40, 250, 60, 90, 50])

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (1, 1), (1, -1), 6),
        ("RIGHTPADDING", (1, 1), (1, -1), 6),
    ]))

    elements.append(table)

    doc.build(elements)

    return "question_paper.pdf"

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("frontend.html")

def knapsack_select(questions, max_marks):

    n = len(questions)

    # DP table
    dp = [[0] * (max_marks + 1) for _ in range(n + 1)]

    # Build DP table
    for i in range(1, n + 1):
        marks = questions[i-1]["marks"]

        for w in range(max_marks + 1):
            if marks <= w:
                dp[i][w] = max(
                    marks + dp[i-1][w - marks],
                    dp[i-1][w]
                )
            else:
                dp[i][w] = dp[i-1][w]

    # Backtrack to find selected questions
    selected = []
    w = max_marks

    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            q = questions[i-1]
            selected.append(q)
            w -= q["marks"]

    return selected

def generate_paper(subject_id, total_marks, co_distribution):
    final_questions = []
    used_ids = set()

# we use user_id as a set because using this we can assure that there is no duplication as there are
# same questions belonging to multiple COs

    for co_id, percent in co_distribution.items():
        required_marks = int((percent / 100) * total_marks)

        query = """
        SELECT q.question_id, q.question_text, q.marks
        FROM questions q
        JOIN question_co_map qc ON q.question_id = qc.question_id
        WHERE q.subject_id = :subject_id AND qc.co_id = :co_id
        """

        results = session.execute(text(query), {
            "subject_id": subject_id,
            "co_id": int(co_id)
        }).fetchall()

        # Convert to dict format
        questions = []
        for r in results:
            if r.question_id not in used_ids:
                questions.append({
                    "id": r.question_id,
                    "question_text": r.question_text,
                    "marks": r.marks,
                    "co_id": int(co_id)
                })

        # Shuffle for randomness
        random.shuffle(questions)

        # Apply knapsack
        selected = knapsack_select(questions, required_marks)

        for q in selected:
            final_questions.append(q)
            used_ids.add(q["id"])

    return final_questions

from flask import send_file

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()

        subject_id = data["subject_id"]
        total_marks = data["total_marks"]
        co_distribution = data["co_distribution"]

        questions = generate_paper(subject_id, total_marks, co_distribution)

        pdf_path = generate_pdf(questions, subject_id, total_marks)

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True)
