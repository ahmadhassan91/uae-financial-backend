import smtplib
import socket
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

print(f"Testing connection to {SMTP_HOST}:{SMTP_PORT}")
print(f"Username: {SMTP_USERNAME}")
print(f"Password length: {len(SMTP_PASSWORD) if SMTP_PASSWORD else 0}")

print("-" * 50)
print("Test 1: Standard SMTP with STARTTLS (Port 587)")
try:
    print("Connecting...")
    server = smtplib.SMTP(SMTP_HOST, 587, timeout=10)
    print("Connected. EHLO...")
    server.ehlo()
    print("EHLO success. STARTTLS...")
    server.starttls()
    print("STARTTLS success. Login...")
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    print("Login success!")
    server.quit()
except Exception as e:
    print(f"FAILED: {e}")

print("-" * 50)
print("Test 2: SMTP_SSL (Port 465)")
try:
    print("Connecting...")
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL(SMTP_HOST, 465, context=context, timeout=10)
    print("Connected. EHLO...")
    server.ehlo()
    print("EHLO success. Login...")
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    print("Login success!")
    server.quit()
except Exception as e:
    print(f"FAILED: {e}")
