#!/bin/zsh
# Resets the demo to its starting state, for a rehearsal or before the demo. Run by the presenter, never by Bob.
#   API Connect Sandbox: deletes the test apps (and their subscriptions), every LoyaltyRewards and
#                        LoyaltyMocks version (including the earlier demo kits', which use the same API
#                        paths), and the catalog properties. Keeps the OAuth provider and TLS profile.
#   API Connect Develop: deletes the draft LoyaltyRewards product versions and the drafts of its APIs.
#   Credentials files:   deletes ~/apic-test/<app>.env for each test app (the login file stays).
#   Workspace:           deletes Bob's outputs: requirements/, apic/, docs/.
# Usage: tools/reset-demo.sh        (asks before deleting; logs in with ~/apic-test/apic-login.env if needed)
set -u
WS="${0:A:h:h}"
ENVF="$WS/.bob/rules/sandbox-environment.md"   # the environment values live there only
row() { awk -F'|' -v k="$1" 'index($2,k) { if (match($3, /`[^`]+`/)) print substr($3, RSTART+1, RLENGTH-2); exit }' "$ENVF"; }
SERVER=$(row 'Platform API server'); ORG=$(row 'Provider org')
[[ -z $SERVER || -z $ORG || $SERVER == *'<'* || $ORG == *'<'* ]] && { echo "Fill in the platform API server and provider org in $ENVF first."; exit 1; }
CAT=sandbox; CORG=sandbox-test-org
APPS=(mobapp burstapp ibapp atmapp)
PRODUCTS=(loyaltyrewards:1.1.0 loyaltyrewards:1.0.0 loyaltyrewards:1.2.0 loyaltymocks:1.0.1 loyaltymocks:1.0.0)
PROPS=(loyalty-omw-redemption-url loyalty-lms-session-token-url loyalty-partnerhub-offers-url loyalty-partnerhub-api-key loyalty-omw-inquiry-url)
DRAFT_PRODUCTS=(loyaltyrewards:1.1.0 loyaltyrewards:1.0.0)
DRAFT_APIS=(loyalty-points-redemption-api:1.0.1 loyalty-points-redemption-api:1.0.0 loyalty-token-api:1.0.0 loyalty-partner-offers-api:1.0.0)
A=(--catalog $CAT --org $ORG --server $SERVER)
O=(--org $ORG --server $SERVER)

echo "This deletes, in Sandbox: products $PRODUCTS, apps $APPS, ${#PROPS} catalog properties;"
echo "in Develop: draft products $DRAFT_PRODUCTS and draft APIs $DRAFT_APIS;"
echo "the apps' credentials files in ~/apic-test/ (the login file stays); and in $WS: requirements/ apic/ docs/."
read "ok?Type yes to continue: "; [ "$ok" = yes ] || { echo "Nothing changed."; exit 1; }

LOGIN=~/apic-test/apic-login.env
if ! apic catalogs:list --org $ORG --server $SERVER >/dev/null 2>&1; then
  [ -f $LOGIN ] || { echo "Not logged in and $LOGIN is missing: see .bob/rules/sandbox-environment.md."; exit 1; }
  ( source $LOGIN && apic login --server $SERVER --username "$APIC_USER" --password "$APIC_PASSWORD" --realm "$APIC_REALM" >/dev/null 2>&1 ) \
    && echo "logged in with $LOGIN" || { echo "Login failed: check the user, password and realm in $LOGIN."; exit 1; }
fi

for app in $APPS; do
  apic apps:delete --consumer-org $CORG $A $app >/dev/null 2>&1 && echo "deleted app $app" || echo "app $app: not there"
done
for pr in $PRODUCTS; do
  apic products:delete --scope catalog $A $pr >/dev/null 2>&1 && echo "deleted product $pr" || echo "product $pr: not there"
done
for p in $PROPS; do
  apic properties:delete --scope catalog $A $p >/dev/null 2>&1 && echo "deleted property $p" || echo "property $p: not there"
done
for dp in $DRAFT_PRODUCTS; do   # the draft products first: they refer to the draft APIs
  apic draft-products:delete $O $dp >/dev/null 2>&1 && echo "deleted draft product $dp" || echo "draft product $dp: not there"
done
for da in $DRAFT_APIS; do
  apic draft-apis:delete $O $da >/dev/null 2>&1 && echo "deleted draft API $da" || echo "draft API $da: not there"
done
for app in $APPS; do rm -f ~/apic-test/$app.env; done && echo "deleted the apps' credentials files"
rm -rf "$WS/requirements" "$WS/apic" "$WS/docs" && echo "deleted Bob's outputs in the workspace"

echo; echo "Sandbox now:"
apic products:list-all --scope catalog $A
apic properties:list --scope catalog $A
echo; echo "Develop now (draft products):"
apic draft-products:list-all $O
echo "Done."
