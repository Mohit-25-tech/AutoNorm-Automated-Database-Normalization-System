from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import NormalizationRequest, NormalizationResponse, ViolationItem, TableSchema
from logic import Normalizer

app = FastAPI(title="DB Normalizer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Database Normalization API is running"}

@app.post("/normalize", response_model=NormalizationResponse)
def normalize(request: NormalizationRequest):
    if not request.attributes:
        raise HTTPException(status_code=400, detail="Attributes list cannot be empty.")
    if not request.functional_dependencies:
        raise HTTPException(status_code=400, detail="At least one functional dependency is required.")

    fds = [(frozenset(fd.lhs), frozenset(fd.rhs)) for fd in request.functional_dependencies]

    normalizer = Normalizer(request.attributes, fds)
    candidate_keys = normalizer.find_candidate_keys()

    # Use the methods defined in logic.py without changing its core logic
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
        violations_2nf=[ViolationItem(**v) for v in violations_2nf],
        violations_3nf=[ViolationItem(**v) for v in violations_3nf],
        violations_bcnf=[ViolationItem(**v) for v in violations_bcnf],
        tables_2nf=[TableSchema(**t) for t in tables_2nf],
        tables_3nf=[TableSchema(**t) for t in tables_3nf],
        tables_bcnf=[TableSchema(**t) for t in tables_bcnf],
        is_2nf=len(violations_2nf) == 0,
        is_3nf=len(violations_3nf) == 0,
        is_bcnf=len(violations_bcnf) == 0,
    )