# 📦 ScrapBridge ♻️

**ScrapBridge** is a full-stack web platform that connects households with certified scrap collectors. It simplifies the recycling process by allowing users to schedule pickups, classify scrap using AI, and track live scrap pricing.

🔗 [📽️ Platform Demo](https://drive.google.com/file/d/1bkjLHavZuKS4tNPbYORWf5RfANMBBmTS/view?usp=sharing)
</br>
[LIVE - Scrapbridge.vercel.app](https://scrapbridge.vercel.app/)

---

## 🌟 Features

- 🔐 Secure User & Collector Login System
- 🗓️ Schedule Scrap Pickup Requests
- 🤖 AI-powered Scrap Image Classification (CNN Model)
- 📍 Location-based Collector Assignment (Leaflet.js)
- 🔔 Real-time Notifications (via RapidAPI)
- 💸 Live Scrap Pricing & Secure Payments (Razorpay)
- 📦 Scrap Collector Dashboard for Order Management
- 🔄 Background Tasks via Celery + Redis
- 📬 Email Notifications (via Brevo)

---

## 🧠 Why ScrapBridge?

Managing household scrap can be confusing and inefficient. **ScrapBridge** aims to solve this by offering:
- Awareness about recyclable materials
- Simple and intuitive pickup scheduling
- A digital step toward sustainable waste management 🌱

---

## 🛠 Tech Stack

| Frontend | Backend | Machine Learning | Tools & APIs |
|----------|---------|------------------|--------------|
| React.js | Django (REST Framework) | TensorFlow/Keras (CNN) | Leaflet.js, Razorpay, RapidAPI, SQLite, Brevo, Cloudinary |

---

## 🚀 How to Run Locally

> ✨ **Prerequisite:** Install Python, Node.js, Redis, and Git

### 🔧 Backend (Django)

```bash
# 1. Clone the repo
git clone https://github.com/your-username/Scrapbridge-backend.git
cd Scrapbridge-backend

# 2. Create and activate a virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Start Redis (required for Celery)
redis-server

# 6. Start backend (with Celery worker)
bash ./start.sh
```
### 💻 Frontend (React)

``` bash
# 1. Clone the frontend
git clone https://github.com/your-username/Scrapbridge-frontend.git
cd Scrapbridge-frontend

# 2. Install dependencies
npm install

# 3. Run the development server
npm run dev
```

*Frontend will be available at http://localhost:5173/ and backend at http://localhost:8000/.*

**SCALING & OPTIMIZATION**
1. Added Indexes in databases using db_index and meta.indexes
2. Not using select_related (to avoid N+1 queries) because Using select_related will not save time — in fact, it may slow down the query due to the unnecessary JOIN, as we are accessing related data only once like abc.def (eg. organisation.user or owner.user) not in a loop.
3. Used celery and redis for mail and ML service to work in background, use flower to get information of all background tasks.
4. Used concept of lazy loading for the components that are used less.

**🤝 Contribution**
*Fork this repo, make your changes, and submit a pull request. Let’s build green tech together 🌏*
