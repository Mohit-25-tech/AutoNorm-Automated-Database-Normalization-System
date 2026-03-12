# AutoNorm — Automated Database Normalization System

A full-stack tool that takes a relational schema (attributes + FDs) and produces a step-by-step, visual normalization report up to BCNF.

---

## Project Structure

```
DBMS_assignment/
├── backend/
│   ├── main.py           # FastAPI routes + CORS
│   ├── models.py         # Pydantic request/response schemas
│   ├── logic.py          # Core normalization engine (Normalizer class)
│   └── requirements.txt
├── public/
│   └── index.html
├── src/
│   ├── App.js                          # Root state management + API call
│   ├── App.css                         # Global styles, themes, typography
│   └── components/
│       ├── SchemaInput.js              # Attribute + FD form
│       └── ResultsDisplay.js           # Tabbed results (Keys, 2NF, 3NF, BCNF)
├── package.json
└── readme.md
```

---

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be live at: http://localhost:8000  
Swagger docs at: http://localhost:8000/docs

### API Endpoint

**POST** `/normalize`

Request body:
```json
{
  "attributes": ["A", "B", "C", "D"],
  "functional_dependencies": [
    { "lhs": ["A", "B"], "rhs": ["C"] },
    { "lhs": ["C"], "rhs": ["D"] }
  ]
}
```

---

## Frontend Setup

```bash
cd DBMS_assignment
npm install
npm start
```

App will be live at: http://localhost:3000

> **Note:** The frontend expects the backend at `http://localhost:8000`.  
> To change this, set `REACT_APP_API_URL` in a `.env` file in the project root (same folder as `package.json`).

---

## Features

- **Candidate Key Detection** — finds **all** minimal candidate keys using attribute closure
- **Prime/Non-Prime Classification** — identifies prime attributes automatically  
- **2NF / 3NF / BCNF Analysis** — detects partial, transitive, and BCNF violations with explanations
- **Step-by-Step Decomposition** — shows resulting normalized table schemas for each normal form
- **Interactive UI** — add/remove attributes and FDs with live validation
- **Dark / Light Themes & Fonts** — switch between dark/light mode and multiple font styles directly from the header

---

## Example Test Case

Attributes: `StudentID, CourseID, Instructor, Grade, InstructorOffice`

Functional Dependencies:
- `StudentID, CourseID → Grade`
- `CourseID → Instructor`
- `Instructor → InstructorOffice`

Expected: 2NF violated (partial: CourseID → Instructor), 3NF violated (transitive: Instructor → InstructorOffice), BCNF violated.
