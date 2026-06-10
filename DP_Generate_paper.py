import random
import re
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

from playwright.sync_api import sync_playwright
from db import get_session
from flask import Flask, request, jsonify, render_template
from add_question import add_question_bp
from sqlalchemy import text
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, Flowable, KeepInFrame
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Frame

class Square(Flowable):
    def __init__(self, size=10):
        super().__init__()
        self.size = size

    def draw(self):
        self.canv.rect(0, 0, self.size, self.size, fill=1)

class MarkBoxes(Flowable):
    def __init__(self, size=14, gap=8):
        super().__init__()
        self.size = size
        self.gap = gap
        self.width = (2 * size) + gap
        self.height = size

    def draw(self):
        # center boxes inside available space
        # Start drawing the Boxes from X = 0
        x_offset = 0
        # First Box creation 
        self.canv.rect(x_offset, 0, self.size, self.size, fill=0)
        # Second Box creation
        self.canv.rect(x_offset + self.size + self.gap, 0, self.size, self.size, fill=0)

class RollNoBoxes(Flowable):
    def __init__(self, size=12, gap=4):
        super().__init__()
        self.size = size
        self.gap = gap
        # 2 boxes, slash gap, 3 boxes
        self.width = (5 * size) + (6 * gap)
        self.height = size

    def draw(self):
        x = 0
        # first two boxes
        for _ in range(2):
            self.canv.rect(x, 0, self.size, self.size, fill=0)
            x += self.size + self.gap
        # draw slash
        self.canv.setFont("Helvetica", 10)
        self.canv.drawString(x, 0, "/")
        x += self.gap * 2
        # last three boxes
        for _ in range(3):
            self.canv.rect(x, 0, self.size, self.size, fill=0)
            x += self.size + self.gap


class SemesterBoxes(Flowable):
    def __init__(self, size=12, gap=4, digits=1):
        super().__init__()
        self.size = size
        self.gap = gap
        self.digits = digits
        self.width = (digits * size) + ((digits - 1) * gap)
        self.height = size

    def draw(self):
        x = 0
        for _ in range(self.digits):
            self.canv.rect(x, 0, self.size, self.size, fill=0)
            x += self.size + self.gap

# Corner markers using canvas later
def draw_corners(canvas, doc):
    width, height = A4
    size = 12

    margin_x = 15
    margin_y = 15

    # top-left
    canvas.rect(margin_x, height - margin_y - size, size, size, fill=1)
    # top-right
    canvas.rect(width - margin_x - size, height - margin_y - size, size, size, fill=1)
    # bottom-left
    canvas.rect(margin_x, margin_y, size, size, fill=1)
    # bottom-right
    canvas.rect(width - margin_x - size, margin_y, size, size, fill=1)

# Requires:
# pip install playwright
# playwright install
def latex_to_png(latex):
    try:
        os.makedirs("temp", exist_ok=True)

        filename = f"temp/{uuid.uuid4().hex}.png"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <link rel='stylesheet'
            href='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css'>

            <script defer
            src='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js'></script>

            <script defer
            src='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js'></script>
<style>
body {{
    margin: 0;
    padding: 2px;
    background: white;
}}

