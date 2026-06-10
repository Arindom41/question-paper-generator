let currentUser = null;

const authScreen = document.getElementById("authScreen");
const authForm = document.getElementById("authForm");
const authError = document.getElementById("authError");
const userStatus = document.getElementById("userStatus");
const logoutBtn = document.getElementById("logoutBtn");
const generateForm = document.getElementById("generateForm");
const generateBtn = document.getElementById("generateBtn");
const resultBox = document.getElementById("result");
const popup = document.getElementById("popup");
const infoBtn = document.getElementById("infoBtn");
const infoModal = document.getElementById("infoModal");
const closeInfoBtn = document.getElementById("closeInfoBtn");
const subjectInfoContent = document.getElementById("subjectInfoContent");
const addQuestionBtn = document.getElementById("addQuestionBtn");
const addCustomQuestionBtn = document.getElementById("addCustomQuestionBtn");
const customQuestionsContainer = document.getElementById("customQuestionsContainer");
const scanForm = document.getElementById("scanForm");
const coInputs = ["co1", "co2", "co3"].map(id => document.getElementById(id));
const selectedQuestionsInput = document.getElementById("selectedQuestions");
const summaryAuth = document.getElementById("summaryAuth");
const summaryCo = document.getElementById("summaryCo");
const summaryCustom = document.getElementById("summaryCustom");
const summaryMandatory = document.getElementById("summaryMandatory");
const coTotal = document.getElementById("coTotal");

function setResult(message, type = "") {
    if (!resultBox) {
        return;
    }

    resultBox.textContent = message;
    resultBox.className = `result ${type}`.trim();
}

function isAuthorized() {
    return Boolean(currentUser);
}

function applyAuthState(message) {
    const authorized = isAuthorized();

    if (authScreen) {
        authScreen.classList.toggle("is-hidden", authorized);
    }

    if (userStatus) {
        userStatus.textContent = authorized ? `Authorized: ${currentUser}` : "Locked";
    }

    if (summaryAuth) {
        summaryAuth.textContent = authorized ? "Active" : "Locked";
    }

    [generateBtn, infoBtn, addQuestionBtn, document.getElementById("scanBtn")].forEach(button => {
        if (button) {
            button.disabled = !authorized;
        }
    });

    setResult(
        message || (authorized ? "Ready to generate a question paper." : "Authorize first to use the dashboard."),
        authorized ? "success" : ""
    );
}

async function loadAuthState() {
    try {
        const response = await fetch("/auth/status", {
            credentials: "same-origin"
        });
        const data = await response.json();

        currentUser = data.authorized ? data.username : null;
        applyAuthState();
    } catch (error) {
        console.error(error);
        currentUser = null;
        applyAuthState("Could not verify authorization status.");
    }
}

function parseMandatoryIds() {
    if (!selectedQuestionsInput) {
        return [];
    }

    return selectedQuestionsInput.value
        .split(",")
        .map(id => id.trim())
        .filter(Boolean)
        .map(Number)
        .filter(Number.isFinite);
}

function getCoValues() {
    return coInputs.map(input => parseInt(input?.value || "0", 10) || 0);
}

function updateSummary() {
    const total = getCoValues().reduce((sum, value) => sum + value, 0);
    const customRows = document.querySelectorAll(".custom-question").length;
    const mandatoryCount = parseMandatoryIds().length;
    const coLabel = `${total}%`;

    if (coTotal) {
        coTotal.textContent = coLabel;
        coTotal.style.color = total === 100 ? "#14532d" : "#b42318";
        coTotal.style.background = total === 100 ? "#ecfdf3" : "#fff1f0";
        coTotal.style.borderColor = total === 100 ? "#86efac" : "#fda29b";
    }

    if (summaryCo) {
        summaryCo.textContent = coLabel;
    }

    if (summaryCustom) {
        summaryCustom.textContent = String(customRows);
    }

    if (summaryMandatory) {
        summaryMandatory.textContent = String(mandatoryCount);
    }
}

function createCustomQuestionRow() {
    const row = document.createElement("div");
    row.className = "custom-question";

    row.innerHTML = `
        <div class="field">
            <label>Question Text</label>
            <textarea class="custom-question-text" placeholder="Write the temporary question"></textarea>
        </div>

        <div class="field">
            <label>CO</label>
            <input type="number" class="custom-question-co" min="1" max="3" placeholder="1">
        </div>

        <div class="field">
            <label>Marks</label>
            <input type="number" class="custom-question-marks" min="0" placeholder="5">
        </div>

        <button class="btn btn-danger remove-custom-question" type="button" title="Remove row" aria-label="Remove custom question">x</button>
    `;

    return row;
}

