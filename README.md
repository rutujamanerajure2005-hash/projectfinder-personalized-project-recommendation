ProjectFinder – Personalized Student Project Recommendation System

About the Project

ProjectFinder is a web-based project recommendation system that helps students discover suitable projects based on their skills, interests, domain, experience level, and preferred technologies.

It uses machine learning techniques such as TF-IDF and cosine similarity to identify relevant projects. It also performs skill-gap analysis to show students which skills they already have and which additional skills they need to learn.

Problem Statement

Students often struggle to find projects that match their technical skills and interests. ProjectFinder helps solve this problem by recommending relevant projects and identifying the additional skills required for each project.

Key Features

- Personalized project recommendations
- Top three relevant project suggestions
- TF-IDF and cosine similarity-based matching
- Skill-gap analysis
- Project details
- Save and remove projects
- User profile management
- Recommendation history
- Admin dashboard

Technologies Used

- Programming Language: Python
- Web Framework: Flask
- Machine Learning: Scikit-learn (TF-IDF and cosine similarity)
- Data Processing: Pandas
- Frontend: HTML and CSS
- Database: MySQL
- Dataset: CSV
- Development Tools: Visual Studio Code and MySQL Workbench

Project Structure

ProjectFinder/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── projects.csv
│
├── static/
│   ├── css/
│   └── js/
│
└── templates/
    ├── index.html
    ├── recommendations.html
    ├── profile.html
    ├── project_details.html
    ├── saved_projects.html
    ├── history.html
    └── admin.html

How It Works

1. Students enter their skills, domain, experience level, difficulty, and preferred technologies.
2. The application processes the input using Python and Pandas.
3. TF-IDF converts the project information into numerical vectors.
4. Cosine similarity compares the student's input with the available project data.
5. The system ranks the projects and displays the top three recommendations.
6. Skill-gap analysis identifies existing and missing skills.

Database

MySQL is used to manage saved projects, user profile information, and recommendation history.

Create the required database and tables before running the application. Configure your MySQL connection details securely using environment variables.

Installation and Execution

1. Clone the repository:

git clone https://github.com/YOUR-GITHUB-USERNAME/projectfinder-personalized-project-recommendation.git

2. Open the project folder:

cd projectfinder-personalized-project-recommendation

3. Create and activate a virtual environment:

python -m venv venv

Windows:

venv\Scripts\activate

4. Install the required libraries:

pip install -r requirements.txt

5. Configure the MySQL database and set the "PROJECTFINDER_DB_PASSWORD" environment variable to your MySQL password.

6. Run the application:

python app.py

7. Open the application in your browser:

http://127.0.0.1:5000/

Future Enhancements

- Expand the project dataset.
- Improve skill extraction using natural language processing.
- Add individual student login and personalized accounts.
- Enhance recommendation techniques.

Author

Developed as an academic project to help students discover suitable project ideas and identify skill gaps.
