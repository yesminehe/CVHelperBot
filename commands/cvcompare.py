import discord
from discord.ext import commands
import io
from utils.cv_processor import extract_text_from_pdf
from utils.scoring import extract_contact_info, score_cv
import logging
import re
import asyncio

logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(name)s: %(message)s'
)

def extract_skills_from_text(cv_text: str) -> list:
    skills = []
    skills_section = re.search(r'skills[:\n]+([\s\S]+?)(\n\w+:|$)', cv_text, re.IGNORECASE)
    if skills_section:
        section_text = skills_section.group(1)
        skills = re.split(r',|;|\n', section_text)
        skills = [s.strip() for s in skills if s.strip()]
    else:
        words = re.findall(r'\b([A-Z][a-zA-Z0-9\+\#\-]*)\b', cv_text)
        common_words = {'The', 'And', 'With', 'For', 'From', 'This', 'That', 'Have', 'Will', 'Your', 'You', 'Are', 'Was', 'But', 'Not', 'All', 'Any', 'Can', 'Has', 'Had', 'May', 'One', 'Two', 'Three'}
        skills = list({w for w in words if w not in common_words})
    return skills

async def extract_text_from_attachment(attachment):
    file_bytes = await attachment.read()
    with io.BytesIO(file_bytes) as file_obj:
        return extract_text_from_pdf(file_obj)

async def async_score_cv(cv_text):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, score_cv, cv_text)

def setup(bot: commands.Bot) -> None:
    @bot.command()
    async def cvcompare(ctx: commands.Context) -> None:
        """
        Compare two CVs (PDFs) and highlight differences or strengths.
        """
        await ctx.send("Please upload the **first** CV PDF file.")

        def check_pdf(m: discord.Message) -> bool:
            return (
                m.author == ctx.author and
                m.attachments and
                m.attachments[0].filename.lower().endswith(".pdf")
            )

        # Get first CV
        try:
            msg1 = await bot.wait_for('message', check=check_pdf, timeout=120)
            attachment1 = msg1.attachments[0]
        except Exception:
            logging.exception("Error while waiting for the first CV upload in cvcompare.")
            await ctx.send("Timeout or invalid upload for the first CV. Please try again.")
            return

        await ctx.send("Now, please upload the **second** CV PDF file.")

        # Get second CV
        try:
            msg2 = await bot.wait_for('message', check=check_pdf, timeout=120)
            attachment2 = msg2.attachments[0]
        except Exception:
            logging.exception("Error while waiting for the second CV upload in cvcompare.")
            await ctx.send("Timeout or invalid upload for the second CV. Please try again.")
            return

        await ctx.send("Processing both CVs, please wait...")

        # Extract text from both attachments (no saving)
        cv1_text = await extract_text_from_attachment(attachment1)
        cv2_text = await extract_text_from_attachment(attachment2)

        # Extract skills and scores
        skills1 = set(extract_skills_from_text(cv1_text))
        skills2 = set(extract_skills_from_text(cv2_text))
        score1 = await async_score_cv(cv1_text)
        score2 = await async_score_cv(cv2_text)

        # Compare skills
        unique1 = skills1 - skills2
        unique2 = skills2 - skills1
        common = skills1 & skills2

        # Prepare the comparison message
        msg = (
            f"**CV 1 Score:** {score1}/100\n"
            f"**CV 2 Score:** {score2}/100\n\n"
            f"**Common Skills:** {', '.join(common) if common else 'None'}\n"
            f"**Unique to CV 1:** {', '.join(unique1) if unique1 else 'None'}\n"
            f"**Unique to CV 2:** {', '.join(unique2) if unique2 else 'None'}"
        )

        await ctx.send(msg)
