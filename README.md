# Blogging API with Admin Panel

A full-featured RESTful Blogging API with a Jinja2-rendered Admin Panel built using **FastAPI**, **MongoDB Atlas (Motor)**, and **JWT Authentication**.

## Features
- **Blog CRUD API:** Create, Read, Update, and Delete blog posts.
- **Categories Management:** Create, list, and delete blog categories.
- **Search & Filter:** Search blogs by title, tag, or category.
- **Authentication:** User registration and login with hashed passwords (bcrypt) and JWT tokens (Bearer header & HTTP-only cookie support for Admin Panel).
- **Admin Panel (Jinja2):** Clean web dashboard to log in, create posts, manage categories, and delete blogs.
- **Auto Docs:** Interactive Swagger UI at `/docs` and ReDoc at `/redoc`.

## Quick Start
1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your MongoDB Atlas URI.
4. Run the development server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
5. Open:
   - **Admin Panel:** `http://127.0.0.1:8000/admin/login`
   - **Swagger API Docs:** `http://127.0.0.1:8000/docs`
