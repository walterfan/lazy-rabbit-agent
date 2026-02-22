# CSMS Agent — Complete Guide

> **Audience**: Developers and SREs deploying, operating, and troubleshooting CSMS Agent.  
> **Doc purpose**: One-stop reference for deployment, upgrade, and troubleshooting.

---

## Overview

### What it is

**CSMS Agent** is a Go-based local HTTP service that:

- Retrieves secrets and public keys from **CSMS** (Centralized Secrets Management Service)
- Caches them locally
- Serves multiple application processes on the same host or pod

### Why it exists

Some languages and services use **ThinSDK**, which talks to the agent locally instead of calling the CSMS server directly. The agent centralizes and standardizes secret retrieval and rotation.

### At a glance

| Item | Value |
|------|-------|
| **Agent listen** | `127.0.0.1:7890` (recommended) |
| **Health** | `GET http://127.0.0.1:7890/agent/csms/healthcheck` |
| **Prometheus metrics** | `GET http://127.0.0.1:7890/metrics` |
| **CSMS prod** | `https://csms.zoom.us` |
| **CSMS dev** | `https://csmsdev.zoomdev.us` |

### Deployment modes

| Mode | Best for |
|------|----------|
| **DevOps platform / ZAgent** | VM/bare-metal fleets |
| **ZCP sidecar injection** | ZCP-managed Kubernetes |
| **Manual systemd** | Linux hosts |
| **Docker / Kubernetes sidecar** | Manual setups |

### Security baseline

- **Bind to localhost only** — do not expose the agent externally
- **Run as dedicated user** (`csms-agent`) where possible
- **Limit filesystem writes** to `storage_path` and log path only

---

## Deploy

### Pre-deploy checklist (all environments)

| Check | Action |
|-------|--------|
| **Role/IAM** | Role (or IRSA/serviceAccount for Kubernetes) is attached and validated for the target `prefixPath` |
| **CSMS polling** | CSMS web console: polling switch enabled if you need rotation/push behavior |
| **Local filesystem** | `storage_path` exists and is writable by the service user; log directory exists (or use `stdout`) |
| **Network** | Host can reach CSMS endpoint over HTTPS |

---

### Deploy option A: DevOps platform / ZAgent (recommended)

- Use the DevOps platform flow for agent installation, upgrade, and rollback
- If you lack permissions, ask **#Ask Devops Platform**

---

### Deploy option B: ZCP sidecar injection (recommended for ZCP)

Add CSMS config to your ZCP `app.yaml`:

```yaml
config:
- type: csms
  injectAgent:
    enable: true
    version: v8.0.1
    # image: artifacts.corp.zoom.us/web-docker-dev/async/csms-agent:v0.1.11.103
    # version and image cannot be configured at the same time
  config:
    port: "7890"
    log_level: info
    log_path: stdout
  pathMapping:
    dev/int: /dev-int/xx/va
  roleMapping:
    dev/int: arn:aws:iam::003833989744:role/csms@xxx
  serviceAccountMapping:
    dev/int: sa-dev-xxx
```

**Operational notes:**

- **Sidecar scope**: One pod’s agent serves that pod only — do not share an agent across pods
- **Startup order**: Ensure your app starts only after agent healthcheck passes

---

### Deploy option C: Manual systemd (Linux)

