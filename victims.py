import os

from dotenv import load_dotenv

from api_client import get_json
from country_full_name import country_code_to_name
from database import empty_to_none, parse_date, upsert_victims

load_dotenv()


def json_to_rows(data, year):
    results = data.get('victims', [])
    rows = []

    for item in results:
        victim_id = item.get('id')
        if victim_id is None:
            continue

        country = empty_to_none(item.get('country'))
        rows.append((
            str(victim_id),
            parse_date(item.get('discovered')),
            parse_date(item.get('attackdate')),
            empty_to_none(item.get('victim')),
            empty_to_none(item.get('group')),
            empty_to_none(item.get('description')),
            empty_to_none(item.get('post_url')),
            country,
            country_code_to_name(country),
            empty_to_none(item.get('activity')),
            empty_to_none(item.get('screenshot')),
            int(year),
        ))

    return rows

def fetch_victims_and_save(api_key, year):
    url = f"https://api-pro.ransomware.live/victims/?year={year}"
    headers = {
        'accept': 'application/json',
        'X-API-KEY': api_key
    }

    try:
        data = get_json(url, headers=headers)
        row_count = upsert_victims(json_to_rows(data, year))
        print(f"✅ Victims {year}: upserted {row_count} rows into PostgreSQL")

    except Exception as e:
        print(f"❌ Error: {e}")

def export_victims(year):
    MY_API_KEY = os.getenv("MY_API_KEY") 

    fetch_victims_and_save(MY_API_KEY, year)
