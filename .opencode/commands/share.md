---
description: "Share: a public link to my page that anyone can open (frp-publish)"
agent: build
---
Make a public link to my page, so anyone can open it without my login (classmates, family, a phone, Demo Day).

1. Find the project folder: $ARGUMENTS if I wrote one, else the project we work on now (a folder in ~/work/projects/
   with an index.html). If there are several and you are not sure, ask me which one (one short question).
2. Check the page first: links, scripts and pictures must use relative paths (`js/main.js`, `./img/a.png`), not paths
   that start with `/`, and never `127.0.0.1`, `localhost` or `/proxy/`. Fix them with the smallest change.
3. In ~/work run: `frp-publish projects/<folder>`. It prints the public link `https://kitan-a.com/frp/pub/<id>/<folder>/`.
   If it prints a warning, read it, fix the cause, and run it again.
4. If the page needs a server (Python/Flask) or calls the AI model, the public link cannot run that part: read
   ~/work/materials/DEPLOY.md and tell me my options in 2 short lines (for example: save example answers in a file).
5. Answer in 2 lines: the public link, and "After each change, type /share again: the link stays the same."
   Do not start `frp-serve` for this: its links need my login.
