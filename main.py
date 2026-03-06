import os
import json
import requests
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="RenoComputerFix Inventory Sync")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "demo_key")
MARKUP_PERCENTAGE = 30
VENDOR_STORE = "Electro Room Laptop Parts"

def scrape_ebay_laptops():
    """Scrape laptop listings from Electro Room eBay store using Serper API"""
    try:
        headers = {"X-API-KEY": SERPER_API_KEY}
        query = f"site:ebay.com {VENDOR_STORE} laptop"
        
        payload = {
            "q": query,
            "num": 15,
            "gl": "us"
        }
        
        response = requests.post(
            "https://google.serper.dev/shopping",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            laptops = []
            
            for item in data.get('shopping', [])[:15]:
                # Extract price and apply markup
                price_str = item.get('price', '0')
                price = float(''.join(filter(str.isdigit, price_str))) if price_str else 0
                marked_up_price = price * (1 + MARKUP_PERCENTAGE / 100)
                
                laptop = {
                    'title': item.get('title', 'Unknown Laptop'),
                    'price': price,
                    'marked_up_price': round(marked_up_price, 2),
                    'image': item.get('imageUrl', '/static/laptop-placeholder.png'),
                    'source': item.get('source', 'eBay'),
                    'link': item.get('link', '#'),
                    'snippet': item.get('snippet', 'Refurbished laptop in good condition')
                }
                
                laptops.append(laptop)
            
            # Save scraped data
            with open('data/scraped_inventory.json', 'w') as f:
                json.dump({
                    'laptops': laptops,
                    'last_updated': datetime.now().isoformat(),
                    'source': 'live_scrape'
                }, f, indent=2)
            
            return laptops
            
    except Exception as e:
        print(f"Scraping failed: {e}")
        return None

def load_fallback_data():
    """Load fallback mock data if live scraping fails"""
    try:
        with open('data/fallback.json', 'r') as f:
            data = json.load(f)
            return data['laptops']
    except:
        return []

def get_inventory():
    """Get laptop inventory - try live scrape first, fallback to mock data"""
    
    # Try to load recently scraped data first
    try:
        with open('data/scraped_inventory.json', 'r') as f:
            data = json.load(f)
            # Use cached data if less than 1 hour old
            last_updated = datetime.fromisoformat(data['last_updated'])
            if (datetime.now() - last_updated).seconds < 3600:
                return data['laptops'], data['source']
    except:
        pass
    
    # Try live scrape
    laptops = scrape_ebay_laptops()
    if laptops:
        return laptops, 'live_scrape'
    
    # Fallback to mock data
    return load_fallback_data(), 'fallback'

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    laptops, source = get_inventory()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "laptops": laptops,
        "total_laptops": len(laptops),
        "markup_percentage": MARKUP_PERCENTAGE,
        "vendor_store": VENDOR_STORE,
        "last_updated": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "data_source": source
    })

@app.get("/api/refresh")
async def refresh_inventory():
    """Force refresh of inventory data"""
    laptops = scrape_ebay_laptops()
    if laptops:
        return {
            "status": "success", 
            "message": f"Refreshed {len(laptops)} laptop listings",
            "laptops": len(laptops)
        }
    else:
        return {
            "status": "error", 
            "message": "Failed to refresh - using cached data"
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)