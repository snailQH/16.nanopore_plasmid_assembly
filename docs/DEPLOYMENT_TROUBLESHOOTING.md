# Deployment Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Jump Host Authentication Failed

**Error**: `root@8.133.18.117: Permission denied (publickey,password)`

**Cause**: The jump host requires authentication, but the GitHub Actions runner doesn't have the necessary credentials.

**Solutions**:

#### Option A: Configure Jump Host Key (Recommended)

If the jump host requires SSH key authentication:

1. Generate a separate SSH key for the jump host:
   ```bash
   ssh-keygen -t ed25519 -C "github-actions-jump-host" -f ~/.ssh/jump_host_key
   ```

2. Add the public key to the jump host:
   ```bash
   ssh-copy-id -i ~/.ssh/jump_host_key.pub root@8.133.18.117
   ```

3. Add the jump host private key to GitHub Secrets:
   - Go to GitHub repository → Settings → Secrets → Actions
   - Add new secret: `SSH_JUMP_HOST_KEY`
   - Value: Contents of `~/.ssh/jump_host_key` (private key)

4. Update the workflow to use both keys (see below)

#### Option B: Use Password Authentication (Less Secure)

If the jump host allows password authentication, you can use `sshpass`:

1. Add jump host password to GitHub Secrets: `SSH_JUMP_HOST_PASSWORD`
2. Install `sshpass` in the workflow
3. Use password authentication for jump host

### Issue 2: SSH Config File Not Found

**Error**: `Can't open user config file ~/.ssh/config: No such file or directory`

**Solution**: The workflow now uses absolute paths (`$HOME/.ssh/config`) to ensure the file is found.

### Issue 3: Target Server Connection Failed

**Error**: Connection to target server fails even though jump host works

**Possible Causes**:
1. Target server host key not in known_hosts
2. SSH key not authorized on target server
3. Port forwarding issue through jump host

**Solutions**:
1. Verify SSH key is added to target server:
   ```bash
   ssh -J root@8.133.18.117 qinghuili@localhost -p 2223 "echo 'Test'"
   ```

2. Check if the key is in `~/.ssh/authorized_keys` on target server:
   ```bash
   ssh -J root@8.133.18.117 qinghuili@localhost -p 2223 "cat ~/.ssh/authorized_keys"
   ```

## Updated Workflow for Jump Host Key

If you need to use a separate key for the jump host, update the workflow:

```yaml
- name: Setup SSH
  run: |
    SSH_DIR="$HOME/.ssh"
    mkdir -p "$SSH_DIR"
    chmod 700 "$SSH_DIR"
    
    # Save target server SSH private key
    echo "${{ secrets.SSH_PRIVATE_KEY }}" > "$SSH_DIR/deploy_key"
    chmod 600 "$SSH_DIR/deploy_key"
    
    # Save jump host SSH private key (if separate)
    echo "${{ secrets.SSH_JUMP_HOST_KEY }}" > "$SSH_DIR/jump_host_key"
    chmod 600 "$SSH_DIR/jump_host_key"
    
    # Create SSH config
    cat > "$SSH_DIR/config" << 'EOF'
    Host jump-host
      HostName 8.133.18.117
      User root
      StrictHostKeyChecking no
      IdentityFile ~/.ssh/jump_host_key
    
    Host target-server
      HostName localhost
      Port 2223
      User qinghuili
      ProxyJump jump-host
      StrictHostKeyChecking no
      IdentityFile ~/.ssh/deploy_key
    EOF
    chmod 600 "$SSH_DIR/config"
```

## Testing SSH Connection Locally

Before deploying, test the SSH connection locally:

```bash
# Test jump host connection
ssh -i ~/.ssh/id_ed25519 root@8.133.18.117 "echo 'Jump host OK'"

# Test target server through jump host
ssh -i ~/.ssh/id_ed25519 -J root@8.133.18.117 qinghuili@localhost -p 2223 "echo 'Target server OK'"

# Test rsync through jump host
rsync -avz -e "ssh -J root@8.133.18.117" \
  --dry-run \
  ./ qinghuili@localhost:/Users/qinghuili/AmpSeq/repository/16.nanopore_plasmid_assembly/
```

## Debugging GitHub Actions

To debug deployment issues:

1. Check GitHub Actions logs for detailed error messages
2. Enable verbose SSH logging in the workflow:
   ```yaml
   ssh -vvv -F "$SSH_CONFIG" target-server "echo 'Test'"
   ```
3. Test each step separately:
   - Test jump host connection
   - Test target server connection
   - Test rsync

## Current Configuration

The current workflow assumes:
- Jump host (`root@8.133.18.117`) allows password authentication OR uses the same SSH key
- Target server (`qinghuili@localhost:2223`) uses the SSH key from `SSH_PRIVATE_KEY` secret
- Both hosts are accessible from GitHub Actions runners

If your setup differs, please update the workflow accordingly.

---

**Last Updated**: 2025-12-04

