from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from db import Base, engine, SessionLocal
from models import Rsvp, RsvpDrink, Event


# Создаём таблицы при старте (для MVP нормально).
# После смены схемы удалите wedding.db, чтобы таблицы создались заново.
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RsvpIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    comment: str | None = Field(default=None, max_length=2000)
    attending: bool = Field(description="True = придёт, False = не придёт")
    hot_dish: str | None = Field(default=None, pattern="^(fish|meat)$", description="fish или meat")
    drinks: list[str] = Field(default_factory=list, max_length=20, description="Список напитков")

class EventIn(BaseModel):
    event_name: str = Field(min_length=1, max_length=100)
    element_id: str | None = Field(default=None, max_length=100)
    page: str | None = Field(default=None, max_length=100)
    session_id: str | None = Field(default=None, max_length=100)

app = FastAPI()

CODE_STATS = "14012021"


# API-маршруты регистрируем до mount("/"), иначе POST /api/... перехватит статика и вернёт 405
@app.post("/api/rsvp")
def create_rsvp(payload: RsvpIn, db: Session = Depends(get_db)):
    row = Rsvp(
        name=payload.name,
        comment=payload.comment,
        attending=payload.attending,
        hot_dish=payload.hot_dish,
    )
    db.add(row)
    db.flush()  # чтобы получить row.id
    for drink in payload.drinks:
        db.add(RsvpDrink(rsvp_id=row.id, drink=drink))
    db.commit()
    db.refresh(row)
    return {"id": row.id}

@app.post("/api/event")
def create_event(payload: EventIn, db: Session = Depends(get_db)):
    row = Event(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id}


@app.get("/api/stats/{code}")
def get_stats(code: str, db: Session = Depends(get_db)):
    if code != CODE_STATS:
        raise HTTPException(status_code=403, detail="Invalid code")

    rsvps = (
        db.query(Rsvp)
        .options(joinedload(Rsvp.drinks))
        .order_by(Rsvp.created_at.asc())
        .all()
    )

    total = len(rsvps)
    attending_yes = sum(1 for r in rsvps if r.attending)
    attending_no = total - attending_yes

    hot_counts = {"meat": 0, "fish": 0, "none": 0}
    drinks_counts: dict[str, int] = {}
    details: list[dict] = []

    for r in rsvps:
        # горячеe
        if r.hot_dish == "meat":
            hot_counts["meat"] += 1
            hot_label = "Мясо"
        elif r.hot_dish == "fish":
            hot_counts["fish"] += 1
            hot_label = "Рыба"
        else:
            hot_counts["none"] += 1
            hot_label = "—"

        # напитки
        r_drinks = [d.drink for d in r.drinks]
        for dname in r_drinks:
            drinks_counts[dname] = drinks_counts.get(dname, 0) + 1

        details.append(
            {
                "id": r.id,
                "name": r.name,
                "attending": r.attending,
                "attending_label": "Придёт" if r.attending else "Не придёт",
                "hot_dish": r.hot_dish,
                "hot_dish_label": hot_label,
                "drinks": r_drinks,
                "created_at": r.created_at.isoformat() if isinstance(r.created_at, datetime) else str(r.created_at),
            }
        )

    return {
        "code": CODE_STATS,
        "total": total,
        "attending": {"yes": attending_yes, "no": attending_no},
        "hot_dish": hot_counts,
        "drinks": drinks_counts,
        "details": details,
    }


@app.get(f"/{CODE_STATS}", include_in_schema=False)
def stats_page():
    return FileResponse(STATIC_DIR / "stats.html")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
# Монтируем static в корень: тогда / отдаёт index.html, а /рилс_files/... — файлы из static/рилс_files/
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")