# Deltecho Production Deployment Guide

This guide covers deploying the Deltecho cognitive AI ecosystem with the
full **Dove9-Dovecot integration** — the "Everything is a Chatbot" mail-as-IPC
architecture where Dovecot serves as the cognitive CPU and every email becomes
a process-thread in the Dove9 triadic loop.

---

## Architecture Overview

```
Internet / Local MUA
      │  IMAP(143) / IMAPS(993)
      ▼
┌─────────────┐   LMTP socket       ┌────────────────────────────┐
│   Dovecot   │ ──────────────────► │  Deep Tree Echo            │
│  mail server│ ◄────────────────── │  Orchestrator              │
└─────────────┘   Milter socket     │                            │
      │                             │  ┌──────────────────────┐  │
      │ IMAP (process-state query)  │  │ Dove9 Kernel         │  │
      └────────────────────────────►│  │ + TriadicEngine      │  │
                                    │  │ + Sys6MailScheduler  │  │
                                    │  └──────────────────────┘  │
                                    └────────────────────────────┘
```

### Port Map

| Port | Protocol | Purpose |
|------|----------|---------|
| 143  | IMAP     | Mail client access / process-state queries |
| 993  | IMAPS    | Encrypted IMAP |
| 24   | LMTP     | Local mail delivery to orchestrator |
| 3000 | HTTP     | Orchestrator webhook server |
| 9876 | TCP      | IPC server for desktop apps |

---

## Quick Start (Docker Compose)

### 1. Clone the repository

```bash
git clone https://github.com/ReZorg/delovecho.git
cd delovecho
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set at least:

```env
# LLM provider key (at least one required)
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...

# Security
ENCRYPTION_KEY=<32-byte hex string>

# Mail identity
BOT_EMAIL_ADDRESS=echo@yourdomain.com
MAIL_ALLOWED_DOMAINS=yourdomain.com

# Dovecot auth (production: use a real passdb driver)
DOVECOT_PASSDB_DRIVER=static
DOVECOT_PASSDB_ARGS=password=changeme
```

### 3. Start the full stack

```bash
# Core stack (Dovecot + Orchestrator)
docker compose up -d

# With Redis caching
docker compose --profile with-cache up -d

# With PostgreSQL persistence
docker compose --profile with-db up -d
```

### 4. Verify deployment

```bash
# Check service health
docker compose ps

# Tail orchestrator logs
docker compose logs -f deltecho

# Verify IMAP is reachable (plain; use port 993 only after enabling TLS)
nc -z localhost 143 && echo "IMAP OK"

# Check LMTP socket is shared
docker compose exec deltecho ls -la /var/run/dovecot/
```

---

## Configuration Reference

### Orchestrator environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_ENV` | `production` | Node.js environment |
| `LOG_LEVEL` | `info` | Log verbosity (`debug`/`info`/`warn`/`error`) |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `OPENROUTER_API_KEY` | — | OpenRouter API key |
| `ENCRYPTION_KEY` | — | 32-byte hex encryption key |
| `WEBHOOK_PORT` | `3000` | Webhook HTTP port |
| `IPC_TCP_PORT` | `9876` | IPC TCP port |
| `ENABLE_MEMORY_SYSTEM` | `true` | Enable RAG memory |
| `ENABLE_PERSONALITY_EVOLUTION` | `true` | Enable persona evolution |
| `ENABLE_EMOTIONAL_DYNAMICS` | `true` | Enable affective dynamics |
| `ENABLE_SECURITY_HARDENING` | `true` | Enable email sanitizer |
| `ENABLE_DOVE9` | `true` | Enable Dove9 cognitive loop |
| `ENABLE_DOVECOT` | `true` | Enable Dovecot mail interface |
| `DOVECOT_MILTER_SOCKET` | `/var/run/dovecot/milter.sock` | Milter Unix socket path |
| `DOVECOT_LMTP_SOCKET` | `/var/run/dovecot/lmtp.sock` | LMTP Unix socket path |
| `BOT_EMAIL_ADDRESS` | `echo@deltecho.local` | Bot's email address |
| `MAIL_ALLOWED_DOMAINS` | `*` | Comma-separated allowed sender domains |

### Dovecot configuration

Dovecot configuration files are located in `docker/dovecot/`:

| File | Purpose |
|------|---------|
| `dovecot.conf` | Main configuration |
| `conf.d/10-auth.conf` | Authentication backend |
| `conf.d/10-imap.conf` | IMAP service + mailbox layout |
| `conf.d/10-lmtp.conf` | LMTP delivery service |

For production, update `conf.d/10-auth.conf` to use a real authentication
backend (e.g., SQL or LDAP):

```
passdb {
  driver = sql
  args = /etc/dovecot/dovecot-sql.conf.ext
}
```

---

## Dove9-Dovecot Integration Details

### How mail becomes a cognitive process

