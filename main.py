# This is a quick-and-dirty bot to solve an issue in RLSMP.
# Therefore, the code practices/styles is going to be horrendous. Feel free to refactor it if you want to.

import hikari
import lightbulb
import miru
import json
import datetime as dt
# Message block format
from textwrap import dedent

# The modal/form itself.
class VerifyModal(miru.Modal):
    prompt1 = miru.TextInput(label = "Question 1", min_length = 10, max_length = 500, required = True)
    prompt2 = miru.TextInput(label = "Question 2", min_length = 10, max_length = 500, required = True)

    async def callback(self, ctx: miru.ModalContext):
        # approvals
        STAFF_REVIEW_CHANNEL_ID = 1102780545609515118

        embed = hikari.Embed(
            title = "Verification Pending",
            description = f"Oncoming response from {ctx.author.mention}",
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
            "Your response has been recorded. Please be patient while the staffs verify this response. This can take up to a few hours due to timezones. Sorry about that.",
            flags = hikari.MessageFlag.EPHEMERAL,
        )

        await ctx.bot.rest.add_reaction(STAFF_REVIEW_CHANNEL_ID, msg.id, '✅')
        await ctx.bot.rest.add_reaction(STAFF_REVIEW_CHANNEL_ID, msg.id, '❌')

# The button used to spawn the modal.
class ModalTrigger(miru.View):
    @miru.button(label = "Click here to answer the questions!", custom_id = "SUPER_UNIQUE_ID_FOR_VERIFY_BUTTON", style = hikari.ButtonStyle.PRIMARY)
    async def modal_button(self, btn: miru.Button, ctx: miru.ViewContext):
        modal = VerifyModal("Verification Form")
        await ctx.respond_with_modal(modal)

if __name__ == "__main__":
    with open("./setup/token.json") as fin:
        data = json.load(fin)
        token = data["token"]
        persisting_msg = data["target_msg"]
    
    bot = lightbulb.BotApp(token)

    # These 2 are needed for the bot to listen for buttons even after restart.
    # For more info, visit https://hikari-miru.readthedocs.io/en/latest/guides/persistent_views.html#bound
    bot.d.msg_id = persisting_msg
    bot.d.initial_view = None

    # Add an event listener. This function will run exactly once when the bot connects to Discord.
    @bot.listen()
    async def startup_views(event: hikari.StartedEvent):
        view = ModalTrigger()
        event.app.d.initial_view = view

        message = await event.app.rest.fetch_message(
            channel = 1102847625813831680,
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
        if ctx.bot.d.initial_view.message:
            message: hikari.Message = ctx.bot.d.initial_view.message # Mostly for linting purpose, you can remove this line tbh.
            await ctx.respond(f"Detected an active prompt here: {message.make_link(ctx.guild_id)}. Unlinking it...")
            ctx.bot.d.initial_view.stop()

        
        view = ModalTrigger()
        msg = await ctx.bot.rest.create_message(
            1102847625813831680, 
            dedent('''
            Welcome to RLSMP! The Minecraft and Discord server are locked behind this gate to ensure a safe atmosphere. While it's a private server now, you can request access if you wish to chat or play.

            1. Who invited you/How did you find out about this server? Why did you join it?
            2. What's your Java/Bedrock name? If you're just here to chill, answer so.

            Note that we may remove your access if we notice that you stir up trouble or harm the atmosphere of the server.
            If we already have negative experiences, you may not get access at all. The server is designed to house a small but safe community, which is why it was formally disassociated from Rolling Lounge.
            '''), 
            components = view.build()
        )
        await view.start(msg)
        
        ctx.bot.d.initial_view = view
        # Tbf this attr only matters on startup so you can probably not update this.
        ctx.bot.d.msg_id = msg.id

        # No I don't care if it's going to corrupt the json, it's a small bot.
        with open("./setup/token.json", mode = "w") as fout:
            data = {}
            data["token"] = ctx.bot._token
            data["target_msg"] = msg.id
            json.dump(data, fout, indent = 4)
    
    miru.install(bot)
    bot.run()