function collectCustomQuestions() {
    const customQuestions = [];

    document.querySelectorAll(".custom-question").forEach(row => {
        const questionText = row.querySelector(".custom-question-text")?.value.trim();
        const coId = parseInt(row.querySelector(".custom-question-co")?.value || "1", 10);
        const marks = parseInt(row.querySelector(".custom-question-marks")?.value || "0", 10);

        if (questionText) {
            customQuestions.push({
                question_text: questionText,
                co_id: Number.isFinite(coId) ? coId : 1,
                marks: Number.isFinite(marks) ? marks : 0
            });
        }
    });

    return customQuestions;
}

function validatePaperForm(data) {
    const coTotalValue = Object.values(data.co_distribution).reduce((sum, value) => sum + value, 0);

    if (!isAuthorized()) {
        return "Please authorize before generating a paper.";
    }

    if (!data.subject_id || data.subject_id < 1) {
        return "Enter a valid subject ID.";
    }

    if (!data.total_marks || data.total_marks < 1) {
        return "Enter valid total marks.";
    }

    if (coTotalValue !== 100) {
        return "CO distribution must total exactly 100%.";
    }

    return "";
}

async function readErrorMessage(response, fallback) {
    try {
        const data = await response.json();
        return data.message || fallback;
    } catch (error) {
        return fallback;
    }
}

function closePopup() {
    if (popup) {
        popup.classList.remove("is-open");
    }
}

window.closePopup = closePopup;

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function closeInfoModal() {
    if (infoModal) {
        infoModal.classList.remove("is-open");
    }
}

function renderSubjectInfo(subjects) {
    if (!subjectInfoContent) {
        return;
    }

    if (!subjects.length) {
        subjectInfoContent.className = "result";
        subjectInfoContent.textContent = "No subject information found.";
        return;
    }

    subjectInfoContent.className = "subject-list";
    subjectInfoContent.innerHTML = subjects.map(subject => {
        const coItems = subject.course_outcomes.length
            ? subject.course_outcomes.map(co => `
                <li>
                    <strong>${escapeHtml(co.co_code)}</strong>
                    <span>${escapeHtml(co.description || "No description added")}</span>
                </li>
            `).join("")
            : `<li><strong>CO</strong><span>No course outcomes added</span></li>`;

        return `
            <article class="subject-item">
                <div class="subject-meta">
                    <h3>${escapeHtml(subject.subject_id)} · ${escapeHtml(subject.subject_name)}</h3>
                    <span class="helper">Semester ${escapeHtml(subject.semester || "-")}</span>
                </div>
                <ul class="co-list">
                    ${coItems}
                </ul>
            </article>
        `;
    }).join("");
}

async function openSubjectInfo() {
    if (!isAuthorized()) {
        setResult("Please authorize before viewing subject information.", "error");
        return;
    }

    if (infoModal) {
        infoModal.classList.add("is-open");
    }

    if (subjectInfoContent) {
        subjectInfoContent.className = "result";
        subjectInfoContent.textContent = "Loading subject information...";
    }

    try {
        const response = await fetch("/subjects-info", {
            credentials: "same-origin"
        });

        if (response.status === 401) {
            currentUser = null;
            closeInfoModal();
            applyAuthState("Your session expired. Please authorize again.");
            return;
        }

        if (!response.ok) {
            throw new Error(await readErrorMessage(response, "Could not load subject information."));
        }

        const data = await response.json();
        renderSubjectInfo(data.subjects || []);
    } catch (error) {
        console.error(error);
        if (subjectInfoContent) {
            subjectInfoContent.className = "result error";
            subjectInfoContent.textContent = error.message || "Could not load subject information.";
        }
    }
}

if (authForm) {
    authForm.addEventListener("submit", async event => {
        event.preventDefault();

        const username = document.getElementById("teacherId")?.value.trim();
        const accessCode = document.getElementById("accessCode")?.value;

        if (!username || !accessCode) {
            if (authError) {
                authError.textContent = "Username and access code are required.";
            }
            return;
        }

        try {
            const response = await fetch("/login", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username,
                    access_code: accessCode
                })
            });

            if (!response.ok) {
                throw new Error(await readErrorMessage(response, "Invalid username or access code."));
            }

            const data = await response.json();
            currentUser = data.username;

            if (authError) {
                authError.textContent = "";
            }

            applyAuthState("Authorization successful.");
            updateSummary();
        } catch (error) {
            currentUser = null;
            if (authError) {
                authError.textContent = error.message;
            }
            applyAuthState("Authorize first to use the dashboard.");
        }
    });
}

