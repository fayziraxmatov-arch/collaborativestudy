import streamlit as st
import json
from datetime import datetime
from pathlib import Path

PROGRAM_TITLE = "Collaborative Study Satisfaction and Group Work Dynamics Survey"


def load_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as file:
            questions = json.load(file)
        return questions
    except FileNotFoundError:
        st.error("questions.json file was not found.")
        return None
    except json.JSONDecodeError:
        st.error("questions.json is not a valid JSON file.")
        return None


def validate_name(name):
    pattern = r"^[A-Za-z]+([ '-][A-Za-z]+)*$"
    return re.fullmatch(pattern.strip(), name.strip()) is not None


def validate_date_of_birth(date_text):
    try:
        dob = datetime.strptime(date_text, "%Y-%m-%d")
        return dob <= datetime.today()
    except ValueError:
        return False


def validate_student_id(student_id):
    return student_id.isdigit()


def determine_result_state(total_score):
    if 0 <= total_score <= 10:
        return "Strongly Avoidant of Group Work"
    elif 11 <= total_score <= 20:
        return "Highly Dissatisfied with Collaboration"
    elif 21 <= total_score <= 30:
        return "Low Engagement in Group Study"
    elif 31 <= total_score <= 40:
        return "Moderately Engaged but Needs Better Group Support"
    elif 41 <= total_score <= 50:
        return "Satisfied and Cooperative Team Member"
    elif 51 <= total_score <= 60:
        return "Highly Collaborative and Academically Engaged"
    else:
        return "Outstandingly Positive Group Work Experience"


def convert_result_to_text(result_data):
    lines = []
    lines.append(PROGRAM_TITLE)
    lines.append("=" * 60)
    lines.append(f"Name: {result_data['full_name']}")
    lines.append(f"Date of Birth: {result_data['date_of_birth']}")
    lines.append(f"Student ID: {result_data['student_id']}")
    lines.append(f"Total Score: {result_data['total_score']} / {result_data['maximum_score']}")
    lines.append(f"Score Percentage: {result_data['score_percentage']}%")
    lines.append(f"Final State: {result_data['result_state']}")
    lines.append(f"Completed At: {result_data['completed_at']}")
    lines.append("=" * 60)
    lines.append("Answers:")

    for item in result_data["answers"]:
        lines.append(f"- {item['question']}")
        lines.append(f"  Answer: {item['selected_answer']}")
        lines.append(f"  Score: {item['score']}")

    return "\n".join(lines)


def convert_result_to_csv(result_data):
    rows = [
        ["Program Title", result_data["program_title"]],
        ["Name", result_data["full_name"]],
        ["Date of Birth", result_data["date_of_birth"]],
        ["Student ID", result_data["student_id"]],
        ["Total Score", result_data["total_score"]],
        ["Maximum Score", result_data["maximum_score"]],
        ["Score Percentage", result_data["score_percentage"]],
        ["Final State", result_data["result_state"]],
        ["Completed At", result_data["completed_at"]],
        [],
        ["Question", "Selected Answer", "Score"]
    ]

    for item in result_data["answers"]:
        rows.append([item["question"], item["selected_answer"], item["score"]])

    output_lines = []
    for row in rows:
        escaped_row = []
        for cell in row:
            cell = str(cell)
            if "," in cell or '"' in cell or "\n" in cell:
                cell = '"' + cell.replace('"', '""') + '"'
            escaped_row.append(cell)
        output_lines.append(",".join(escaped_row))

    return "\n".join(output_lines)


st.set_page_config(page_title="Group Work Survey", layout="wide")
st.title(PROGRAM_TITLE)
st.write("This web application evaluates satisfaction with collaborative study and group work dynamics in academic tasks.")

questions = load_questions()

