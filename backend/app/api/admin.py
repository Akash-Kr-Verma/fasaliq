from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.users import User, UserRole
from app.models.crops import Crop
from app.models.recommendations import Recommendation
from app.models.surplus_alerts import SurplusAlert
from app.models.market_prices import MarketPrice
from app.models.anomalies import Anomaly
from app.crisp.surplus_checker import check_surplus
from datetime import date
from fastapi.responses import HTMLResponse
from app.core.security import verify_dashboard_credentials

router = APIRouter(prefix="/api/admin", tags=["Admin"])

class MarketPriceInput(BaseModel):
    crop_name: str
    district: str
    price: float
    source: Optional[str] = "Manual"

class MSPUpdateInput(BaseModel):
    crop_name: str
    msp: float

class SurplusCheckInput(BaseModel):
    district: str

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    total_farmers = db.query(User).filter(
        User.role == UserRole.farmer
    ).count()

    total_buyers = db.query(User).filter(
        User.role == UserRole.buyer
    ).count()

    total_recommendations = db.query(Recommendation).count()

    total_surplus_alerts = db.query(SurplusAlert).count()

    total_anomalies = db.query(Anomaly).count()

    return {
        "total_farmers": total_farmers,
        "total_buyers": total_buyers,
        "total_recommendations": total_recommendations,
        "total_surplus_alerts": total_surplus_alerts,
        "total_anomalies": total_anomalies
    }

