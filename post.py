import os
import requests
import json
import hashlib
import re
import time
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
# CLIENTS
# ==============================
client = Groq(api_key=GROQ_API_KEY)

headers = {
    "Authorization": f"Bearer {LINKEDIN_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

# ==============================
# DUPLICATE PREVENTION
# ==============================
HISTORY_FILE = "posted_hashes.json"

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"\W+", " ", text)
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
# ENGAGEMENT OPTIMIZED PROMPT
# ==============================
PROMPT = """
Write a high-engagement LinkedIn post about AI or Computer Science.

Rules:
- Max 120 words
- Strong hook in first 2 lines (question, stat, or bold claim)
- 1 actionable insight
- End with a soft CTA (question or opinion)
- Professional tone, no emojis
- 2–3 relevant hashtags
- Topics rotate: AI, ML, DSA, Cybersecurity, Cloud, Careers
"""

# ==============================
# GENERATE UNIQUE POST
# ==============================
existing_hashes = load_hashes()

for _ in range(5):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": PROMPT}]
    )

    post_text = response.choices[0].message.content.strip()
    post_hash = hash_text(normalize(post_text))

    if post_hash not in existing_hashes:
        save_hash(post_hash)
        break
else:
    raise RuntimeError("Failed to generate unique post")

# ==============================
# IMAGE UPLOAD
# ==============================
def upload_image(image_path):
    register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"

    payload = {
        "registerUploadRequest": {
            "owner": AUTHOR_URN,
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }

    r = requests.post(register_url, headers=headers, json=payload)
    r.raise_for_status()
    data = r.json()

    upload_url = data["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]

    asset_urn = data["value"]["asset"]

    with open(image_path, "rb") as img:
        requests.put(upload_url, data=img, headers={
            "Authorization": f"Bearer {LINKEDIN_TOKEN}",
            "Content-Type": "application/octet-stream"
        })

    return asset_urn

# ==============================
# AUTO-RETRY POST FUNCTION
# ==============================
def post_with_retry(url, payload, retries=3):
    for attempt in range(1, retries + 1):
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code in (200, 201):
            return r
        print(f"Retry {attempt}/{retries} failed → {r.status_code}")
        time.sleep(2 ** attempt)
    raise RuntimeError("LinkedIn API failed after retries")

# ==============================
# CREATE POST (IMAGE + TEXT)
# ==============================
image_urn = upload_image("post_image.png")  # make sure file exists

post_url = "https://api.linkedin.com/v2/ugcPosts"

payload = {
    "author": AUTHOR_URN,
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": post_text},
            "shareMediaCategory": "IMAGE",
            "media": [{
                "status": "READY",
                "media": image_urn,
                "title": {"text": "AI Insights"}
            }]
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

response = post_with_retry(post_url, payload)

print("Posted successfully ✅")
print(post_text)
