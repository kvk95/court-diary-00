# app/whatsapp/session_store.py

sessions = {}

def get(phone: str):
    return sessions.get(phone)

def set(phone: str, data: dict):
    sessions[phone] = data

def clear(phone: str):
    sessions.pop(phone, None)