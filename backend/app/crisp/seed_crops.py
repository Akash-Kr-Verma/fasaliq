from app.core.database import SessionLocal
from app.models.crops import Crop
from app.crisp.crop_data import CROPS

def seed():
    db = SessionLocal()
    existing = db.query(Crop).first()
    if existing:
        print("Crops already seeded.")
        db.close()
        return

    for c in CROPS:
        crop = Crop(
            name=c["name"],
            season=c["season"],
            water_need=c["water_need"],
            soil_fit=", ".join(c["soil_fit"]),
            msp=c["msp"],
            avg_yield=c["avg_yield"],
            has_msp=c["has_msp"]
        )
        db.add(crop)

    db.commit()
    db.close()
    print(f"Seeded {len(CROPS)} crops successfully.")

if __name__ == "__main__":
    seed()