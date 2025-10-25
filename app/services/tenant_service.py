async def handle_incoming_message(platform: str, data: dict):
    # Parse nội dung message từ payload Zalo / Messenger
    text = data.get("message", {}).get("text", "")
    sender = data.get("sender", {}).get("id")
    # Gọi chat module / queue xử lý
    print(f"📨 [{platform}] {sender}: {text}")
