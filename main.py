import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()  # โหลดค่าจากไฟล์ .env

# ---------- ตั้งค่าจาก Environment Variables ----------
GMAIL_USER = os.getenv("GMAIL_USER")              # อีเมล Gmail ที่ใช้ส่ง เช่น thtech10530@gmail.com
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # App Password 16 หลักจาก Google (ไม่ใช่รหัสผ่านปกติ)
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", GMAIL_USER)  # อีเมลปลายทางที่จะรับข้อความ (ค่าเริ่มต้น = อีเมลเดียวกับที่ส่ง)

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
    """ส่งอีเมลแจ้งเตือนเข้า Gmail inbox"""
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = f"[เว็บไซต์] ข้อความใหม่: {subject}"
    msg["Reply-To"] = email  # ตอบกลับอีเมลลูกค้าได้ทันทีจาก Gmail

    body = f"""
มีข้อความใหม่จากฟอร์มติดต่อบนเว็บไซต์ TH-TECHNOLOGY

ชื่อผู้ติดต่อ / บริษัท: {name}
อีเมลติดต่อกลับ: {email}
บริการที่สนใจ: {subject}

รายละเอียด:
{message}
"""
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, RECEIVER_EMAIL, msg.as_string())


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