#formula {{
    font-size: 18px;
    display: inline-block;
}}
</style>
        </head>
        <body>
            <div id='formula'>$$ {latex.strip()} $$</div>

            <script>
            document.addEventListener('DOMContentLoaded', function() {{
                renderMathInElement(document.body);
            }});
            </script>
        </body>
        </html>
        """

        html_file = f"temp/{uuid.uuid4().hex}.html"

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html)

        print("PLAYWRIGHT_BROWSERS_PATH =", os.getenv("PLAYWRIGHT_BROWSERS_PATH"))

        with sync_playwright() as p:
            print("Chromium executable:", p.chromium.executable_path)

            browser = p.chromium.launch(
                executable_path=p.chromium.executable_path,
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )

            page = browser.new_page(
                viewport={"width": 800, "height": 200}
            )
            page.goto("file://" + os.path.abspath(html_file))
            page.wait_for_timeout(1000)
            page.locator("#formula").screenshot(
                path=filename,
                omit_background=True
            )
            browser.close()

        return filename

    except Exception as e:
        print("KATEX ERROR:", e)
        return None

def generate_pdf(questions, subject_id, total_marks):
    doc = SimpleDocTemplate("question_paper.pdf", pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # ===== HEADER =====
    title_style = styles["Title"]
    title_style.alignment = 1
    elements.append(Paragraph("ASSAM ENGINEERING COLLEGE", title_style))
    elements.append(Spacer(1, 10))

    # Roll No and Semester header
    header_data = [
        [
            Paragraph("<b>Roll No:</b>", styles["Normal"]),
            RollNoBoxes(),
            Paragraph("<b>Semester:</b>", styles["Normal"]),
            SemesterBoxes()
        ]
    ]

    header_table = Table(header_data, colWidths=[70, 150, 90, 80])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 8))

    info_style = styles["Normal"]
    info_style.spaceAfter = 3

    # fixed-height header block
    header_content = [
        Paragraph(f"<b>Subject ID:</b> {subject_id}", info_style),
        Paragraph(f"<b>Total Marks:</b> {total_marks}", info_style),
        Spacer(1, 8)
    ]

    fixed_header = KeepInFrame(
        maxWidth=500,
        maxHeight=50,
        content=header_content,
        mode='shrink'
    )

    elements.append(fixed_header)

    heading_style = styles["Heading2"]
    heading_style.alignment = 1

    title_block = KeepInFrame(
        maxWidth=500,
        maxHeight=40,
        content=[Paragraph("<b>Question Paper</b>", heading_style)],
        mode='shrink'
    )

    elements.append(title_block)
    elements.append(Spacer(1, 10))

    # ===== TABLE DATA =====
    data = [
        ["Sl No", "Question", "Marks", "Marks Obtained", "CO"]
    ]

    for i, q in enumerate(questions, 1):

        question_text = q["question_text"]

        flow = []

        parts = re.split(
            r'\$\$(.*?)\$\$',
            question_text,
            flags=re.DOTALL
        )

        for idx, part in enumerate(parts):

            if idx % 2 == 0:

                if part.strip():
                    flow.append(
                        Paragraph(part, styles["Normal"])
                    )

            else:

                formula_image = latex_to_png(part.strip())

                if formula_image and os.path.exists(formula_image):

                    img_formula = RLImage(formula_image)
                    img_formula.drawWidth = 120
                    img_formula.drawHeight = (
                        img_formula.drawWidth *
                        (img_formula.imageHeight / img_formula.imageWidth)
                    )

                    flow.append(img_formula)

                else:
                    flow.append(
                        Paragraph(
                            f"[LaTeX Error: {part.strip()}]",
                            styles["Normal"]
                        )
                    )

        if q.get("image"):
            try:
                base_dir = os.getcwd()
                image_path = os.path.join(base_dir, q["image"].lstrip("/"))

                print("Loading image from:", image_path)

                img = RLImage(image_path)

                # Keep image within Question column
                MAX_WIDTH = 240
                MAX_HEIGHT = 120

                ratio = min(
                    MAX_WIDTH / img.imageWidth,
                    MAX_HEIGHT / img.imageHeight
                )

                img.drawWidth = img.imageWidth * ratio
                img.drawHeight = img.imageHeight * ratio

                flow.append(Spacer(1, 5))
                img.hAlign = 'CENTER'
                flow.append(img)

            except Exception as e:
                print("Image error:", e)

        # Use KeepInFrame for stability inside cell
        inner_table = KeepInFrame(
            maxWidth=260,
            maxHeight=500,
            content=flow,
            mode='overflow'
        )
        
        data.append([
            f"{i}.",
            inner_table,
            q["marks"],
            MarkBoxes(),
            f"CO{q['co_id']}"
        ])

    # ===== CREATE TABLE =====
    # fixed table position stability
    table = Table(
        data,
        colWidths=[40, 270, 60, 120, 50],
        hAlign='CENTER',
        # for multiple pages repeat the first row
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("ALIGN", (3, 1), (3, -1), "CENTER"),
        ("ALIGN", (1, 1), (1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (1, 1), (1, -1), 6),
        ("RIGHTPADDING", (1, 1), (1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(table)

    print("Elements count:", len(elements))

    doc.build(elements, onFirstPage=draw_corners, onLaterPages=draw_corners)

    return "question_paper.pdf"

app = Flask(__name__)
app.register_blueprint(add_question_bp)

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

def generate_paper(subject_id, total_marks, co_distribution, selected_question_ids=None):
    session = get_session()
    try:
        final_questions = []
        used_ids = set()

        if selected_question_ids is None:
            selected_question_ids = []

        # add mandatory questions first
        mandatory_marks = 0

        for qid in selected_question_ids:

            query = """
            SELECT q.question_id,
                   q.question_text,
                   q.marks,
                   q.image_path,
                   qc.co_id
            FROM questions q
            JOIN question_co_map qc
                ON q.question_id = qc.question_id
            WHERE q.question_id = :qid
            """

            row = session.execute(
                text(query),
                {"qid": qid}
            ).fetchone()

            if row:
                q = {
                    "id": row.question_id,
                    "question_text": row.question_text,
                    "marks": row.marks,
                    "co_id": row.co_id,
                    "image": row.image_path if row.image_path else None
                }

                final_questions.append(q)
                used_ids.add(row.question_id)
                mandatory_marks += row.marks

# we use user_id as a set because using this we can assure that there is no duplication as there are
# same questions belonging to multiple COs

        for co_id, percent in co_distribution.items():
            required_marks = int((percent / 100) * total_marks)

            # reduce target because some marks may already be occupied
            remaining_capacity = max(
                0,
                total_marks - mandatory_marks
            )

            required_marks = min(required_marks, remaining_capacity)

            query = """
            SELECT q.question_id, q.question_text, q.marks, q.image_path
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
                        "co_id": int(co_id),
                        "image": r.image_path if hasattr(r, "image_path") and r.image_path else None
                    })

            # Shuffle for randomness
            random.shuffle(questions)

            # Apply knapsack
            selected = knapsack_select(questions, required_marks)

            for q in selected:
                final_questions.append(q)
                used_ids.add(q["id"])

        return final_questions

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()

from flask import send_file

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    subject_id = data["subject_id"]
    total_marks = data["total_marks"]
    co_distribution = data["co_distribution"]

    selected_question_ids = data.get(
        "selected_question_ids",
        []
    )

    questions = generate_paper(
        subject_id,
        total_marks,
        co_distribution,
        selected_question_ids
    )

    pdf_path = generate_pdf(questions, subject_id, total_marks)

    return send_file(pdf_path, as_attachment=True)

@app.route("/scan", methods=["POST"])
def scan():

    file = request.files["file"]
    filepath = "uploads/" + file.filename
    file.save(filepath)

    from mark_scanner import scan_paper
    from mark_detection import extract_marks

    warped = scan_paper(filepath)
    marks = extract_marks(warped)

    return jsonify({"marks": marks})

if __name__ == "__main__":
    app.run(debug=True, port=8000)