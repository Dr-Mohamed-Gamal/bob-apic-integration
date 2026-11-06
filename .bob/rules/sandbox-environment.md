# Sandbox environment for Steps 4 to 7

The API Connect test environment that Steps 4 to 7 deploy to and test. To use a different environment, change
this file only. Tested on API Connect 10.0.11 (Cloud Pak for Integration 16.1.3). Before Step 4, replace
every `<…>` below with the values of your environment: Bob stops if one is left.

| Item | Value |
|---|---|
| Platform API server (`--server`) | `<platform API host, e.g. apic-mgmt-platform-api.example.com>` |
| Provider org (`--org`) | `<provider org name>` |
| Catalog (`--catalog`) | `sandbox` |
| Gateway base URL | `https://<gateway host>/<provider org name>/sandbox` |
| API URL | `<gateway base URL><basePath><operation path>` |
| OAuth provider | `loyalty-oauth-provider` (native, client credentials, scope LOYALTY; already in the catalog) |
| Token URL | `<gateway base URL>/loyalty-oauth-provider/oauth2/token` |
| TLS client profile | `tls-client-profile-catalog-default:1.0.0` (already in the catalog) |
| Test consumer org | `sandbox-test-org` (created by API Connect with the catalog) |
| Test apps | One per consumer in the Project tab: `mobapp`, `atmapp` (Step 5) and, from the revised workbook, `ibapp` (Step 6) |
| Credentials files | `~/apic-test/<app>.env` (for example `~/apic-test/mobapp.env`) with `CID=<client id>` and `CSEC=<client secret>`, outside the workspace, permissions `600` |
| Login file | `~/apic-test/apic-login.env`, outside the workspace, permissions `600`, created once by the developer (below) |

## Login file

The developer creates it once, with their own API Manager user, so Bob can log in without seeing the
password:

```bash
mkdir -p ~/apic-test && cat > ~/apic-test/apic-login.env <<'EOF'
APIC_USER='<API Manager username>'
APIC_PASSWORD='<password>'
APIC_REALM='provider/default-idp-2'
EOF
chmod 600 ~/apic-test/apic-login.env
```

`provider/default-idp-2` is the realm of a local API Manager user on this environment.

## Catalog properties for Sandbox

The backend hosts in the input are mock hosts that do not exist. In Sandbox every backend URL points
to the mock backend that Bob builds in Step 2 and deploys in Step 4 (`LoyaltyMocks`, inside API
Connect). It returns the SRS sample response and reports which headers and query parameters it
received. The real URLs from the input are used in UAT and production.

| Property | Sandbox value |
|---|---|
| `loyalty-omw-redemption-url` | `https://<gateway host>/<provider org name>/sandbox/mock/loyalty-redemption/v1/loyalty-points-redemption` |
| `loyalty-lms-session-token-url` | `https://<gateway host>/<provider org name>/sandbox/mock/loyalty-token/v1/loyalty-session-token` |
| `loyalty-partnerhub-offers-url` | `https://<gateway host>/<provider org name>/sandbox/mock/loyalty-offers/v1/loyalty-partner-offers` |
| `loyalty-partnerhub-api-key` | `sandbox-dummy-key` (a dummy: the real key is supplied by the partner for production only) |
