import os

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "projecthub"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "123456"),
    "port": os.getenv("DB_PORT", "5432")
}

# Security Settings
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-for-projecthub-change-this-in-production")
PASSWORD_SALT = os.getenv("PASSWORD_SALT", "random_salt_for_passwords") # Use a strong, unique salt

# Session Management
SESSION_TIMEOUT_MINUTES = 10
LOGIN_ATTEMPTS_LIMIT = 3
LOGIN_BLOCK_DURATION_MINUTES = 15
DAILY_BLOCK_LIMIT = 3
PASSWORD_RESET_TOKEN_EXPIRATION_MINUTES = 30