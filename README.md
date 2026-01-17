# Python Drive Project

A Django-based authentication and management system for drivers, vehicles, and related operations.

## Features

- User authentication and role management
- Driver and vehicle management
- Biometric integration
- Document upload and verification
- OTP verification
- SMS and email notifications

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/ajaythakre2040/python_drive.git
   cd python_drive
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env` and fill in your values (if available).
   - Ensure sensitive data like API keys are configured.

5. Run migrations:
   ```
   1. python manage.py makemigration 
   2. python manage.py migrate
   ```
6. Seeder :
   ^^^^^^^^
   python manage.py seed_admin 
   ^^^^^^^^^
7. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

8. Run the development server:
   ```
   python manage.py runserver
   ```

## Usage

- Access the admin panel at `http://localhost:8000/admin/`
- API endpoints are documented in `URLS.md`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.