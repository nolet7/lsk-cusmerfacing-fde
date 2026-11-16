# Enterprise UI — Microsoft Entra SPA

An independent, minimal Vite SPA using MSAL Browser 5.x. This is the enterprise alternative to the demo-only `frontend/index.html`, which the API disables in Azure mode.

## Run
```bash
cd enterprise-ui
cp .env.example .env.local
# Edit .env.local with approved nonsecret Entra IDs and API scope
npm install
npm run dev
npm run build
```

## Identity prerequisites
- Create Entra SPA registration, register **exact** redirect origins.
- Create separate protected API registration with exposed delegated scope `Logistics.Access` (or your approved scope).
- Configure API app roles `Logistics.Read` and `Logistics.Write` and trusted `customer_tenant_id` claim issuance in **access tokens**. A delegated scope alone does not satisfy backend app-role checks.
- Grant approved client consent. Confirm delegated access tokens contain `roles`, correct `aud`, `iss`, `tid` and authorized customer scope. Claim mapping must be validated against actual tokens.
- Use same-origin routing through approved Azure Front Door / API Management / reverse proxy. Set `/api/v2/*` to gateway, static assets to approved UI host. No `X-Demo-Tenant` headers.

MSAL obtains short-lived tokens silently when possible and falls back to interactive redirect. Tokens are not copied into local app state, rendered to the UI or committed. Do not log sensitive response content in production browsers.

## Limitations
This is a minimal functional SPA, not a completed enterprise UX. Missing SAST/a11y/UAT, packaging pipeline, E2E browser tests, live Entra registration, corporate routing and CSP headers. Build success alone does not prove authentication works with a customer's Entra tenant.
