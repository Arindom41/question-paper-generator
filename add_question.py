from flask import Blueprint, render_template, request, redirect
from sqlalchemy import text
from db import engine

import os

add_question_bp = Blueprint(
    "add_question",
    __name__
)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@add_question_bp.route("/add_question")
def add_question_page():
    return render_template("add_question.html")


@add_question_bp.route(
    "/save_question",
    methods=["POST"]
)
def save_question():

    question_text = request.form["question_text"]
    marks = int(request.form["marks"])
    co_id = int(request.form["co_id"])
    subject_id = int(request.form["subject_id"])

    image = request.files.get("image")

    image_path = None

    if image and image.filename:

        image_path = os.path.join(
            UPLOAD_FOLDER,
            image.filename
        )

        image.save(image_path)

    with engine.begin() as conn:

        result = conn.execute(
            text("""
                INSERT INTO questions
                (
                    question_text,
                    marks,
                    subject_id,
                    image_path
                )
                VALUES
                (
                    :question_text,
                    :marks,
                    :subject_id,
                    :image_path
                )
                RETURNING question_id
            """),
            {
                "question_text": question_text,
                "marks": marks,
                "subject_id": subject_id,
                "image_path": image_path
            }
        )

        question_id = result.scalar()

        conn.execute(
            text("""
                INSERT INTO question_co_map
                (
                    question_id,
                    co_id
                )
                VALUES
                (
                    :question_id,
                    :co_id
                )
            """),
            {
                "question_id": question_id,
                "co_id": co_id
            }
        )

    return redirect("/add_question?success=1")