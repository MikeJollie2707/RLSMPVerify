# This is a quick-and-dirty bot to solve an issue in MooseSMP.
# Therefore, the code practices/styles is going to be horrendous. Feel free to refactor it if you want to.

# For Discord components: https://hikari-miru.readthedocs.io/en/latest/
# For Discord commands in general: https://hikari-lightbulb.readthedocs.io/en/latest/

import typing as t
import hikari
import lightbulb
import miru
import json
import datetime as dt
# Message block format
from textwrap import dedent

# Modal limitation is 5 prompts, each prompt is 45 characters max.
PROMPTS = (
    "Question 1",
    "Question 2",
    "Question 3",
)
# Make sure to change this in production.
PROMPT_DESTINATION = 1102847625813831680

# The modal/form itself.
class VerifyModal(miru.Modal):
    def __init__(self, title: str, *, custom_id: str | None = None, timeout: float | int | dt.timedelta | None = 300) -> None:
        super().__init__(title, custom_id=custom_id, timeout=timeout)
        
        # Dynamically add prompts to modal.
        for i, prompt in enumerate(PROMPTS):
            self.add_item(miru.TextInput(label = prompt, min_length = 5, max_length = 500, required = True))

    # This function is called when the user submit the form.
    async def callback(self, ctx: miru.ModalContext):
        # approvals
        STAFF_REVIEW_CHANNEL_ID = 1102780545609515118

        embed = hikari.Embed(
            title = "Verification Pending",
            description = f"Oncoming response from {ctx.author.mention} ({ctx.author})",
            timestamp = dt.datetime.now().astimezone(),
        )

        for i, prompt in enumerate(self.children):
            embed.add_field(
                name = f"Prompt {i + 1}:",
                value = prompt.value
            )

        msg = await ctx.bot.rest.create_message(
            STAFF_REVIEW_CHANNEL_ID,
            content = "@everyone",
            embed = embed,
            mentions_everyone = True,
        )

        await ctx.respond(
            "Your response has been recorded. Please be patient while the staffs verify this response. " +
            "This can take up to a few hours due to timezones. Sorry about that. " +
            "If you don't see more channels within a week, it is safe to assume your application is rejected.",
            flags = hikari.MessageFlag.EPHEMERAL,
        )

        await ctx.bot.rest.add_reaction(STAFF_REVIEW_CHANNEL_ID, msg.id, '✅')
        await ctx.bot.rest.add_reaction(STAFF_REVIEW_CHANNEL_ID, msg.id, '❌')

# The button used to spawn the modal.
class ModalTrigger(miru.View):
    def __init__(self, *, timeout: float | int | dt.timedelta | None = 120, autodefer: bool = True) -> None:
        # Have to set it to None so it doesn't expire.
        super().__init__(timeout=None, autodefer=autodefer)
    @miru.button(label = "Click here to answer the questions!", custom_id = "SUPER_UNIQUE_ID_FOR_VERIFY_BUTTON", style = hikari.ButtonStyle.PRIMARY)
    async def modal_button(self, btn: miru.Button, ctx: miru.ViewContext):
        modal = VerifyModal("Verification Form")
        await ctx.respond_with_modal(modal)

if __name__ == "__main__":
    with open("./setup/config.json") as fin:
        data = json.load(fin)
        token = data["token"]
        persisting_msg = data["target_msg"]
    
    bot = lightbulb.BotApp(token)

    # These 2 are needed for the bot to listen for buttons even after restart.
    # For more info, visit https://hikari-miru.readthedocs.io/en/latest/guides/persistent_views.html#bound
    # Using bot.d we can store custom attributes without global variables.
    bot.d.msg_id = persisting_msg
    bot.d.initial_view = None

    # Add an event listener. This function will run exactly once when the bot connects to Discord.
    @bot.listen()
    async def startup_views(event: hikari.StartedEvent):
        view = ModalTrigger()
        event.app.d.initial_view = view

        message = await event.app.rest.fetch_message(
            channel = PROMPT_DESTINATION,
            message = event.app.d.msg_id,
        )

        # Start listening for buttons at target_msg.
        await view.start(message)
    
    @bot.command()
    # Check for Operators role.
    @lightbulb.add_checks(lightbulb.has_roles(868609637778346024))
    @lightbulb.add_cooldown(length = 10.0, uses = 1, bucket = lightbulb.GlobalBucket)
    @lightbulb.command("send_prompt", "Send the prompt for verification. Only used once unless there are errors.")
    @lightbulb.implements(lightbulb.SlashCommand)
    async def send_prompt(ctx: lightbulb.Context):
        # Check if we're listening for interactions in a message.
        if ctx.bot.d.initial_view.message:
            message: hikari.Message = ctx.bot.d.initial_view.message # Mostly for linting purpose, you can remove this line tbh.
            await ctx.respond(f"Detected an active prompt here: {message.make_link(ctx.guild_id)}. Unlinking it...")
            ctx.bot.d.initial_view.stop()
        
        view = ModalTrigger()
        msg = await ctx.bot.rest.create_message(
            PROMPT_DESTINATION, 
            dedent('''
            Welcome to the MooseSMP! To access the Minecraft and Discord server, we would like you to answer a few questions:

            1. Why did you join this server? Do you intend on playing in the SMP or are you just here to chill?
            2. If you're here to play, what's your Java/Bedrock name? (Type "None" if you don't play on the SMP) *We don't support names with spaces in it.*
            3. What is the exception to SMP Rule 3?

            Note that we may revoke your access at anytime if we notice that you stir up trouble or harm the atmosphere of the server.
            '''), 
            components = view.build()
        )
        await view.start(msg)

        # Now we respond to the command's interaction.
        await ctx.respond(f"A new prompt has been created in <#{PROMPT_DESTINATION}>. Go check it out.")
        
        ctx.bot.d.initial_view = view
        # Tbf this attr only matters on startup so you can probably not update this.
        ctx.bot.d.msg_id = msg.id

        # No I don't care if it's going to corrupt the json, it's a small bot.
        with open("./setup/config.json", mode = "w") as fout:
            data = {}
            data["token"] = ctx.bot._token
            data["target_msg"] = msg.id
            json.dump(data, fout, indent = 4)
    
    miru.install(bot)
    bot.run()
