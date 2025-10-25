from app.db.database import Base
import app.db.models  # import để các class được đăng ký
print(Base.metadata.tables.keys())