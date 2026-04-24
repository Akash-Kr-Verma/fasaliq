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

DIVISION_MAP = {
    'Konkan':     ['Mumbai City', 'Mumbai Suburban', 'Thane', 'Palghar', 'Raigad', 'Ratnagiri', 'Sindhudurg'],
    'Nashik':     ['Nashik', 'Dhule', 'Nandurbar', 'Jalgaon', 'Ahmednagar'],
    'Pune':       ['Pune', 'Solapur', 'Satara', 'Sangli', 'Kolhapur'],
    'Aurangabad': ['Aurangabad', 'Jalna', 'Beed', 'Osmanabad', 'Latur', 'Hingoli', 'Nanded', 'Parbhani'],
    'Amravati':   ['Amravati', 'Akola', 'Washim', 'Buldhana', 'Yavatmal'],
    'Nagpur':     ['Nagpur', 'Wardha', 'Bhandara', 'Gondia', 'Chandrapur', 'Gadchiroli'],
}

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

    # Get latest 5 anomalies with farmer names
    latest_anomalies = db.query(Anomaly).join(User, Anomaly.farmer_id == User.id).order_by(
        Anomaly.reported_at.desc()
    ).limit(5).all()

    # Get latest 5 recommendations with farmer and crop names
    latest_recs = db.query(Recommendation).join(User, Recommendation.farmer_id == User.id).join(
        Crop, Recommendation.crop_id == Crop.id
    ).order_by(Recommendation.created_at.desc()).limit(5).all()

    return {
        "total_farmers": total_farmers,
        "total_buyers": total_buyers,
        "total_recommendations": total_recommendations,
        "total_surplus_alerts": total_surplus_alerts,
        "total_anomalies": total_anomalies,
        "recent_anomalies": [
            {
                "id": a.id,
                "farmer": a.farmer.name,
                "district": a.farmer.district,
                "type": a.anomaly_type,
                "detected_crop": a.detected_crop,
                "reason": a.reason,
                "reported_at": a.reported_at
            } for a in latest_anomalies
        ],
        "recent_recommendations": [
            {
                "id": r.id,
                "farmer": r.farmer.name,
                "crop": r.crop.name,
                "district": r.farmer.district,
                "score": round(r.score, 2),
                "created_at": r.created_at
            } for r in latest_recs
        ]
    }

