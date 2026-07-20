import os
import requests


MAILTRAP_SEND_URL = "https://send.api.mailtrap.io/api/send"


def send_email_with_mailtrap(
    recipients: list[str],
    subject: str,
    text: str,
    category: str = "delay_message"
) -> dict:
    api_token = os.environ.get("MAILTRAP_API_TOKEN")
    from_email = os.environ.get("MAILTRAP_FROM_EMAIL")
    from_name = os.environ.get("MAILTRAP_FROM_NAME", "BoardGamer App")

    if not api_token:
        raise RuntimeError("MAILTRAP_API_TOKEN ist nicht gesetzt.")

    if not from_email:
        raise RuntimeError("MAILTRAP_FROM_EMAIL ist nicht gesetzt.")

    clean_recipients = sorted({
        email.strip()
        for email in recipients
        if email and email.strip()
    })

    if not clean_recipients:
        raise RuntimeError("Es wurden keine gültigen Empfänger gefunden.")

    payload = {
        "from": {
            "email": from_email,
            "name": from_name
        },
        "to": [
            {
                "email": email
            }
            for email in clean_recipients
        ],
        "subject": subject,
        "text": text,
        "category": category
    }

    response = requests.post(
        MAILTRAP_SEND_URL,
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=15
    )

    if not response.ok:
        raise RuntimeError(
            f"Mailtrap-Fehler: {response.status_code} {response.text}"
        )

    if response.text:
        return response.json()

    return {}