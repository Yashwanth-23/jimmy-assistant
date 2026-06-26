"""
Antigravity Bridge — Spawns a Google Antigravity SDK agent in a background thread.

Used by Jimmy/Sammy to autonomously build software via voice commands.
"""

import asyncio
import logging
import threading

from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig

log = logging.getLogger("jimmy.antigravity")


def spawn_agent_background(feature_request: str, model_id: str, workspace_dir: str, on_complete=None):
    """Spawn an Antigravity agent in a background thread so the assistant isn't blocked."""
    def _run():
        asyncio.run(_async_spawn(feature_request, model_id, workspace_dir))
        if on_complete:
            on_complete()

    threading.Thread(target=_run, daemon=True).start()


async def _async_spawn(feature_request: str, model_id: str, workspace_dir: str):
    """Connect to the Antigravity SDK, send the prompt, and stream the response."""
    log.info("Spawning Antigravity Agent [%s] in %s...", model_id, workspace_dir)

    config = LocalAgentConfig(
        model=model_id,
        workspaces=[workspace_dir],
        system_instructions=(
            f"You are an expert autonomous developer. "
            f"You MUST write all code and files inside the {workspace_dir} directory. "
            f"Complete the user's feature request."
        ),
        capabilities=CapabilitiesConfig(),
    )

    try:
        async with Agent(config) as agent:
            log.info("Agent connected. Sending prompt...")
            response = await agent.chat(feature_request)

            full_response = ""
            async for token in response:
                full_response += token

            log.info("Agent finished execution. Response length: %d", len(full_response))
    except Exception as e:
        log.error("Error during agent execution: %s", e)
