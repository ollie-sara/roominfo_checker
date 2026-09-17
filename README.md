# Sick Room Finder

Room occupancy checker and visual timetable for centrally administered lecture halls and seminar rooms across ETH Zurich.

Website: [rooms.saravanja.ch](https://rooms.saravanja.ch)

## Overview

Sick Room Finder scrapes room occupancy schedules directly from the central ETH website, processes them into 15-minute availability blocks (Monday–Friday, 08:00–20:00 for the current and following week), and displays them on an interactive timetable.

Only centrally administered teaching rooms (Rektorat) are included; department-administered rooms are omitted.

## Architecture

- **Data Scraper** (`checker_script/main.py`): Scrapes room data and schedules directly from the ETH Zurich website, generates availability matrices, and writes the output to `docs/data/data.json`.
- **Frontend** (`docs/`): Jekyll site with jQuery, jQuery UI slider, and DataTables hosted on GitHub Pages.
- **Automation** (`.github/workflows/update-data.yml`): GitHub Actions workflow scheduled twice daily to refresh data and redeploy the site.

## Local Setup

### Scraper

```bash
poetry install
poetry run python checker_script/main.py
```

Alternatively, using pip:

```bash
pip install -r checker_script/requirements.txt requests
python checker_script/main.py
```

### Website

```bash
cd docs
bundle install
bundle exec jekyll serve
```

## License

[MIT](LICENSE)