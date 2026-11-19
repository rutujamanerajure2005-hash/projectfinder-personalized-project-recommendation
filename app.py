
import re
import pandas as pd
import mysql.connector

from flask import Flask, render_template, request, redirect,session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


app = Flask(__name__)

app.secret_key="projectfinder_dev_key_change_later"
# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Rutuja@2005",
    database="projectfinder"
)


# Load project dataset
projects = pd.read_csv("data/projects.csv").fillna("")


# Ensure text columns are strings
text_columns = [
    "project_id",
    "project_name",
    "domain",
    "description",
    "skills",
    "technologies",
    "difficulty",
    "duration"
]

for column in text_columns:
    if column in projects.columns:
        projects[column] = projects[column].astype(str)


# Create combined text for each project
projects["project_text"] = (
    projects["domain"] + " " +
    projects["description"] + " " +
    projects["skills"] + " " +
    projects["technologies"] + " " +
    projects["difficulty"]
)


# Convert project text into TF-IDF vectors
vectorizer = TfidfVectorizer()
project_vectors = vectorizer.fit_transform(
    projects["project_text"]
)


# Skills recognized by the skill-gap system
common_skills = [
    "natural language processing",
    "machine learning",
    "deep learning",
    "recommendation systems",
    "image processing",
    "data visualization",
    "data analysis",
    "data cleaning",
    "text processing",
    "computer vision",
    "neural networks",
    "scikit-learn",
    "tensorflow",
    "postgresql",
    "javascript",
    "typescript",
    "statistics",
    "matplotlib",
    "seaborn",
    "transformers",
    "classification",
    "regression",
    "clustering",
    "agriculture",
    "pytorch",
    "xgboost",
    "opencv",
    "tesseract",
    "streamlit",
    "power bi",
    "tableau",
    "jupyter",
    "pandas",
    "numpy",
    "python",
    "flask",
    "django",
    "mysql",
    "sqlite",
    "html",
    "css",
    "react",
    "nlp",
    "nltk",
    "spacy",
    "plotly",
    "keras",
    "rest api",
    "api",
    "json",
    "ocr",
    "yolo",
    "docker",
    "github",
    "git",
    "sql",
    "java",
    "c++",
    "c"
]


def find_skills(text):
    """Find recognized skills in the supplied text."""
    text = str(text).lower()
    found_skills = set()

    for skill in common_skills:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.add(skill)

    return found_skills


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        skills = request.form.get("skills", "").strip()
        domain = request.form.get("domain", "").strip()
        experience = request.form.get("experience", "Beginner")

        cursor.execute(
            "SELECT id FROM user_profile ORDER BY id LIMIT 1"
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE user_profile
                SET name=%s, email=%s, skills=%s,
                    domain=%s, experience=%s
                WHERE id=%s
            """, (name, email, skills, domain, experience,
                  existing["id"]))
        else:
            cursor.execute("""
                INSERT INTO user_profile
                (name, email, skills, domain, experience)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, email, skills, domain, experience))

        db.commit()
        message = "Profile saved successfully!"
    else:
        message = ""

    cursor.execute(
        "SELECT * FROM user_profile ORDER BY id LIMIT 1"
    )
    profile_data = cursor.fetchone() or {}
    cursor.close()

    return render_template(
        "profile.html",
        profile=profile_data,
        message=message
    )
    



