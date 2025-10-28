# 📝 Todo FastAPI App

A modern **Todo application** built with **FastAPI**, **PostgreSQL**, and **Docker**.  
Designed for personal and group task management with a simple, scalable backend and a clean frontend.

---

## 🚀 Features

- **User Management**
  - Register and login users (hashed passwords with bcrypt)
- **Group Tasks**
  - Create groups and assign tasks to multiple users
  - Only group members can see group tasks
- **Personal Tasks**
  - Each user can manage individual tasks
- **Permissions**
  - Users can modify tasks they created or are assigned to
  - Group admins can manage members and group names
- **Database**
  - PostgreSQL (Dockerized)
  - Alembic for migrations
- **Modern Frontend**
  - FastAPI templates with **Jinja2**
  - Styled using **Bootstrap 5**
  - Responsive and mobile-friendly design
- **Dockerized Development**
  - Run Postgres and app in isolated containers
  - Easy setup and reproducibility

---

## 📦 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend   | FastAPI |
| Database  | PostgreSQL |
| ORM       | SQLAlchemy |
| Migrations| Alembic |
| Auth      | Passlib bcrypt |
| Frontend  | Jinja2 + Bootstrap 5 |
| Containers| Docker + Docker Compose |

---

## ⚡ Installation

```bash
# 1. Clone the repository
git clone https://github.com/<username>/todo-fastapi.git
cd todo-fastapi

# 2. Create virtual environment and activate it
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start PostgreSQL container
docker compose up -d

# 5. Run database migrations
alembic upgrade head

# 6. Start FastAPI app
uvicorn app.main:app --reload
```

---

## 🌐 Usage

- Open your browser at `http://127.0.0.1:8000`

**API Endpoints**:

| Endpoint | Description |
|----------|-------------|
| `/users` | User management |
| `/groups`| Group management |
| `/tasks` | Task management |

**Frontend**:

- Homepage displays project overview and instructions
- Responsive and modern layout with Bootstrap 5
- Favicon included

---

## 🗂️ Project Structure

```
todo-fastapi/
├─ app/
│  ├─ core/           # Database, settings, utils
│  ├─ models/         # SQLAlchemy models
│  ├─ schemas/        # Pydantic schemas
│  ├─ routes/         # API route modules
│  ├─ templates/      # Jinja2 HTML templates
│  └─ static/         # CSS, JS, favicon
├─ alembic/           # Alembic migrations
├─ docker-compose.yml # Docker setup
├─ requirements.txt   # Python dependencies
├─ README.md          # Project overview
└─ .env               # Environment variables
```

---

## 🛠️ Contributing

```bash
# 1. Create a feature branch
git checkout -b feature_branch

# 2. Commit your changes
git add .
git commit -m "Describe your feature"

# 3. Push branch and create a pull request
git push -u origin feature_branch
```

- PRs should be reviewed before merging into `development`  
- Keep `development` branch stable

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 💡 Notes

- Make sure Docker and Docker Compose are installed  
- Virtual environment is recommended for local development  
- Alembic ensures your database schema is always versioned  
- Frontend is ready for expansion with dynamic task lists in the future
