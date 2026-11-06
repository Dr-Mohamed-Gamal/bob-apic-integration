# Demo Guide – IBM Bob with API Connect, Loyalty Rewards

Six steps and two questions take the backend teams' Excel sheet to tested APIs in API Connect, then a
revised sheet to a new version with request validation and a new consumer. The workspace starts with no YAML
file. Bob does the work; the presenter plays the API Connect developer who approves.

| Step | Bob | About |
|---|---|---|
| 1 | fills the SRS from the Excel sheet | 2 min |
| 2 | creates the YAML, and a mock backend from the SRS samples | 2 min |
| 3 | validates the YAML | 1 min |
| 4 | deploys to Sandbox | 2 min |
| 5 | tests every API: 401, 200 with the SRS sample, 429 on the ATM plan | 3 min + 1 approval |
| Ask | "Why does it accept an empty body?" | 1 min |
| 6 | applies the revised Excel sheet: new version, validation, a new consumer | 5 min + 1 approval |
| Optional | "Why does it return 400?" (only if the client asks) | 1 min |

**Opening line:** "Today each API takes your team days of manual work. Let's see what Bob does with the
same input."

## One time only: create the login file

Do this once on the Mac you present from. Redo it only if your password changes or you move to
another Mac or environment. The file holds your API Manager login so Bob can deploy without seeing
your password. It sits outside the workspace and only you can read it.

Open Terminal, paste the command, and replace the two values in `<…>` with your own API Manager
username and password (keep the single quotes):

```bash
mkdir -p ~/apic-test && cat > ~/apic-test/apic-login.env <<'EOF'
APIC_USER='<your API Manager username>'
APIC_PASSWORD='<your API Manager password>'
APIC_REALM='provider/default-idp-2'
EOF
chmod 600 ~/apic-test/apic-login.env
```

The command prints nothing. The reset script (below) checks it: it says "logged in with
…/apic-login.env".

**If the reset script says "Login failed":** check the password by logging in to API Manager in the
browser, then correct the file (`open -e ~/apic-test/apic-login.env`). Or log in by hand, which asks
for the username and password:

```bash
apic login --server <platform API host from .bob/rules/sandbox-environment.md> --realm provider/default-idp-2
```

## Before the demo (10 minutes)

1. Reset to the starting state (asks you to type `yes`). Run the script of the folder you will open
   in Bob:
   ```bash
   tools/reset-demo.sh
   ```
   It also removes what earlier demo kits published, because they use the same API paths. Only one
   kit can be live in Sandbox at a time.
2. Check your API Connect environment is up.
3. Open the folder in Bob, with auto-approve for terminal commands and file writes (or be ready to
   click Approve on each command).
4. Open in browser tabs: the input workbook (`inputs/LoyaltyAPIsForMobApp_20261030.xlsx`), the
   revised one (`inputs/revisions/LoyaltyAPIsForMobApp_20261105.xlsx`), and API Manager
   (logged in, on Manage → Sandbox).

---

## Step 1 – Bob fills in the document from the Excel sheet

> Step 1: fill the requirement document from the input workbook. Author: `<your name>`. Today is `<date>`.

**Show:** the workbook next to the Word document (`requirements/`). Backend URLs, headers and samples
are copied exactly; the headers API Connect sets are listed separately; the partner's key appears
nowhere. Point at the requirement IDs (R-01, API-001): Step 5 tests against them.

**Say:** "Today a developer retypes this sheet into the SRS by hand. Bob does it in a minute and
invents nothing: every choice the sheet doesn't state is in `docs/decisions.md`."

## Step 2 – Bob creates the YAML files

> I approve the SRS. Step 2: create the YAML files.

**Show:** `apic/`: one YAML per API and the product, written from nothing. In one file: the backend
URL comes from a catalog property (`$(…)`), so the same file works in every environment, and the
header allowlist keeps the app's credentials from the backend. Every operation also documents the
401 and 429 errors and has the activity log on, as in your own API files. Then `apic/mocks/`: a mock
of each backend, built from the SRS sample responses.

**Say:** "The backends don't exist yet, so Bob builds mocks from the SRS. The mobile team can start
before the backend team is ready."

## Step 3 – Bob validates the YAML files

> Step 3: validate the YAML files.

**Show:** `docs/validation.md`: "Validated" for every file, a check of each rule, the comparison with
the SRS value by value, and the safety checks.

## Step 4 – Bob deploys the YAML files

> Step 4: deploy to Sandbox.

**Show:** API Manager → Manage → Sandbox → Products: LoyaltyRewards 1.0.0 and LoyaltyMocks 1.0.0
**Published**. Then `docs/deployment.md`: each API answers 401 without credentials, so it is live
and secured.

## Step 5 – Bob tests the APIs

> Step 5: test the deployed APIs.

Bob creates one test app per consumer in the sheet (MOBAPP for mobile banking, ATMAPP for the ATM
network) and subscribes each to its own plan, then **stops for your approval**. In API Manager →
Manage → Sandbox → Tasks, approve both subscriptions, then tell Bob:

