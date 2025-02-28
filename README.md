<a href="https://livekit.io/">
  <img src="./.github/assets/livekit-mark.png" alt="LiveKit logo" width="100" height="100">
</a>

# No-Interrupt First Response Voice Agent

<p>
  <a href="https://cloud.livekit.io/projects/p_/sandbox"><strong>Deploy a sandbox app</strong></a>
  •
  <a href="https://docs.livekit.io/agents/overview/">LiveKit Agents Docs</a>
  •
  <a href="https://livekit.io/cloud">LiveKit Cloud</a>
  •
  <a href="https://blog.livekit.io/">Blog</a>
</p>

A specialized voice agent implementation using LiveKit Agents that prevents interruptions during the agent's first response to improve conversation flow.

## Overview

This project addresses the issue of users interrupting an agent before it can respond to their first input. Such interruptions can cause significant delays in conversation flow, increasing response times from 1.5 seconds to over 5 seconds.

### Solution Architecture

The implementation is based on LiveKit's VoicePipelineAgent with customizations to:

1. Ignore all user interruptions after the first user input until the agent has fully spoken its first response
2. Resume normal interruption behavior after the first response is completed
3. Minimize any additional latency in the system

## Project Structure

```
/
├── src/                     # Source code directory
│   ├── __init__.py          # Package definition
│   ├── no_interrupt_agent.py # Custom agent implementation
│   └── agent.py             # Main agent application logic
├── tests/                   # Test directory
│   ├── __init__.py          # Test package definition
│   ├── test_no_interrupt_agent.py  # Tests for the custom agent
│   └── run_tests.py         # Test runner script
├── main.py                  # Entry point script
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

## Implementation Details

### Custom Agent Class

The solution introduces a custom `NoInterruptFirstResponseAgent` class that extends the standard `VoicePipelineAgent`. This class tracks the state of the conversation using two key variables:

- `_first_user_input_received`: Flags whether the user has provided their first input
- `_agent_responses`: Counts how many responses the agent has delivered

### Key Components

1. **Interruption Control**:
   - Overrides the `_should_interrupt` method to prevent interruptions specifically during the first response cycle
   - All subsequent interactions allow interruptions as per normal behavior

2. **Event Tracking**:
   - Uses event handlers to track user speech and agent speech events
   - Updates state variables to ensure proper transition from non-interruptible to interruptible states

3. **Timing Management**:
   - Maintains default endpointing delays for turn detection (0.5s min, 5.0s max)
   - No additional timing overhead introduced in the critical path

## Handling Edge Cases

The implementation accounts for several important edge cases:

1. **Initial Greeting**: The agent's initial greeting (before any user input) is not counted as the "first response" - only responses after the user's first input count
   
2. **Multiple Interruptions**: All interruption attempts during the first response cycle are consistently ignored

3. **Error Recovery**: If errors occur during processing (STT, LLM, or TTS), the agent response counter still increments properly to ensure the system can transition to normal behavior

4. **Pipeline Timing**: The solution preserves the natural flow of STT → LLM → TTS without introducing unnecessary delays

## Assumptions

The implementation makes the following assumptions:

1. The first user input is defined as the first time a user's speech is committed to the agent
   
2. The agent's first response is defined as the first agent speech committed after receiving the first user input
   
3. The initial greeting from the agent (before any user input) is not considered part of the first response cycle

4. The LiveKit turn detection system provides appropriate natural pause detection

## Testing

The implementation includes a comprehensive test suite to verify the interruption handling logic:

### Test Suite Coverage

- **Basic State Verification**: Tests that agent state variables are initialized correctly
- **Interruption Logic**: Tests that interruptions are blocked during first response but allowed otherwise
- **Event Handling**: Tests that event handlers correctly update agent state
- **Complete Flow**: Tests the full conversation flow from initial state through first response

### Running Tests

To run the tests:

```console
# From the project root
./tests/run_tests.py

# Or using Python directly
python -m tests.run_tests
```

All tests are isolated using mocking to avoid dependencies on the LiveKit infrastructure.

## Dev Setup

Clone the repository and install dependencies to a virtual environment:

```console
# Linux/macOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

<details>
  <summary>Windows instructions (click to expand)</summary>
  
```cmd
:: Windows (CMD/PowerShell)
python3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
</details>


Set up the environment by copying `.env.example` to `.env.local` and filling in the required values:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `OPENAI_API_KEY`
- `DEEPGRAM_API_KEY`

You can also do this automatically using the LiveKit CLI:

```console
lk app env
```

Run the agent:

```console
# From the project root
./main.py dev

# Or using Python directly
python main.py dev
```

This agent requires a frontend application to communicate with. You can use one of the example frontends in [livekit-examples](https://github.com/livekit-examples/), create your own following one of the [client quickstarts](https://docs.livekit.io/realtime/quickstarts/), or test instantly against one of the hosted [Sandbox](https://cloud.livekit.io/projects/p_/sandbox) frontends.
