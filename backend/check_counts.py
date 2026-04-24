from app.core.database import SessionLocal
from app.models.users import User, UserRole

def check_counts():
    db = SessionLocal()
    try:
        total_farmers = db.query(User).filter(User.role == UserRole.farmer).count()
        total_buyers = db.query(User).filter(User.role == UserRole.buyer).count()
        total_admins = db.query(User).filter(User.role == UserRole.admin).count()
        
        print(f"Total Farmers: {total_farmers}")
        print(f"Total Buyers: {total_buyers}")
        print(f"Total Admins: {total_admins}")
        
        farmers = db.query(User).filter(User.role == UserRole.farmer).all()
        if farmers:
            print("\nRecent Farmers:")
            for f in farmers[:5]:
                print(f"- {f.name} ({f.district})")
                
        buyers = db.query(User).filter(User.role == UserRole.buyer).all()
        if buyers:
            print("\nRecent Buyers:")
            for b in buyers[:5]:
                print(f"- {b.name} ({b.district})")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_counts()
