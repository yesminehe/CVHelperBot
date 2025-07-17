import discord
from discord.ext import commands
import tempfile
import os
from utils.cv_processor import extract_text_from_pdf
from utils.scoring import extract_contact_info
import logging

logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(name)s: %(message)s'
)

def setup(bot: commands.Bot) -> None:
    @bot.command()
    async def extractinfo(ctx: commands.Context) -> None:
        """
        Command to extract contact info from an uploaded CV PDF.
        """
        await ctx.send("Please upload the CV PDF file to extract contact info.")

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
            logging.exception("An error occurred while waiting for the CV upload in extractinfo.")
            await ctx.send("An unexpected error occurred. Please try again later.")
            return

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            temp_path = tmp.name

        try:
            await attachment.save(temp_path)
            cv_text = extract_text_from_pdf(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        info = extract_contact_info(cv_text)
        if not info:
            await ctx.send("No contact information found in the CV.")
        else:
            info_lines = [f"**{key.capitalize()}**: {value}" for key, value in info.items()]
            await ctx.send("Extracted Contact Information:\n" + "\n".join(info_lines))
