# Ransomware.live PostgreSQL Export

This project downloads the latest 3 years of **Victims** and **Cyberattack/Press events** data from the Ransomware.live PRO API and saves the results into PostgreSQL.

Date-range CSV exports and manual year input have been removed.

## Environment

Create or update `.env`:

```env
MY_API_KEY=YOUR_API_KEY_HERE
```

## Run With Docker

Start PostgreSQL and run the importer:

```bash
docker compose run --rm -it app
```

The importer automatically fetches the current year and the previous 2 years. For example, when run in 2026, it fetches 2024 through 2026.

## Tables

The app creates the configured database automatically when using `POSTGRES_*` settings. By default, data is stored under the `ransomware_live` database.

Inside that database, the app creates these tables automatically:

* `victims`
* `cyberattacks`

Rows are upserted, so re-running the same year updates existing records instead of creating duplicates.

## Database Defaults

Docker Compose starts PostgreSQL with:

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ransomware_live
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

To use another PostgreSQL server, override the `POSTGRES_*` variables. When `POSTGRES_DB=ransomware_live`, the app first connects to `POSTGRES_MAINTENANCE_DB` (`postgres` by default), creates the `ransomware_live` database if needed, then creates the two tables inside it.

`DATABASE_URL` is also supported, but it must point to an existing database because a URL already includes the target database name.

Example for AWS RDS:

```env
POSTGRES_HOST=cc-db.cduoewasul1d.ap-southeast-1.rds.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_DB=ransomware_live
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_RDS_PASSWORD
```
