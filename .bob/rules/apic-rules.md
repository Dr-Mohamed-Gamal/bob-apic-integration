# API Connect rules for Bob in this workspace

Bob reads this file on every turn. The work has seven steps, one prompt each:

1. fill the requirement document (SRS) from the input workbook;
2. create the API Connect YAML files, and a mock backend built from the SRS samples;
3. validate the YAML files;
4. deploy them to the Sandbox catalog;
5. test the deployed APIs;
6. apply a change from a revised workbook as a new version;
7. answer the developer's questions on how the deployed APIs behave.

The workspace starts with no YAML file: Bob writes every one. The rules come from the bank's API
Connect standards and from tests on API Connect 10.0.11 (marked *(tested)*). The environment values
are in [`sandbox-environment.md`](sandbox-environment.md).

## 1. How to work

- **W-01** Take every value from the input workbook (`inputs/*.md`, same content as the `.xlsx`), the
  prompt or these rules. Steps 1 to 5 never read `inputs/revisions/`; only Step 6 does. Never invent a value. If one is missing, stop and name it; do not write a
  placeholder.
- **W-02** Dates and the author come from the prompt. If the prompt gives no date, run `date`.
- **W-03** Record in `docs/decisions.md` every choice the input does not state outright, one table row
  each: what, the value, the source (input tab, rule id or prompt).
- **W-04** Never write a secret (password, client secret, API key, token) in any file in this workspace,
  in a document or in your reply. Mask it as `****`.
- **W-05** Do one step per prompt, then stop. In replies, do not cite step numbers of steps not yet
  asked for, or rule ids. End your reply with what the developer should review or
  decide in what you produced. Do not name, announce or suggest the next step: the developer leads.

## 2. Step 1 – fill the requirement document (SRS)

- **SRS-01** Copy the structure of `templates/API-SRS-API_Connect_TEMPLATE.md` exactly. Save the filled
  document as `requirements/API-SRS-<Project Name>_V<document version>.md`, then run
  `python3 tools/md_to_docx.py <that file>` to create the Word file next to it.
- **SRS-02** One section 2.1.n per API, in the order of the Project tab's exposure table. All APIs are
  new: use layout A. Remove the template's guidance notes, layout B and the "(layout A/B)" labels.
- **SRS-03** Project values (name, description, document version, released by, reviewed by, approver,
  product, scope, requirement references, priority, gateway, version, paths, operation names, backend
  system) come from the Project tab. In 1.2.1 In Scope, add a "Consumers and plans" table (consumer,
  application, plan, rate limit, approval) copied from the Project tab. Creation, release, revision and approval dates are the prompt's
  date, written as `04 Nov 2026`; the author is the prompt's author.
- **SRS-04** Backend URL, method, timeout (written as `<n> seconds`), headers, samples and important
  fields are copied exactly from the API's tab. The URL is copied as given, with its query string.
- **SRS-05** The Input Headers table lists only the headers the consumer sends (`Sent by: Consumer`),
  after ClientId and Authorization, with M/O from the tab and data type String. A header that API Connect
  sets goes on its own line under API Details: "Header set by API Connect toward the backend: <name>".
  For a fixed value, give the value; for a secret, write "value from a protected catalog property" and
  never the value.
- **SRS-06** The SRS has no place for the sample error responses; leave them out. Step 2 uses them.

## 3. Step 2 – create the YAML files

Files: `apic/<APIName>.yaml` for each API and `apic/LoyaltyRewards.yaml` for the product, written from
the approved SRS and the input tabs.

**API definition**
- **API-01** OpenAPI 2.0 (`swagger: '2.0'`). `info.title` = the API name, `info.x-ibm-name` = the API
  name in kebab case (`loyalty-token-api`), `info.version` from the Project tab, and a description that
  names the backend system and the requirement reference.
- **API-02** `host: $(catalog.host)`, `schemes: [https]`, and `basePath` from the Project tab: every API
  has its own base path *(tested)*. The single operation uses the operation path, method and operation
  name from the Project tab.
