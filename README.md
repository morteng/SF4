# Stipend Discovery Website

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.0+-blue.svg)](https://flask.palletsprojects.com/)

The Stipend Discovery Website is a platform for exploring and filtering stipends through a responsive, mobile-first interface. Built using Flask with HTMX for real-time interactivity, it includes a secure admin interface and automated bots for data management.

## Features

- Real-time stipend discovery with tag-based filtering
- Secure admin interface for managing stipends, tags, and organizations
- Automated bots for tagging, updates, and validation
- Responsive design with mobile-first approach
- Comprehensive testing with 80%+ coverage goal

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


2. Make your changes following our [coding conventions](CONVENTIONS.md)

3. Write tests for new functionality

4. Submit a pull request with a clear description of changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask and SQLAlchemy for the backend framework
- HTMX for frontend interactivity
- Alembic for database migrations
