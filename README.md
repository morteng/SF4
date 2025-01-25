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
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.0+-blue.svg)](https://flask.palletsprojects.com/)

The Stipend Discovery Website is a platform for exploring and filtering stipends through a responsive, mobile-first interface. Built using Flask with HTMX for real-time interactivity, it includes a secure admin interface and automated bots for data management.

## Features

- Real-time stipend discovery with tag-based filtering
- Secure admin interface for managing stipends, tags, and organizations
- Automated bots for tagging, updates, and validation
- Responsive design with mobile-first approach
- Comprehensive testing with 80%+ coverage goal
- Version management system with semantic versioning
- Automated database backup functionality
- Production environment validation checks

## Installation

1. Clone the repository:

   git clone https://github.com/yourusername/stipend-discovery.git
   cd stipend-discovery


2. Create and activate a virtual environment:

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate


3. Install dependencies:

   pip install -r requirements.txt


4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration

5. Initialize the database:

   flask db upgrade


6. Run the development server:

   flask run


## Usage

### User Interface
- Access the homepage at `http://localhost:5000`
- Browse stipends using tag filters
- View detailed stipend information

### Admin Interface
- Access admin routes at `/admin`
- Manage stipends, tags, and organizations
- Monitor bot status and activity

## Testing

Run tests with:

pytest --cov=app --cov-report=term-missing


We aim to maintain 80%+ test coverage. Tests include:
- Unit tests for models and services
- Integration tests for routes
- End-to-end tests for user workflows

## Contributing

1. Create a new branch:

   git checkout -b feature/your-feature-name


2. Make your changes following our Coding conventions.

3. Write tests for new functionality

4. Submit a pull request with a clear description of changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Version Management

- **Versioning Policy**: The project follows semantic versioning (MAJOR.MINOR.PATCH).
- **Current Version**: v1.2.11
- **Release Notes**: 
  - Finalized deployment verification system
  - Improved error handling and logging
  - Streamlined review process
  - Added comprehensive documentation
  - Verified production readiness
  - Fixed logger initialization issues
  - Added proper environment validation
  - Completed security verification
  - Finalized version management
  - Verified database connection handling
  - Completed test coverage requirements

## Deployment Instructions

### Backup Procedures
- To create a production database backup:
  ```bash
  /run python scripts/verification/verify_backup.py --create
  ```

### Running Migrations
- To run database migrations:
  ```bash
  /run python scripts/startup/init_db.py --migrate
  ```

### Release Process
1. Update release notes:
   ```bash
   /run python scripts/finalize_docs.py --include-deployment
   ```
2. Commit and push changes:
   ```bash
   /run python scripts/commit_changes.py --message "Release v1.2.11" --push
   ```
3. Create and push version tag:
   ```bash
   git tag v1.2.11
   git push origin v1.2.11
   ```

### Final Verification
- Validate production environment:
  ```bash
  /run python scripts/verification/verify_production.py --full
  ```
- Verify deployment readiness:
  ```bash
  /run python scripts/verification/verify_deployment.py --check-type=final-check
  ```

- Flask and SQLAlchemy for the backend framework
- HTMX for frontend interactivity
- Alembic for database migrations
