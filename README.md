<div dir="rtl" lang="fa">

<div dir="rtl" lang="fa">

<style>
li {
  text-align: right;
  direction: rtl;
}
ul, ol {
  padding-right: 20px;
  padding-left: 0;
}
</style>

# IoT Lab - پلتفرم تحلیل استراتژیک ارزهای دیجیتال

سیستم IoT Lab یک پلتفرم کامل برای تحلیل استراتژیک و نظارت بر ارزهای دیجیتال است که شامل:
- Frontend (رابط کاربری با Nginx)
- Backend (Django REST API)  
- PostgreSQL (پایگاه داده)
- Redis (برای Celery)
- Celery Worker (پردازش وظایف)

## پیش‌نیازها

برای اجرای این پروژه نیاز به نصب موارد زیر دارید:

### نصب Docker و Docker Compose

#### نصب در Ubuntu/Debian:
برای نصب Docker و Docker Compose از لینک زیر استفاده کنید:
<br>
**[راهنمای نصب Docker - Ubuntu](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)**

#### مشکل تحریم و استفاده از میرور داخلی:
**⚠️ توجه مهم:** به دلیل مشکلات تحریم در دسترسی به Docker Registry جهانی، حتماً از میرور داخلی آروان استفاده کنید:
<br>
**[تنظیم میرور Docker آروان](https://www.arvancloud.ir/fa/dev/docker)**

## راه‌اندازی سریع

### 1. دریافت و اجرای پروژه

```bash
# کلون کردن پروژه (در صورت نیاز)
git clone https://github.com/amirrs82/IoT_Lab
cd IoT_Lab

# ساخت و راه‌اندازی تمام سرویس‌ها
docker compose up --build -d
```

### 2. دسترسی به سیستم

پس از راه‌اندازی موفق، سرویس‌های زیر در دسترس خواهند بود:

- **🌐 Original Website**: [http://localhost:10004](http://localhost:10004)

- **⚙️ Django Admin Panel**: [http://localhost:10003/admin/](http://localhost:10003/admin/)

- **🔗 Backend API**: [http://localhost:10003](http://localhost:10003)

### 3. ورود به پنل مدیریت

یک حساب کاربری مدیر و پایگاه داده ارزهای دیجیتال به صورت خودکار ایجاد می‌شوند:

- **Username**: `admin`
- **Password**: `admin`
- **Currencies**: More than 17 currencies like Bitcoin، Ethereum، Solana, etc.

## ویژگی‌های سیستم

### صفحات Frontend:
- **صفحه ورود**: `/pages/login.html`
- **صفحه ثبت‌نام**: `/pages/signup.html`
- **پروفایل کاربر**: `/pages/profile.html`
- **ارزهای دیجیتال**: `/pages/crypto.html`
- **جزئیات ارز دیجیتال**: `/pages/crypto_details.html`
- **اشتراک‌ها**: `/pages/subscriptions.html`

### ویژگی‌های تحلیل ارزهای دیجیتال:
- **پایگاه داده ارزهای محبوب**: بیش از 17 ارز دیجیتال محبوب از جمله Bitcoin، Ethereum، Solana و غیره
- **به‌روزرسانی خودکار قیمت‌ها**: سیستم Celery برای دریافت قیمت‌های به‌روز از CoinGecko
- **تحلیل تکنیکال**: ابزارهای تحلیل قیمت و روند بازار
- **مدیریت اشتراک**: امکان اشتراک در سیگنال‌های تحلیلی

## توسعه و تست

### مشاهده وضعیت سرویس‌ها:
```bash
docker compose ps
```

### مشاهده لاگ‌ها:
```bash
# تمام سرویس‌ها
docker compose logs

# سرویس خاص
docker compose logs backend
docker compose logs frontend
```

### ری‌استارت سرویس‌ها:
```bash
# ری‌استارت همه سرویس‌ها
docker compose restart

# ری‌استارت سرویس خاص
docker compose restart backend
```

### اجرای Migration ها:
```bash
docker compose exec backend python manage.py migrate
```

### ایجاد superuser دستی (اختیاری):
```bash
docker compose exec backend python manage.py createsuperuser
```

### کامندهای مدیریت ارزهای دیجیتال:
```bash
# اضافه کردن ارزهای محبوب به پایگاه داده
docker compose exec backend python manage.py add_popular_currencies

# به‌روزرسانی قیمت‌های ارزها
docker compose exec backend python manage.py update_prices
```

## متوقف کردن سیستم

```bash
# متوقف کردن سرویس‌ها
docker compose down

# متوقف کردن و حذف داده‌ها (شامل پایگاه داده)
docker compose down -v
```

## عیب‌یابی

### اگر کانتینرها شروع نمی‌شوند:
1. بررسی در دسترس بودن پورت‌های 10001-10004
2. اطمینان از نصب صحیح Docker و Docker Compose
3. بررسی لاگ‌ها: `docker compose logs [service-name]`

### اگر Frontend به Backend متصل نمی‌شود:
1. بررسی وضعیت backend: `docker compose ps`
2. بررسی لاگ‌های backend: `docker compose logs backend`
3. بررسی تنظیمات CORS

</div>
