# app/utils/phone.py

def normalize_phone(phone: str) -> str:
    if not phone:
        return ""

    phone = phone.replace("whatsapp:", "").strip()
    phone = phone[-10:]

    return phone