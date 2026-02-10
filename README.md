# LinkedIn AI Automation Suite

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-blueviolet)
![LLM](https://img.shields.io/badge/LLM-Groq%20%7C%20LLaMA-orange)
![LinkedIn API](https://img.shields.io/badge/LinkedIn-API-0A66C2)
![License](https://img.shields.io/badge/License-MIT-green)

## Introduction

An AI-powered LinkedIn automation system that creates, publishes, and engages with content automatically using Large Language Models and LinkedIn APIs. Built for developers, creators, and professionals who want consistent personal branding with zero daily effort.

## Features

- **AI-Generated Posts**: Generates high-engagement LinkedIn posts on AI and Computer Science topics.
- **Duplicate Prevention**: Uses hashing to prevent posting duplicate content.
- **Image Uploads**: Automatically uploads images along with posts.
- **Sentiment-Aware Replies**: Analyzes and replies to comments intelligently based on sentiment.
- **Automated Scheduling**: Runs fully automated using GitHub Actions for daily posting and replying.

## System Architecture

![System Architecture](image.png)

## Project Structure

![Project Structure](image-1.png)

## Setup

### Prerequisites

- Python 3.10 or higher
- A Groq API key
- LinkedIn API access token and person URN

### Environment Variables

Set the following environment variables in your system or GitHub Secrets:

```bash
GROQ_API_KEY=your_groq_api_key
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
LINKEDIN_PERSON_URN=urn:li:person:xxxxxxxx
```

**⚠️ Warning**: Keep these values secure. Never commit them to version control.

## Installation

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/linkedin-ai-automation.git
   cd linkedin-ai-automation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the posting script:
   ```bash
   python post.py
   ```

### Deployment

For automated deployment, configure GitHub Actions as described in the Automation section.

## Usage

### Posting Content

Run `post.py` to generate and post a new LinkedIn update. The script will:
- Generate unique AI/CS content using Groq LLM.
- Check for duplicates using hash-based prevention.
- Upload an image and post to LinkedIn.

### Replying to Comments

Run `reply.py` to analyze and reply to recent comments on your posts. The script:
- Fetches recent posts and comments.
- Classifies comment sentiment (Positive, Neutral, Negative, Toxic).
- Generates appropriate replies using AI, skipping toxic comments.

## Automation

This project uses GitHub Actions for fully automated operation:

- **daily_post.yml**: Schedules daily posting of AI/CS content.
- **reply_comments.yml**: Handles intelligent replying to comments.

Once configured, the system runs unattended.

## Safety & Ethics

- **Duplicate Protection**: Ensures no repeated content.
- **Rate Limiting**: Respects LinkedIn API limits.
- **Toxic Comment Filtering**: Skips inappropriate comments.
- **Professional Tone**: Enforces professional communication.

## Future Enhancements

- Analytics dashboard for engagement metrics.
- Support for carousel posts.
- Multi-account management.
- Approval-based posting mode for manual review.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

**Sulekh Niwal**  
AI Automation • Backend Systems • Developer Productivity  

⭐ Star the repo if you find this useful.
