import requests
import logging
import time
import csv
from dotenv import load_dotenv
import os
load_dotenv()
#Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")

endpoint = "https://atlas.microsoft.com/search/fuzzy/json"


tunisian_cities = [
    {"name": "Tunis", "lat": 36.8065, "lon": 10.1815},
    {"name": "Sfax", "lat": 34.7406, "lon": 10.7603},
    {"name": "Sousse", "lat": 35.8256, "lon": 10.6084},
    {"name": "Kairouan", "lat": 35.6781, "lon": 10.0963},
    {"name": "Bizerte", "lat": 37.2744, "lon": 9.8739},
    {"name": "Gabès", "lat": 33.8815, "lon": 10.0982},
    {"name": "Ariana", "lat": 36.8663, "lon": 10.1934},
    {"name": "Gafsa", "lat": 34.4250, "lon": 8.7842},
    {"name": "Monastir", "lat": 35.7770, "lon": 10.8261},
    {"name": "Ben Arous", "lat": 36.7530, "lon": 10.2189},
    {"name": "Nabeul", "lat": 36.4500, "lon": 10.7380},
    {"name": "Kasserine", "lat": 35.1667, "lon": 8.8333},
    {"name": "Zaghouan", "lat": 36.4000, "lon": 10.1000},
    {"name": "Siliana", "lat": 36.0833, "lon": 9.4000},
    {"name": "Jendouba", "lat": 36.5000, "lon": 8.7500},
    {"name": "Le Kef", "lat": 36.1700, "lon": 8.7100},
    {"name": "Medenine", "lat": 33.3500, "lon": 10.5000},
    {"name": "Tozeur", "lat": 33.9167, "lon": 8.1333},
    {"name": "Tataouine", "lat": 33.0000, "lon": 10.4500}
]

def search_atms_in_city(city, limit=100):
    """Search for ATMs in a given city using Azure Maps Search Fuzzy API."""
    params = {
        "api-version": "1.0",
        "subscription-key": subscription_key,
        "query": "BAnque Zitouna ATM",
        "lat": city["lat"],
        "lon": city["lon"],
        "radius": 100000, 
        "limit": limit,
        "countrySet": "TN"  # Restrict to Tunisia
    }
    
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        logging.info(f"Response for {city['name']}: {len(data.get('results', []))} results")
        return data
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP Error for {city['name']}: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error searching ATMs in {city['name']}: {e}")
        return None

def extract_atm_locations(response, city_name):
    """Extract ATM locations from the API response."""
    locations = []
    if not response or 'results' not in response:
        logging.warning(f"No results found for {city_name}")
        return locations

    for result in response['results']:
        try:
            poi_name = result.get('poi', {}).get('name', 'Unknown ATM')
            coordinates = result.get('position', {})
            lat = coordinates.get('lat')
            lon = coordinates.get('lon')
            address = result.get('address', {}).get('freeformAddress', 'No address')
            
            if lat is not None and lon is not None:
                locations.append({
                    'name': poi_name or 'Unknown ATM',
                    'address': address or 'No address',
                    'latitude': lat,
                    'longitude': lon,
                    'city': city_name
                })
        except (KeyError, TypeError) as e:
            logging.warning(f"Error extracting ATM data in {city_name}: {e}")
            continue
    return locations

def save_to_csv(locations, filename="tunisia_atm_locations.csv"):
    """Save ATM locations to a CSV file."""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'address', 'latitude', 'longitude', 'city']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for location in locations:
                writer.writerow(location)
        logging.info(f"Saved {len(locations)} locations to {filename}")
    except Exception as e:
        logging.error(f"Error saving to CSV: {e}")

def main():
    target_count = 193
    all_locations = []
    seen_coordinates = set()  #Track unique coordinates

    for city in tunisian_cities:
        if len(all_locations) >= target_count:
            logging.info("Reached target of 193 unique ATMs")
            break

        #Calculate how many more ATMs are needed
        remaining = target_count - len(all_locations)
        logging.info(f"Searching for ATMs in {city['name']} (need {remaining} more)")
        
        #limit API request to remaining needed ATMs 
        response = search_atms_in_city(city, limit=min(remaining, 100))
        if response:
            locations = extract_atm_locations(response, city['name'])
            for loc in locations:
                coord = (loc['latitude'], loc['longitude'])
                if coord not in seen_coordinates and len(all_locations) < target_count:
                    seen_coordinates.add(coord)
                    all_locations.append(loc)
                    logging.info(f"Added: {loc['name']} at ({loc['latitude']}, {loc['longitude']})")
        
        time.sleep(1)  #aavoid rate limits

    if all_locations:
        save_to_csv(all_locations)
        logging.info(f"Collected {len(all_locations)} unique ATM locations")
    else:
        logging.warning("No ATM locations were found")

if __name__ == "__main__":
    main()