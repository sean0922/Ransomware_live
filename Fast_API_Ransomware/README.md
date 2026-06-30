# Fast API Ransomware

FastAPI service for querying the `ransomware_live` PostgreSQL database.

This folder is separate from the ransomware data import script. Run the importer from the parent folder, and run this API from `Fast_API_Ransomware`.

## Setup

Create `.env` from the example:

```bash
cp .env.example .env
```

For the parent project's local Docker PostgreSQL, keep:

```env
POSTGRES_HOST=host.docker.internal
POSTGRES_PORT=5433
POSTGRES_DB=ransomware_live
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

For AWS RDS, use:

```env
POSTGRES_HOST=cc-db.cduoewasul1d.ap-southeast-1.rds.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_DB=ransomware_live
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_RDS_PASSWORD
```

## Run With Docker

```bash
docker compose up --build
```

API docs:

```text
http://localhost:7000/docs
```

Check which database the API is connected to:

```bash
curl "http://localhost:7000/db-info"
```

The response should include:

```json
{
  "database": "ransomware_live",
  "tables": ["cyberattacks", "victims"]
}
```

If `tables` is empty or missing `cyberattacks` / `victims`, update `.env` so the API points to the same PostgreSQL database used by the importer.

## Endpoints

### Search cyberattacks

```http
GET /cyberattacks
```

Query parameters:

* `event_date`: exact date, format `YYYY-MM-DD`
* `event_date_start`: start date, format `YYYY-MM-DD`
* `event_date_end`: end date, format `YYYY-MM-DD`
* `country`: country code, case-insensitive
* `ransomware_group`: partial match, case-insensitive
* `limit`: default `100`, max `1000`
* `offset`: default `0`

Example:

```bash
curl "http://localhost:7000/cyberattacks?event_date_start=2026-06-01&event_date_end=2026-06-30&country=US&ransomware_group=qilin"
```

### Search victims

```http
GET /victims
```

Query parameters:

* `attackdate`: exact date, format `YYYY-MM-DD`
* `attackdate_start`: start date, format `YYYY-MM-DD`
* `attackdate_end`: end date, format `YYYY-MM-DD`
* `country`: country code, case-insensitive
* `group_name`: partial match, case-insensitive
* `limit`: default `100`, max `1000`
* `offset`: default `0`

Example:

```bash
curl "http://localhost:7000/victims?attackdate_start=2026-06-01&attackdate_end=2026-06-30&country=US&group_name=qilin"
```
