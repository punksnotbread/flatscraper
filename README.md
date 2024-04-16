# Flatscraper

Quick scrapy project for scraping various Lithuanian apartment listings.

# Setup
```commandline
docker compose up -d mongo
```

```commandline
poetry install
```

# Running
```
poetry run python -m scrapy crawl domoplius &
poetry run python -m scrapy crawl aruodas &
poetry run python -m scrapy crawl skelbiu &
```

## TODO
* [ ] Fix docker-compose builds & running.
* [ ] GitHub actions for linting.