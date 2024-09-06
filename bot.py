import discord
import re
import asyncio

from download_video import download_video, remove_video
from load_config import discord_token
from analyze import upload_to_gemini, generate_analyze, ask_followup, genai
from split import splitmsg

client = discord.Client(intents=discord.Intents.all())

now_message = 0

async def progress(message, reset=False):
    global now_message
    if reset:
        now_message = 0
    messages = [
        "Downloading Video From Source...",
        "Uploading Video To Gemini...",
        "Extracting Tokens From Video...",
        "Analyzing Video With Gemini. This may take a while...",
        "Cleaning Up Temporary Files...",
        ""
    ]
    edit_message = ""

    for content in messages:
        if len(content) == 0:
            continue
        elif now_message == messages.index(content):
            edit_message = edit_message + "\n## <a:loading:1281561134968606750> " + content
        elif now_message > messages.index(content):
            edit_message = edit_message + "\n-# ✅ " + content        
        elif now_message < messages.index(content):
            edit_message = edit_message + "\n-# ❌ " + content

    if now_message == 0:
        reply_msg = await message.reply(edit_message)
    else:
        reply_msg = await message.edit(content=edit_message)
    now_message += 1
    return reply_msg

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(f"<@{str(client.user.id)}>"):
        url = message.content.split(" ")[1]
        if re.match(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", url):
            reply_msg = await progress(message, True)
            download_video(url)
            await progress(reply_msg)
            file = upload_to_gemini("temp_vid.mp4")
            await progress(reply_msg)
            while file.state.name == "PROCESSING":
                await asyncio.sleep(3)
                file = genai.get_file(file.name)
            await progress(reply_msg)
            reply = await generate_analyze(file)
            replys = await splitmsg(reply)
            for i in replys:
                if replys.index(i) == 0:
                    await message.reply(i)
                else:
                    await message.channel.send(i)
            await progress(reply_msg)
            remove_video()
            await progress(reply_msg)
            return
        else:
            await message.reply("Invalid URL")
            return
        
    if client.user.mentioned_in(message):
        await message.add_reaction("<a:loading:1281561134968606750>")
        reply_msg_follow = await ask_followup(message.content)
        replys = await splitmsg(reply_msg_follow)
        for i in replys:
            if replys.index(i) == 0:
                await message.reply(i)
            else:
                await message.channel.send(i)
        await message.remove_reaction("<a:loading:1281561134968606750>", client.user)
        return


client.run(discord_token)