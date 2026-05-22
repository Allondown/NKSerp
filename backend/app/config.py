import os


MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/nkserp?connectTimeoutMS=3000&serverSelectionTimeoutMS=3000&maxPoolSize=20&minPoolSize=2")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
