# GitHub Secrets Setup Guide

## SSH_PRIVATE_KEY Configuration

When adding the SSH private key to GitHub Secrets, it's important to copy the **entire** key file content, including:

- The header line: `-----BEGIN OPENSSH PRIVATE KEY-----`
- All the key data lines
- The footer line: `-----END OPENSSH PRIVATE KEY-----`
- **All newlines** (line breaks)

## How to Copy SSH Key Correctly

### Method 1: Using `cat` (Recommended)

```bash
# Display the entire key
cat ~/.ssh/id_ed25519

# Copy the entire output (including BEGIN/END lines and all content)
# Paste it into GitHub Secrets → SSH_PRIVATE_KEY
```

### Method 2: Using `pbcopy` (macOS)

```bash
# Copy key to clipboard
cat ~/.ssh/id_ed25519 | pbcopy

# Then paste into GitHub Secrets
```

### Method 3: Manual Copy

1. Open the key file:
   ```bash
   cat ~/.ssh/id_ed25519
   ```

2. Copy **everything** including:
   - `-----BEGIN OPENSSH PRIVATE KEY-----`
   - All lines of encoded data
   - `-----END OPENSSH PRIVATE KEY-----`

3. Paste into GitHub Secrets → `SSH_PRIVATE_KEY`

## Common Mistakes

### ❌ Wrong: Copying only part of the key
Only copying the encoded data without the BEGIN/END headers.

### ✅ Correct: Copying the entire key with headers
Copy everything from `-----BEGIN OPENSSH PRIVATE KEY-----` to `-----END OPENSSH PRIVATE KEY-----`, including all newlines.

## Verification Steps

After adding the secret to GitHub:

1. **Check the secret exists**:
   - Go to: `https://github.com/snailQH/16.nanopore_plasmid_assembly/settings/secrets/actions`
   - Verify `SSH_PRIVATE_KEY` is listed

2. **Test locally** (to ensure key works):
   ```bash
   # Test connection to target server
   ssh -i ~/.ssh/id_ed25519 -J root@8.133.18.117 qinghuili@localhost -p 2223 "echo 'Test'"
   ```

3. **Check GitHub Actions logs**:
   - After workflow runs, check if key format error appears
   - Look for: "SSH key format is valid" message

## Troubleshooting

### Error: "Load key: error in libcrypto"

**Cause**: SSH key format is incorrect or corrupted.

**Solution**:
1. Re-copy the entire key file (including BEGIN/END lines)
2. Ensure no extra spaces or characters were added
3. Ensure all newlines are preserved
4. Update the GitHub Secret

### Error: "Permission denied"

**Possible causes**:
1. Key not authorized on target server
2. Wrong key format
3. Key permissions issue

**Solutions**:
1. Verify key is in `~/.ssh/authorized_keys` on target server:
   ```bash
   ssh -J root@8.133.18.117 qinghuili@localhost -p 2223 "cat ~/.ssh/authorized_keys"
   ```

2. Re-add the public key to target server:
   ```bash
   ssh-copy-id -i ~/.ssh/id_ed25519.pub -o "ProxyJump root@8.133.18.117" -p 2223 qinghuili@localhost
   ```

3. Check key format in GitHub Secrets (should start with `-----BEGIN`)

## Key Format Requirements

The SSH private key must:
- Start with `-----BEGIN OPENSSH PRIVATE KEY-----`
- End with `-----END OPENSSH PRIVATE KEY-----`
- Contain all encoded data lines between headers
- Preserve all newlines (line breaks)
- Be in OpenSSH format (not PEM format)

## Example: Complete Key Format

Your SSH private key should look like this (with your actual key data):

```
-----BEGIN OPENSSH PRIVATE KEY-----
[Base64 encoded key data - multiple lines]
[More base64 encoded data]
...
-----END OPENSSH PRIVATE KEY-----
```

**Important**: 
- Replace `[Base64 encoded key data]` with your actual key content
- Your actual key will be much longer (typically 5-10 lines of base64 data)
- Make sure to include the BEGIN and END lines
- Preserve all newlines when copying

---

**Last Updated**: 2025-12-04