@router.get("/recommendations")
def get_all_recommendations(
    district: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Recommendation).join(User, Recommendation.farmer_id == User.id).join(Crop, Recommendation.crop_id == Crop.id)
    if district:
        query = query.filter(User.district == district)
    
    recs = query.order_by(Recommendation.created_at.desc()).all()

    return {
        "total": len(recs),
        "recommendations": [
            {
                "id": r.id,
                "farmer_name": r.farmer.name,
                "crop_name": r.crop.name,
                "district": r.farmer.district,
                "score": round(r.score, 2),
                "income_estimate": r.income_estimate,
                "selected": r.selected,
                "created_at": r.created_at
            }
            for r in recs
        ]
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
    from app.models.buyer_interests import BuyerInterest
    
    farmers = db.query(User).filter(
        User.role == UserRole.farmer,
        User.district == district
    ).all()

    farmer_ids = [f.id for f in farmers]

    # Crops in progress (recommendations that were selected)
    active_recs = db.query(Recommendation).filter(
        Recommendation.farmer_id.in_(farmer_ids),
        Recommendation.selected == True
    ).all()

    crops_in_progress = {}
    projected_yield = 0.0
    yield_breakdown = []
    
    crop_yield_sums = {}
    for rec in active_recs:
        crop = db.query(Crop).filter(Crop.id == rec.crop_id).first()
        if crop:
            crops_in_progress[crop.name] = crops_in_progress.get(crop.name, 0) + 1
            projected_yield += crop.avg_yield
            crop_yield_sums[crop.name] = crop_yield_sums.get(crop.name, 0) + crop.avg_yield

    for crop_name, total in crop_yield_sums.items():
        yield_breakdown.append({
            "crop": crop_name,
            "total_yield": round(total, 2)
        })

    # Buyer Demand in this district
    buyer_demand = db.query(BuyerInterest).filter(
        BuyerInterest.district == district
    ).all()
    
    demand_stats = {}
    for demand in buyer_demand:
        crop = db.query(Crop).filter(Crop.id == demand.crop_id).first()
        if crop:
            demand_stats[crop.name] = demand_stats.get(crop.name, 0) + demand.quantity

    # All recommendations for distribution chart
    all_recs = db.query(Recommendation).filter(
        Recommendation.farmer_id.in_(farmer_ids)
    ).all()
    
    crop_counts = {}
    for rec in all_recs:
        crop = db.query(Crop).filter(Crop.id == rec.crop_id).first()
        if crop:
            crop_counts[crop.name] = crop_counts.get(crop.name, 0) + 1

    surplus_alerts = check_surplus(district, crop_counts)

    # Save alerts to DB
    for alert in surplus_alerts:
        crop = db.query(Crop).filter(Crop.name == alert["crop_name"]).first()
        if crop:
            existing = db.query(SurplusAlert).filter(
                SurplusAlert.district == district,
                SurplusAlert.crop_id == crop.id
            ).first()

            if not existing:
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
        "crops_in_progress": crops_in_progress,
        "projected_yield": projected_yield,
        "yield_breakdown": yield_breakdown,
        "buyer_demand": demand_stats,
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
                "detected_crop": a.detected_crop,
                "reason": a.reason,
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

@router.get("/district-analytics/{district}")
def district_analytics(district: str, db: Session = Depends(get_db)):
    from app.models.buyer_interests import BuyerInterest

    farmers = db.query(User).filter(
        User.role == UserRole.farmer,
        User.district == district
    ).all()
    farmer_ids = [f.id for f in farmers]

    # Active crops from selected recommendations
    active_recs = db.query(Recommendation).filter(
        Recommendation.farmer_id.in_(farmer_ids),
        Recommendation.selected == True
    ).all()

    # Supply per crop (avg_yield per farmer who chose it)
    crop_supply = {}
    active_crop_ids = set()
    for rec in active_recs:
        crop = db.query(Crop).filter(Crop.id == rec.crop_id).first()
        if crop:
            crop_supply[crop.name] = crop_supply.get(crop.name, 0) + crop.avg_yield
            active_crop_ids.add(crop.id)

    # Buyer demand per crop in this district
    buyer_demand_rows = db.query(BuyerInterest).filter(
        BuyerInterest.district == district
    ).all()
    crop_demand = {}
    for d in buyer_demand_rows:
        crop = db.query(Crop).filter(Crop.id == d.crop_id).first()
        if crop:
            crop_demand[crop.name] = crop_demand.get(crop.name, 0) + d.quantity

    # MSP vs Market Price for all active/demanded crops in this district
    all_crop_names = set(list(crop_supply.keys()) + list(crop_demand.keys()))
    msp_vs_market = []
    for crop_name in all_crop_names:
        crop = db.query(Crop).filter(Crop.name == crop_name).first()
        if crop:
            latest_price = db.query(MarketPrice).filter(
                MarketPrice.crop_id == crop.id,
                MarketPrice.district == district
            ).order_by(MarketPrice.date.desc()).first()
            market_p = latest_price.price if latest_price else None
            msp_vs_market.append({
                "crop": crop_name,
                "msp": round(crop.msp, 2),
                "market_price": round(market_p, 2) if market_p else None,
                "has_msp": crop.has_msp,
                "below_msp": (market_p < crop.msp) if (market_p and crop.has_msp and crop.msp > 0) else False
            })

    # Supply-demand gap per crop
    all_crops_union = set(list(crop_supply.keys()) + list(crop_demand.keys()))
    supply_demand_gap = []
    for crop_name in all_crops_union:
        supply = round(crop_supply.get(crop_name, 0), 2)
        demand = round(crop_demand.get(crop_name, 0), 2)
        supply_demand_gap.append({
            "crop": crop_name,
            "supply": supply,
            "demand": demand,
            "gap": round(supply - demand, 2)
        })

    # MSP Compliance
    active_crops_all = db.query(Crop).filter(Crop.id.in_(list(active_crop_ids))).all()
    total_active = len(active_crops_all)
    msp_covered = sum(1 for c in active_crops_all if c.has_msp and c.msp > 0)
    compliance_rate = round((msp_covered / total_active * 100) if total_active > 0 else 0, 1)

    # --- NEW: Cross-District Matchmaking ---
    from sqlalchemy import func
    supply_matches = [] # Where can we sell our surplus?
    demand_matches = [] # Where can we source our deficit?

    # For crops we have supply of, find demand elsewhere
    for crop_name, supply_qty in crop_supply.items():
        crop_obj = db.query(Crop).filter(Crop.name == crop_name).first()
        if not crop_obj: continue
        
        other_demands = db.query(
            BuyerInterest.district, 
            func.sum(BuyerInterest.quantity).label('total_qty')
        ).filter(
            BuyerInterest.crop_id == crop_obj.id,
            BuyerInterest.district != district
        ).group_by(BuyerInterest.district).all()

        for d_dist, d_qty in other_demands:
            supply_matches.append({
                "crop": crop_name,
                "target_district": d_dist,
                "demand_qty": round(d_qty, 2),
                "potential_match": round(min(supply_qty, d_qty), 2)
            })

    # For crops we have demand for, find supply elsewhere
    for crop_name, demand_qty in crop_demand.items():
        crop_obj = db.query(Crop).filter(Crop.name == crop_name).first()
        if not crop_obj: continue

        # Find other districts where this crop is "selected" in recommendations
        # This is a bit expensive, but necessary for the "Smart" feel
        other_dist_farmers = db.query(User.district, func.count(User.id)).filter(
            User.role == UserRole.farmer,
            User.district != district
        ).join(Recommendation, Recommendation.farmer_id == User.id).filter(
            Recommendation.crop_id == crop_obj.id,
            Recommendation.selected == True
        ).group_by(User.district).all()

        for s_dist, f_count in other_dist_farmers:
            # Estimate supply from farmer count * avg_yield
            s_qty = f_count * crop_obj.avg_yield
            demand_matches.append({
                "crop": crop_name,
                "source_district": s_dist,
                "available_supply": round(s_qty, 2),
                "potential_match": round(min(demand_qty, s_qty), 2)
            })

    return {
        "district": district,
        "msp_vs_market": msp_vs_market,
        "supply_demand_gap": supply_demand_gap,
        "msp_compliance": {
            "total_active_crops": total_active,
            "msp_covered": msp_covered,
            "compliance_rate": compliance_rate
        },
        "supply_matches": supply_matches,
        "demand_matches": demand_matches
    }

@router.get("/state-heatmap")
def state_heatmap(db: Session = Depends(get_db)):
    from app.models.buyer_interests import BuyerInterest

    result = []
    for division_name, districts in DIVISION_MAP.items():
        total_farmers = db.query(User).filter(
            User.role == UserRole.farmer,
            User.district.in_(districts)
        ).count()

        surplus_count = db.query(SurplusAlert).filter(
            SurplusAlert.district.in_(districts)
        ).count()

        farmer_ids = [
            f.id for f in db.query(User).filter(
                User.role == UserRole.farmer,
                User.district.in_(districts)
            ).all()
        ]

        crop_counts = {}
        for rec in db.query(Recommendation).filter(
            Recommendation.farmer_id.in_(farmer_ids),
            Recommendation.selected == True
        ).all():
            crop = db.query(Crop).filter(Crop.id == rec.crop_id).first()
            if crop:
                crop_counts[crop.name] = crop_counts.get(crop.name, 0) + 1

        top_crop = max(crop_counts, key=crop_counts.get) if crop_counts else None
        total_buyers = db.query(User).filter(
            User.role == UserRole.buyer,
            User.district.in_(districts)
        ).count()
        demand_entries = db.query(BuyerInterest).filter(
            BuyerInterest.district.in_(districts)
        ).count()

        # Risk calculation
        if surplus_count >= 5:
            risk = "critical"
        elif surplus_count >= 2:
            risk = "high"
        elif surplus_count >= 1:
            risk = "medium"
        else:
            risk = "low"

        result.append({
            "division": division_name,
            "districts": districts,
            "total_farmers": total_farmers,
            "total_buyers": total_buyers,
            "surplus_alerts": surplus_count,
            "top_crop": top_crop,
            "demand_entries": demand_entries,
            "risk_level": risk
        })

    return {"divisions": result}

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