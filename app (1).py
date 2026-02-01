# ===============================
# Medication Extractor Pro
# FINAL WORKING FastAPI APP
# ===============================

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from passlib.hash import bcrypt
import json

from database import engine, SessionLocal
import models
from extractor import extract_medications


# ===============================
# INIT
# ===============================

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="💊 Medication Extractor Pro")

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


# ===============================
# DB CONNECTION
# ===============================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===============================
# DEMO USER SETUP (IMPORTANT)
# first time open /setup
# ===============================

@app.get("/setup")
def setup(db: Session = Depends(get_db)):

    if not db.query(models.User).first():

        doctor = models.User(
            username="doctor",
            password=bcrypt.hash("123"),
            role="doctor"
        )

        patient = models.User(
            username="patient1",
            password=bcrypt.hash("123"),
            role="patient"
        )

        db.add(doctor)
        db.add(patient)
        db.commit()

    return {"message": "Demo users created ✅"}


# ===============================
# LOGIN PAGE
# ===============================

@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# ===============================
# LOGIN POST
# ===============================

@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter_by(username=username).first()

    # correct login
    if user and bcrypt.verify(password, user.password):

        # doctor → dashboard
        if user.role == "doctor":
            return RedirectResponse(url="/dashboard", status_code=303)

        # patient → records
        else:
            return RedirectResponse(url=f"/patient/{user.id}", status_code=303)

    # wrong login
    return RedirectResponse(url="/", status_code=303)


# ===============================
# DOCTOR DASHBOARD
# ===============================

@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# ===============================
# SAVE PRESCRIPTION
# ===============================

@app.post("/save")
def save_prescription(
    patient_id: int = Form(...),
    text: str = Form(...),
    db: Session = Depends(get_db)
):

    meds = extract_medications(text)

    record = models.Prescription(
        patient_id=patient_id,
        raw_text=text,
        extracted=json.dumps(meds, indent=2)
    )

    db.add(record)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)


# ===============================
# PATIENT RECORDS PAGE
# ===============================

@app.get("/patient/{uid}")
def patient_page(
    uid: int,
    request: Request,
    db: Session = Depends(get_db)
):

    records = db.query(models.Prescription).filter_by(patient_id=uid).all()

    return templates.TemplateResponse(
        "patient.html",
        {
            "request": request,
            "records": records
        }
    )


# ===============================
# OPTIONAL: EXTRACTION API
# ===============================

@app.post("/api/extract")
def api_extract(text: str = Form(...)):
    meds = extract_medications(text)
    return {"medications": meds}