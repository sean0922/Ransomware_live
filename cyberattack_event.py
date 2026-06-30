import os
import hashlib

from dotenv import load_dotenv

from api_client import get_json
from country_full_name import country_code_to_name
from database import empty_to_none, parse_date, upsert_cyberattacks

load_dotenv()


def build_source_key(row):
    if row.get('url'):
        return row['url']

    raw_key = "|".join(str(row.get(field) or "") for field in ("date", "victim", "title"))
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def json_to_rows(data, year):
    results = data.get('results', [])
    rows = []

    for item in results:
        row = {
            'date': item.get('date'),
            'victim': empty_to_none(item.get('victim')),
            'domain': empty_to_none(item.get('domain')),
            'country': empty_to_none(item.get('country')),
            'summary': empty_to_none(item.get('summary')),
            'title': empty_to_none(item.get('title')),
            'url': empty_to_none(item.get('url')),
        }

        ransom_info = item.get('ransomware')
        if ransom_info and isinstance(ransom_info, dict):
            ransomware_group = empty_to_none(ransom_info.get('group'))
        else:
            ransomware_group = None

        rows.append((
            build_source_key(row),
            parse_date(row['date']),
            row['victim'],
            row['domain'],
            row['country'],
            country_code_to_name(row['country']),
            row['summary'],
            row['title'],
            row['url'],
            ransomware_group,
            int(year),
        ))

    return rows

def fetch_cyberattacks_and_save(api_key, params, year):
    url = "https://api-pro.ransomware.live/press/all"
    headers = {
        'accept': 'application/json',
        'X-API-KEY': api_key
    }

    try:
        data = get_json(url, headers=headers, params=params)
        row_count = upsert_cyberattacks(json_to_rows(data, year))
        print(f"✅ Cyberattacks {year}: upserted {row_count} rows into PostgreSQL")

    except Exception as e:
        print(f"❌ Error: {e}")

def export_cyberattacks(year):
    MY_API_KEY = os.getenv("MY_API_KEY") 

    params = {}
    if year:
        params['year'] = year

    fetch_cyberattacks_and_save(MY_API_KEY, params, year)
