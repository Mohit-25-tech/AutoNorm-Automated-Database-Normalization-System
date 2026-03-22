# AutoNorm — Automated Database Normalization System

A full-stack web application that accepts a relational schema and functional dependencies and produces a complete, step-by-step normalization walkthrough from 1NF through BCNF.

---

## Features

| Requirement | Status | Details |
|---|---|---|
| Graphical User Interface | ✅ | React frontend with dark/light theme and font selector |
| Accept relational schema | ✅ | Add attributes as chips with duplicate validation |
| Accept functional dependencies | ✅ | Add/remove LHS → RHS pairs with schema validation |
| 1NF check | ✅ | Flag multi-valued attributes and repeating groups |
| Closure & candidate keys | ✅ | Full closure algorithm + minimal candidate key finder |
| 2NF decomposition | ✅ | Detects partial dependencies, decomposes with named tables |
| 3NF decomposition | ✅ | Minimal cover algorithm + synthesis into 3NF tables |
| BCNF decomposition | ✅ | Recursive lossless decomposition |
| Step-by-step output | ✅ | Expandable accordion steps for every normal form |

---

## Tech Stack

- **Frontend**: React 18, CSS custom properties (dark/light themes)
- **Backend**: Python 3, FastAPI, Pydantic
- **Communication**: REST API (JSON)

---

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`.

### Frontend

```bash
npm install
npm start
```

Frontend runs at `http://localhost:3000`.

Set the backend URL via environment variable if needed:
```bash
REACT_APP_API_URL=http://localhost:8000 npm start
```

---

## How to Use

1. **Step 01 — Define Attributes**: Type each attribute name and click Add (or press Enter). Attributes are auto-uppercased.

2. **Step 02 — 1NF Check**: Optionally flag any attribute that holds multiple values (e.g. a list of phone numbers). Check the box if your schema has repeating groups (e.g. Phone1, Phone2, Phone3 columns).

3. **Step 03 — Functional Dependencies**: Enter one or more FDs. LHS and RHS are comma-separated attribute names. Example: `A, B → C`.

4. **Click "⚡ Normalize Schema"**: Results appear on the right panel in five tabs:

   | Tab | Shows |
   |---|---|
   | **1NF** | Atomicity violations + step-by-step reasoning |
   | **Keys** | All candidate keys, prime/non-prime attributes + derivation steps |
   | **2NF** | Partial dependency violations, decomposed tables, step-by-step |
   | **3NF** | Transitive dependency violations, minimal cover, tables, steps |
   | **BCNF** | Superkey violations, lossless decomposition, final tables, steps |

   Each step in the accordion can be clicked to expand its full explanation.

---

## Example

**Schema**: `STUDENT_ID, COURSE_ID, STUDENT_NAME, COURSE_NAME, GRADE`

**FDs**:
- `STUDENT_ID, COURSE_ID → GRADE`
- `STUDENT_ID → STUDENT_NAME`
- `COURSE_ID → COURSE_NAME`

**Expected output**:
- Candidate key: `{STUDENT_ID, COURSE_ID}`
- 2NF violations: `STUDENT_ID → STUDENT_NAME`, `COURSE_ID → COURSE_NAME` (partial dependencies)
- 3NF decomposition into `Students(STUDENT_ID, STUDENT_NAME)`, `Courses(COURSE_ID, COURSE_NAME)`, `Enrollment(STUDENT_ID, COURSE_ID, GRADE)`

---

## API

### `POST /normalize`

**Request body**:
```json
{
  "attributes": ["A", "B", "C", "D"],
  "functional_dependencies": [
    { "lhs": ["A"], "rhs": ["B", "C"] },
    { "lhs": ["B"], "rhs": ["D"] }
  ],
  "multivalued_attributes": [],
  "has_repeating_groups": false
}
```

**Response** includes:
- `candidate_keys`, `prime_attributes`
- `is_1nf`, `is_2nf`, `is_3nf`, `is_bcnf`
- `violations_1nf`, `violations_2nf`, `violations_3nf`, `violations_bcnf`
- `tables_2nf`, `tables_3nf`, `tables_bcnf`
- `steps_1nf`, `steps_keys`, `steps_2nf`, `steps_3nf`, `steps_bcnf`