> Approved.

**Show:** `docs/test-results.md`, each row linked to its SRS requirement:

| Test | Expected | Proves |
|---|---|---|
| No ClientId | 401 | Only subscribed apps get in, and the error is the one the YAML documents |
| Valid call (MOBAPP) | 200, body = the SRS sample | End to end works. The mock also shows the app's credentials never reached the backend, and the headers and parameters API Connect added did |
| 6 calls in a row (ATMAPP, ATM plan: 5 per minute) | 5 × 200, then 429 | Each consumer has its own limit: an ATM cannot flood the backend |

**Say:** "You said the YAML should be deployed and tested directly. Today that testing is by hand.
Bob built the tests from the SRS and ran them against the gateway, with a different policy per
consumer, as you described."

## Ask Bob – review the deployed API

> Why does PointsRedemption accept a request with an empty body (`{}`)?

Bob answers from the files and proves it with a real call (200): the sheet does not say which body
fields are mandatory, so Bob did not invent any. He names who must provide them, and says the fix is
a new version.

**Say:** "So we ask the backend team for the validation rules."

## Step 6 – The revised Excel sheet becomes a new version

The backend team replies with a revised sheet (`inputs/revisions/`). Show it: the Points Redemption
tab has a new mandatory header, a renamed response field and a validation table; the Project tab has
a new consumer, Internet Banking.

> The backend team sent a revised workbook. Step 6: apply the change.

**What Bob does:**
1. compares the two sheets and lists every difference;
2. flags the impact: the new header, the renamed field and the validation are **breaking** for apps
   already calling the API; Internet Banking is **onboarding only** (no API change);
3. writes SRS 1.1 with a revision record;
4. moves only Points Redemption to 1.0.1 (new header, renamed field, request validation) and the
   product to 1.1.0 (with the new Internet Banking plan);
5. validates;
6. releases 1.1.0 so that it supersedes 1.0.0: MOBAPP and ATMAPP stay on 1.0.0 and keep working
   until their apps send the new header; new apps get 1.1.0;
7. creates IBAPP and subscribes it to 1.1.0, then **stops for your approval**.

**You:** approve IBAPP in API Manager → Tasks, then tell Bob `Approved.`

**Show:** `docs/change-1.1.0.md`: the differences between the sheets, the impact, the diff of each
changed file, which app is on which version, and the retest:

| Retest | App | Expected |
|---|---|---|
| Without the new header | IBAPP (1.1.0) | 400 |
| Full call | IBAPP (1.1.0) | 200, with the renamed field |
| Empty body `{}`, missing field, wrong format | IBAPP (1.1.0) | 422, with the exact field in the gateway's message |
| The old call, without the new header | MOBAPP (still on 1.0.0) | 200: the apps already live keep working |
| The two unchanged APIs | MOBAPP | 200 (nothing broke) |

**Say:** "Every change is a new version, and changes happen far more often than new APIs. Bob found
what changed, changed only that, told you who is affected, added the validators and onboarded a new
channel. The apps already live stay on 1.0.0 and keep working; they move when they're ready. The one
thing API Connect can't hold back is the renamed field, because it comes from the backend, so Bob
flags it for the backend team."

## Optional – keep for the client's questions

> Why does PointsRedemption return 400?

Use it only if the client asks something like "what happens to an app that has not been updated?".
Bob explains, with a real call on version 1.0.1: the revised sheet made `X-CHANNEL-ID` mandatory, so
a call without it is rejected. He names the apps that must add it before they move from 1.0.0
(MOBAPP, ATMAPP), which until then are not affected.

**Why it is optional:** the change report from Step 6 already shows that the new header is mandatory
and breaking, so in the main flow this answer mostly repeats it. And the client asked to focus on
implementation first and to keep troubleshooting for a later phase, so a second "why" question pulls
the demo towards what they said comes later. The first question stays in the main flow because it
leads into the request validation the client asked for.

**Closing line:** "From the backend teams' sheet to tested APIs, and a change to a new version, with
validators and a new consumer. Bob did the work; your developer made the decisions. Deployment to UAT
and production stays with your pipeline."

---

## If something goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| Bob says login failed | Wrong user, password or realm in the login file | See "If the reset script says Login failed" above, then tell Bob "continue" |
| Bob says a product is already in the catalog | The reset was not run | Run `tools/reset-demo.sh`, then start again from Step 1 |
| A valid call returns 500 or an httpbin echo | A catalog property is wrong, or the mock was not published before the product | Run the reset and start again: property values are fixed when the product is published |
| Token request returns "client not subscribed" | A subscription is not approved yet | Approve it in API Manager → Sandbox → Tasks |
| The burst gets 429 too early | `atmapp` was called in the minute before | Wait one minute and ask Bob to repeat the burst test |
| Everything times out | The API Connect environment is down or expired | Check the environment |
