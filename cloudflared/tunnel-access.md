# Cloudflare Tunnel + Access Setup

## Tunnel Setup
1. Install cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
2. Authenticate: `cloudflared tunnel login`
3. Create tunnel: `cloudflared tunnel create ai-workflow-tunnel`
4. Copy the generated credentials JSON to `cloudflared/ai-workflow-tunnel.json`
5. Update hostnames in `cloudflared/config.yml`
6. Run locally: `cloudflared tunnel run --config cloudflared/config.yml ai-workflow-tunnel`

## Access Policy
1. Go to Cloudflare Zero Trust > Access > Applications
2. Create two applications:
   - App: `ai-workflow` -> `ai-workflow.your-domain.com`
   - App: `langflow` -> `langflow.your-domain.com`
3. Add Access policies (email, SSO, or IP allowlist)
4. Enforce MFA for admin access

## Notes
- Do not expose Docker ports publicly. Use Cloudflare Tunnel only.
- Access policies should be required for all non-public endpoints.
