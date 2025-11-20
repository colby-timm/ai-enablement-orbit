# Overview

As part of this Capstone project, I decided to use OpenSpec to design and track my specs. I used GH Copilot with Claude Sonnet 4.5 for implementing specs. Used a mix of Claude Sonnet 4.5 and GPT-5 for generating my specs.

## Findings

- First Spec (to setup the project) added tasks for follow-up tasks that the agent never did or checked off. These follow-up tasks are really other specs. I had to manually remove and create new specs for them.
- Possible improvement: Have specs create branches or worktrees. Don't do that automatically.
- Ensure you use the slash command `/openspec:apply {spec-name}` directly vs telling the agent to implement with the slash command.
- I continuously had hard times to get Copilot to do all the tasks. Had to reword my Agents.md file and `opencode-apply` slash command.
- It seems to only check off the tasks at the end, which doesn't inspire too much confidence that it did all of them. Definitely can modify the slash commands to improve this to ensure it goes one by one.

### What I liked

- Being able to view the completed changes and active changes with percent complete was helpful visually.
