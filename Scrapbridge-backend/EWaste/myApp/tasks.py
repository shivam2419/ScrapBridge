from celery import shared_task
import requests
import os

BREVO_API_KEY = os.getenv("BREVO_API_KEY")

@shared_task
def send_mail_via_brevo(receiver_email, receiver_name, subject, html_content):
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    data = {
        "sender": {
            "name": "Scrapbridge",
            "email": "csdslt2309@glbitm.ac.in"
        },
        "to": [
            {
                "email": receiver_email,
                "name": receiver_name
            }
        ],
        "subject": subject,
        "htmlContent": html_content,
        "textContent": "Scrapbridge - Connecting you to World 🌍 !!"
    }

    response = requests.post(url, json=data, headers=headers)

    # Optional: Logging or error handling here
    return {
        "status": response.status_code,
        "response": response.json() if response.content else {}
    }


@shared_task
def get_ml_prediction_from_hf(text):
    headers = {"Authorization": "Bearer YOUR_HF_API_KEY"}
    payload = {"inputs": text}
    res = requests.post("https://api-inference.huggingface.co/models/your_model", headers=headers, json=payload)
    return res.json()
