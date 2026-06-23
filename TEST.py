import asyncio
import edge_tts

async def test():
    communicate = edge_tts.Communicate(
        "Hello world",
        voice="en-US-AriaNeural"
    )
    await communicate.save("test.mp3")

asyncio.run(test())