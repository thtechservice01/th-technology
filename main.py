import os
import requests

from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()  # โหลดค่าจากไฟล์ .env

# ---------- ตั้งค่าจาก Environment Variables ----------
RESEND_API_KEY = os.getenv("RESEND_API_KEY")          # API Key จาก resend.com
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")          # อีเมลปลายทางที่จะรับข้อความ
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")  # อีเมลผู้ส่ง (ใช้ค่า default ของ Resend ได้เลยถ้ายังไม่ได้ผูกโดเมนตัวเอง)

app = FastAPI(title="TH-Technology Contact Backend")

# อนุญาตให้หน้าเว็บ (frontend) เรียก API นี้ได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ให้เว็บเข้าถึงไฟล์รูป/โลโก้ใน static/ ผ่าน path /static/...
app.mount("/static", StaticFiles(directory="static"), name="static")


def send_email(name: str, email: str, subject: str, message: str) -> None:
    """ส่งอีเมลแจ้งเตือนผ่าน Resend API (ใช้ HTTPS แทน SMTP เพราะ Render บล็อกพอร์ต SMTP)"""
    body_text = f"""
มีข้อความใหม่จากฟอร์มติดต่อบนเว็บไซต์ TH-TECHNOLOGY

ชื่อผู้ติดต่อ / บริษัท: {name}
อีเมลติดต่อกลับ: {email}
บริการที่สนใจ: {subject}

รายละเอียด:
{message}
"""

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": SENDER_EMAIL,
            "to": [RECEIVER_EMAIL],
            "reply_to": email,  # ตอบกลับอีเมลลูกค้าได้ทันทีจาก Gmail
            "subject": f"[เว็บไซต์] ข้อความใหม่: {subject}",
            "text": body_text,
        },
        timeout=10,
    )
    response.raise_for_status()  # ถ้า Resend ตอบ error จะ raise exception ให้ endpoint ด้านล่างจับได้


@app.post("/submit-contact/")
async def submit_contact(
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
):
    try:
        send_email(name, email, subject, message)
        return JSONResponse(
            {"status": "success", "message": "ขอบคุณสำหรับข้อมูล ทีมงานจะติดต่อกลับโดยเร็วที่สุด"}
        )
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": f"ไม่สามารถส่งข้อความได้: {str(e)}"},
            status_code=500,
        )


@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "TH-Technology contact backend"}
