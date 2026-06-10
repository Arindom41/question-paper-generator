document.getElementById("generateForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const subject_id = document.querySelector('[name="subject_id"]').value;
    const total_marks = document.querySelector('[name="total_marks"]').value;
    const co1 = document.querySelector('[name="co1"]').value;
    const co2 = document.querySelector('[name="co2"]').value;
    const co3 = document.querySelector('[name="co3"]').value;

    const selectedQuestions = document
        .getElementById('selectedQuestions')
        .value
        .split(',')
        .map(id => id.trim())
        .filter(id => id !== '')
        .map(Number);

    const customQuestions = [];

    document.querySelectorAll('.custom-question').forEach(row => {
        const questionText = row.querySelector('.custom-question-text')?.value.trim();
        const coId = row.querySelector('.custom-question-co')?.value;
        const marks = row.querySelector('.custom-question-marks')?.value;

        if (questionText) {
            customQuestions.push({
                question_text: questionText,
                co_id: parseInt(coId || 1, 10),
                marks: parseInt(marks || 0, 10)
            });
        }
    });

    const data = {
        subject_id: parseInt(subject_id, 10),
        total_marks: parseInt(total_marks, 10),
        co_distribution: {
            "1": parseInt(co1, 10),
            "2": parseInt(co2, 10),
            "3": parseInt(co3, 10)
        },
        selected_question_ids: selectedQuestions,
        custom_questions: customQuestions
    };

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "question_paper.pdf";
        a.click();

        document.getElementById("popup").style.display = "flex";
    } catch (error) {
        console.error(error);
        alert("Server error");
    }
});

function closePopup(){
    document.getElementById("popup").style.display = "none";
}

// scan button click
if (document.getElementById("scanBtn")) {
    document.getElementById("scanBtn").addEventListener("click", function(){
        alert("Redirect to scanning module (to be implemented)");
    });
}
