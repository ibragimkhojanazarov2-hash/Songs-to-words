# Welcome to FRP AI Engineering

> **Say hello first!** Write on Telegram to Vladimir **@vladimir_albrekht_ccr** (https://t.me/vladimir_albrekht_ccr)
> or to Arailym **@vrvilyw** (https://t.me/vrvilyw).
> Send your **first name** and your workspace ID: **s22**. This is how we stay in touch all week.

## Your folders

| Folder | What is in it |
|---|---|
| `projects/` | **Your projects**, one folder each. Everything you save here stays. |
| `materials/` | Project ideas (IDEAS.md), how to share a page (DEPLOY.md), the agent's skills (skills/, SKILLS.md), class guides (TRACKS.md: your track), files of each day. |

## Talk to the AI agent

1. The terminal is at the bottom of the window. OpenCode starts there by itself (if not, type `opencode` and press Enter).
2. Need a second terminal (for example for your page)? Click **+** at the top right of the terminal.
3. Write what you want to build, for example:
   "Make a single-file index.html: a cat facts page with a button that shows a random cat fact."

To leave OpenCode, press Ctrl+C.

## See your page

1. In a terminal, type `cd ~/work && frp-serve 8000` and press Enter. Keep this terminal open. It prints your links.
2. Open https://kitan-a.com/frp/s22/proxy/8000/projects/ in a new browser tab, then your project folder.
3. To stop the server, press Ctrl+C in that terminal. (Your agent can start it in the background with `frp-serve --bg 8000`.)

## Share your page with anyone

Your workspace links need your login. To share a finished page (a classmate, your family, a phone, Demo Day):

```
frp-publish projects/my-page
```

It prints a public link like https://kitan-a.com/frp/pub/s22/my-page/ . Run it again after every change.
More (Flask apps, problems): `materials/DEPLOY.md`.

## Extra

- The agent with browser tools (it can open and click your page itself): type `opencode-mcp` instead of `opencode`.
- The internet works here: `pip install`, `npm install` and `git` are allowed.

## How to work with the agent: step by step

Start the agent: type `opencode` in the terminal. Then use these commands in this order (type `/` to see them):

| Step | Type | What happens |
|---|---|---|
| 1 | `/ask a quiz game about space` | The agent asks you up to 5 questions. Answer them. |
| 1b | `/tasks` | Once per project: your tasks for the whole week in TASKS.md (see materials/TRACKS.md). Show them to your mentor. |
| 2 | `/plan` | It writes the clear task (goal, input, how to check, limits) and a short plan. No code yet. Change what is wrong, then say OK. |
| 3 | `/build` | It builds only the next small step and tells you what to click. |
| 4 | `/check` | It tests its own work and shows you proof. Then **you** open the page and click it too. |
| 5 | `/fix the button does nothing` | When something is wrong: say what you saw or paste the red error. |
| 6 | `/save` | A git checkpoint. If a later step breaks things, you can go back. |
| share | `/share` | A public link to your page that anyone can open (no login). Type it again after changes. |
| next | `/plan task 2` | When a task is done: the plan for the next task in TASKS.md, then `/build` again. |

Then repeat 3 → 4 → 6 for the next step of the plan. Steps 1 and 2 use the "plan" agent, which cannot change files.

## GitHub and Hugging Face

See `materials/GITHUB.md` (GitHub) and `materials/GUIDE-github-hf.md` (Hugging Face).