- **API-03** Security: one requirement with both `clientID` and `oauth` (scope `LOYALTY`).
  `clientID` is `type: apiKey`, `in: header`, `name: ClientId`, `x-key-type: client_id` (without it
  API Connect only accepts the header name `X-IBM-Client-Id` *(tested)*). `oauth` is `type: oauth2`,
  `flow: application`, `x-ibm-oauth-provider: <OAuth provider from sandbox-environment.md>` and
  `tokenUrl: https://$(catalog.host)/<OAuth provider>/oauth2/token` *(tested)*.
- **API-04** Parameters: every consumer header from the tab with `required: true` for M and `false` for
  O; consumer query parameters as `required: true` with their allowed values as `enum`; a body parameter
  (`required: true`) for a request payload. Do not declare `ClientId` or `Authorization` as parameters.
- **API-05** Responses: `200` with the sample response as the example and a schema built from it;
  `401` and `429` on every operation, as in the bank's own API files; and the tab's sample error under
  its own status code (from its `statusCode`, or 401 / 429 when the sample's code says so) with the
  sample as example. Field types follow the samples (quoted value: string; number: integer).
  - `401` and `429` are API Connect's own errors (missing or invalid credentials; rate limit reached).
    Each points to a definition, `#/definitions/401ErrorResponse` and `#/definitions/429ErrorResponse`,
    in the gateway's error format: `httpCode`, `httpMessage`, `moreInformation`, all strings. Examples:
    `{"httpCode":"401","httpMessage":"Unauthorized","moreInformation":"Invalid client id or secret."}`
    and `{"httpCode":"429","httpMessage":"Too Many Requests","moreInformation":"Rate Limit exceeded"}`.
    Descriptions: `Unauthorized` and `Too Many Requests`.
  - If the tab's sample error is itself a 401 or 429 (it comes from the backend), keep API Connect's
    definition for that code and add the backend's sample to its description: "The backend can also
    return: <the sample on one line>".
- **API-06** Assembly: an `invoke` (version 2.0.0) with:
  - `target-url` built from a catalog property, never a literal host. Fixed query parameters
    (`channel=MOBILE`, `country=AE`) and consumer query parameters (`$(request.parameters.<name>)`) are
    added to the target URL;
  - `verb` set explicitly to the method (POST / GET), never `keep`;
  - `timeout` from the tab;
  - `tls-profile: <TLS client profile from sandbox-environment.md>`: without it an https backend fails
    with "Backside URL invalid" *(tested)*;
  - a `header-control` allowlist with only the headers the tab lists, so `ClientId` and `Authorization`
    never reach the backend, and an empty `parameter-control` allowlist.
  A header that API Connect sets is set with a `set-variable` before the invoke
  (`message.headers.<name>`): the fixed value, or `$(<catalog property>)` for a secret.
- **API-07** Catalog properties: one per backend URL (the URL without its query string) and one per
  secret: `loyalty-omw-redemption-url`, `loyalty-lms-session-token-url`,
  `loyalty-partnerhub-offers-url`, `loyalty-partnerhub-api-key`.
- **API-08** Activity log: in `x-ibm-configuration`, next to the assembly,
  `activity-log: {enabled: true, success-content: header, error-content: header}`, as in the bank's
  own API files.

**Product**
- **PRD-01** `product: 1.0.0`, `info.name: loyaltyrewards`, `info.title: LoyaltyRewards`, `info.version`
  from the Project tab (1.0.0), `gateways: [datapower-api-gateway]`.
- **PRD-02** Every API of the Project tab, keys `<x-ibm-name><version>` with `$ref: <file>.yaml`.
- **PRD-03** One plan per row of the Project tab's "Consumers and plans" table: the plan name in
  brackets (`default-plan`, `atm-plan`), the title before the brackets, `approval` from the table, the
  rate limit (`100 per hour` → `100/1hour`, `5 per minute` → `5/1minute`) with `hard-limit: true` for
  hard and `false` for soft (the bank's default). A soft limit only logs and never returns 429
  *(tested)*. Every plan lists every API.

**Mock backend**

The backends in the input do not exist in Sandbox. Bob builds a mock of each backend from the SRS
sample responses, inside API Connect, so the APIs can be tested before the real backends are ready.
- **MCK-01** Files: `apic/mocks/<APIName>Mock.yaml` per API and `apic/mocks/LoyaltyMocks.yaml` for the
  mock product. Each mock API: OpenAPI 2.0, `info.title` `<APIName>Mock`, `info.x-ibm-name`
  `<x-ibm-name>-mock`, `info.version` = the API's version, `host: $(catalog.host)`, `schemes: [https]`,
  `basePath: /mock<the API's basePath>`, `security: []` (no credentials: it stands in for a backend),
  one operation with the API's operation path and method, response `200`.
- **MCK-02** Assembly: one `gatewayscript` (version 2.0.0) that returns the API's sample response from
  the SRS, exactly, and reports what it received *(tested)*:
  ```
  var h = context.get('request.headers') || {};
  context.message.header.set('Content-Type', 'application/json');
  context.message.header.set('X-Mock-Received-Headers', Object.keys(h).join(','));
  context.message.header.set('X-Mock-Received-Uri', String(context.get('request.uri')));
  context.message.body.write(JSON.stringify(<the sample response JSON from the SRS>));
  context.message.statusCode = '200 OK';
  ```
  The mock reports header names only, never values.
- **MCK-03** Mock product: `product: 1.0.0`, `info.name: loyaltymocks`, `info.title: LoyaltyMocks`,
  `info.version: 1.0.0`, `gateways: [datapower-api-gateway]`, every mock API, one plan `default-plan`
  with `approval: false` and no rate limit.

## 4. Step 3 – validate the YAML files

- **VAL-01** Run `apic validate apic/LoyaltyRewards.yaml` and `apic validate apic/mocks/LoyaltyMocks.yaml`;
  each validates the product and every API it references. Fix every error and run it again until every file reports "Validated".
- **VAL-02** Write `docs/validation.md` with four sections:
  1. **apic validate**: the command, the final result per file, and every failed run: the error as
     `apic` printed it, the cause and the fix. If the first run passed, say so.
  2. **Rule checks**: one table per API with a row for each rule API-01 to API-08, and one for the
     product with PRD-01 to PRD-03: the rule, the value found in the file, OK / NOT OK. Read the values
     from the files, not from memory.
  3. **Traceability**: one table per API comparing the file with the SRS and the input tab: base path,
     operation path, method, operation name, timeout, consumer headers with M/O, query parameters, the
     headers API Connect sets, and the catalog property of the backend URL. Columns: item, SRS / input
     value, file value, match yes / no. For each mock: base path, operation path, method, and the
     sample response compared with the SRS sample (parse both as JSON and compare).
  4. **Safety checks**: no literal backend host in `apic/` (search for `bank.example` and
     `partnerhub.example`); no secret value in `apic/` (search for the Sandbox API key value from
     `sandbox-environment.md` without printing it; report "not found").
  End with a one-line verdict. If a row is NOT OK, fix the file, validate again and update the report.

## 5. Step 4 – deploy to Sandbox

Step 4 runs only against the Sandbox catalog in `sandbox-environment.md`.

- **DEP-01 Safety.** Sandbox only. Never publish to, change or delete anything in another catalog.
  Never delete anything in API Connect, and never run `tools/reset-demo.sh` (the presenter's script).
  Never republish a product version that is already in the catalog: republishing replaces the product
  *(tested)*. Deploy only after Step 3 passed.
- **DEP-02 Log in.** First check for a session: `apic catalogs:list --org <org> --server <server>`. If
  it fails, log in with the login file from `sandbox-environment.md` (check it exists and has
  permissions `600`; never print or copy it), in one command:
  `source <login file> && apic login --server <server> --username "$APIC_USER" --password "$APIC_PASSWORD" --realm "$APIC_REALM"`.
  Report only "Logged in" or the error. If it fails, stop and ask the developer to fix the file or
  log in by hand.
- **DEP-03 Check the target.** Record each result: the catalog is there; the OAuth provider is in the
  catalog (`apic configured-oauth-providers:list --scope catalog …`); the TLS client profile is in the
  catalog (`apic configured-tls-client-profiles:list --scope catalog … <profile name without :version>`);
  products `loyaltyrewards:<version>` and `loyaltymocks:<version>` are not in the catalog
  (`apic products:list-all --scope catalog …`).
  If something is missing or the product is already there, stop and tell the developer.
- **DEP-04 Catalog properties.** Create each property from `sandbox-environment.md` that does not exist
  yet (`apic properties:create --scope catalog`), with the value exactly as written there (no leading
  space or tab *(tested)*). Then list them and check every value; mask the API key.
- **DEP-05 Publish.** Catalog property values are fixed when a product is published; changing a
  property later does not reach a published API *(tested)*. So create the properties first (DEP-04),
  then publish the mock product, then the product:
  `apic products:publish apic/mocks/LoyaltyMocks.yaml --catalog <catalog> --org <org> --server <server>`
  and `apic products:publish apic/LoyaltyRewards.yaml …`. Check with `apic products:list-all --scope
  catalog …` that both are `published`.
- **DEP-06 Smoke check.** For each API, call its URL (`<gateway base URL><basePath><operation path>`)
  with `curl -sk`, the consumer headers and query parameters from the tab, and no credentials. Expect
  401: the API is live on the gateway and refuses callers without credentials. Call each mock URL
  (the catalog property value) directly: expect 200 and the SRS sample response.
- **DEP-07 Report.** Write `docs/deployment.md`: the target (server, org, catalog), the checks from
  DEP-03, the properties (key masked), the publish result and state, the API URLs, and the smoke check
  per API (expected 401, actual), then a one-line verdict. If a step fails, stop, report the error and
  what to fix; do not retry a publish.

## 6. Step 5 – test the deployed APIs

- **TST-01 Safety.** DEP-01 applies. Log in as in DEP-02 if the session expired.
- **TST-02 Apps.** In the test consumer org from `sandbox-environment.md`, create each test app that
  does not exist yet (`apic apps:create … --format json`), one per consumer in the Project tab: the
  application in lower case as the name (`mobapp`, `atmapp`) and as given as the title (`MOBAPP`). Write each app's client ID and secret to its credentials file from
  `sandbox-environment.md` (`CID=…`, `CSEC=…`, `chmod 600`), never shown. If an app exists but its
  credentials file does not, stop and ask.
- **TST-03 Subscriptions.** Subscribe each app to its plan from the Project tab, in the published
  product (`product_url` from `apic products:list-all`). The plans need approval, so the subscriptions
  are `pending`: stop and ask the developer to approve them all in API Manager (Manage → Sandbox →
  Tasks). Continue only when they say so, and check every subscription is `enabled`.
- **TST-04 Tokens.** Per app, get a token from the token URL, form-encoded
  (`-H 'Content-Type: application/x-www-form-urlencoded' -d 'grant_type=client_credentials&scope=LOYALTY&client_id=…&client_secret=…'`);
  a JSON body returns 400 *(tested)*. Keep tokens in shell variables, never in a file.
- **TST-05 Tests per API, with `mobapp`,** built from the API's SRS section, `curl -sk`:
  1. consumer headers and query parameters, no ClientId and no token → expect **401**, and the body has
     the fields of `401ErrorResponse` in the API file;
  2. consumer headers, query parameters, ClientId, Bearer token and the SRS sample request → expect
     **200**, and the body equals the SRS sample response (parse both as JSON and compare). From the
     mock's response headers, check: every consumer header arrived; `clientid` and `authorization`
     did not; the headers API Connect sets arrived (`x-lms-app-id`, `x-api-key`: name only); in
     `X-Mock-Received-Uri`, the fixed query parameters (`channel=MOBILE`, `country=AE`) and the
     consumer query parameters arrived.
- **TST-06 Burst, with the app whose plan has a hard per-minute limit (`atmapp`),** on LoyaltyTokenAPI:
  the limit plus one full calls back to back (5 + 1). Expect every call within the limit 200 and the
  last **429**, with the fields of `429ErrorResponse` in the API file; record `retry-after` and
  `x-ratelimit-limit`. Use that app for nothing else in Step 5.
  This proves each consumer has its own limit.
- **TST-07 Report.** `docs/test-results.md`: one row per test with the SRS Requirement Serial No.
  (R-01…) and Unique Req. Ref. No. (API-001…), the API, the test, expected, actual, the checks, and
  PASS / FAIL. The burst test also carries the requirement IDs of the API it ran on, and the plan's
  rate limit from the SRS "Consumers and plans" table. Then a one-line verdict. Mask client IDs, secrets and tokens. If a test fails, report
  the gateway's message and the likely cause, and stop: a fix needs a new version, never a
  republish.

## 7. Step 6 – a change from a revised workbook becomes a new version

- **CHG-01 Compare.** Read the revised workbook in `inputs/revisions/` (the `.md`; same content as the
  `.xlsx`) and compare it with the original in `inputs/`, tab by tab. List every difference: tab, item,
  old value, new value, including the Project tab (consumers and plans). List the affected APIs, and
  confirm the others are unchanged.
- **CHG-02 Impact.** For each difference, say what it means for consumers. A new mandatory consumer
  header, or a renamed or removed response field, is a **breaking change**: apps that already call the
  API must change. New request validation is breaking for apps that send invalid data. A new consumer
  with no API change is **onboarding only**: a new plan and app, no API version change. The release
  protects the apps already live: they stay on the old version, which keeps working, and move only when
  they are ready (CHG-07). A renamed or removed response field comes from the backend: once the backend
  changes, it reaches the callers of every version, so say the backend team must keep the old field
  until the existing apps have moved. Say all this
  clearly in the report and the reply. Versions: each changed API patch
  (1.0.0 → 1.0.1); the product minor (1.0.0 → 1.1.0); the SRS document (1.0 → 1.1); the changed mock
  API and the mock product patch (1.0.0 → 1.0.1). Unchanged APIs keep their version.
- **CHG-03 Keep the release.** Before changing anything, copy `apic/` to `apic/releases/<product version>/`.
- **CHG-04 SRS.** Create `requirements/API-SRS-<Project Name>_V1.1.md` from V1.0; never edit V1.0. Set
  the version, file name and dates; add a revision record row (number, date, sections, a one-line
  summary of the change, version 1.1). Update only the affected API sections. Run
  `python3 tools/md_to_docx.py` on it.
- **CHG-05 YAML.** Change only the affected API files: raise `info.version`; a new consumer header
  becomes a header parameter (`required: true` for M, `enum` for a fixed value) and is added to the
  `header-control` allowlist; a renamed response field is renamed in the 200 schema and example.
  - Request validation: the body schema gets a `required` list and, per field, `pattern`, `enum` or
    `maxLength` from the table (`9 digits` → `^[0-9]{9}$`; `LM followed by 8 digits` → `^LM[0-9]{8}$`;
    `digits only` → `^[0-9]+$`; `15 digits` → `^[0-9]{15}$`). As the first two assembly steps: `parse`
    (version 2.2.0, `parse-settings-reference: {default: apic-default-parsesettings}`) then `validate`
    (version 2.7.0, `validate-against: body-param`). Without `parse`, `validate` rejects every request
    *(tested)*. Add a `422` response "Request body failed validation".
  Update the affected mock so it returns the revised sample response. Products: raise `info.version`,
  update the keys of the changed APIs, keep the existing plans unchanged and add a plan for each new
  consumer (as PRD-03).
- **CHG-06 Validate.** As Step 3, for both products. Write `docs/validation-<product version>.md`.
- **CHG-07 Release.** DEP-01 applies; the new versions must not already be in the catalog. Never delete
  the old versions.
  1. Mock (it stands in for the backend, and the backend has changed): replace it.
     `apic products:publish apic/mocks/LoyaltyMocks.yaml --stage …`, then
     `apic products:replace --scope catalog loyaltymocks:<new version> <mapping file> …`, with the mapping
     file `apic/releases/mock-plan-mapping.yaml`: `product_url` of the old mock version (from
     `apic products:list-all`) and `plans: [{source: default-plan, target: default-plan}]` *(tested)*.
  2. Product: supersede it, never replace it, so the apps already subscribed stay on the old version
     and keep working: a breaking change must not reach them before they are ready.
     `apic products:publish apic/LoyaltyRewards.yaml --stage …`, then
     `apic products:supersede --scope catalog loyaltyrewards:<new version> <mapping file> …`, with
     `apic/releases/plan-mapping.yaml`: `product_url` of the old version and each existing plan mapped
     to itself (`default-plan` → `default-plan`, `atm-plan` → `atm-plan`); a new plan has no source. If
     the command's options differ, follow `apic products:supersede --help`.
  Check: the new versions are `published`; the old mock is `retired`; the old product is `deprecated`
  (it still serves its apps but takes no new subscriptions); every existing subscription is still
  `enabled` on the old product's `product_url`. Do not move those subscriptions: the developer moves
  them when the apps send the new header.
  3. New consumers: create each new app as in TST-02 and subscribe it to its plan of the new version.
     Stop and ask the developer to approve it in API Manager; continue when they say so.
- **CHG-08 Retest.** The new version, with the new consumer's app (`ibapp`, the only app on it), on
  the changed API, sending its own channel:
  1. without the new header → **400**;
  2. full call with it → **200**, the body equals the revised sample, and the new header is in
     `X-Mock-Received-Headers`;
  3. empty JSON body `{}` → **422**. (A request with no body at all returns 500 "Found no input for
     the policy" from `parse` *(tested)*: if you test it, report it as a known gateway behaviour, not a
     pass);
  4. body without a mandatory field (`pointsToRedeem`) → **422**;
  5. body with a wrong format (`memberId: "XX1"`) → **422**.
  Record the gateway's message for each 422. Then the old version, with `mobapp` (still on it): the
  same call as in Step 5, without the new header → **200**, proving the apps already live keep
  working; the body shows the renamed field, because the backend changed (CHG-02). Then each unchanged
  API, with `mobapp`: full call → 200 (regression). No burst test.
- **CHG-09 Report.** `docs/change-<product version>.md`:
  1. the workbook differences (table);
  2. the impact, with breaking changes marked, and the version of every file before and after;
  3. the changes per file against `apic/releases/…`: a summary table (file, what changed, which
     workbook difference), then the `diff -u` of each changed file in a code block; unchanged files
     confirmed with `cmp`;
  4. the release steps and states, and which app is on which version;
  5. the retest table with the requirement IDs, and a one-line verdict.

## 8. Step 7 – answer questions on how the deployed APIs behave

- **ASK-01** When the developer asks why an API behaves in some way, answer from the files in `apic/`
  (name the file and the part: parameter, schema, assembly step) and the SRS, and prove it with one
  real call to the Sandbox gateway, with the credentials (masked) of an app on the version asked
  about: `mobapp` for the first version, `ibapp` for the new one. Show the status code and the
  gateway's message.
- **ASK-02** If the behaviour comes from something the input does not state (for example, which
  request body fields are mandatory), say so, name who must provide it, and say what the fix would be
  that a change to a deployed API is always a new version. In replies to the developer, do not refer
  to step numbers or to these rules by their ids.
- **ASK-03** Step 7 changes nothing, neither a file nor anything in API Connect, unless the developer
  asks for the change in a new prompt.
