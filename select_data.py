"""Просмотр данных из wedding.db (RSVP и Event). Запуск: python select_data.py"""
import sys
sys.stdout.reconfigure(encoding="utf-8")  # чтобы в консоли Windows не ломалась кириллица

from db import SessionLocal
from models import Rsvp, Event

def main():
    db = SessionLocal()
    print("=== RSVP ===")
    for r in db.query(Rsvp).all():
        drinks = [d.drink for d in r.drinks]
        print(f"  id={r.id} name={r.name!r} attending={r.attending} hot_dish={r.hot_dish!r} drinks={drinks} comment={r.comment!r} created_at={r.created_at}")
    print("=== Event ===")
    for e in db.query(Event).all():
        print(f"  id={e.id} event_name={e.event_name!r} element_id={e.element_id} page={e.page} session_id={e.session_id} created_at={e.created_at}")
    db.close()

if __name__ == "__main__":
    main()