if questions is not None:
    tab1, tab2 = st.tabs(["Start New Questionnaire", "Load Existing JSON Result"])

    with tab1:
        st.subheader("Student Information")

        full_name = st.text_input("Surname and given name")
        date_of_birth = st.text_input("Date of birth (YYYY-MM-DD)")
        student_id = st.text_input("Student ID number")

        st.subheader("Survey Questions")

        selected_answers = []

        for i, question in enumerate(questions):
            option_texts = [option["text"] for option in question["options"]]

            selected_text = st.radio(
                question["question"],
                option_texts,
                key=f"q_{i}"
            )
            selected_answers.append(selected_text)

        submit = st.button("Submit Questionnaire")

        if submit:
            errors = []

            if not validate_name(full_name):
                errors.append("Invalid name. Use only letters, spaces, hyphens, and apostrophes.")

            if not validate_date_of_birth(date_of_birth):
                errors.append("Invalid date of birth. Please use YYYY-MM-DD format.")

            if not validate_student_id(student_id):
                errors.append("Student ID must contain digits only.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                answers = []
                total_score = 0
                maximum_score = 0

                for i, question in enumerate(questions):
                    chosen_text = selected_answers[i]

                    selected_option = None
                    for option in question["options"]:
                        if option["text"] == chosen_text:
                            selected_option = option
                            break

                    answers.append({
                        "question": question["question"],
                        "selected_answer": selected_option["text"],
                        "score": selected_option["score"]
                    })

                    total_score += selected_option["score"]
                    maximum_score += max(option["score"] for option in question["options"])

                score_percentage = round((total_score / maximum_score) * 100, 2)
                result_state = determine_result_state(total_score)

                result_data = {
                    "program_title": PROGRAM_TITLE,
                    "full_name": full_name,
                    "date_of_birth": date_of_birth,
                    "student_id": student_id,
                    "total_score": total_score,
                    "maximum_score": maximum_score,
                    "score_percentage": score_percentage,
                    "result_state": result_state,
                    "answers": answers,
                    "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                st.success("Questionnaire completed successfully.")

                st.subheader("Questionnaire Result")
                st.write(f"**Name:** {result_data['full_name']}")
                st.write(f"**Date of Birth:** {result_data['date_of_birth']}")
                st.write(f"**Student ID:** {result_data['student_id']}")
                st.write(f"**Total Score:** {result_data['total_score']} / {result_data['maximum_score']}")
                st.write(f"**Score Percentage:** {result_data['score_percentage']}%")
                st.write(f"**Final State:** {result_data['result_state']}")
                st.write(f"**Completed At:** {result_data['completed_at']}")

                json_text = json.dumps(result_data, indent=4, ensure_ascii=False)
                txt_text = convert_result_to_text(result_data)
                csv_text = convert_result_to_csv(result_data)

                st.subheader("Download Result")
                st.download_button(
                    label="Download as JSON",
                    data=json_text,
                    file_name="result.json",
                    mime="application/json"
                )

                st.download_button(
                    label="Download as TXT",
                    data=txt_text,
                    file_name="result.txt",
                    mime="text/plain"
                )

                st.download_button(
                    label="Download as CSV",
                    data=csv_text,
                    file_name="result.csv",
                    mime="text/csv"
                )

    with tab2:
        st.subheader("Load Existing JSON Result")
        uploaded_file = st.file_uploader("Upload a JSON result file", type=["json"])

        if uploaded_file is not None:
            try:
                loaded_data = json.load(uploaded_file)

                st.success("JSON result file loaded successfully.")

                st.write(f"**Name:** {loaded_data.get('full_name', '')}")
                st.write(f"**Date of Birth:** {loaded_data.get('date_of_birth', '')}")
                st.write(f"**Student ID:** {loaded_data.get('student_id', '')}")
                st.write(f"**Total Score:** {loaded_data.get('total_score', '')} / {loaded_data.get('maximum_score', '')}")
                st.write(f"**Score Percentage:** {loaded_data.get('score_percentage', '')}%")
                st.write(f"**Final State:** {loaded_data.get('result_state', '')}")
                st.write(f"**Completed At:** {loaded_data.get('completed_at', '')}")

                st.subheader("Answers")
                for item in loaded_data.get("answers", []):
                    st.write(f"- **{item['question']}**")
                    st.write(f"Answer: {item['selected_answer']}")
                    st.write(f"Score: {item['score']}")

            except Exception as error:
                st.error(f"Error loading JSON file: {error}")