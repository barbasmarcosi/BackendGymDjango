#!/usr/bin/env bash
set -euo pipefail

python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
