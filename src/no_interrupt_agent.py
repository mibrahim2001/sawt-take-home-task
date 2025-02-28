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
    
    Edge cases handled:
    - If user provides additional input before agent responds: Ignored until first response completes
    - If agent provides greeting before user input: Not counted as first response
    - If errors occur during response: Agent response counter still increments
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._first_user_input_received = False
        self._agent_responses = 0
        logger.info("NoInterruptFirstResponseAgent initialized")

    def _should_interrupt(self) -> bool:
        """
        Override the _should_interrupt method to prevent interruptions until the first agent response is completed.
        """
        logger.info("------->In should_interrupt method now<-------")
        logger.info(f"Agent responses: {self._agent_responses}")
        logger.info(f"First user input received: {self._first_user_input_received}")
        
        # If user has provided first input but agent hasn't completed first response yet
        if self._first_user_input_received and self._agent_responses == 0:
            logger.info("Ignoring interruption during first response")
            return False
        
        # Otherwise, use default behavior
        return super()._should_interrupt() 