# --- مرحله‌ی build: نصب پکیج‌ها -------------------------------------------
FROM python:3.12-slim AS base

# جلوگیری از ساخت فایل .pyc و بافر نشدن لاگ‌ها (تا لاگ فوری دیده شود)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# وابستگی‌های سیستمی لازم برای psycopg2 و Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# کاربر غیر-روت برای اجرا (نکته‌ی امنیتی: کانتینر هرگز نباید با root اجرا شود)
RUN useradd -m melkyar && chown -R melkyar:melkyar /app
USER melkyar

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
