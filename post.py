import openai, requests, os

openai.api_key = os.getenv("OPENAI_API_KEY")
token = os.getenv("LINKEDIN_ACCESS_TOKEN")
author = os.getenv("LINKEDIN_PERSON_URN")

prompt = """
Create a professional LinkedIn post about AI or Computer Science.
Max 120 words.
Professional, engaging.
Include 2-3 hashtags.
Rotate topics like AI, ML, DSA, Cybersecurity, Cloud.
"""

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}]
)

post_text = response.choices[0].message.content

url = "https://api.linkedin.com/v2/ugcPosts"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

data = {
    "author": author,
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

requests.post(url, headers=headers, json=data)
