# How to Upload Domain Checker to GitHub

Step-by-step guide to push this project to your GitHub account.

---

## Step 1: Install Git (if not already)

Download from: https://git-scm.com/downloads

After installing, open **Command Prompt** or **PowerShell** and verify:

```bash
git --version
```

## Step 2: Create GitHub Repository

1. Go to **https://github.com/new**
2. Fill in:
   - **Repository name:** `domain-checker` (or whatever you prefer)
   - **Description:** `Multi-TLD domain availability checker — WHOIS/RDAP + DNS + HTTP matrix view`
   - **Visibility:** Public (so others can find and star it)
   - **DO NOT** check "Add a README" (we already have one)
   - **DO NOT** check "Add .gitignore" (we already have one)
   - **DO NOT** check "Choose a license" (we already have one)
3. Click **Create repository**
4. You'll see a page with push instructions — keep this tab open

## Step 3: Set Up Your Project Folder

Create a folder on your PC and put all the files in it:

```
C:\Users\SECURITY-BREACH\Projects\domain-checker\
    domain_checker.py       <-- The main script
    domains_v3.txt          <-- Sample domain list
    README.md               <-- Documentation
    CHANGELOG.md            <-- Version history
    LICENSE                 <-- MIT License
    .gitignore              <-- Git ignore rules
```

## Step 4: Initialize Git and Push

Open **Command Prompt** in your project folder:

```bash
cd C:\Users\SECURITY-BREACH\Projects\domain-checker

# Initialize git
git init

# Add all files
git add .

# Verify what's being committed
git status

# Create first commit
git commit -m "feat: Domain Availability Checker v3.0 - Multi-TLD matrix"

# Connect to your GitHub repo (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/domain-checker.git

# Set main branch
git branch -M main

# Push!
git push -u origin main
```

If git asks for authentication, you need a **Personal Access Token**:

1. Go to https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Give it a name like "domain-checker push"
4. Check the **repo** scope
5. Click **Generate token**
6. **Copy the token** (you won't see it again)
7. When git asks for password, paste this token instead

## Step 5: Verify

Go to `https://github.com/YOUR_USERNAME/domain-checker`

You should see all your files with the README rendered beautifully.

## Step 6: Create a Release (Optional but Recommended)

1. On your repo page, click **Releases** (right sidebar)
2. Click **Create a new release**
3. Fill in:
   - **Tag:** `v3.0.0`
   - **Release title:** `v3.0.0 - Multi-TLD Domain Checker`
   - **Description:** Copy the v3.0.0 section from CHANGELOG.md
4. Click **Publish release**

## Step 7: Add Topics for Discoverability

1. On your repo page, click the gear icon next to **About**
2. Add these topics:
   ```
   domain-checker, whois, rdap, dns, domain-availability, 
   domain-investing, cli-tool, python, terminal-app, 
   domain-search, tld, ai-domains
   ```
3. Add a short description
4. Click **Save changes**

---

## Updating the Repo Later

When you make changes to the code:

```bash
cd C:\Users\SECURITY-BREACH\Projects\domain-checker

# Check what changed
git status

# Add changes
git add .

# Commit with a descriptive message
git commit -m "fix: improved WHOIS timeout handling"

# Push to GitHub
git push
```

## Common Git Commands Reference

```bash
git status              # See what's changed
git add .               # Stage all changes
git add file.py         # Stage specific file
git commit -m "msg"     # Commit with message
git push                # Push to GitHub
git pull                # Pull latest from GitHub
git log --oneline       # View commit history
git diff                # See uncommitted changes
```

---

That's it! Your tool is now on GitHub for the world to see.
