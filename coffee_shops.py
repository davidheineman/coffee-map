import json
import os
import requests
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
api_key = os.getenv('PLACES_API_KEY')

MAX_PAGE_COUNT = 3 # API allows up to 60 results

QUERY = 'coffee shops'
# QUERY = 'bar with live music'
# QUERY = 'mens haircut'
# QUERY = 'grocery store'

if not api_key:
    raise ValueError("Please set your PLACES_API_KEY in the .env file")

def get_coffee_shops(latitude=47.6615197, longitude=-122.3368014999999):
    base_url = "https://places.googleapis.com/v1/places:searchText"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': 'nextPageToken,places.displayName,places.formattedAddress,places.rating,places.nationalPhoneNumber,places.location.latitude,places.location.longitude,places.websiteUri,places.primaryType,places.reviewSummary.text',
    }
    
    data = {
        'textQuery': QUERY,
        'pageSize': 20,
        'rankPreference': 'DISTANCE',
        'locationBias': {
            'circle': {
                'center': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'radius': 1000.0  # 1km radius
            }
        }
    }
    
    all_places = []
    page_count = 1
    
    try:
        while page_count <= MAX_PAGE_COUNT:
            response = requests.post(base_url, headers=headers, json=data)
            response.raise_for_status()
            
            results = response.json()
            places = results.get('places', [])
            all_places.extend(places)
            
            # print(f"Fetched page {page_count}/{MAX_PAGE_COUNT} with {len(places)} results")
            
            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break
                
            data['pageToken'] = next_page_token
            page_count += 1
            
        return all_places
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        if hasattr(e, 'response') and e.response and e.response.text:
            print(f"Response: {e.response.text}")
        return []

def get_all_locations():
    # List of coordinates
    coordinates = [
        (47.646431, -122.335499),
        (47.637757, -122.357305),
        (47.667322, -122.381464),
        (47.696397, -122.374767),
        (47.699731, -122.331796),
        (47.730342, -122.363560),
        (47.672106, -122.259184),
        (47.631856, -122.304601),
        (47.617278, -122.303571),
        (47.616005, -122.321256),
        (47.638334, -122.326750),
        (47.621675, -122.337739),
        (47.616931, -122.335163),
        (47.621097, -122.356280),
        (47.604802, -122.329135),
        (47.627784, -122.215864),
        (47.614593, -122.185645),
        (47.667798, -122.123814),
        (47.677045, -122.205543),
        (47.704996, -122.212411),
        (47.562736, -122.219772),
        (47.742137, -122.225582)
    ]
    
    # Use a set to store unique places based on their formatted address
    unique_places = {}
    
    for lat, lng in tqdm(coordinates, desc="Searching locations"):
        tqdm.write(f"Searching near: {lat:.4f}, {lng:.4f}")
        places = get_coffee_shops(lat, lng)
        
        # Add places to unique_places dict using formatted address as key
        for place in places:
            addr = place.get('formattedAddress')
            if addr and addr not in unique_places:
                unique_places[addr] = place
    
    # Convert dict values back to list
    all_unique_places = list(unique_places.values())
    
    print(f"\nFound {len(all_unique_places)} unique Coffee Shops in all locations:")
    print("-" * 50)
    
    for i, place in enumerate(all_unique_places, 1):
        name = place.get('displayName', {}).get('text', 'N/A')
        address = place.get('formattedAddress', 'N/A')
        rating = place.get('rating', 'N/A')
        print(f"{i}. {name} ({address})")

    output_file = 'assets/coffee.json'
    with open(output_file, 'w') as f:
        json.dump(all_unique_places, f, indent=2)
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    get_all_locations()