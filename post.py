import os
import requests
import json
import hashlib
import re
from groq import Groq

# ==============================
# ENVIRONMENT VARIABLES
# ==============================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LINKEDIN_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
AUTHOR_URN = os.getenv("LINKEDIN_PERSON_URN")

if not all([GROQ_API_KEY, LINKEDIN_TOKEN, AUTHOR_URN]):
    raise EnvironmentError("Missing required environment variables")

# ==============================
# GROQ CLIENT
# ==============================
client = Groq(api_key=GROQ_API_KEY)

# ==============================
# DUPLICATE PREVENTION SETUP
# ==============================
HISTORY_FILE = "posted_hashes.json"

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"#\w+", "", text)     # remove hashtags
    text = re.sub(r"\W+", " ", text)     # remove punctuation/symbols
    return text.strip()

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_hashes():
    try:
        with open(HISTORY_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_hash(new_hash: str):
    hashes = load_hashes()
    hashes.add(new_hash)
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(hashes), f, indent=2)

# ==============================
# PROMPT
# ==============================
PROMPT = """
Create a professional LinkedIn post about AI or Computer Science.
Max 120 words.
Professional, engaging, and insightful.
Include 2–3 relevant hashtags.
Rotate topics like AI, ML, DSA, Cybersecurity, Cloud.
No emojis.
"""

# ==============================
# GENERATE UNIQUE POST
# ==============================
existing_hashes = load_hashes()

for attempt in range(5):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": PROMPT}]
    )

    post_text = response.choices[0].message.content.strip()

    normalized = normalize(post_text)
    post_hash = hash_text(normalized)

    if post_hash not in existing_hashes:
        save_hash(post_hash)
        break
else:
    raise RuntimeError("Could not generate a unique post after 5 attempts")

# ==============================
# POST TO LINKEDIN
# ==============================
url = "https://api.linkedin.com/v2/ugcPosts"

headers = {
    "Authorization": f"Bearer {LINKEDIN_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

payload = {
    "author": AUTHOR_URN,
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": post_text},
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

response = requests.post(url, headers=headers, json=payload)

print("LinkedIn Status Code:", response.status_code)
print("Response:", response.text)
print("\nPosted Content:\n", post_text)
