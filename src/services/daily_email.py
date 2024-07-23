import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

def send_email(sender_email, sender_password, recipient_email, subject, body, attachment_path=None):
    # Створення об'єкта повідомлення
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Додавання тексту повідомлення
    msg.attach(MIMEText(body, 'plain'))

    # Додавання вкладення
    if attachment_path and os.path.isfile(attachment_path):
        attachment = open(attachment_path, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
        msg.attach(part)

    # Підключення до сервера SMTP та відправка електронної пошти
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

if __name__ == "__main__":
    # Налаштування параметрів
    sender_email = "your_email@gmail.com"
    sender_password = "your_password"
    recipient_email = "recipient_email@example.com"
    subject = f"Щоденний звіт {datetime.now().strftime('%Y-%m-%d')}"
    body = "Вітаю, це ваш щоденний звіт."

    # Шлях до файлу вкладення (якщо потрібно)
    attachment_path = "path/to/your/report.pdf"

    # Виклик функції для відправки електронної пошти
    send_email(sender_email, sender_password, recipient_email, subject, body, attachment_path)
