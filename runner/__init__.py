# runner/ — the task execution engine, kept SEPARATE from the server.
# Version 1 ships only echo_agent.py (a fake agent that echoes the task).
# Keeping this isolated means version 2 can swap in a real AI model
# without touching any API/routing code.
