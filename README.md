Code Quality Analyzer & Visualizer
A web application to analyze Python code quality, providing metrics like cyclomatic complexity, code smells, and maintainability index. Features interactive charts, detailed reports, and PDF downloads. Built with FastAPI, React, Pylint, and ReportLab.
Features

Upload Python (.py) files for analysis.
Displays cyclomatic complexity, code smells, and maintainability index.
Interactive bar charts visualizing code metrics.
Detailed code smell reports in an accordion view.
Downloadable PDF reports with metrics and charts.
Stores analysis results in MongoDB.

Prerequisites

Python: 3.10+
Node.js: 16+
MongoDB: Community Edition
Git: For cloning the repository

Installation
1. Clone the Repository
git clone https://github.com/your-username/code-quality-analyzer.git
cd code-quality-analyzer

2. Set Up Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn reportlab pylint radon pymongo

3. Set Up Frontend
cd ../frontend
npm install
npm install react-chartjs-2 chart.js html2canvas axios bootstrap

4. Install and Start MongoDB

Windows: Download MongoDB Community Edition from mongodb.com. Run:mongod --dbpath <path-to-data-folder>

5. Verify Dependencies

Backend: pip show fastapi uvicorn reportlab pylint radon pymongo
Frontend: npm list react-chartjs-2 chart.js html2canvas axios bootstrap
MongoDB: mongosh --version

Start MongoDB:
mongod --dbpath <path-to-data-folder>  # Adjust path as needed

Run Backend:
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app:app --reload

Run Frontend:
cd frontend
npm run dev

Access the Application:

Open http://localhost:5173 in your browser.
Upload a .py file 

View analysis results, charts, and download the PDF report.

Project Structure
code-quality-analyzer/
├── backend/
│   ├── app.py
│   ├── analyzer/
│   │   └── python_analyzer.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── ReportViewer.jsx
│   │   └── main.jsx
│   └── package.json
└── README.md

Troubleshooting

Pylint Issues: Ensure pylint==3.2.6. Run pylint --version.
PDF Errors: Verify reportlab is installed (pip show reportlab).
MongoDB: Ensure mongod is running and accessible at localhost:27017.
Frontend: Clear cache (npm cache clean --force) if dependencies fail.

License
MIT License. See LICENSE for details.
