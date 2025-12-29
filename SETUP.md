# Notion → GitHub Sync: Setup Guide

This guide will help you set up automatic synchronization from your Notion workspace to a GitHub repository.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Create Notion Integration](#step-1-create-notion-integration)
3. [Step 2: Get Your Notion Page ID](#step-2-get-your-notion-page-id)
4. [Step 3: Configure Environment](#step-3-configure-environment)
5. [Step 4: Install Dependencies](#step-4-install-dependencies)
6. [Step 5: Run Your First Sync](#step-5-run-your-first-sync)
7. [Step 6: Set Up GitHub Repository](#step-6-set-up-github-repository)
8. [Step 7: Enable Automatic Sync](#step-7-enable-automatic-sync)
9. [CLI Reference](#cli-reference)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Python 3.11+** installed
- **Git** installed
- **Notion account** with pages you want to sync
- **GitHub account** (for automatic sync)

---

## Step 1: Create Notion Integration

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)

2. Click **"+ New integration"**

3. Configure your integration:
   - **Name:** `GitHub Sync` (or any name you prefer)
   - **Associated workspace:** Select your workspace
   - **Capabilities:**
     - ✅ Read content
     - ✅ Read user information (optional)
     - ❌ Update content (not needed)
     - ❌ Insert content (not needed)

4. Click **"Submit"**

5. Copy the **Internal Integration Token** (starts with `secret_`)
   
   ⚠️ **Keep this token secure! Never commit it to git.**

6. **Connect the integration to your pages:**
   - Open your "Tech Notes" page in Notion
   - Click the `•••` menu (top right)
   - Select "Connections" → "Connect to" → Select your integration
   - **Important:** The integration needs access to the parent page AND all child pages

---

## Step 2: Get Your Notion Page ID

1. Open your **"Tech Notes"** page in Notion

2. Click **"Share"** (top right)

3. Click **"Copy link"**

4. The URL will look like:
   ```
   https://www.notion.so/Tech-Notes-abc123def456789...
   ```

5. The **Page ID** is the part after the page name:
   ```
   abc123def456789...
   ```
   
   It's a 32-character hexadecimal string (may include dashes).

---

## Step 3: Configure Environment

1. Create your `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```bash
   # Required
   NOTION_TOKEN=secret_your_token_here
   NOTION_PARENT_PAGE_ID=abc123def456789...
   
   # Optional (for local git commits)
   GIT_USER_NAME=Your Name
   GIT_USER_EMAIL=your.email@example.com
   ```

---

## Step 4: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Step 5: Run Your First Sync

Test the sync locally:

```bash
# Preview what will happen (no changes made)
python sync.py --dry-run

# Run actual sync (local only, no push)
python sync.py --no-push

# Run full sync with push to GitHub
python sync.py
```

After running, you should see:
- Topic directories created (e.g., `linux/`, `docker/`, `kubernetes/`)
- Each directory contains a `README.md` with your Notion content
- Images downloaded to `<topic>/images/`
- Root `README.md` with an index of all topics

---

## Step 6: Set Up GitHub Repository

### Option A: Push to Existing Repository

```bash
# Initialize git (if not already done)
git init

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Run sync and push
python sync.py
```

### Option B: Create New Repository

1. Create a new repository on GitHub (without README)

2. Initialize and push:
   ```bash
   git init
   git remote add origin https://github.com/YOUR_USERNAME/tech-notes.git
   python sync.py
   ```

---

## Step 7: Enable Automatic Sync

### Add Secrets to GitHub

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add two secrets:
   - **`NOTION_TOKEN`**: Your Notion integration token
   - **`NOTION_PARENT_PAGE_ID`**: Your Tech Notes page ID

### Verify Workflow

The sync workflow (`.github/workflows/sync.yml`) will:
- Run automatically every 6 hours
- Can be triggered manually from GitHub Actions tab
- Can be triggered via API

To manually trigger:
1. Go to **Actions** tab in your repository
2. Select **"Sync Notion to GitHub"**
3. Click **"Run workflow"**

---

## CLI Reference

### Basic Commands

```bash
# Run full sync
python sync.py

# Run sync without pushing to remote
python sync.py --no-push

# Force sync all pages (ignore change detection)
python sync.py --force

# Preview changes without committing
python sync.py --dry-run

# Enable debug output
python sync.py --debug

# Show sync status
python sync.py status

# Remove all synced content
python sync.py clean
```

### Command Options

| Option | Description |
|--------|-------------|
| `--no-push` | Sync and commit locally, but don't push to remote |
| `--force` | Sync all pages regardless of last edit time |
| `--dry-run` | Preview changes without making any commits |
| `--debug` | Show detailed debug information |

### Subcommands

| Command | Description |
|---------|-------------|
| `status` | Show current sync status and last sync time |
| `clean` | Remove all synced content and reset state |
| `version` | Show version information |

---

## Example Commit Messages

The system generates semantic commit messages automatically:

```
# Single page, initial sync
docs(linux): initial sync

# Single page, content update
docs(docker): update container networking section

# Single page, new images
docs(kubernetes): add deployment diagrams

# Multiple pages changed
docs: sync updates across 3 topics

Updated: docker, kubernetes, linux

# Initial sync of entire workspace
docs: initial sync of 8 topics

Topics: aws, docker, git-github, jenkins, kubernetes, linux, spring-boot, ssh-secure-shell
```

---

## Troubleshooting

### "NOTION_TOKEN environment variable is required"

Make sure you:
1. Created the `.env` file (copy from `.env.example`)
2. Added your Notion token to the file
3. The token starts with `secret_`

### "No pages found under the parent page"

The integration doesn't have access to your pages:
1. Open your Tech Notes page in Notion
2. Click `•••` → "Connections" → Your integration
3. Ensure the integration is connected

### "API Error 401: Unauthorized"

Your token is invalid or expired:
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Select your integration
3. Regenerate the token
4. Update your `.env` file

### Images Not Downloading

- External image URLs may expire or be blocked
- Notion-hosted images require authentication
- Check network connectivity

### Git Push Fails

- Ensure you have a remote configured: `git remote -v`
- Check you have push access to the repository
- For GitHub Actions, ensure `GITHUB_TOKEN` has write permissions

---

## Repository Structure

After syncing, your repository will look like:

```
tech-notes/
├── README.md                    # Auto-generated index
├── linux/
│   ├── README.md               # Synced content
│   └── images/                 # Downloaded images
├── ssh-secure-shell/
│   ├── README.md
│   └── images/
├── git-github/
│   ├── README.md
│   └── images/
├── aws/
│   ├── README.md
│   └── images/
├── docker/
│   ├── README.md
│   └── images/
├── kubernetes/
│   ├── README.md
│   └── images/
├── jenkins/
│   ├── README.md
│   └── images/
├── spring-boot/
│   ├── README.md
│   └── images/
├── .notion-sync/               # Sync tooling
│   └── state.json              # Sync state
├── .github/
│   └── workflows/
│       └── sync.yml            # GitHub Actions
├── .env.example
├── .gitignore
├── requirements.txt
├── sync.py
└── SETUP.md                    # This file
```

---

## Security Best Practices

1. **Never commit `.env`** - It's in `.gitignore` for a reason
2. **Use GitHub Secrets** - For automated workflows
3. **Rotate tokens periodically** - Update your Notion token regularly
4. **Review permissions** - Only grant necessary access to integrations

---

## Future Improvements

Potential enhancements you might consider:

- [ ] Notion webhooks (when available in API)
- [ ] Bidirectional sync (GitHub → Notion)
- [ ] GitHub Pages deployment
- [ ] Slack/Discord notifications
- [ ] Custom page mappings via config file
- [ ] Multiple Notion workspaces

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Run with `--debug` flag for more information
3. Check Notion API status: [status.notion.so](https://status.notion.so)

---

*Happy syncing! 🚀*
