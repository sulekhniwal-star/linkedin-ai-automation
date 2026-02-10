import openai, requests, os
from datetime import datetime, timedelta
from dateutil import parser

openai.api_key = os.getenv("OPENAI_API_KEY")
token = os.getenv("LINKEDIN_ACCESS_TOKEN")
author = os.getenv("LINKEDIN_PERSON_URN")

headers = {"Authorization": f"Bearer {token}"}

# Fetch recent posts
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

        ai_reply = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"Reply professionally to this LinkedIn comment:\n{comment_text}"
            }]
        ).choices[0].message.content

        reply_url = f"https://api.linkedin.com/v2/socialActions/{c['id']}/comments"
        requests.post(reply_url, headers=headers, json={
            "message": {"text": ai_reply}
        })