if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
        try {
            await fetch("/logout", {
                method: "POST",
                credentials: "same-origin"
            });
        } catch (error) {
            console.error(error);
        }

        currentUser = null;
        applyAuthState("You have been logged out.");
    });
}

infoBtn?.addEventListener("click", openSubjectInfo);
closeInfoBtn?.addEventListener("click", closeInfoModal);

if (addCustomQuestionBtn && customQuestionsContainer) {
    addCustomQuestionBtn.addEventListener("click", () => {
        customQuestionsContainer.appendChild(createCustomQuestionRow());
        updateSummary();
    });
}

if (customQuestionsContainer) {
    customQuestionsContainer.addEventListener("click", event => {
        const removeButton = event.target.closest(".remove-custom-question");

        if (!removeButton) {
            return;
        }

        const rows = customQuestionsContainer.querySelectorAll(".custom-question");
        if (rows.length === 1) {
            rows[0].querySelectorAll("input, textarea").forEach(field => {
                field.value = "";
            });
        } else {
            removeButton.closest(".custom-question")?.remove();
        }

        updateSummary();
    });

    customQuestionsContainer.addEventListener("input", updateSummary);
}

coInputs.forEach(input => {
    input?.addEventListener("input", updateSummary);
});

selectedQuestionsInput?.addEventListener("input", updateSummary);

if (generateForm) {
    generateForm.addEventListener("submit", async event => {
        event.preventDefault();

        const data = {
            subject_id: parseInt(document.querySelector('[name="subject_id"]')?.value || "0", 10),
            total_marks: parseInt(document.querySelector('[name="total_marks"]')?.value || "0", 10),
            co_distribution: {
                "1": parseInt(document.querySelector('[name="co1"]')?.value || "0", 10),
                "2": parseInt(document.querySelector('[name="co2"]')?.value || "0", 10),
                "3": parseInt(document.querySelector('[name="co3"]')?.value || "0", 10)
            },
            selected_question_ids: parseMandatoryIds(),
            custom_questions: collectCustomQuestions()
        };

        const validationError = validatePaperForm(data);
        if (validationError) {
            setResult(validationError, "error");
            return;
        }

        try {
            generateBtn.disabled = true;
            setResult("Generating PDF. Please wait...", "");

            const response = await fetch("/generate", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            if (response.status === 401) {
                currentUser = null;
                applyAuthState("Your session expired. Please authorize again.");
                return;
            }

            if (!response.ok) {
                throw new Error(await readErrorMessage(response, "The server could not generate the PDF."));
            }

            const contentType = response.headers.get("content-type") || "";
            if (contentType.includes("application/json")) {
                const errorData = await response.json();
                throw new Error(errorData.message || "Generation failed.");
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");

            link.href = url;
            link.download = "question_paper.pdf";
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            setResult("PDF generated and downloaded successfully.", "success");

            if (popup) {
                popup.classList.add("is-open");
            }
        } catch (error) {
            console.error(error);
            setResult(error.message || "Server error while generating the paper.", "error");
        } finally {
            generateBtn.disabled = !isAuthorized();
        }
    });
}

if (scanForm) {
    scanForm.addEventListener("submit", async event => {
        event.preventDefault();

        if (!isAuthorized()) {
            setResult("Please authorize before scanning a paper.", "error");
            return;
        }

        const scanFile = document.getElementById("scanFile")?.files[0];
        if (!scanFile) {
            setResult("Choose a checked paper file before uploading.", "error");
            return;
        }

        const formData = new FormData();
        formData.append("file", scanFile);

        try {
            setResult("Uploading scan for mark detection...", "");

            const response = await fetch("/scan", {
                method: "POST",
                credentials: "same-origin",
                body: formData
            });

            if (response.status === 401) {
                currentUser = null;
                applyAuthState("Your session expired. Please authorize again.");
                return;
            }

            if (!response.ok) {
                throw new Error(await readErrorMessage(response, "The scan could not be processed."));
            }

            const data = await response.json();
            const marks = Array.isArray(data.marks) ? data.marks.join(", ") : JSON.stringify(data.marks);

            setResult(`Detected marks: ${marks}`, "success");
        } catch (error) {
            console.error(error);
            setResult(error.message || "Server error while scanning the paper.", "error");
        }
    });
}

if (addQuestionBtn) {
    addQuestionBtn.addEventListener("click", () => {
        if (!isAuthorized()) {
            setResult("Please authorize before adding questions.", "error");
            return;
        }

        window.location.href = "/add_question";
    });
}

document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        closePopup();
        closeInfoModal();
    }
});

applyAuthState();
updateSummary();
loadAuthState();
