# 📝 Full Stack Blog Web Application

A full-stack blog web application built using **Django**, **Django REST Framework**, and **JavaScript**.  
This project allows users to create, manage, and interact with blog posts through a clean and responsive interface.

---

## 🚀 Features

- 🔐 User Authentication (Signup/Login/Logout)
- ✍️ Create, Edit, Delete Blog Posts
- 📄 View All Blogs / Single Blog Detail
- 🔎 REST API for backend operations
- 📱 Responsive UI using HTML, CSS, JavaScript
- ⚡ Fast and scalable backend with Django

---

## 🛠️ Tech Stack

**Frontend:**
- HTML
- CSS
- JavaScript

**Backend:**
- Django
- Django REST Framework

**Database:**
- SQL

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
#Create virtual environment
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)
Install dependencies
pip install -r requirements.txt
4️⃣ Run migrations
python manage.py migrate
5️⃣ Run server
python manage.py runserver

👉 Open in browser:
http://127.0.0.1:8000/

🔗 API Endpoints (Sample)
GET /api/blogs/ → Get all blogs
POST /api/blogs/ → Create blog
PUT /api/blogs/{id}/ → Update blog
DELETE /api/blogs/{id}/ → Delete blog
