from app.db.database import SessionLocal
from app.db import models

db = SessionLocal()

# 1. Tạo tenant
tenant = models.Tenant(name="SpaX", api_key="spa123")
db.add(tenant)
db.commit()
db.refresh(tenant)

# 2. Thêm channel
channel = models.Channel(name="Zalo OA", platform="zalo", tenant_id=tenant.id)
db.add(channel)
db.commit()
db.refresh(channel)

# 3. Thêm customer
customer = models.Customer(name="Chị Hoa", phone="0909xxx", tenant_id=tenant.id, channel="zalo")
db.add(customer)
db.commit()
db.refresh(customer)

# 4. Tạo conversation
conv = models.Conversation(tenant_id=tenant.id, channel_id=channel.id, customer_id=customer.id)
db.add(conv)
db.commit()
db.refresh(conv)

# 5. Gửi message
msg1 = models.Message(conversation_id=conv.id, sender="customer", text="Em ơi spa còn mở không?")
msg2 = models.Message(conversation_id=conv.id, sender="bot", text="Dạ, bên em mở tới 9h ạ!")
db.add_all([msg1, msg2])
db.commit()

# ✅ Kiểm tra join
res = db.query(models.Conversation).filter(models.Conversation.tenant_id == tenant.id).first()
print(f"Tenant: {res.tenant_id} | Channel: {res.channel.name} | Messages: {[m.text for m in res.messages]}")

db.close()
