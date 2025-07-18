# CV Helper Bot

CV Helper Bot is a powerful and modular Discord bot designed to assist HR professionals and job seekers with CV (resume) analysis and management. The bot leverages AI and NLP to provide automated feedback, extract key information, and compare CVs directly within your Discord server.

![Bot Demo](assets/demo.png)

## Features

- **CV Review & Scoring:** Analyze and score CVs based on structure, content, and grammar.
- **AI-Powered Feedback:** Summarize and provide actionable feedback using advanced language models.
- **Contact Info Extraction:** Automatically extract email, phone, and LinkedIn from uploaded CVs.
- **Format Checking:** Check if a CV follows best formatting practices (length, sections, bullet points, etc.).
- **Job Match (AI Skills Extraction):** Compare a job description (text or job board URL) and a CV to see if they match, using AI to extract and match real skills.
- **Interview Preparation:** Generate likely interview questions from a job description (text or URL) and a CV, and quiz you interactively.
- **User-Friendly Commands:** Simple commands for HR and job seekers, including custom help.

## Commands

- `!reviewcv` — Analyze and summarize a CV, provide feedback, and score it.
- `!extractinfo` — Extract contact information (email, phone, LinkedIn) from a CV.
- `!cvformatcheck` — Check if the CV follows best formatting practices (length, sections, bullet points, etc.).
- `!cvmatch` — Compare a job description (text or job board URL) and a CV, and say if they match, using AI to extract and match real skills.
- `!interviewprep` — Generate likely interview questions from a job description (text or URL) and a CV, and quiz you interactively.
- `!cvhelp` — List all available commands and what they do.

## Tech Stack

- Python 3
- discord.py
- pdfplumber
- transformers (HuggingFace, TinyLlama)
- torch
- language-tool-python
- matplotlib
- requests
- beautifulsoup4

## Getting Started

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Discord bot token to `config.py`.
4. Run the bot: `python bot.py`
5. Invite the bot to your Discord server and start using the commands!

### Required Bot Permissions

- Send Messages
- Attach Files
- Read Message History

---

Empower your HR workflow and job search with AI-driven CV analysis—right in Discord!
