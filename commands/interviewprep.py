import discord
from discord.ext import commands
import tempfile
import os
from utils.cv_processor import extract_text_from_pdf
from transformers import pipeline
import asyncio
import re
import requests
from bs4 import BeautifulSoup

# Load the model ONCE at the top (this may take a while the first time)
pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")

def setup(bot: commands.Bot) -> None:
    @bot.command()
    async def interviewprep(ctx: commands.Context) -> None:
        """
        Generate likely interview questions based on a job description and a candidate's CV using TinyLlama locally.
        Then, interactively quiz the user one question at a time.
        """
        await ctx.send("Please paste the job description (as text or a job board URL).")

        def check_msg(m: discord.Message) -> bool:
            return m.author == ctx.author and m.content

        try:
            job_msg = await bot.wait_for('message', check=check_msg, timeout=180)
            job_input = job_msg.content.strip()
        except Exception:
            await ctx.send("Timeout or invalid job description. Please try again.")
            return

        # Detect if input is a URL
        if re.match(r'^https?://', job_input):
            await ctx.send("Fetching job description from the provided URL...")
            def fetch_job_description_from_url(url: str) -> str:
                try:
                    headers = {"User-Agent": "Mozilla/5.0 (compatible; CVHelperBot/1.0)"}
                    resp = requests.get(url, headers=headers, timeout=10)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    for tag in ['section', 'div', 'article']:
                        for elem in soup.find_all(tag):
                            text = elem.get_text(separator=' ', strip=True)
                            if len(text) > 200:
                                return text
                    return soup.get_text(separator=' ', strip=True)
                except Exception as e:
                    return f"[Error fetching job description: {e}]"
            job_desc = fetch_job_description_from_url(job_input)
            if job_desc.startswith('[Error'):
                await ctx.send(job_desc)
                return
            await ctx.send(f"**Job Link:** {job_input}")
        else:
            job_desc = job_input
            await ctx.send("**Job Description received.**")

        await ctx.send("Now, please upload the candidate's CV PDF file.")

        def check_pdf(m: discord.Message) -> bool:
            return (
                m.author == ctx.author and
                m.attachments and
                m.attachments[0].filename.lower().endswith('.pdf')
            )

        try:
            cv_msg = await bot.wait_for('message', check=check_pdf, timeout=120)
            attachment = cv_msg.attachments[0]
        except Exception:
            await ctx.send("Timeout or invalid upload for the CV. Please try again.")
            return

        await ctx.send("Processing, please wait...")

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            temp_path = tmp.name

        try:
            await attachment.save(temp_path)
            cv_text = extract_text_from_pdf(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # Truncate to avoid exceeding model context length
        max_chars = 500
        if len(job_desc) > max_chars:
            job_desc = job_desc[:max_chars]
        if len(cv_text) > max_chars:
            cv_text = cv_text[:max_chars]

        # Generate interview questions locally
        prompt = (
            "Given the following job description and candidate CV, generate 1-5 likely interview questions the candidate might face. "
            "Focus on the required skills, experience, and any gaps.\n\n"
            f"Job Description:\n{job_desc}\n\n"
            f"Candidate CV:\n{cv_text}\n\n"
            "Interview Questions:"
        )
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, lambda: pipe(prompt, max_new_tokens=200)
        )
        questions_text = result[0]['generated_text'].split("Interview Questions:")[-1].strip()
        # Split questions by line or number
        questions = [q.strip("- ") for q in questions_text.split("\n") if q.strip()]
        # Remove empty and non-question lines
        questions = [q for q in questions if len(q) > 10 and (q.endswith('?') or q[0].isdigit())]
        if not questions:
            await ctx.send("Sorry, I couldn't generate interview questions. Please try again.")
            return

        await ctx.send(f"I have generated {len(questions)} interview questions. Do you want to start with the first question? (yes/no)")

        def check_yes_no(m: discord.Message) -> bool:
            return m.author == ctx.author and m.content.lower() in ['yes', 'no']

        try:
            reply = await bot.wait_for('message', check=check_yes_no, timeout=60)
        except Exception:
            await ctx.send("No response received. Session ended.")
            return

        if reply.content.lower() != 'yes':
            await ctx.send("Okay, session ended. You can run !interviewprep again anytime.")
            return

        # Ask questions one by one
        for idx, question in enumerate(questions, 1):
            await ctx.send(f"Question {idx}: {question}")
            try:
                answer = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=180)
            except Exception:
                await ctx.send("No answer received. Moving to the next question.")
                continue
            await ctx.send(f"Received your answer. Ready for the next question? (yes/no)")
            try:
                next_reply = await bot.wait_for('message', check=check_yes_no, timeout=60)
            except Exception:
                await ctx.send("No response received. Session ended.")
                return
            if next_reply.content.lower() != 'yes':
                await ctx.send("Okay, session ended. You can run !interviewprep again anytime.")
                return
        await ctx.send("You have completed all the interview questions! Good luck with your preparation.")