@router.get("/farmers")
def get_all_farmers(
    district: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(User).filter(User.role == UserRole.farmer)
    if district:
        query = query.filter(User.district == district)
    farmers = query.all()

    return {
        "total": len(farmers),
        "farmers": [
            {
                "id": f.id,
                "name": f.name,
                "phone": f.phone,
                "district": f.district,
                "created_at": f.created_at
            }
            for f in farmers
        ]
    }

@router.get("/district-overview/{district}")
def district_overview(district: str, db: Session = Depends(get_db)):
    farmers = db.query(User).filter(
        User.role == UserRole.farmer,
        User.district == district
    ).all()

    farmer_ids = [f.id for f in farmers]

    recs = db.query(Recommendation).filter(
        Recommendation.farmer_id.in_(farmer_ids)
    ).all()

    crop_counts = {}
    for rec in recs:
        crop = db.query(Crop).filter(Crop.id == rec.crop_id).first()
        if crop:
            crop_counts[crop.name] = crop_counts.get(crop.name, 0) + 1

    surplus_alerts = check_surplus(district, crop_counts)

    for alert in surplus_alerts:
        existing = db.query(SurplusAlert).filter(
            SurplusAlert.district == district,
            SurplusAlert.crop_id == db.query(Crop).filter(
                Crop.name == alert["crop_name"]
            ).first().id
        ).first()

        if not existing:
            crop = db.query(Crop).filter(
                Crop.name == alert["crop_name"]
            ).first()
            if crop:
                new_alert = SurplusAlert(
                    district=district,
                    crop_id=crop.id,
                    farmer_count=alert["farmer_count"],
                    market_capacity=alert["market_capacity"],
                    ratio=alert["ratio"],
                    severity=alert["severity"]
                )
                db.add(new_alert)

    db.commit()

    return {
        "district": district,
        "total_farmers": len(farmers),
        "crop_distribution": crop_counts,
        "surplus_alerts": surplus_alerts
    }

@router.post("/market-price")
def add_market_price(
    data: MarketPriceInput,
    db: Session = Depends(get_db)
):
    crop = db.query(Crop).filter(Crop.name == data.crop_name).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    price = MarketPrice(
        crop_id=crop.id,
        district=data.district,
        price=data.price,
        date=date.today(),
        source=data.source
    )
    db.add(price)
    db.commit()
    db.refresh(price)

    return {
        "message": "Market price added",
        "crop": data.crop_name,
        "district": data.district,
        "price": data.price,
        "date": date.today()
    }

@router.put("/msp-update")
def update_msp(
    data: MSPUpdateInput,
    db: Session = Depends(get_db)
):
    crop = db.query(Crop).filter(Crop.name == data.crop_name).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    crop.msp = data.msp
    crop.has_msp = True
    db.commit()

    return {
        "message": f"MSP updated for {data.crop_name}",
        "crop": data.crop_name,
        "new_msp": data.msp
    }

@router.get("/surplus-alerts")
def get_surplus_alerts(
    district: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SurplusAlert)
    if district:
        query = query.filter(SurplusAlert.district == district)

    alerts = query.order_by(
        SurplusAlert.alerted_at.desc()
    ).all()

    return {
        "total": len(alerts),
        "alerts": [
            {
                "id": a.id,
                "district": a.district,
                "crop_id": a.crop_id,
                "farmer_count": a.farmer_count,
                "market_capacity": a.market_capacity,
                "ratio": a.ratio,
                "severity": a.severity,
                "alerted_at": a.alerted_at
            }
            for a in alerts
        ]
    }

@router.get("/anomalies")
def get_anomalies(
    district: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Anomaly).join(
        User, Anomaly.farmer_id == User.id
    )
    if district:
        query = query.filter(User.district == district)

    anomalies = query.order_by(
        Anomaly.reported_at.desc()
    ).all()

    return {
        "total": len(anomalies),
        "anomalies": [
            {
                "id": a.id,
                "farmer_id": a.farmer_id,
                "crop_id": a.crop_id,
                "type": a.anomaly_type,
                "description": a.description,
                "reported_at": a.reported_at
            }
            for a in anomalies
        ]
    }

@router.get("/crops")
def get_all_crops(db: Session = Depends(get_db)):
    crops = db.query(Crop).all()
    return {
        "total": len(crops),
        "crops": [
            {
                "id": c.id,
                "name": c.name,
                "season": c.season,
                "msp": c.msp,
                "has_msp": c.has_msp,
                "avg_yield": c.avg_yield
            }
            for c in crops
        ]
    }

@router.get("/users-ui", response_class=HTMLResponse)
def get_users_ui(
    username: str = Depends(verify_dashboard_credentials),
    db: Session = Depends(get_db)
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    rows_html = ""
    for u in users:
        role_val = u.role.value if hasattr(u.role, 'value') else str(u.role)
        role_color = "bg-green-100 text-green-800" if role_val == "farmer" else ("bg-blue-100 text-blue-800" if role_val == "buyer" else "bg-purple-100 text-purple-800")
        
        created_at_str = u.created_at.strftime('%Y-%m-%d %H:%M') if u.created_at else '-'
        email_str = u.email if u.email else '-'
        
        rows_html += f"""
        <tr class="hover:bg-gray-50 transition-colors">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{u.id}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{u.name}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{u.phone}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{email_str}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {role_color}">
                    {role_val.capitalize()}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{u.district}, {u.state}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{created_at_str}</td>
        </tr>
        """
        
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FasalIQ - Admin Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; background-color: #f3f4f6; }}
        </style>
    </head>
    <body class="antialiased text-gray-900">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <div class="sm:flex sm:items-center">
                <div class="sm:flex-auto">
                    <h1 class="text-3xl font-bold text-gray-900">User Dataset Dashboard</h1>
                    <p class="mt-2 text-sm text-gray-700">A secure, real-time overview of all registered farmers, buyers, and admins in the FasalIQ platform.</p>
                </div>
            </div>
            <div class="mt-8 flex flex-col">
                <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
                    <div class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
                        <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg bg-white">
                            <table class="min-w-full divide-y divide-gray-300">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-gray-200">
                                    {rows_html}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="mt-6 text-center text-sm text-gray-500">
                Securely authenticated as <strong>{username}</strong>. Data refreshed at {date.today().strftime('%B %d, %Y')}.
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)