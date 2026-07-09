import os
import resend
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

resend.api_key = RESEND_API_KEY

app = FastAPI()

# อนุญาตให้หน้าเว็บ (frontend) เรียก API นี้ได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def send_email(name: str, email: str, subject: str, message: str) -> None:
    """ส่งอีเมลแจ้งเตือนผ่าน Resend API"""
    body_text = f"""
มีข้อความใหม่จากฟอร์มติดต่อบนเว็บไซต์ TH-TECHNOLOGY

ชื่อผู้ติดต่อ / บริษัท: {name}
อีเมลติดต่อกลับ: {email}
บริการที่สนใจ: {subject}

รายละเอียด:
{message}
"""
    resend.Emails.send({
        "from": SENDER_EMAIL,
        "to": RECEIVER_EMAIL,
        "reply_to": email,
        "subject": f"[เว็บไซต์] ข้อความใหม่: {subject}",
        "text": body_text,
    })


@app.post("/submit-contact/")
async def submit_contact(
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
):
    try:
        send_email(name, email, subject, message)
        return JSONResponse({"status": "success", "message": "ส่งข้อความสำเร็จ ขอบคุณที่ติดต่อเรา"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
