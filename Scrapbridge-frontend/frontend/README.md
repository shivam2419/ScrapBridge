# ♻️ ScrapBridge

**ScrapBridge** is a smart waste management platform that connects users with local scrap collectors. The platform supports **automated scrap classification**, **real-time notifications**, and **request scheduling**, all while maintaining performance and scalability.

---

## 🚀 Features

- 🔐 **Secure Authentication** system for users and collectors (Login/Signup)
- 🧠 **CNN-based deep learning model** for automatic scrap classification
- 📦 **Scrap pickup request** flow between users and collectors
- 🔔 **Real-time notification system** to update users on pickup status
- 🌍 **Nearby Scrap Collector** search using geolocation
- 📊 **Admin dashboard** and tracking features
- ⚙️ **Celery + Redis integration** for background tasks (Mail/ML prediction)

---

## 🛠️ Tech Stack

- **Backend**: Django + Django REST Framework  
- **Frontend**: React (Responsive design)  
- **Database**: PostgreSQL / SQLite  
- **AI/ML**: CNN Model for scrap type prediction  
- **Async Tasks**: Celery + Redis  
- **File Hosting**: Cloudinary  

---

## 📦 Installation

Follow these steps to run the project locally:

1. **Clone the repository**  
   ```bash
   git clone https://github.com/shivam2419/Scrapbridge-backend.git
   ```

2. **Navigate to the project directory**  
   ```bash
   cd Scrapbridge-backend
   ```

3. **Create a virtual environment**

   - For Linux/macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

   - For Windows:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```

4. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

5. **Apply database migrations**  
   ```bash
   python manage.py migrate
   ```

6. **Start Redis server**  
   - For Windows (from Redis directory):  
     ```bash
     redis-server.exe
     ```

7. **Start the development server (Django + Celery)**  
   ```bash
   bash ./start.sh
   ```

8. **Open in browser**  
   Visit: [http://localhost:8000](http://localhost:8000)

---

## 📸 A Short Look at ScrapBridge
👉 [Try ScrapBridge Live](https://scrapbridge.vercel.app)

> 🔎 *Want more? Clone the repo and explore the full experience!*

---

## 📈 Optimization & Performance

1. 🧩 **Lazy Loading**  
   Used concept of lazy loading for the components that are used less.
---

## 📬 Contributions

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
