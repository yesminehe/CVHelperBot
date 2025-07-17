import discord
from discord.ext import commands
import tempfile
import os
from utils.cv_processor import extract_text_from_pdf

def extract_keywords(text: str) -> set:
    # Simple keyword extraction: split by common delimiters, filter out short/common words
    import re
    words = re.findall(r'\b\w{4,}\b', text.lower())
    stopwords = {'with', 'from', 'this', 'that', 'have', 'will', 'your', 'you', 'are', 'was', 'but', 'not', 'all', 'any', 'can', 'has', 'had', 'may', 'one', 'two', 'three', 'and', 'for', 'the'}
    return set(w for w in words if w not in stopwords)

def setup(bot: commands.Bot) -> None:
    @bot.command()
    async def cvmatch(ctx: commands.Context) -> None:
        """
        Compare a job description and a CV, and say if they match.
        """
        await ctx.send("Please paste the job description (as a message).")

        def check_msg(m: discord.Message) -> bool:
            return m.author == ctx.author and m.content

        try:
            job_msg = await bot.wait_for('message', check=check_msg, timeout=180)
            job_desc = job_msg.content
        except Exception:
            await ctx.send("Timeout or invalid job description. Please try again.")
            return

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

        # Extract keywords from both
        job_keywords = extract_keywords(job_desc)
        cv_keywords = extract_keywords(cv_text)

        # Calculate match
        common = job_keywords & cv_keywords
        match_score = len(common) / max(1, len(job_keywords)) * 100

        if match_score > 50:
            result = f"✅ The CV matches the job description! (Match: {match_score:.1f}%)"
        else:
            result = f"❌ The CV does not match the job description well. (Match: {match_score:.1f}%)"

        await ctx.send(
            f"{result}\n\n"
            f"**Job Keywords:** {', '.join(list(job_keywords)[:10])} ...\n"
            f"**CV Keywords:** {', '.join(list(cv_keywords)[:10])} ...\n"
            f"**Common Keywords:** {', '.join(list(common)[:10])} ..."
        )
