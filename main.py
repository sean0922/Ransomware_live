from datetime import datetime

from cyberattack_event import export_cyberattacks
from database import init_db
from victims import export_victims


def get_recent_years(year_count=3):
    current_year = datetime.now().year
    start_year = current_year - year_count + 1
    return range(start_year, current_year + 1)


if __name__ == "__main__":
    init_db()

    years = list(get_recent_years())
    print(f"Fetching data for the last {len(years)} years: {years[0]}-{years[-1]}")

    for year in years:
        print(f"Fetching data for {year}...")
        export_victims(year)
        export_cyberattacks(year)
