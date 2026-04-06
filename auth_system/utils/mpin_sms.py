# utils/notify_utils.py
def send_sms(phone_number: str, message: str) -> bool:
    # यहाँ अपना SMS provider call implement करो
    try:
        print(f"SMS sent to {phone_number}: {message}")
        return True
    except Exception as e:
        print(f"SMS failed: {e}")
        return False

def send_email(email: str, subject: str, message: str) -> bool:
    # यहाँ अपना Email provider call implement करो
    try:
        print(f"Email sent to {email}: {subject} | {message}")
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False