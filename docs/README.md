# Stipend Discovery Platform

A Flask-based platform for discovering and managing stipends with tag-based filtering.

## Installation

1. Clone the repository
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```bash
   /run python scripts/db_init.py
   ```

## Usage

1. Start the application:
   ```bash
   python app.py
   ```
2. Access the admin dashboard at `/admin`
3. Use tag-based filtering to find relevant stipends
