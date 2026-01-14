
class OTPStatus:
    SENT = "sent"
    PENDING = "pending"
    DELIVERED = "delivered"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"

    CHOICES = (
        (SENT, "Sent"),
        (PENDING, "Pending"),
        (DELIVERED, "Delivered"),
        (VERIFIED, "Verified"),
        (FAILED, "Failed"),
        (EXPIRED, "Expired"),
    )
