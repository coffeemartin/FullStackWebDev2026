# FullStackWebDev2026 – Group Project

**Team Members**  
- Ananya Moolampally (25080771)  
- Faiz Qazi (25040556)  
- Franco Meng (23370209)  
- Swathy Shenoy (25068786)  

---


## 1. Application Proposal

For our group project, we propose to build a **fitness and nutrition tracking website** that provides useful exercise and diet information, while allowing users to create a personal profile and track their progress.

The system will allow users to:

- Create an account and store personal details  
- Log exercise / gym sessions  
- Log food / nutrition intake  
- View educational content about exercise and nutrition  
- Receive personalised training and nutrition recommendations  

For the recommendations we plan to use modern AI techniques including:

- LLM API calls  
- Prompt engineering  
- Retrieval-Augmented Generation (RAG)  
- Vector database for storing user history  
- Dynamic recommendation generation based on user data  

The goal is to generate **personalised training plans and nutrition suggestions** based on the user's profile and activity history.

---

## 2. User Stories

We will create **at least 10 user stories** describing how users interact with the system, including:

As a user:
- I want to calculate my BMI so that I can better manage my diet and exercise plan.
- I want to track my exercise activities so that I can monitor my progress and achieve my fitness goals.
- I want to track my nutrition and food habits so that I can maintain a balanced and healthy diet.
- I want to understand whether my diet is appropriate for my age so that I can assess my overall health.
- I want to log the food I consume with details (meal type, name, quantity, calories) so that I can accurately track my daily intake.
- I want access to exercise recommendations without needing a personal trainer so that I can save money while staying fit.
- I want to categorize my meals (e.g., breakfast, lunch, dinner) so that my food intake is well organized.
- I want to calculate my calorie intake based on the quantity of food (in grams) so that I can monitor my energy consumption accurately.
- I want to save all my food entries at once so that I can maintain a complete record of my daily diet.
- I want to add multiple food entries in one session so that I can log an entire meal efficiently.
- I want validation for empty or incorrect inputs so that I do not save incomplete or invalid data.
- I want to manually enter food names so that I can log any type of food I consume.
- I want to recieve some customised recommendation based on my current exercise and diet.
As a system administrator:
- I want to manage the profile for each user so that the system works efficiently.
  

---

## 3. Main Pages of the Website

### 🏠 Main Page — *@faizqazi*
- Brief description of the website purpose
- Sign up / log in functionality
- Collect initial personal information:
  - Age
  - Gender
  - Height
  - Weight
  - Occupation
  - Current exercise level
- Calculate BMI
- Generate initial training plan

---

### 🏋️ Exercise Page — *@Swathymahesh*

Two main sections:

1. **Exercise Information**
   - Text / images / videos explaining exercises
   - Help users understand recommended workouts

2. **Exercise Log**
   - Record completed exercises
   - Frequency / duration
   - Difficulty feedback
   - Motivation / comments

---

### 🍎 Nutrition Page — *@AnanyaBhavani*

Two main sections:

1. **Nutrition Information**
   - Text / images / videos about food and diet
   - Help users manage nutrition

2. **Food Log**
   - Record food intake
   - Frequency / quantity
   - User feedback / comments

---

### 🤖 LLM Summary / Recommendation Page — *@coffeemartin*

This page will use:

- Prompt engineering
- Vector database
- RAG (Retrieval-Augmented Generation)
- LLM API

The system will send user data to the LLM and return structured feedback, such as:

- Training plan for next week / next 4 weeks
- Nutrition recommendations
- Motivation tips
- Progress feedback

---

## 4. CSS Framework

Proposed framework:

- Bootstrap (to be confirmed)

---

## 5. Initial HTML / CSS Pages 

(Optional but Recommended especially for groups whose meeting is in the later weeks) Start creating some of your pages with HTML and CSS. The page does not need to be interactive (e.g. no need for buttons to work) but it should be sufficient 

# Flask Server Local Setup Guide

This guide explains how to set up and run the Flask backend for this project on a local machine. It is written for new contributors who have just cloned the repository.

## 1. Prerequisites

Install these before running the Flask server:

- **Git**: used to clone and update the repository.
- **Python 3.11 or newer**: used to run the Flask backend.
- **pip**: Python package installer. It is usually included with Python.
- **Terminal access**:
  - Windows: PowerShell or Command Prompt.
  - macOS/Linux: Terminal.
- **Code editor**: Visual Studio Code is recommended, but any editor is fine.

