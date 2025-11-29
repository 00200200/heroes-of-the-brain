# Heroes of the Brain

## Quick start

### Requiremeents

- [Docker](https://www.docker.com/get-started) i Docker Compose
- Or without DOCKER:
  - Python 3.11+
  - Node.js 18+

### Run with docker

1. **Clone repo**

   ```bash
   git clone https://github.com/00200200/heroes-of-the-brain
   cd heroes-of-the-brain
   ```

2. **Run app**

   ```bash
   docker-compose up --build
   ```

3. **Open in browser**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000
   - Documentation API: http://localhost:8000/docs

### Run without docker

#### Backend

```bash
cd backend
pip install uv
uv sync
uv run uvicorn src.main:app
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
heroes-of-the-brain/
├── backend/    #backend
├── frontend/   #frontend
└── docker-compose.yml
```

### Backend

```bash
cd backend
uv sync
uv run python src/main.py
```

### Frontend

```bash
cd frontend
npm run dev
```
