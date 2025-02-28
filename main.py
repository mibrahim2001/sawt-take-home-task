#!/usr/bin/env python3
"""
Main entry point for the NoInterruptFirstResponseAgent
"""

from src.agent import cli, WorkerOptions, entrypoint, prewarm

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    ) 