# NormalForm — Database Normalization Tool

A full-stack tool that takes a relational schema (attributes + FDs) and produces a step-by-step normalization report up to BCNF.

---

## Project Structure

```
project/
├── backend/
│   ├── main.py           # FastAPI routes + CORS
│   ├── models.py         # Pydantic request/response schemas
│   ├── logic.py          # Core normalization engine (Normalizer class)
│   └── requirements.txt
└── frontend/
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── App.js                          # Root state management + API call
    │   ├── App.css                         # Global styles
    │   └── components/
    │       ├── SchemaInput.js              # Attribute + FD form
    │       └── ResultsDisplay.js          # Tabbed results (Keys, 2NF, 3NF, BCNF)
    └── package.json
```

---

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
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
cd frontend
npm install
npm start
```

App will be live at: http://localhost:3000

> **Note:** The frontend expects the backend at `http://localhost:8000`.  
> To change this, set `REACT_APP_API_URL` in a `.env` file in the `frontend/` directory.

---

## Features

- **Candidate Key Detection** — finds ALL minimal candidate keys using attribute closure
- **Prime/Non-Prime Classification** — identifies prime attributes automatically  
- **2NF Analysis** — detects all partial dependencies with explanations
- **3NF Analysis** — detects all transitive dependencies
- **BCNF Analysis** — detects all BCNF violations
- **Decomposition** — shows resulting normalized table schemas for each normal form
- **Dynamic UI** — add/remove attributes and FDs with live validation

---

## Example Test Case

Attributes: `StudentID, CourseID, Instructor, Grade, InstructorOffice`

Functional Dependencies:
- `StudentID, CourseID → Grade`
- `CourseID → Instructor`
- `Instructor → InstructorOffice`

Expected: 2NF violated (partial: CourseID → Instructor), 3NF violated (transitive: Instructor → InstructorOffice), BCNF violated.
