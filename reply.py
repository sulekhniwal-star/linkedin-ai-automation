import os
import requests
from groq import Groq
from datetime import datetime, timedelta
from dateutil import parser

# ==============================
# ENV
# ==============================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LINKEDIN_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
AUTHOR_URN = os.getenv("LINKEDIN_PERSON_URN")

if not all([GROQ_API_KEY, LINKEDIN_TOKEN, AUTHOR_URN]):
    raise EnvironmentError("Missing environment variables")

client = Groq(api_key=GROQ_API_KEY)

headers = {
    "Authorization": f"Bearer {LINKEDIN_TOKEN}",
    "Content-Type": "application/json"
}

# ==============================
# SENTIMENT CLASSIFIER
# ==============================
def classify_sentiment(comment: str) -> str:
    """
    Returns: POSITIVE | NEUTRAL | NEGATIVE | TOXIC
    """
    prompt = f"""
Classify the sentiment of this LinkedIn comment.

Return ONLY one word:
POSITIVE
NEUTRAL
NEGATIVE
TOXIC

Comment:
{comment}
"""
    r = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return r.choices[0].message.content.strip().upper()

# ==============================
# REPLY GENERATOR
# ==============================
def generate_reply(comment: str, sentiment: str) -> str | None:
    if sentiment == "TOXIC":
        return None

    prompts = {
        "POSITIVE": f"""
Reply warmly and professionally.
Thank the commenter and reinforce the idea.
Keep it under 2 lines.

Comment:
{comment}
""",
        "NEUTRAL": f"""
Reply professionally.
Add one helpful insight or clarification.
Invite further discussion.

Comment:
{comment}
""",
        "NEGATIVE": f"""
Reply calmly and professionally.
Acknowledge the concern without being defensive.
Offer clarification or perspective.
Do NOT argue.

Comment:
{comment}
"""
    }

    r = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompts[sentiment]}]
    )

    return r.choices[0].message.content.strip()

# ==============================
# FETCH POSTS
# ==============================
posts = requests.get(
    f"https://api.linkedin.com/v2/shares?q=owners&owners={AUTHOR_URN}",
    headers=headers
).json()

# ==============================
# PROCESS COMMENTS
# ==============================
for post in posts.get("elements", []):
    post_urn = post["id"]

    comments = requests.get(
        f"https://api.linkedin.com/v2/socialActions/{post_urn}/comments",
        headers=headers
    ).json()

    for c in comments.get("elements", []):
        created = parser.parse(c["created"]["time"])

        # Only recent comments
        if datetime.utcnow() - created > timedelta(minutes=60):
            continue

        # Skip if already replied
        if c.get("commentsSummary", {}).get("hasReplies"):
            continue

        comment_text = c["message"]["text"]

        sentiment = classify_sentiment(comment_text)
        print(f"🧠 Sentiment: {sentiment}")

        reply = generate_reply(comment_text, sentiment)

        if not reply:
            print("🚫 Skipped toxic / low-value comment")
            continue

        reply_url = f"https://api.linkedin.com/v2/socialActions/{c['id']}/comments"

        r = requests.post(
            reply_url,
            headers=headers,
            json={"message": {"text": reply}}
        )

        if r.status_code in (200, 201):
            print("✅ Replied successfully")
        else:
            print("❌ Failed to reply:", r.text)
