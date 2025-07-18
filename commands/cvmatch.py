import discord
from discord.ext import commands
import tempfile
import os
from utils.cv_processor import extract_text_from_pdf
import re
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import asyncio

# Load the model ONCE at the top (this may take a while the first time)
skill_pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")

# Replace extract_keywords with LLM-based extraction
async def extract_skills_llm(text: str) -> set:
    prompt = (
        "Extract a list of the main required skills and technologies from the following job description or CV. "
        "Return only a comma-separated list of skills, no explanations.\n\n"
        f"Text:\n{text}\n\nSkills:"
    )
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: skill_pipe(prompt, max_new_tokens=60))
    skills_text = result[0]['generated_text'].split("Skills:")[-1].strip()
    skills = [s.strip() for s in skills_text.split(',') if len(s.strip()) > 1]
    return set(skills)

def fetch_job_description_from_url(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; CVHelperBot/1.0)"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Try to find the main job description content
        # This is a simple heuristic; can be improved for specific job boards
        for tag in ['section', 'div', 'article']:
            for elem in soup.find_all(tag):
                text = elem.get_text(separator=' ', strip=True)
                if len(text) > 200:  # Heuristic: likely a job description
                    return text
        # Fallback: return all visible text
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        return f"[Error fetching job description: {e}]"

def suggest_courses_for_skills(skills):
    suggestions = []
    for skill in list(skills)[:5]:  # Limit to 5 for brevity
        coursera = f"https://www.coursera.org/search?query={skill}"
        udemy = f"https://www.udemy.com/courses/search/?q={skill}"
        freecodecamp = f"https://www.freecodecamp.org/news/search/?query={skill}"
        suggestions.append(f"**{skill.title()}**:\n- [Coursera]({coursera})\n- [Udemy]({udemy})\n- [FreeCodeCamp]({freecodecamp})")
    return "\n\n".join(suggestions)

def setup(bot: commands.Bot) -> None:
    @bot.command()
    async def cvmatch(ctx: commands.Context) -> None:
        """
        Compare a job description and a CV, and say if they match. Accepts job description as text or a job board URL.
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
            job_desc = fetch_job_description_from_url(job_input)
            if job_desc.startswith('[Error'):
                await ctx.send(job_desc)
                return
        else:
            job_desc = job_input

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

        # Extract skills from both using LLM
        job_skills = await extract_skills_llm(job_desc)
        cv_skills = await extract_skills_llm(cv_text)

        # Calculate match
        common = job_skills & cv_skills
        match_score = len(common) / max(1, len(job_skills)) * 100

        if match_score > 50:
            result = f"✅ The CV matches the job description! (Match: {match_score:.1f}%)"
        else:
            result = f"❌ The CV does not match the job description well. (Match: {match_score:.1f}%)"

        missing = job_skills - cv_skills
        course_suggestions = suggest_courses_for_skills(missing)
        response = (
            f"{result}\n\n"
            f"**Job Skills:** {', '.join(list(job_skills)[:10])} ...\n"
            f"**CV Skills:** {', '.join(list(cv_skills)[:10])} ...\n"
            f"**Common Skills:** {', '.join(list(common)[:10])} ...\n"
            f"**Missing Skills:** {', '.join(list(missing)[:10])} ...\n\n"
            f"**Course Suggestions for Missing Skills:**\n{course_suggestions}"
        )
        # Split and send if too long
        for chunk in [response[i:i+1900] for i in range(0, len(response), 1900)]:
            await ctx.send(chunk)
