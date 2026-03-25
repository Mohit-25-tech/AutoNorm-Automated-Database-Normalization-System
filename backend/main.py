import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import NormalizationRequest, NormalizationResponse, ViolationItem, OneNFViolationItem, TableSchema, NormStep
from logic import Normalizer

app = FastAPI(title="DB Normalizer API", version="2.0.0")

# ─── CORS ────────────────────────────────────────────────────────────────────
# In production, set CORS_ORIGINS env var to your frontend URL.
# Example: CORS_ORIGINS=https://autonorm.vercel.app
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Limits ──────────────────────────────────────────────────────────────────
MAX_ATTRIBUTES = 26
MAX_FDS = 50
MAX_ATTR_NAME_LENGTH = 50


@app.get("/")
def root():
    return {"message": "Database Normalization API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/normalize", response_model=NormalizationResponse)
def normalize(request: NormalizationRequest):
    # ── Input validation ──
    if not request.attributes:
        raise HTTPException(status_code=400, detail="Attributes list cannot be empty.")
    if not request.functional_dependencies:
        raise HTTPException(status_code=400, detail="At least one functional dependency is required.")
    if len(request.attributes) > MAX_ATTRIBUTES:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_ATTRIBUTES} attributes allowed.")
    if len(request.functional_dependencies) > MAX_FDS:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_FDS} functional dependencies allowed.")
    for attr in request.attributes:
        if len(attr) > MAX_ATTR_NAME_LENGTH:
            raise HTTPException(status_code=400, detail=f"Attribute name '{attr[:20]}...' exceeds {MAX_ATTR_NAME_LENGTH} characters.")

    fds = [(frozenset(fd.lhs), frozenset(fd.rhs)) for fd in request.functional_dependencies]

    normalizer = Normalizer(
        request.attributes,
        fds,
        multivalued_attributes=request.multivalued_attributes or [],
        has_repeating_groups=request.has_repeating_groups or False,
    )
    candidate_keys = normalizer.find_candidate_keys()

    violations_1nf = normalizer.check_1nf_violations()
    violations_2nf = normalizer.check_2nf_violations()
    violations_3nf = normalizer.check_3nf_violations()
    violations_bcnf = normalizer.check_bcnf_violations()

    tables_2nf = normalizer.decompose_to_2nf() if violations_2nf else [
        {"name": "Original_Table", "attributes": sorted(request.attributes),
         "primary_key": sorted(list(candidate_keys[0])) if candidate_keys else []}
    ]

    tables_3nf = normalizer.decompose_to_3nf() if violations_3nf else (
        tables_2nf if violations_2nf else [
            {"name": "Original_Table", "attributes": sorted(request.attributes),
             "primary_key": sorted(list(candidate_keys[0])) if candidate_keys else []}
        ]
    )

    tables_bcnf = normalizer.decompose_to_bcnf() if violations_bcnf else tables_3nf

    return NormalizationResponse(
        candidate_keys=[sorted(list(k)) for k in candidate_keys],
        prime_attributes=sorted(list(normalizer.prime_attributes)),
        violations_1nf=[OneNFViolationItem(**v) for v in violations_1nf],
        violations_2nf=[ViolationItem(**v) for v in violations_2nf],
        violations_3nf=[ViolationItem(**v) for v in violations_3nf],
        violations_bcnf=[ViolationItem(**v) for v in violations_bcnf],
        tables_2nf=[TableSchema(**t) for t in tables_2nf],
        tables_3nf=[TableSchema(**t) for t in tables_3nf],
        tables_bcnf=[TableSchema(**t) for t in tables_bcnf],
        is_1nf=len(violations_1nf) == 0,
        is_2nf=len(violations_2nf) == 0,
        is_3nf=len(violations_3nf) == 0,
        is_bcnf=len(violations_bcnf) == 0,
        steps_1nf=[NormStep(**s) for s in normalizer.get_1nf_steps()],
        steps_keys=[NormStep(**s) for s in normalizer.get_candidate_key_steps()],
        steps_2nf=[NormStep(**s) for s in normalizer.get_2nf_steps()],
        steps_3nf=[NormStep(**s) for s in normalizer.get_3nf_steps()],
        steps_bcnf=[NormStep(**s) for s in normalizer.get_bcnf_steps()],
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
