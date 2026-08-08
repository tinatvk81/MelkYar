#!/bin/sh
set -e

echo "در انتظار آماده‌شدن دیتابیس..."
python - <<'PYEOF'
import os, time, sys
import psycopg2

if os.environ.get("DB_ENGINE") == "postgresql":
    for i in range(30):
        try:
            psycopg2.connect(
                dbname=os.environ["DB_NAME"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                host=os.environ.get("DB_HOST", "db"),
                port=os.environ.get("DB_PORT", "5432"),
            ).close()
            print("دیتابیس آماده است.")
            break
        except Exception:
            print("دیتابیس هنوز آماده نیست، تلاش مجدد...")
            time.sleep(2)
    else:
        print("دیتابیس بعد از چند تلاش در دسترس نبود.")
        sys.exit(1)
PYEOF

echo "اجرای migrate..."
python manage.py migrate --noinput

echo "جمع‌آوری فایل‌های استاتیک..."
python manage.py collectstatic --noinput

echo "اجرای gunicorn..."
exec gunicorn melkyar.wsgi:application --bind 0.0.0.0:8000 --workers 3
