## Publish to Gitea Wiki

There are two simple ways to push this `wiki/` content to your Gitea wiki repository.

### 0) Enable Wiki in Gitea
In your repository settings on Gitea, ensure the Wiki feature is enabled. Note the wiki Git URL, typically:
`https://<gitea-host>/<owner>/<repo>.wiki.git`

### Option A: Use `wiki/` as a standalone Git repo
This treats `wiki/` as its own repository and pushes directly to the Gitea wiki remote.

```bash
cd wiki
git init
git add .
git commit -m "Initial NutriCoach wiki"
git branch -M master   # or: git branch -M main (if your Gitea wiki uses main)
git remote add origin https://<gitea-host>/<owner>/<repo>.wiki.git
git push -u origin master
# If default branch is main instead of master:
# git push -u origin HEAD:main
```

### Option B: Clone the wiki repo and copy files in
Useful if you prefer not to nest a Git repo under `wiki/`.

```bash
# From project root
git clone https://<gitea-host>/<owner>/<repo>.wiki.git wiki-publish

# Copy (Linux/macOS):
rsync -av --delete wiki/ wiki-publish/

# Copy (Windows PowerShell):
robocopy wiki wiki-publish /MIR

cd wiki-publish
git add .
git commit -m "Initial NutriCoach wiki"
git push
```

### Verify
- Visit the repo’s Wiki tab in Gitea.
- The sidebar should list pages like Home, Getting-Started, Architecture, API, Deployment, etc.

### Updating later
- Edit files under `wiki/` locally and repeat the push steps, or edit wiki pages directly in Gitea’s web UI.

