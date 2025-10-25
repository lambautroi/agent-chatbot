from .database import Base, engine
from . import models

def init_db():
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Done!")