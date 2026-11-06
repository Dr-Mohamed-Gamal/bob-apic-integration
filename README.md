# API Connect demo workspace (IBM Bob) – Loyalty Rewards

Bob takes the backend teams' API details to tested APIs in API Connect, then applies a revised sheet
as a new version. The workspace starts with no YAML file: Bob writes all of them. All content is mock
data prepared by IBM; nothing here is a bank document.

## The seven steps

1. **Fill the document.** Bob fills the API Connect SRS template from the input workbook, in Markdown
   and Word. The developer approves it.
2. **Create the YAML.** One OpenAPI YAML per API and the product (LoyaltyRewards 1.0.0), plus a mock
   backend per API built from the SRS sample responses (LoyaltyMocks 1.0.0).
3. **Validate.** `apic validate` on both products, and `docs/validation.md`.
4. **Deploy.** Bob logs in, checks Sandbox, creates the catalog properties, publishes the mocks and
   the product, checks each API is live, and writes `docs/deployment.md`.
5. **Test.** One test app per consumer (mobile banking, ATM), each on its own plan; the developer
   approves the subscriptions. Per API: 401, and 200 with the SRS sample. Then a burst on the ATM plan
   that gets 429. Results in `docs/test-results.md`, linked to the SRS
   requirement IDs.
6. **Change.** From the revised workbook in `inputs/revisions/`:
   - the differences and their impact (a new header, a renamed field, request validation, and a new
     consumer, Internet Banking, onboarded with no API change);
   - SRS 1.1, the changed API at 1.0.1 and the product at 1.1.0;
   - validation, a release that supersedes 1.0.0 (the apps already live stay on it and keep working
     until they move), and a retest;
   - the report `docs/change-1.1.0.md`.
7. **Ask.** Bob answers questions on how the deployed APIs behave, from the files and a real call.

The prompts and what to show are in [`DEMO_GUIDE.md`](DEMO_GUIDE.md).

## Folders

| Folder | What it holds |
|---|---|
| `.bob/rules/` | `apic-rules.md`: how Bob does the seven steps. `sandbox-environment.md`: the API Connect Sandbox |
| `inputs/` | `LoyaltyAPIsForMobApp_20261030.xlsx`: a Project tab and one tab per API (`.md` copy alongside). `revisions/`: the revised workbook for Step 6 |
| `templates/` | `API-SRS-API_Connect_TEMPLATE.docx`: the empty SRS (`.md` copy alongside) |
| `tools/` | `md_to_docx.py`: turns the SRS into Word. `reset-demo.sh`: returns Sandbox and the workspace to the starting state (run by the presenter) |

Bob creates during a run: `requirements/`, `apic/` (with `mocks/` and, in Step 6, `releases/`) and
`docs/`.

## Running it yourself

You need:

- **IBM Bob**, opened on this folder: Agent mode, one chat for all the steps.
- **An API Connect 10.0.x environment** (tested on 10.0.11) with a provider org and its `sandbox`
  catalog. The catalog must already have a native OAuth provider `loyalty-oauth-provider` (client
  credentials, scope `LOYALTY`), the TLS client profile `tls-client-profile-catalog-default:1.0.0`, and
  the test consumer org `sandbox-test-org`.
- **The `apic` toolkit** of the same version as your API Connect server, on your PATH (download it
  from API Manager).
- **Python 3**, standard library only, for `tools/md_to_docx.py`.

Then:

1. Replace every `<…>` in `.bob/rules/sandbox-environment.md` with your environment's values. Bob
   and the reset script stop if one is left.
2. Create the login file once (`DEMO_GUIDE.md`, "One time only").
3. Run `tools/reset-demo.sh`. It removes earlier runs from Sandbox and Bob's outputs from this folder.
4. Open the folder in Bob and follow `DEMO_GUIDE.md`.

Bob's outputs (`requirements/`, `apic/`, `docs/`) are git-ignored.

The companion kit for App Connect Enterprise is
[bob-ace-integration](https://github.com/Dr-Mohamed-Gamal/bob-ace-integration).
