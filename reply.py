import requests, os
from groq import Groq
from datetime import datetime, timedelta
from dateutil import parser

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

token = os.getenv("LINKEDIN_ACCESS_TOKEN")
author = os.getenv("LINKEDIN_PERSON_URN")

headers = {"Authorization": f"Bearer {token}"}

posts = requests.get(
    f"https://api.linkedin.com/v2/shares?q=owners&owners={author}",
    headers=headers
).json()

for post in posts.get("elements", []):
    post_urn = post["id"]

    comments = requests.get(
        f"https://api.linkedin.com/v2/socialActions/{post_urn}/comments",
        headers=headers
    ).json()

    for c in comments.get("elements", []):
        created = parser.parse(c["created"]["time"])
        if datetime.utcnow() - created > timedelta(minutes=30):
            continue

        comment_text = c["message"]["text"]

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{
                "role": "user",
                "content": f"Reply professionally to this LinkedIn comment:\n{comment_text}"
            }]
        )

        ai_reply = response.choices[0].message.content

        reply_url = f"https://api.linkedin.com/v2/socialActions/{c['id']}/comments"
        requests.post(reply_url, headers=headers, json={
            "message": {"text": ai_reply}
        })
