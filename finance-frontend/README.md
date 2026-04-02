# FinanceOS — Frontend

React + Tailwind CSS frontend for the Finance Dashboard Backend.

## Stack

- **React 18** with React Router v6
- **Tailwind CSS** for utility styling
- **Recharts** for charts (Area, Bar, Pie)
- **DM Sans + Syne** (Google Fonts) for typography

## Pages

| Route | Access | Description |
|---|---|---|
| `/login` | Public | JWT login form |
| `/dashboard` | All roles | Summary cards, trend chart, category breakdowns, recent transactions |
| `/transactions` | All roles | Table with filters, search, pagination. Admin can add/edit/delete |
| `/users` | Admin only | User list with role/status management |

## Project Structure

```
src/
├── components/
│   ├── ui/index.jsx        # Button, Input, Select, Badge, Modal, Card, Spinner…
│   └── layout/
│       ├── Sidebar.jsx     # Fixed sidebar with role-aware nav
│       └── AppLayout.jsx   # Shell wrapping sidebar + page content
├── context/
│   └── AuthContext.jsx     # Global auth state (JWT, user, login, logout)
├── pages/
│   ├── LoginPage.jsx
│   ├── DashboardPage.jsx
│   ├── TransactionsPage.jsx
│   └── UsersPage.jsx
├── services/
│   └── api.js              # All fetch calls to the FastAPI backend
├── App.jsx                 # Router + protected routes
└── index.css               # Tailwind + CSS variables + global styles
```

## Setup

### 1. Install dependencies

```bash
cd finance-frontend
npm install
```

### 2. Start the dev server

Make sure the **backend is running on port 8000** first (the `proxy` field in `package.json` forwards `/api` calls to it automatically).

```bash
npm start
```

App opens at **http://localhost:3000**

### 3. Login

Default admin credentials (auto-seeded by the backend):
- Username: `admin`
- Password: `Admin@123`

## Role Behaviour in UI

| Feature | Viewer | Analyst | Admin |
|---|---|---|---|
| View Dashboard | ✅ | ✅ | ✅ |
| View Transactions | ✅ | ✅ | ✅ |
| Add/Edit/Delete Transactions | ❌ | ❌ | ✅ |
| View Users page | ❌ | ❌ | ✅ |
| Edit user roles/status | ❌ | ❌ | ✅ |

## Production Build

```bash
npm run build
```

The `build/` folder can be served as static files, or you can serve it directly from FastAPI:

```python
# In app/main.py — add after routes:
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")
```

Then copy `finance-frontend/build/` to `finance-backend/frontend/build/`.
