from discord.ext import commands

def setup(bot: commands.Bot) -> None:
    @bot.command(name="cvhelp")
    async def custom_help(ctx: commands.Context) -> None:
        """
        List all available commands and what they do.
        """
        help_text = (
            "**CV Helper Bot Commands:**\n\n"
            "`!reviewcv` — Analyze and summarize a CV, provide feedback, and score it.\n"
            "`!extractinfo` — Extract contact information (email, phone, LinkedIn) from a CV.\n"
            "`!cvformatcheck` — Check if the CV follows best formatting practices (length, sections, bullet points, etc.).\n"
            "`!cvmatch` — Compare a job description (text or job board URL) and a CV, and say if they match, using AI to extract and match real skills.\n"
            "`!interviewprep` — Generate likely interview questions from a job description (text or URL) and a CV, and quiz you interactively.\n"
            "`!cvhelp` — List all available commands and what they do.\n"
        )
        await ctx.send(help_text)