@app.route("/history")
def history():
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM recommendation_history
        ORDER BY id DESC
    """)

    history_records = cursor.fetchall()
    cursor.close()

    return render_template(
        "history.html",
        history_records=history_records
    )
    

@app.route("/admin")
def admin():
    total_projects = len(projects)

    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM saved_projects")
    total_saved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM recommendation_history")
    total_searches = cursor.fetchone()[0]

    cursor.close()

    return render_template(
        "admin.html",
        total_projects=total_projects,
        total_saved=total_saved,
        total_searches=total_searches
    )





@app.route("/recommend", methods=["POST"])
def recommend():

    # Get student information from form
    skills = request.form.get("skills", "")
    domain = request.form.get("domain", "")
    experience = request.form.get("experience", "")
    difficulty = request.form.get("difficulty", "")
    technologies = request.form.get("technologies", "")

    # Combine student information for recommendations
    student_text = (
        skills + " " +
        domain + " " +
        experience + " " +
        difficulty + " " +
        technologies
    )

    # Convert student input into a TF-IDF vector
    student_vector = vectorizer.transform([student_text])

    # Calculate similarity with all projects

    # Calculate similarity with all projects
    similarity_scores = cosine_similarity(
        student_vector,
        project_vectors
    )[0]

    # Find the student's known skills and technologies
    student_known_items = (
        find_skills(skills) |
        find_skills(technologies)
    )

    # Copy project dataset and add similarity scores
    ranked_projects = projects.copy()
    ranked_projects["similarity"] = similarity_scores

    # Calculate skill match for each project
    skill_match_scores = []

    for _, project in ranked_projects.iterrows():

        required_items = (
            find_skills(project["skills"]) |
            find_skills(project["technologies"])
        )

        if required_items:
            matched_items = required_items & student_known_items
            skill_score = len(matched_items) / len(required_items)
        else:
            skill_score = 0

        skill_match_scores.append(skill_score)

    ranked_projects["skill_match"] = skill_match_scores

    # Combine text similarity and skill match
    ranked_projects["final_score"] = (
        0.7 * ranked_projects["similarity"] +
        0.3 * ranked_projects["skill_match"]
    )

    # Select the top 3 projects
    recommended_projects = (
        ranked_projects
        .sort_values(
            by="final_score",
            ascending=False
        )
        .head(3)
        .to_dict("records")
    )



    # Find skills and technologies supplied by the student
    student_known_skills = find_skills(skills)
    student_known_technologies = find_skills(technologies)

    # Combine the student's known skills and technologies
    student_known_items = (
        student_known_skills |
        student_known_technologies
    )

    # Calculate the skill gap separately for every project
    for project in recommended_projects:

        # Get requirements for THIS project only
        project_skills = find_skills(
            project.get("skills", "")
        )

        project_technologies = find_skills(
            project.get("technologies", "")
        )

        required_items = (
            project_skills |
            project_technologies
        )

        # Skills and technologies the student already knows
        have_items = (
            required_items &
            student_known_items
        )

        # Skills and technologies the student still needs to learn
        learn_items = (
            required_items -
            student_known_items
        )

        # Store separate results inside each project
        project["have_skills"] = sorted(have_items)
        project["learn_skills"] = sorted(learn_items)
        print("\nProject:", project["project_name"])
        print("CSV skills:", repr(project["skills"]))
        print("CSV technologies:", repr(project["technologies"]))
        print("You Have:", project["have_skills"])
        print("Learn:", project["learn_skills"])
                

        # Store all requirements for checking/debugging
        project["required_skills"] = sorted(required_items)

        # Match percentage is text similarity, not probability
        project["match_percentage"] = round(
            float(project["similarity"]) * 100,
            1
        )
        
    session["recommended_project_ids"] = [
    project["project_id"]
    for project in recommended_projects
]

    session["student_known_items"] = sorted(student_known_items)

    session["match_percentages"] = {
    project["project_id"]: round(
        float(project["similarity"]) * 100, 1
    )
    for project in recommended_projects
}
    

    # Save this recommendation search in MySQL
    recommended_names = ", ".join(
        project["project_name"]
        for project in recommended_projects
    )

    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO recommendation_history
        (skills, domain, experience, difficulty,
         technologies, recommended_projects)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        skills,
        domain,
        experience,
        difficulty,
        technologies,
        recommended_names
    ))

    db.commit()
    cursor.close()


    return render_template(
    "recommendations.html",
    projects=recommended_projects
)








@app.route("/recommendations")
def show_recommendations():

    project_ids = session.get("recommended_project_ids", [])

    if not project_ids:
        return redirect("/#recommendation-form")

    recommended_projects = []

    for project_id in project_ids:
        matching_project = projects[
            projects["project_id"] == project_id
        ]

        if not matching_project.empty:
            project = matching_project.iloc[0].to_dict()

            required_items = (
                find_skills(project.get("skills", "")) |
                find_skills(project.get("technologies", ""))
            )

            # Restore the student's known skills from the session
            student_items = set(session.get("student_known_items", []))

            project["have_skills"] = sorted(required_items & student_items)
            project["learn_skills"] = sorted(required_items - student_items)

            project["match_percentage"] = session.get(
                "match_percentages", {}
            ).get(project_id, 0)

            recommended_projects.append(project)

    return render_template(
        "recommendations.html",
        projects=recommended_projects
    )   
    
    
    
    

@app.route("/project/<project_id>")
def project_details(project_id):

    project = projects[
        projects["project_id"] == project_id
    ]

    if project.empty:
        return "Project not found", 404

    project = project.iloc[0].to_dict()

    return render_template(
        "project_details.html",
        project=project
    )


@app.route("/save_project", methods=["POST"])
def save_project():

    project_id = request.form["project_id"]
    project_name = request.form["project_name"]

    cursor = db.cursor()

    try:
        # Prevent saving the same project twice
        cursor.execute(
            "SELECT id FROM saved_projects WHERE project_id = %s",
            (project_id,)
        )

        existing_project = cursor.fetchone()

        if existing_project:
            return redirect("/saved_projects")

        cursor.execute(
            """
            INSERT INTO saved_projects (project_id, project_name)
            VALUES (%s, %s)
            """,
            (project_id, project_name)
        )

        db.commit()

    except mysql.connector.Error:
        db.rollback()
        raise

    finally:
        cursor.close()

    return redirect("/saved_projects")


@app.route("/saved_projects")
def saved_projects():

    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM saved_projects ORDER BY saved_at DESC"
        )

        saved_projects_list = cursor.fetchall()

    finally:
        cursor.close()

    return render_template(
        "saved_projects.html",
        projects=saved_projects_list
    )


@app.route("/remove_saved_project", methods=["POST"])
def remove_saved_project():

    saved_id = request.form["id"]

    cursor = db.cursor()

    try:
        cursor.execute(
            "DELETE FROM saved_projects WHERE id = %s",
            (saved_id,)
        )

        db.commit()

    except mysql.connector.Error:
        db.rollback()
        raise

    finally:
        cursor.close()

    return redirect("/saved_projects")


if __name__ == "__main__":
    app.run(debug=True)

