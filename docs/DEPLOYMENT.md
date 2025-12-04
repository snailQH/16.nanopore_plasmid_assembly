# Deployment Guide

This document describes how to set up automatic deployment from GitHub to the remote server.

## GitHub Actions Deployment

The project includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that automatically deploys code to the remote server when changes are pushed to the `main` branch.

## Setup Instructions

### Step 1: Generate SSH Key Pair

On your local machine, generate an SSH key pair for deployment (if you don't already have one):

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key
```

This creates:
- `~/.ssh/github_deploy_key` (private key)
- `~/.ssh/github_deploy_key.pub` (public key)

### Step 2: Add Public Key to Remote Server

Copy the public key to the remote server:

```bash
# Copy public key to remote server
ssh-copy-id -i ~/.ssh/github_deploy_key.pub \
  -o "ProxyJump root@8.133.18.117" \
  -p 2223 \
  qinghuili@localhost
```

Or manually add it:

```bash
# View public key
cat ~/.ssh/github_deploy_key.pub

# SSH to remote server and add to authorized_keys
ssh -J root@8.133.18.117 qinghuili@localhost -p 2223
mkdir -p ~/.ssh
echo "YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Step 3: Add Private Key to GitHub Secrets

1. Go to your GitHub repository: `https://github.com/snailQH/16.nanopore_plasmid_assembly`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `SSH_PRIVATE_KEY`
5. Value: Copy the entire contents of `~/.ssh/github_deploy_key` (the private key)
6. Click **Add secret**

### Step 4: Verify Deployment

After pushing to the `main` branch, check the GitHub Actions tab to see the deployment status:

1. Go to **Actions** tab in your GitHub repository
2. Click on the latest workflow run
3. Check if the deployment completed successfully

## Manual Deployment

If you need to deploy manually without GitHub Actions:

```bash
cd /Users/liqinghui/AmpSeq/00.workflows/pipelines/16.nanopore_plasmid_assembly

# Sync files to remote server
rsync -avz --delete \
  -e "ssh -J root@8.133.18.117 -p 2223" \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '*.log' \
  --exclude 'output/' \
  --exclude 'results/' \
  ./ qinghuili@localhost:/Users/qinghuili/AmpSeq/repository/16.nanopore_plasmid_assembly/

# Set permissions
ssh -J root@8.133.18.117 qinghuili@localhost -p 2223 \
  "chmod +x /Users/qinghuili/AmpSeq/repository/16.nanopore_plasmid_assembly/run_pipeline.sh"
```

## Deployment Configuration

The deployment workflow:
- **Triggers**: On push to `main` branch or manual trigger
- **Target Server**: `qinghuili@localhost:2223` (via jump host `root@8.133.18.117`)
- **Deployment Path**: `/Users/qinghuili/AmpSeq/repository/16.nanopore_plasmid_assembly`
- **Excluded Files**: Logs, output directories, temporary files, Python cache files

## Troubleshooting

### Deployment Fails with SSH Authentication Error

1. Verify the SSH key is correctly added to GitHub Secrets
2. Check that the public key is in `~/.ssh/authorized_keys` on the remote server
3. Test SSH connection manually:
   ```bash
   ssh -i ~/.ssh/github_deploy_key \
     -o ProxyJump=root@8.133.18.117 \
     -p 2223 \
     qinghuili@localhost
   ```

### Files Not Syncing

1. Check GitHub Actions logs for specific errors
2. Verify the deployment path exists on the remote server
3. Check file permissions on the remote server

### Permission Denied Errors

Ensure the remote user has write permissions to the deployment directory:
```bash
ssh -J root@8.133.18.117 qinghuili@localhost -p 2223 \
  "mkdir -p /Users/qinghuili/AmpSeq/repository/16.nanopore_plasmid_assembly && \
   chmod -R 755 /Users/qinghuili/AmpSeq/repository/16.nanopore_plasmid_assembly"
```

---

**Last Updated**: 2025-12-04  
**Pipeline Version**: 1.0