Check that Python and pip are installed:

```powershell
python --version
pip --version
```

If `python` does not work on Windows, try:

```powershell
py --version
py -m pip --version
```

## 2. Clone the Repository

If you have not cloned the project yet:

```powershell
git clone https://github.com/coffeemartin/FullStackWebDev2026.git
cd FullStackWebDev2026
```

If you already have the repository, move into the project folder:

```powershell
cd "FullStackWebDev2026"
```

## 3. Go to the Backend Folder

The Flask server is inside `webapp/backend`.

```powershell
cd webapp\backend
```

From this folder, you should see files such as:

- `run.py`
- `requirements.txt`
- `config.py`
- `app.db`
- `app/`
- `migrations/`

## 4. Create a Virtual Environment

A virtual environment keeps this project's Python packages separate from packages used by other projects.

### Windows

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\activate
```

If `python` does not work, use:

```powershell
py -m venv venv
.\venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

After activation, the terminal prompt usually starts with `(venv)`.

## 5. Install Required Python Packages

Install all backend dependencies from `requirements.txt`:

```powershell
pip install -r requirements.txt
```

The required packages include Flask and project extensions such as:

- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-WTF
- python-dotenv
- SQLAlchemy
- WTForms

## 6. Environment Variables

The app loads environment variables from a `.env` file if one exists.

Create a `.env` file inside `webapp/backend`:

```text
SECRET_KEY=change-this-local-dev-secret
```

This project already has fallback development values in `config.py`, so the server can still run without a `.env` file. However, creating one is recommended for a clearer local setup.

Optional database setting:

```text
DATABASE_URL=sqlite:///app.db
```

If `DATABASE_URL` is not set, the app uses the local SQLite database at:

```text
webapp/backend/app.db
```

Do not commit `.env` files to Git. They are already ignored by `.gitignore`.

## 7. Database Setup

The repository currently includes a local SQLite database file:

```text
webapp/backend/app.db
```

If `app.db` exists, you can usually run the server immediately.

If you need to create or update the database from migrations, run:

```powershell
flask db upgrade
```

If Flask cannot find the app, set the Flask app first:

```powershell
$env:FLASK_APP = "run.py"
flask db upgrade
```

For macOS/Linux:

```bash
export FLASK_APP=run.py
flask db upgrade
```

Optional seed data can be loaded with:

```powershell
python seed.py
```

Use seed data carefully because it adds sample records to the database.

## 8. Run the Flask Server

From the `webapp/backend` folder, run:

```powershell
python run.py
```

You should see output showing that the Flask development server is running.

Open this URL in your browser:

```text
http://127.0.0.1:5000
```

You can also use:

```text
http://localhost:5000
```

## 9. Access from Another Device on the Same Network

By default, `run.py` uses:

```python
app.run(debug=True)
```

That normally binds the server to `127.0.0.1`, which only works from the same computer.

To allow another device on the same Wi-Fi network to access the server, update `webapp/backend/run.py` temporarily:

```python
from app import app

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
```

Then find your local IP address.

Windows:

```powershell
ipconfig
```

Look for the IPv4 address under your Wi-Fi or Ethernet adapter.

Then another device on the same network can open:

```text
http://YOUR_LOCAL_IP:5000
```

Example:

```text
http://192.168.1.56:5000
```

If it does not load, check Windows Firewall and make sure both devices are on the same network.

## 10. Stop the Server

In the terminal where Flask is running, press:

```text
Ctrl + C
```

## 11. Common Problems

### `ModuleNotFoundError`

Install the requirements again:

```powershell
pip install -r requirements.txt
```

Make sure your virtual environment is activated before installing packages.

### `flask` command is not recognized

Use Python directly:

```powershell
python run.py
```

Or check that the virtual environment is activated and dependencies are installed.

### Database errors

Run migrations:

```powershell
flask db upgrade
```

If Flask cannot find the app:

```powershell
$env:FLASK_APP = "run.py"
flask db upgrade
```

### Port 5000 is already in use

Another app is already using port 5000. Either stop that app or run Flask on another port by editing `run.py`:

```python
app.run(port=5001, debug=True)
```

Then open:

```text
http://127.0.0.1:5001
```

### PowerShell blocks virtual environment activation

If PowerShell blocks `.\venv\Scripts\activate`, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Close and reopen PowerShell, then activate the virtual environment again.

## 12. Quick Start Summary

For Windows:

```powershell
cd webapp\backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Open:

```text
http://127.0.0.1:5000
```