See [How to deploy CSMS Agent — Using Systemd for Linux](https://eng.corp.zoom.com/1/doc/eyJ0eXBlSWQiOjUsImRvY0lkIjo2NjYxNn0=#Using%20Systemd%20for%20Linux).

**Summary:**

1. **Create user and directories:**

```bash
sudo useradd -r -s /bin/false zoom || true
sudo mkdir -p /opt/csms-agent /opt/csms-agent/storage /var/log/csms-agent
sudo chown -R zoom:zoom /opt/csms-agent /var/log/csms-agent
```

2. **Install binary and config:**

```bash
sudo cp ./csms-agent /opt/csms-agent/csms-agent
sudo chmod 755 /opt/csms-agent/csms-agent
sudo chown csms-agent:csms-agent /opt/csms-agent/csms-agent

sudo cp ./deploy/config.json.template /opt/csms-agent/config.json
sudo chown csms-agent:csms-agent /opt/csms-agent/config.json
sudo chmod 640 /opt/csms-agent/config.json
```

3. **Install systemd unit:**

```bash
sudo cp ./deploy/csms-agent.service /etc/systemd/system/csms-agent.service
sudo systemctl daemon-reload
sudo systemctl enable csms-agent
sudo systemctl start csms-agent
sudo systemctl status csms-agent
```

4. **Verify:**

```bash
curl -f http://127.0.0.1:7890/agent/csms/healthcheck
curl -s http://127.0.0.1:7890/metrics | head
```

---

### Deploy option D: Docker (manual)

```bash
docker run -d --name csms_agent --restart always \
  -v /data/csms/config.json:/opt/csms-agent/config.json \
  -v /data/csms/storage:/opt/csms-agent/storage \
  -v /data/csms/log:/var/log/csms-agent \
  --network host \
  csms-agent:local \
  -- agent --config=/opt/csms-agent/config.json
```

**Notes:**

- Linux `--network host` is recommended if the agent must bind `127.0.0.1:7890`
- macOS Docker Desktop does not support host networking; use a Linux host or compatible runtime

---

### Deploy option E: Kubernetes (manual sidecar)

1. Create ConfigMap holding `config.json`
2. Mount it into the agent container
3. Add liveness probe (healthcheck)
4. Gate app startup on agent health:

```bash
#!/bin/sh
until curl -fsS http://127.0.0.1:7890/agent/csms/healthcheck >/dev/null; do
  sleep 5
done
exec "$@"
```

---

## Upgrade

### Principles

| Principle | Action |
|-----------|--------|
| **Preserve config** | Keep config and storage unless you explicitly need to reset |
| **Rollback plan** | Keep last-known-good binary/image and config backup |
| **Verify** | After upgrade: healthcheck + a real `getSecret` call + metrics scraped |

### Upgrade: systemd (manual)

```bash
sudo systemctl stop csms-agent
sudo cp /opt/csms-agent/csms-agent /opt/csms-agent/csms-agent.backup.$(date +%Y%m%d%H%M%S)
sudo cp ./csms-agent /opt/csms-agent/csms-agent
sudo chown csms-agent:csms-agent /opt/csms-agent/csms-agent
sudo chmod 755 /opt/csms-agent/csms-agent
sudo systemctl start csms-agent
sudo systemctl status csms-agent
curl -f http://127.0.0.1:7890/agent/csms/healthcheck
```

### Upgrade: ZCP / DevOps platform

- Use platform-native rollout, rollback, and version pinning
- Run the same post-upgrade checklist as above

---

## Troubleshooting Guide

### Decision flow (start here)

```
┌─────────────────────────────────────────┐
│ Is the agent process running?          │
│ (systemd: status / K8s: pod running)   │
└──────────────┬────────────────────────┘
               │
       ┌───────┴───────┐
       │ No            │ Yes
       ▼               ▼
┌──────────────┐  ┌─────────────────────────────────────────┐
│ See §1.1     │  │ Does healthcheck pass?                   │
│ Service      │  │ curl http://127.0.0.1:7890/agent/csms/   │
│ won't start  │  │   healthcheck                            │
└──────────────┘  └──────────────┬──────────────────────────┘
                                 │
                         ┌───────┴───────┐
                         │ No            │ Yes
                         ▼               ▼
                 ┌──────────────┐  ┌─────────────────────────────────────────┐
                 │ See §1.2     │  │ Does getSecret work?                    │
                 │ Healthcheck  │  │ (real call with your prefixPath/alias)  │
                 │ fails        │  └──────────────┬──────────────────────────┘
                 └──────────────┘                 │
                                          ┌───────┴───────┐
                                          │ 401/403/404   │ 5xx/timeout │ OK
                                          ▼               ▼             ▼
                                   ┌──────────────┐ ┌─────────┐   Done
                                   │ See §1.3–1.5 │ │ See §1.6│
                                   │ Auth / Path  │ │ 5xx/    │
                                   │              │ │ timeout │
                                   └──────────────┘ └─────────┘
```

---

### 1.1 Service won't start / exits immediately

| Step | Action |
|------|--------|
| **Check** | `sudo journalctl -u csms-agent -n 200 --no-pager` (systemd) or pod logs (K8s) |
| **Look for** | Port in use, config parse error, permission denied, panic/segfault |

**Fixes:**

| Root cause | Fix |
|------------|-----|
| **Port conflict** | `ss -tulnp \| grep 7890` or `lsof -i :7890`. Kill conflicting process or change agent port in config. |
| **Invalid config** | `python3 -m json.tool < /opt/csms-agent/config.json` — must parse cleanly. Fix typos, missing commas, trailing commas. |
| **Permissions** | Ensure `csms-agent` user can write `storage_path` and log directory. `ls -la /opt/csms-agent/storage` |
| **Missing binary** | Verify binary exists and is executable: `ls -la /opt/csms-agent/csms-agent` |

**If still failing:** Capture full log output and config (redact secrets) before escalating.

---

### 1.2 Healthcheck fails

| Step | Action |
|------|--------|
| **Check** | `curl -v http://127.0.0.1:7890/agent/csms/healthcheck` |
| **Expected** | `200 OK` with JSON body |

**Fixes:**

| Root cause | Fix |
|------------|-----|
| **Service not listening** | Confirm agent is running. Restart: `sudo systemctl restart csms-agent` |
| **Firewall / network policy** | On host, ensure localhost is not blocked. In K8s, check NetworkPolicy if app and agent share network namespace. |
| **Wrong port** | Config may use different port; verify `port` in config matches curl URL. |
| **Bind address** | Agent should bind `127.0.0.1` only. Do not expose externally. |

---

### 1.3 getSecret returns 401 Unauthorized

| Cause | Fix |
|-------|-----|
| **Expired credentials** | Role/IRSA token expired. Rebind role or restart pod so IRSA refreshes. |
| **Wrong identity** | VM/pod role or serviceAccount is not what CSMS expects. Verify IAM/IRSA binding. |

**Validation:** Use getSecret shell script or CSMS_Tool (internal docs) to test role before deploying agent.

---

### 1.4 getSecret returns 403 Forbidden

| Cause | Fix |
|-------|-----|
| **Cross-account** | Role ARN passed to agent must match the account/prefixPath. Verify `roleMapping` or `serviceAccountMapping` in config. |
| **PrefixPath mismatch** | Instance/pod role must have permission for the requested prefixPath. Check CSMS console and IAM policy. |
| **Kubernetes (IRSA)** | Confirm serviceAccount is annotated correctly and trust relationship is set. |

---

### 1.5 getSecret returns 404 Not Found

| Cause | Fix |
|-------|-----|
| **Wrong path** | Verify `prefixPath` and `alias` exist in CSMS and were created successfully. |
| **Typos** | Check for trailing slashes, case sensitivity, environment (dev vs prod) mismatch. |
| **Not yet provisioned** | Secret may still be provisioning. Check CSMS web console. |

---

### 1.6 getSecret returns 5xx or timeouts

| Cause | Fix |
|-------|-----|
| **CSMS server issue** | Check CSMS status page or ask #Ask-Secrets. Retry after a few minutes. |
| **Network/DNS** | From host/pod: `curl -I https://csms.zoom.us` (prod) or `https://csmsdev.zoomdev.us` (dev). |
| **TLS/proxy** | Corporate proxy or TLS inspection can break HTTPS. Test from a known-good host. |
| **Rate limiting** | Check metrics for 429 or throttling. Reduce request frequency or contact CSMS team. |

**Timeouts:** Increase client timeout if calls are slow. Check `csms_request_duration_seconds` in `/metrics`.

---

### 1.7 High memory usage

| Step | Action |
|------|--------|
| **Check** | `curl -s http://127.0.0.1:7890/metrics` — look at `go_memstats_*` and agent-specific metrics. |
| **Mitigation** | `sudo systemctl restart csms-agent` (or restart pod) while investigating. |
| **Escalation** | If growth is continuous, capture pprof heap snapshot: `curl -s "http://127.0.0.1:7890/debug/heap?debug=1"` (if enabled) and share with team. |

---

### Environment-specific checks

#### Systemd (Linux)

```bash
sudo systemctl status csms-agent
sudo journalctl -u csms-agent -n 200 --no-pager
sudo systemctl restart csms-agent
```

#### Kubernetes / ZCP sidecar

```bash
kubectl get pod <pod-name> -o jsonpath='{.status.containerStatuses[*].name}'
kubectl logs <pod-name> -c csms-agent --tail=200
kubectl exec <pod-name> -c <app-container> -- curl -s http://127.0.0.1:7890/agent/csms/healthcheck
```

**Common ZCP issues:** Wrong `serviceAccountMapping`, `pathMapping` typo, agent not ready before app starts (use healthcheck gate in entrypoint).

#### Docker

```bash
docker logs csms_agent --tail 200
curl -s http://127.0.0.1:7890/agent/csms/healthcheck  # from host if --network host
```

**Note:** macOS Docker Desktop does not support host networking. Use a Linux host or alternative setup.

---

### Quick triage checklist (copy-paste)

```bash
# 1) Is it up?
curl -v http://127.0.0.1:7890/agent/csms/healthcheck

# 2) Is it exposing metrics?
curl -s http://127.0.0.1:7890/metrics | head -50

# 3) Can it reach CSMS? (prod)
curl -I https://csms.zoom.us

# 4) Logs (systemd)
sudo journalctl -u csms-agent -n 200 --no-pager

# 5) Config valid?
python3 -m json.tool < /opt/csms-agent/config.json

# 6) Port in use?
ss -tulnp | grep 7890
```

---

### Useful endpoints for debugging

| Endpoint | Purpose |
|----------|---------|
| `GET http://127.0.0.1:7890/agent/csms/healthcheck` | Agent health |
| `GET http://127.0.0.1:7890/metrics` | Prometheus metrics |
| `GET http://127.0.0.1:7890/agent/csms/reload` | Reload config without restart |
| `GET http://127.0.0.1:7890/agent/csms/stop` | Stop agent |
| `GET http://127.0.0.1:7890/agent/csms/safestop` | Graceful stop |
| `GET http://127.0.0.1:7890/debug/heap?debug=1` | pprof heap (if enabled) |
| `GET http://127.0.0.1:7890/debug/goroutine?debug=1` | pprof goroutines (if enabled) |

---

### When to escalate

Escalate to **#Ask-Secrets** or **#Ask CSMS SDK&Agent** when:

- You've run the triage checklist and fixes above with no resolution
- You see panic, segfault, or unrecoverable errors in logs
- getSecret works from one environment but not another (same config)
- Suspected CSMS server-side issue (many 5xx across multiple agents)

**Include when escalating:**

- Agent version
- Environment (dev/staging/prod)
- Deployment mode (systemd / ZCP / Docker / K8s manual)
- Redacted config (no secrets)
- Last 200 lines of logs
- Output of `curl -v` healthcheck and a failing getSecret call (redact alias/path if sensitive)

---

## How to

### How to validate role can read a secret (before deploying agent)

- Prefer using a known-good verification method:
  - getSecret shell script guidance (internal doc)
  - CSMS_Tool guidance (internal doc)

### How to verify agent is working end-to-end (E2E)

Use a real secret retrieval through the agent:

```bash
curl -X GET "http://127.0.0.1:7890/api/1.0/getSecret?mode=rotate&prefixPath=<prefix>&aliasList=<alias>" \
  -H "App-SDK-Version: monitor" \
  -H "App-Process-ID: <unique-id>"
```

**Expected success:** `{"success": true, ...}`

### How to enable monitoring (logs + metrics)

| Item | Recommendation |
|------|----------------|
| **Metrics scrape** | `http://127.0.0.1:7890/metrics` every 15s |
| **Logs collection** | Use ZDCA (Zoom Data Collect Agent) to ship logs/metrics to AsyncMQ/Cube monitor |
| **Template-based onboarding** | Use Cube onboarding template `csms_agent_monitor_template` if available for your org/app |
| **Reference** | [How to monitor CSMS Agent](https://eng.corp.zoom.com/1/doc/eyJ0eXBlSWQiOjUsImRvY0lkIjo2NjU4M30=) |

---

### Key metrics to watch

| Metric | What it means | Alert threshold (example) |
|--------|---------------|---------------------------|
| `csms_agent_requests_total` | Total requests to agent | Sudden drop = app not calling |
| `csms_agent_request_errors_total` | Failed requests | > 0 for getSecret |
| `csms_request_duration_seconds` | Latency to CSMS | p99 > 5s |
| `go_memstats_alloc_bytes` | Memory usage | Steady growth = leak |

---

## FAQ

### Do I need the agent if I use Go/Java full SDK?

Often **no**. If you use the full SDK and call CSMS server directly, you typically don’t need the agent. ThinSDK + agent is mainly for languages/services that don’t have (or don’t want) direct SDK integration.

### What is the recommended binding address/port?

Use `127.0.0.1:7890` unless you have a strong reason to change. Exposing the agent externally is not recommended.

### Why do I get 403 on Kubernetes?

Most commonly IRSA/serviceAccount role mapping is wrong, or the role doesn’t have permission for the requested prefixPath. Confirm role binding and prefixPath mapping.

### How do I ensure my app starts after the agent in Kubernetes?

Gate the app entrypoint on agent healthcheck (`/agent/csms/healthcheck`) as shown in the deployment section.

---

## Reference (links, tools)

| Resource | Link |
|----------|------|
| **Role binding / validation / integration guide** | https://eng.corp.zoom.com/1/doc/eyJ0eXBlSWQiOjUsImRvY0lkIjo3NjY1OX0= |
| **CSMS agent monitoring (metrics/logs, ZDCA/Cube)** | [How to monitor CSMS Agent](https://eng.corp.zoom.com/1/doc/eyJ0eXBlSWQiOjUsImRvY0lkIjo2NjU4M30=) |
| **CSMS agent multi-env deployment & configuration** | [How to deploy CSMS Agent](https://eng.corp.zoom.com/1/doc/eyJ0eXBlSWQiOjUsImRvY0lkIjo2NjYxNn0=) |
| **Release notes** | [CSMS Agent release note](https://zoomvideo.atlassian.net/wiki/spaces/SecurityDevops/pages/2775942031/CSMS+Agent+release+note) |
| **Support channels** | #Ask-Secrets / #Ask CSMS SDK&Agent, #Ask zcp |
