# HimGaon Dairy — Pure Milk, Pure Pahad
## हिमगांव डेयरी — शुद्ध दूध, शुद्ध पहाड़

Complete Bilingual Dairy E-Commerce Website with Order Management

**Copyright © 2025 Sagar Kohli. All Rights Reserved.**

---

## 🎯 Features

### Customer Features:
- Bilingual interface (English/Hindi)
- Browse 7 dairy products
- Shopping cart with real-time updates
- Order placement with unique Order IDs
- **Track orders by Order ID + Phone Number**
- Real-time order status updates

### Admin Features:
- **Accept/Reject orders**
- Stock management (auto-restore on reject)
- Order history in SQL database
- Admin notes for customers
- Low stock alerts
- Bilingual product management

### Technical Features:
- **Persistent SQL Database** (data never erased)
- **Unique Order IDs**: HGD2025001, HGD2025002, etc.
- Indian Rupee (₹) pricing
- Mountain-themed design
- Responsive layout

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Locally
```bash
python app.py
```

### 3. Access
- **Website**: http://localhost:5000
- **Admin**: http://localhost:5000/admin/login
- **Track Order**: http://localhost:5000/track-order

## 🔐 Admin Login
- **Username**: admin
- **Password**: himgaon2025

---

## 📊 Order System

### Order ID Format:
- **HGD2025001**, **HGD2025002**, etc.
- HGD = HimGaon Dairy
- Auto-incremented

### Order States:
1. **Pending** - Awaiting admin review
2. **Accepted** - Admin approved
3. **Rejected** - Admin rejected (stock restored)
4. **Delivered** - Completed

### Customer Tracking:
1. Go to `/track-order`
2. Enter Order ID (e.g., HGD2025001)
3. Enter Phone Number
4. View status

---

## 🌐 Free Deployment on Render.com

```bash
# Push to GitHub
git init
git add .
git commit -m "HimGaon Dairy Website"
git remote add origin YOUR-GITHUB-URL
git push -u origin main

# Deploy on Render
# 1. Go to render.com
# 2. New Web Service from GitHub
# 3. Deploy!
```

Your site: `https://himgaon-dairy.onrender.com`

---

## 📦 Pre-loaded Products

| Product (English) | Product (Hindi) | Price (₹) |
|-------------------|-----------------|-----------|
| Fresh Cow Milk | ताजा गाय का दूध | 60 |
| Buffalo Milk | भैंस का दूध | 70 |
| Buttermilk | छाछ | 30 |
| Fresh Dahi | ताजा दही | 50 |
| Pure Desi Ghee | शुद्ध देसी घी | 650 |
| Mountain Butter | पहाड़ी मक्खन | 200 |
| Free Range Eggs | देसी अंडे | 80 |

---

## 🎨 Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite/PostgreSQL
- **Frontend**: Bootstrap 5, HTML, CSS, JS
- **Fonts**: Poppins + Noto Sans Devanagari

---

## 📂 Project Structure

```
himgaon-dairy/
├── app.py
├── requirements.txt
├── render.yaml
├── README.md
└── templates/
    ├── base.html
    ├── index.html
    ├── cart.html
    ├── checkout.html
    ├── confirmation.html
    ├── track_order.html
    └── admin/
        ├── login.html
        ├── dashboard.html
        ├── products.html
        ├── add_product.html
        ├── edit_product.html
        ├── orders.html
        └── order_detail.html
```

---

## 🔒 Security

**For Production:**
1. Change SECRET_KEY
2. Update admin password
3. Use environment variables
4. Enable HTTPS (automatic on Render)

---

## 📝 License

**Copyright © 2025 Sagar Kohli. All Rights Reserved.**

HimGaon Dairy — Pure Milk, Pure Pahad
हिमगांव डेयरी — शुद्ध दूध, शुद्ध पहाड़

Built with ❤️ for the mountains of Uttarakhand
