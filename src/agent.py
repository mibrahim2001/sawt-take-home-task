import logging

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.plugins import openai, deepgram, silero, turn_detector
from src.no_interrupt_agent import NoInterruptFirstResponseAgent
from livekit.agents.pipeline.speech_handle import SpeechHandle


load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant. You yap but not that much."
            "You like to talk about random stuff. You are also a bit of a know it all."
            "Do not exceed 100 words in your responses."
        ),
    )

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    agent = NoInterruptFirstResponseAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=deepgram.TTS(),
        turn_detector=turn_detector.EOUModel(),
        # minimum delay for endpointing, used when turn detector believes the user is done with their turn
        min_endpointing_delay=0.5,
        # maximum delay for endpointing, used when turn detector does not believe the user is done with their turn
        max_endpointing_delay=5.0,
        chat_ctx=initial_ctx,
    )

    @agent.on("user_speech_committed")
    def on_user_speech_committed(speech_handle: SpeechHandle):
        logger.info("------->In on_user_speech_committed method now<-------")
        agent._first_user_input_received = True

    @agent.on("agent_speech_committed")
    def on_agent_speech_committed(speech_handle: SpeechHandle):
        logger.info("------->In on_agent_speech_committed method now<-------")
        if agent._first_user_input_received:
            agent._agent_responses += 1
            if agent._agent_responses > 0:
                logger.info("First response completed, interruptions will now be allowed")

    agent.start(ctx.room, participant)

    # The initial greeting is not considered the first response to user input
    await agent.say(
        "Hello, how can I help you today?"
    )

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    ) 
