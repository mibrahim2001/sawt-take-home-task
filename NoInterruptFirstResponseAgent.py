import logging
from typing import AsyncIterable
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.agents.pipeline.speech_handle import SpeechHandle
from livekit.agents import llm

logger = logging.getLogger("voice-agent")

class NoInterruptFirstResponseAgent(VoicePipelineAgent):
    """
    A custom VoicePipelineAgent that ignores all user interruptions after the first input
    until the agent has fully spoken its first response.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._first_response_completed = False
        self._first_user_input_received = False
        self._agent_responses = 0
        self._agent_say_used = False
        logger.info("NoInterruptFirstResponseAgent initialized")

    async def say(
        self,
        source: str | llm.LLMStream | AsyncIterable[str],
        allow_interruptions: bool = True,
        add_to_chat_ctx: bool = True,
    ) -> SpeechHandle:
        """
        Override the say method to control interruptions during the first response.
        For the first response, we force allow_interruptions to False.
        """
        # If this is the first response and we've received user input,
        # force allow_interruptions to False
        logger.info("------->In say method now<-------")
        self._agent_say_used = True
        return await super().say(
            source,
            allow_interruptions=allow_interruptions,
            add_to_chat_ctx=add_to_chat_ctx,
        )

    def _should_interrupt(self) -> bool:
        """
        Override the _should_interrupt method to prevent interruptions during the first response.
        """
        logger.info("------->In should_interrupt method now<-------")
        logger.info(f"Agent responses: {self._agent_responses}")
        # If we haven't completed the first response yet, don't allow interruptions
        if (self._agent_say_used and self._agent_responses < 2) or (
            not self._agent_say_used and self._agent_responses < 1
        ):
            return False

        # Otherwise, use the default behavior
        return super()._should_interrupt()