1. An email arrives at Dovecot via SMTP/LMTP.
2. Dovecot delivers it to the orchestrator's LMTP listener (`/var/run/dovecot/lmtp.sock`).
3. `DovecotInterface` captures the `EmailMessage`.
4. `EmailSanitizer` validates and cleans the content (Phase 6 security hardening).
5. `MailRateLimiter` checks per-sender quotas (Phase 6 DoS protection).
6. `Dove9Integration.processEmail()` converts it to a `MessageProcess` via `MailProtocolBridge`.
7. `Dove9Kernel` places the process in the triadic cognitive engine.
8. Three concurrent streams at 120° phase offset process the message over 12 steps.
9. `Sys6MailScheduler` aligns processing with the 60-step grand cycle (LCM of Dove9's 12-step and Sys6's 30-step cycles).
10. `DeepTreeEchoProcessor` generates a response using LLM + RAG memory + persona.
11. The response is dispatched back as email via SMTP or DeltaChat.

### Mailbox → Process state mapping

| Mailbox | Dove9 ProcessState | Meaning |
|---------|-------------------|---------|
| `INBOX` | `PENDING` | Awaiting cognitive processing |
| `Processing` | `ACTIVE` | Triadic loop running |
| `Sent` | `COMPLETED` | Response dispatched |
| `Drafts` | `SUSPENDED` | Paused for human review |
| `Spam` | `FAILED` | Rejected by sanitizer/rate-limiter |
| `Trash` | `TERMINATED` | Discarded |

### Process state transitions via IMAP

You can query and manipulate process states directly through IMAP:

```bash
# Query active processes (emails in Processing mailbox)
openssl s_client -connect localhost:143 -quiet <<EOF
a LOGIN user password
b SELECT Processing
c FETCH 1:* (FLAGS ENVELOPE)
d LOGOUT
EOF
```

---

## Production Hardening Checklist

- [ ] Replace static Dovecot `passdb` with SQL/LDAP backend
- [ ] Enable TLS: set `ssl = required` in `dovecot.conf` and provide certificates
- [ ] Set a strong `ENCRYPTION_KEY` (32 bytes of random hex)
- [ ] Restrict `MAIL_ALLOWED_DOMAINS` to your own domain(s)
- [ ] Configure firewall rules to expose only required ports
- [ ] Mount `dovecot-mail` volume on durable storage
- [ ] Set `LOG_LEVEL=warn` in production to reduce noise
- [ ] Configure SMTP relay (Postfix or similar) for outbound mail
- [ ] Review `mail-rate-limiter` settings for your expected load
- [ ] Run `pnpm audit` before every deployment
- [ ] Enable Dependabot alerts on the repository

---

## Monitoring & Observability

### Health endpoints

```bash
# Orchestrator health
curl http://localhost:3000/health

# Dovecot log errors
docker compose exec dovecot doveadm log errors
```

### Telemetry

The orchestrator exposes mail processing metrics via the telemetry module:

```typescript
// Access from orchestrator
const metrics = orchestrator.getTelemetry();
// { mailProcessed, mailFailed, avgLatencyMs, rateLimit: { ... } }
```

### Log filtering

```bash
# All mail-related log lines
docker compose logs deltecho 2>&1 | grep -E "DovecotInterface|Dove9Integration|MailProtocol"

# Rate limiter events
docker compose logs deltecho 2>&1 | grep "Rate limit"

# Sanitizer actions
docker compose logs deltecho 2>&1 | grep "sanitized"
```

---

## Performance Benchmarks

Run the mail pipeline benchmarks to establish a baseline before deployment:

```bash
# Build packages first
pnpm build

# Run mail pipeline benchmarks
npx ts-node --esm benchmarks/mail-pipeline.bench.ts
```

Expected throughput on modern hardware:

| Pipeline stage | Expected throughput |
|---------------|-------------------|
| MailProtocolBridge.mailToProcess | > 50,000 ops/sec |
| MailProtocolBridge.processToMail | > 50,000 ops/sec |
| Bidirectional roundtrip | > 25,000 ops/sec |
| Dove9Kernel mail methods | > 1,000 ops/sec |
| Sys6MailScheduler.scheduleMailProcess | > 30,000 ops/sec |
| Sys6MailScheduler.advance (grand cycle) | > 500,000 ops/sec |
| OrchestratorBridge full pipeline | > 100 ops/sec (LLM-bound) |

---

## Troubleshooting

### Orchestrator cannot connect to Dovecot LMTP socket

```bash
# Verify socket exists and has correct permissions
docker compose exec deltecho ls -la /var/run/dovecot/
# Expected: lrwxrwxrwx or -rw-rw---- lmtp.sock

# Check Dovecot LMTP service is running
docker compose exec dovecot doveadm service status lmtp
```

### Rate limiter blocking legitimate traffic

Adjust the rate limiter configuration in orchestrator startup or via environment
variables. Default limits: 10 emails/minute per sender, burst of 3.

### Memory usage growing unbounded

The Dove9 kernel retains completed processes in memory by default. For
long-running deployments, enable process garbage collection:

```typescript
// In OrchestratorConfig
kernelConfig: {
  maxCompletedProcessAge: 3600_000, // 1 hour in ms
}
```
