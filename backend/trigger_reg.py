import requests
import random

def trigger_register():
    phone = str(random.randint(1000000000, 9999999999))
    print(f"Triggering registration for {phone}")
    url = "http://10.0.2.2:8000/api/auth/register"
    # Wait, I should use localhost
    url = "http://localhost:8000/api/auth/register"
    
    data = {
        "name": "Trigger Test",
        "phone": phone,
        "password": "password123",
        "role": "farmer",
        "district": "Pune"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger_register()
