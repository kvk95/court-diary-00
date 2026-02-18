# court-diary

## A Retail Shop POS

### Retail Shop POS – VS Code Setup

This guide explains how to set up and run the **court-diary** fullstack Retail POS project using **VS Code**, **Poetry**, and the provided workspace configuration.

---

## 🚀 Quick Start (TL;DR)

For new developers who want to get running fast:

1. Install prerequisites:
   - **VS Code**
   - **Node.js (LTS)**
   - **Python 3.10+**
   - **Poetry**

2. Open the workspace:
   ```
   # File → Open Workspace from File… → court-diary.code-workspace
   ```

3. Backend setup:
   ```text
   Ctrl + Shift + `
   → select backend1
   → run:
   ```
   ```bash
   poetry install
   ```

4. Frontend setup:
   ```text
   Ctrl + Shift + `
   → select frontend
   → run:
   ```
   ```bash
   npm install
   ```

5. Run everything:
   ```
   Ctrl + Shift + B → Run Fullstack
   ```

✅ Frontend + backend start together  
✅ Logs visible in VS Code terminals

---

## Workspace Overview

This project uses a **multi-root VS Code workspace**:

```json
{
  "folders": [
    { "path": "frontend" },
    { "path": "backend1" }
  ]
}
```

VS Code will ask which folder a new terminal should use.  
Always select the folder you want to work in (**frontend** or **backend1**).

---

## Backend Environment Setup (Poetry)

### Correct Way (Recommended)

```text
Ctrl + Shift + `
→ select backend1
→ run:
```
```bash
poetry install
```

✔ The terminal is already inside `backend1`  
✔ No `cd backend1` needed  
✔ No `poetry shell` required

### ❌ What NOT to do

```bash
cd backend1
poetry shell
poetry install
```

> This is redundant and can cause interpreter mismatches in VS Code.

---

## Running the Application

### Using VS Code Tasks (Recommended)

```
Ctrl + Shift + B → Run Fullstack
```

This runs:
- Backend: `poetry run uvicorn app.main:app --reload`
- Frontend: `npm run dev`

Each service runs in its own terminal with live logs.

---

## Tasks vs Debug vs Manual Run

### VS Code Tasks (Preferred)

**Use when:**
- Daily development
- Fast startup
- Consistent team workflow

**Pros:**
- One-click startup
- Correct working directories
- No manual environment activation

**Cons:**
- No breakpoints

---

### Debug Mode

**Run → Start Debugging → Fullstack Dev**

**Use when:**
- Debugging API logic
- Investigating frontend issues

**Pros:**
- Breakpoints
- Variable inspection
- Stack traces

**Cons:**
- Slightly slower startup

---

### Manual Run (Last Resort)

Backend:
```bash
poetry run uvicorn app.main:app --reload
```

Frontend:
```bash
npm run dev
```

⚠️ Manual runs bypass workspace consistency.  
Use only for CI or deep troubleshooting.

---

## Windows vs macOS / Linux Notes

### Python & Poetry

**macOS / Linux**
```bash
python3 --version
poetry install
```

**Windows**
- Install Python from python.org
- Enable **Add Python to PATH**
- Poetry uses `.venv\Scripts\python.exe`

If interpreter is not detected:
```
Python: Select Interpreter → .venv
```

---

### Node & npm

- Install **Node.js LTS**
- Restart VS Code after installation

---

### Path Differences

| Item | macOS/Linux | Windows |
|---|---|---|
| Python venv | `.venv/bin/python` | `.venv\Scripts\python.exe` |
| Shell | bash / zsh | PowerShell |
| Line endings | LF | CRLF |

---

## Troubleshooting

### Poetry

- `poetry: command not found`  
  → Install Poetry and restart terminal

- Wrong Python version  
  → `poetry env use python`

---

### ESLint

- Run `npm install` inside `frontend`
- Ensure ESLint extension is enabled

---

### Port Conflicts

Defaults:
- Backend: **8000**
- Frontend: **5173**

Check ports:
```bash
lsof -i :8000
lsof -i :5173
```

---

### Node Issues

- `npm not recognized`  
  → Reinstall Node.js and restart VS Code

---

## Notes

- Do **not** use `poetry shell`
- Prefer VS Code Tasks
- Manual runs are last resort

---

Happy coding 🚀
