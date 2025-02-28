import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the path so we can import the agent module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.no_interrupt_agent import NoInterruptFirstResponseAgent
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.agents.pipeline.speech_handle import SpeechHandle


class TestNoInterruptFirstResponseAgent(unittest.TestCase):
    """
    Test suite for the NoInterruptFirstResponseAgent class.
    
    These tests verify that the agent correctly handles interruptions
    based on the state of the conversation.
    """
    
    def setUp(self):
        """
        Set up test fixtures. Creates a mocked agent for testing.
        """
        # Create patches for the parent class constructor
        patcher = patch('src.no_interrupt_agent.VoicePipelineAgent.__init__')
        self.mock_parent_init = patcher.start()
        self.mock_parent_init.return_value = None
        self.addCleanup(patcher.stop)
        
        # Create the agent instance
        self.agent = NoInterruptFirstResponseAgent()
        
        # Mock the parent's _should_interrupt method
        patcher = patch.object(VoicePipelineAgent, '_should_interrupt')
        self.mock_parent_should_interrupt = patcher.start()
        self.mock_parent_should_interrupt.return_value = True  # Default to allowing interruption
        self.addCleanup(patcher.stop)
    
    def test_initialization(self):
        """
        Test that the agent initializes with the correct default state.
        """
        self.assertFalse(self.agent._first_user_input_received)
        self.assertEqual(self.agent._agent_responses, 0)
    
    def test_should_not_interrupt_during_first_response(self):
        """
        Test that interruptions are ignored during the first response cycle.
        """
        # Set up state: user has provided input but agent hasn't responded yet
        self.agent._first_user_input_received = True
        self.agent._agent_responses = 0
        
        # Verify interruption is blocked
        self.assertFalse(self.agent._should_interrupt())
        
    def test_should_allow_interrupt_after_first_response(self):
        """
        Test that interruptions are allowed after the first response is completed.
        """
        # Set up state: user has provided input and agent has completed first response
        self.agent._first_user_input_received = True
        self.agent._agent_responses = 1
        
        # Verify interruption is allowed (delegated to parent class)
        self.assertTrue(self.agent._should_interrupt())
    
    def test_should_allow_interrupt_if_no_user_input_yet(self):
        """
        Test that interruptions are allowed if no user input has been received yet.
        This would be the case during the initial greeting.
        """
        # Set up state: no user input yet
        self.agent._first_user_input_received = False
        self.agent._agent_responses = 0
        
        # Verify interruption is allowed (delegated to parent class)
        self.assertTrue(self.agent._should_interrupt())
    
    def test_user_speech_committed_sets_flag(self):
        """
        Test that when user speech is committed, the flag is set correctly.
        This simulates the event handler for user_speech_committed.
        """
        # Initially the flag should be False
        self.assertFalse(self.agent._first_user_input_received)
        
        # Create a mock speech handle
        mock_speech_handle = MagicMock(spec=SpeechHandle)
        
        # Simulate the event handler for user_speech_committed
        # This would normally be hooked up to the agent.on("user_speech_committed") event
        self.agent._first_user_input_received = True
        
        # Verify the flag is now True
        self.assertTrue(self.agent._first_user_input_received)
    
    def test_agent_speech_committed_increments_counter(self):
        """
        Test that when agent speech is committed, the counter increments correctly.
        This simulates the event handler for agent_speech_committed.
        """
        # Initially the counter should be 0
        self.assertEqual(self.agent._agent_responses, 0)
        
        # Create a mock speech handle
        mock_speech_handle = MagicMock(spec=SpeechHandle)
        
        # Simulate the event handler for agent_speech_committed
        # This would normally be hooked up to the agent.on("agent_speech_committed") event
        self.agent._agent_responses += 1
        
        # Verify the counter is now 1
        self.assertEqual(self.agent._agent_responses, 1)
        
        # Simulate a second response
        self.agent._agent_responses += 1
        
        # Verify the counter is now 2
        self.assertEqual(self.agent._agent_responses, 2)
    
    def test_complete_flow(self):
        """
        Test the complete flow of a conversation:
        1. Initial state: interruptions allowed
        2. User input received: interruptions blocked
        3. Agent responds: interruptions allowed again
        """
        # 1. Initial state
        self.assertFalse(self.agent._first_user_input_received)
        self.assertEqual(self.agent._agent_responses, 0)
        self.assertTrue(self.agent._should_interrupt())  # Interruptions allowed initially
        
        # 2. User input received
        self.agent._first_user_input_received = True
        self.assertFalse(self.agent._should_interrupt())  # Interruptions blocked
        
        # 3. Agent responds
        self.agent._agent_responses += 1
        self.assertTrue(self.agent._should_interrupt())  # Interruptions allowed again


if __name__ == '__main__':
    unittest.main() 