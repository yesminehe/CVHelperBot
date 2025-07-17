import discord
from discord.ext import commands
import tempfile
import os
from utils.cv_processor import extract_text_from_pdf

section_synonyms = {
    'education': ['education', 'academic', 'studies', 'school', 'university', 'college'],
    'experience': ['experience', 'work history', 'employment', 'professional background', 'career'],
    'skills': ['skills', 'abilities', 'competencies', 'proficiencies', 'expertise'],
    'projects': ['projects', 'portfolio', 'works', 'case studies', 'assignments']
}

def setup(bot: commands.Bot) -> None:
    @bot.command()
    async def cvformatcheck(ctx: commands.Context) -> None:
        """
        Check if the CV follows best formatting practices.
        """
        await ctx.send("Please upload your CV PDF file to check formatting.")

        def check(m: discord.Message) -> bool:
            return (
                m.author == ctx.author and
                m.attachments and
                m.attachments[0].filename.lower().endswith(".pdf")
            )

        try:
            msg = await bot.wait_for('message', check=check, timeout=120)
            attachment = msg.attachments[0]
        except Exception:
            await ctx.send("Timeout or invalid upload, please try again.")
            return

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            temp_path = tmp.name

        try:
            await attachment.save(temp_path)
            cv_text = extract_text_from_pdf(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # Simple checks
        length = len(cv_text.split())
        has_bullets = any(b in cv_text for b in ['•', '-', '*'])

        found_sections = []
        text = cv_text.lower()
        for section, keywords in section_synonyms.items():
            if any(keyword in text for keyword in keywords):
                found_sections.append(section)

        msg = f"Word count: {length}\n"
        msg += f"Bullet points: {'Yes' if has_bullets else 'No'}\n"
        msg += f"Sections found: {', '.join(found_sections) if found_sections else 'None'}\n"

        await ctx.send("**CV Format Check Results:**\n" + msg)
