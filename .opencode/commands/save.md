---
description: "Step 5: save a checkpoint with git (and send it to GitHub)"
agent: build
---
Save our work with git in ~/work (the top folder, never a subfolder): if ~/work is not a git repository yet,
run `git init` there first. Then `git add -A` and
`git commit` with a short message that says what works now. Show me the commit line. Then, only if
`git remote get-url origin` works, run `git push` and show me its last line. If there is no remote yet, tell me to read materials/GITHUB.md, step 2. If the push fails because I am not
logged in, tell me to type `gh auth login -w -p https` in the terminal (see materials/GITHUB.md). $ARGUMENTS
