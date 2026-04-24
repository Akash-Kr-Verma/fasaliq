"""
Seed Script: Strawberry Scenario
=================================
Scenario:
  - Mumbai City: Super high buyer demand for strawberries (6,000 T)
  - Satara: 2 farmers growing strawberries (1,000 T supply) — not enough to meet demand
  - Gadchiroli: 1 farmer had strawberries but heat strokes destroyed the crop
                (would have added ~500 T, enough to almost close the gap,
                but the anomaly means that supply is lost)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.users import User, UserRole
from app.models.crops import Crop
from app.models.recommendations import Recommendation
from app.models.buyer_interests import BuyerInterest
from app.models.anomalies import Anomaly
from app.core.security import hash_password

db = SessionLocal()

try:
    # ─────────────────────────────────────────────
    # 1. Ensure Strawberry exists in crops table
    # ─────────────────────────────────────────────
    strawberry = db.query(Crop).filter(Crop.name == "Strawberry").first()
    if not strawberry:
        strawberry = Crop(
            name="Strawberry",
            season="Rabi",
            water_need="High",
            soil_fit="Sandy Loam",
            msp=0.0,
            avg_yield=500.0,   # 500 T per farmer per season
            has_msp=False
        )
        db.add(strawberry)
        db.flush()  # get strawberry.id
        print(f"  ✅ Created crop: Strawberry (id={strawberry.id})")
    else:
        # Make sure avg_yield is set properly
        strawberry.avg_yield = 500.0
        print(f"  ✅ Strawberry already exists (id={strawberry.id})")

    # ─────────────────────────────────────────────
    # 2. Mumbai City — 3 LARGE buyers (2,000 T each = 6,000 T total demand)
    # ─────────────────────────────────────────────
    print("\n📦 Creating Mumbai City buyers...")
    buyers = [
        {"name": "FreshMart Mumbai (Retailer)",  "phone": "9801110001", "email": "freshmart@mumbai.com",   "qty": 2000.0},
        {"name": "Mumbai Hotels Consortium",      "phone": "9801110002", "email": "hotels@mumbai.com",      "qty": 2000.0},
        {"name": "Reliance Fresh Mumbai Central", "phone": "9801110003", "email": "reliance@mumbai.com",    "qty": 2000.0},
    ]
    for b in buyers:
        existing = db.query(User).filter(User.phone == b["phone"]).first()
        if existing:
            buyer_user = existing
            print(f"  ↩ Buyer already exists: {b['name']}")
        else:
            buyer_user = User(
                name=b["name"],
                phone=b["phone"],
                email=b["email"],
                password_hash=hash_password("seed123"),
                role=UserRole.buyer,
                district="Mumbai City",
                state="Maharashtra"
            )
            db.add(buyer_user)
            db.flush()
            print(f"  ✅ Created buyer: {b['name']} (id={buyer_user.id})")

        # Add buyer interest
        existing_interest = db.query(BuyerInterest).filter(
            BuyerInterest.buyer_id == buyer_user.id,
            BuyerInterest.crop_id == strawberry.id
        ).first()
        if not existing_interest:
            interest = BuyerInterest(
                buyer_id=buyer_user.id,
                crop_id=strawberry.id,
                district="Mumbai City",
                quantity=b["qty"],
                offered_price=180.0,   # ₹180/kg premium strawberry price
                status="open"
            )
            db.add(interest)
            print(f"     → Demand: {b['qty']} T at ₹180/kg")

    # ─────────────────────────────────────────────
    # 3. Satara — 2 farmers actively growing strawberries
    #    Supply: 2 × 500 T avg_yield = 1,000 T (far less than 6,000 T demand)
    # ─────────────────────────────────────────────
    print("\n🌱 Creating Satara strawberry farmers...")
    satara_farmers = [
        {"name": "Ramkrishna Patil (Satara)",  "phone": "9701110001", "email": "ramkrishna@satara.mh"},
        {"name": "Suresh Mane (Satara)",        "phone": "9701110002", "email": "suresh@satara.mh"},
    ]
    for f in satara_farmers:
        existing = db.query(User).filter(User.phone == f["phone"]).first()
        if existing:
            farmer_user = existing
            print(f"  ↩ Farmer already exists: {f['name']}")
        else:
            farmer_user = User(
                name=f["name"],
                phone=f["phone"],
                email=f["email"],
                password_hash=hash_password("seed123"),
                role=UserRole.farmer,
                district="Satara",
                state="Maharashtra"
            )
            db.add(farmer_user)
            db.flush()
            print(f"  ✅ Created farmer: {f['name']} (id={farmer_user.id})")

        existing_rec = db.query(Recommendation).filter(
            Recommendation.farmer_id == farmer_user.id,
            Recommendation.crop_id == strawberry.id
        ).first()
        if not existing_rec:
            rec = Recommendation(
                farmer_id=farmer_user.id,
                crop_id=strawberry.id,
                score=0.91,
                income_estimate=90000.0,
                selected=True  # Actively growing
            )
            db.add(rec)
            print(f"     → Active: growing strawberries, ~500 T yield expected")

    # ─────────────────────────────────────────────
    # 4. Gadchiroli — 1 farmer, strawberry crop DESTROYED by heat strokes
    #    Would have contributed ~500 T but anomaly wipes that out
    # ─────────────────────────────────────────────
    print("\n🔥 Creating Gadchiroli heat-stroke anomaly...")
    gadchiroli_phone = "9601110001"
    existing = db.query(User).filter(User.phone == gadchiroli_phone).first()
    if existing:
        gadchiroli_farmer = existing
        print(f"  ↩ Farmer already exists: {gadchiroli_farmer.name}")
    else:
        gadchiroli_farmer = User(
            name="Pandurang Atram (Gadchiroli)",
            phone=gadchiroli_phone,
            email="pandurang@gadchiroli.mh",
            password_hash=hash_password("seed123"),
            role=UserRole.farmer,
            district="Gadchiroli",
            state="Maharashtra"
        )
        db.add(gadchiroli_farmer)
        db.flush()
        print(f"  ✅ Created farmer: Pandurang Atram (id={gadchiroli_farmer.id})")

    # Recommendation NOT selected (crop destroyed, can't deliver)
    existing_rec = db.query(Recommendation).filter(
        Recommendation.farmer_id == gadchiroli_farmer.id,
        Recommendation.crop_id == strawberry.id
    ).first()
    if not existing_rec:
        rec = Recommendation(
            farmer_id=gadchiroli_farmer.id,
            crop_id=strawberry.id,
            score=0.75,
            income_estimate=75000.0,
            selected=False  # NOT active — crop was destroyed
        )
        db.add(rec)

    # Anomaly: heat stroke crop destruction
    existing_anomaly = db.query(Anomaly).filter(
        Anomaly.farmer_id == gadchiroli_farmer.id,
        Anomaly.crop_id == strawberry.id,
        Anomaly.anomaly_type == "crop_loss"
    ).first()
    if not existing_anomaly:
        anomaly = Anomaly(
            farmer_id=gadchiroli_farmer.id,
            crop_id=strawberry.id,
            anomaly_type="crop_loss",
            description=(
                "CRITICAL: Severe heat strokes (temperatures exceeding 43°C) in Gadchiroli "
                "have completely destroyed the strawberry crop of farmer Pandurang Atram. "
                "Estimated 500 metric tonnes of production lost. The crop failure has widened "
                "the supply gap for Mumbai City's 6,000 T demand — only 1,000 T remains "
                "available from Satara. Government intervention required: direct procurement "
                "support and relief compensation for the affected farmer."
            ),
            recovery_plan=(
                "1. Emergency compensation to Pandurang Atram under PMFBY scheme. "
                "2. Redirect procurement from Satara farmers to Mumbai City markets. "
                "3. Issue cold-chain transport subsidy to reduce post-harvest losses. "
                "4. Plant heat-resistant strawberry varieties next season."
            )
        )
        db.add(anomaly)
        print(f"  ✅ Anomaly logged: Heat stroke crop loss (500 T lost, Gadchiroli)")

    db.commit()

    print("\n" + "="*55)
    print("✅  SEED COMPLETE — Strawberry Scenario Summary")
    print("="*55)
    print(f"  🏙️  Mumbai City demand   : 6,000 T (3 buyers × 2,000 T)")
    print(f"  🌱  Satara supply         : 1,000 T (2 farmers × 500 T)")
    print(f"  📉  Supply gap            : -5,000 T  ← CRISIS")
    print(f"  🔥  Gadchiroli loss       : 500 T destroyed by heat")
    print(f"  ⚠️  What would close gap  : Need ~10 more Satara-scale farmers")
    print("="*55)

except Exception as e:
    db.rollback()
    print(f"\n❌ Error: {e}")
    import traceback; traceback.print_exc()
finally:
    db.close()
