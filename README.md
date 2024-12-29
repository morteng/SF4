# Stipend Discovery Website

## Development Setup

### Prerequisites
- Python 3.8+
- pip

### Installation
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Verify critical dependencies:
   ```bash
   pip show freezegun pytest Flask
   ```

### Running Tests
```bash
pytest
```

### Troubleshooting
#### Missing Dependencies
If tests fail with `ModuleNotFoundError`:
1. Ensure the virtual environment is activated
2. Run `pip install -r requirements.txt`
3. Verify installation with `pip show <package_name>`

#### Freezegun Issues
If time-based tests are failing:
1. Ensure freezegun is installed:
   ```bash
   pip show freezegun
   ```
2. If not installed:
   ```bash
   pip install freezegun>=1.2.2
   ```

#### Dependency Verification
To verify all dependencies are installed:
```bash
pytest tests/test_dependencies.py
```
