import os
import ollama
import discord
import tiktoken
from discord.ext import commands
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = "/",intents = intents)


summary_system_prompt = 'You are a helpful assistant who provides a consice summary of the provided transcript in bullet points of no more than 500 words'
summary_user_prompt =  f'''
                    Please provide a summary for the following chunk of the transcript:
                    1. Start with a high level title for this chunk.
                    2. Provide 6-8 bullet points the key points in this chunk. 
                    3. Start with the title of the chunk and then provide the summary in bullet points instead of using "here's a summary of the transcript".
                    4. No need to use concluding remarks at the end.
                    5. Return the response in markdown format. 
                    6. Add a divider at the end in markdown format.

                    Chunk:
        '''

idea_system_prompt = 'You are an expert idea generator who is an expert in analysing texts and extracting key ideas'

idea_user_prompt = f'''
                    Extract 3 key ideas based on the topics, ideas, concepts, or toughts discussed in the following text or that are similar to the following text.
                    Each idea should have: 
                    1. Title of the video
                    2. 2-lines description of the idea

                    Text:

        '''
@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user.name}")

@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hello, I am a Bot!")

@bot.command(name="ask")
async def ask(ctx, *, message):
    response = ollama.chat(model='llama3', messages=[
      {
          'role': 'system',
          'content': 'You are a helpful assistant who provides concise answers to questions in no more than 100 words'
      },
      {
        'role': 'user',
        'content': message,
      },
    ])
    await ctx.send(response['message']['content'])

@bot.command(name="summarise")
async def summarise(ctx):
    
    msgs = [message.content async for message in ctx.channel.history(limit=10) ]

    summarise_prompt = f"""
                        Summarise the following messages delimited by 3 backticks:
                        ```
                        {msgs}
                        ``` 

    """

    response = ollama.chat(model='llama3', messages=[
      {
          'role': 'system',
          'content': summary_system_prompt
      },
      {
        'role': 'user',
        'content': summarise_prompt,
      },
    ])
    await ctx.send(response['message']['content'])

async def process_chunk(ctx, chunk, chunk_num, num_chunks, system_prompt,user_prompt):
    await ctx.send("Extracting summary of chunk {chunk_num} of {num_chuks}...")

    response = ollama.chat(model='llama3', messages=[
      {
          'role': 'system',
          'content': summary_system_prompt
      },
      {
        'role': 'user',
        'content': summary_user_prompt + chunk,
      },
    ])
    return response['message']['content']

@bot.command(name="yt_tldr")
async def yt_tldr(ctx, url):
    
    await ctx.send("Fetching and summarising the Youtube video...")

    video_id = url.split("v=")[1]
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    full_transcript = " ".join([i['text'] for i in transcript_list])

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(full_transcript)
    num_tokens = len(tokens)

    print(num_tokens)

    chunk_size = 7000

    if num_tokens > chunk_size:
        num_chunks = (num_tokens + chunk_size - 1)//chunk_size
        chunks = [full_transcript[i*chunk_size:i+1*chunk_size] for i in range(num_chunks)]
        for i, chunk in enumerate(chunks):
            summary = await process_chunk(ctx, chunk, i, num_chunks, summary_system_prompt ,summary_user_prompt)
            await ctx.send(summary)
    else:
      response = ollama.chat(model='llama3', messages=[
        {
            'role': 'system',
            'content': summary_system_prompt
        },
        {
          'role': 'user',
          'content': summary_user_prompt + full_transcript,
        },
      ])
      await ctx.send(response['message']['content'])


@bot.command(name="ideas")
async def ideas(ctx, url):
    await ctx.send("Extracting key ideas from the Youtube video")

    video_id = url.split("v=")[1]
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    full_transcript = " ".join([i['text'] for i in transcript_list])

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(full_transcript)
    num_tokens = len(tokens)

    print(num_tokens)

    chunk_size = 7000

    if num_tokens > chunk_size:
        num_chunks = (num_tokens + chunk_size - 1)//chunk_size
        chunks = [full_transcript[i*chunk_size:i+1*chunk_size] for i in range(num_chunks)]
        for i, chunk in enumerate(chunks):
            summary = await process_chunk(ctx, chunk, i, num_chunks, idea_system_prompt, idea_user_prompt)
            await ctx.send(summary)
    else:
      response = ollama.chat(model='llama3', messages=[
        {
            'role': 'system',
            'content': idea_system_prompt
        },
        {
          'role': 'user',
          'content': idea_user_prompt + full_transcript,
        },
      ])
      await ctx.send(response['message']['content'])

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
