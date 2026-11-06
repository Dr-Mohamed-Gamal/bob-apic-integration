# LoyaltyAPIsForMobApp_20261105.xlsx (revised by the backend teams)

> MOCK DATA – prepared by IBM for the IBM Bob pilot. The project, APIs, hosts and values are invented.

## Tab: Project (PRO_LOY_00)

- **Project Name:** LoyaltyAPIsForMobApp
- **Project description:** Expose the Loyalty Rewards services to the bank's channels: the mobile banking app (MOBAPP) and the ATM network (ATMAPP): redeem points, get the loyalty session token and list partner offers.
- **Consumer application:** MOBAPP (mobile banking app), ATMAPP (ATM network), IBAPP (internet banking)
- **Product:** LoyaltyRewards, new product, version 1.0.0, with the three APIs below
- **OAuth scope:** LOYALTY (all APIs)
- **Document version:** 1.0
- **Released By:** API Connect team
- **Reviewed By:** API Connect Lead (mock reviewer)
- **Approver:** API Connect Lead (mock approver), title: API Connect Lead

**API Connect exposure (agreed with the API Connect team)**

| API Name | Req. Ref. No. | Priority | Existing/New | Backend system | Gateway | API version | Base path | Operation path | Operation name |
|---|---|---|---|---|---|---|---|---|---|
| LoyaltyPointsRedemptionAPI | API-001 | High | New | OMW | Cloud Internal API Gateway | 1.0.0 | /loyalty-redemption/v1 | /loyalty-points-redemption | postLoyaltyPointsRedemption |
| LoyaltyTokenAPI | API-002 | High | New | LMS | Cloud Internal API Gateway | 1.0.0 | /loyalty-token/v1 | /loyalty-session-token | getLoyaltySessionToken |
| LoyaltyPartnerOffersAPI | API-003 | Medium | New | PartnerHub (external) | External API Gateway | 1.0.0 | /loyalty-offers/v1 | /loyalty-partner-offers | getLoyaltyPartnerOffers |

**Consumers and plans (agreed with the API Connect team; all plans include every API)**

| Consumer | Application | Existing/New | Plan | Rate limit | Approval |
|---|---|---|---|---|---|
| Mobile banking | MOBAPP | New | Default Plan (default-plan) | 100 per hour, soft | Yes |
| ATM network | ATMAPP | New | ATM Plan (atm-plan) | 5 per minute, hard: an ATM must never flood the backends | Yes |
| Internet banking | IBAPP | New consumer – onboarding only, no API change | Internet Banking Plan (internet-banking-plan) | 200 per hour, soft | Yes |

## Tab: PointsRedemption (PRO_LOY_01)

- **API Name:** LoyaltyPointsRedemptionAPI
- **URL:** https://omw-uat.bank.example/omw/loyalty/v1/loyalty-points-redemption
- **Method:** POST
- **Timeout (sec):** 30

**Request Headers**

| Key | Value | M/O | Sent by |
|---|---|---|---|
| content-type | application/json | M | Consumer |
| X-USER-ID | <unique username of the calling application> | M | Consumer |
| X-MSG-ID | <unique message id per call> | M | Consumer |
| X-ORG-ID | AE | M | Consumer |
| x-lms-session | <sessionToken from LoyaltyTokenAPI> | M | Consumer |
| X-CHANNEL-ID | MOBILE, IB or ATM (the calling channel) | M | Consumer |

**Sample Request payload**

```json
{
  "cifNumber": "100234567",
  "memberId": "LM00987654",
  "redemptionRefNo": "MOB2026103000001",
  "pointsToRedeem": "5000",
  "redemptionType": "CASHBACK",
  "creditAccountNo": "019100234567001",
  "voucherCode": "",
  "remarks": "Cashback to current account"
}
```

**Sample Response**

```json
{
  "redemptionRefNo": "MOB2026103000001",
  "lmsReferenceNo": "LMS-RD-778812",
  "pointsRedeemed": "5000",
  "availablePoints": "12500",
  "status": "SUCCESS"
}
```

**Sample Error Response**

```json
{
  "statusCode": "400",
  "statusReason": "Bad Request",
  "errorCode": "EAI-LMS-BRK-002",
  "errorDesc": "Invalid field value or format"
}
```

**Important Response fields**

| Field | Description |
|---|---|
| lmsReferenceNo | Reference shown to the customer on the confirmation screen |
| availablePoints | Balance after the redemption (renamed from pointsBalance) |

**Request validation (new: API Connect must reject an invalid request before OMW is called)**

| Field | Mandatory | Format |
|---|---|---|
| cifNumber | Yes | 9 digits |
| memberId | Yes | LM followed by 8 digits |
| redemptionRefNo | Yes | Text, up to 20 characters |
| pointsToRedeem | Yes | Digits only, as a string |
| redemptionType | Yes | One of CASHBACK, VOUCHER, MILES |
| creditAccountNo | No | 15 digits |
| voucherCode | No | Text |
| remarks | No | Text, up to 100 characters |

## Tab: SessionToken (PRO_LOY_02)

- **API Name:** LoyaltyTokenAPI
- **URL:** https://lms-uat.bank.example/lms/auth/v1/session-token?channel=MOBILE
- **Method:** GET
- **Timeout (sec):** 10

**Request Headers**

| Key | Value | M/O | Sent by |
|---|---|---|---|
| Accept | application/json | O | Consumer |
| x-lms-app-id | MOBAPP01 | M | API Connect (fixed value) |
| x-request-id | <unique id per call> | M | Consumer |

**Sample Request payload**

No request body. Query parameter channel=MOBILE is fixed: API Connect adds it toward the backend; the consumer does not send it.

**Sample Response**

```json
{
  "sessionToken": "c2Vzc2lvbi1tb2NrLTAwMDAx",
  "tokenType": "LMS-SESSION",
  "expiresIn": 900
}
```

**Sample Error Response**

```json
{
  "code": "LMS-AUTH-401",
  "message": "Application not registered"
}
```

**Important Response fields**

| Field | Description |
|---|---|
| sessionToken | Sent in the x-lms-session header of LoyaltyPointsRedemptionAPI |
| expiresIn | Token lifetime in seconds; fetch a new token after it expires |

## Tab: PartnerOffers (PRO_LOY_03)

- **API Name:** LoyaltyPartnerOffersAPI
- **URL:** https://api.partnerhub.example/v2/offers?country=AE&category={category}&lang={lang}
- **Method:** GET
- **Timeout (sec):** 10

**Request Headers**

| Key | Value | M/O | Sent by |
|---|---|---|---|
| Accept | application/json | O | Consumer |
| x-api-key | <PartnerHub API key – provided separately by the partner; not in this sheet> | M | API Connect (secret, from a protected catalog property) |

**Sample Request payload**

No request body. Query parameters sent by the consumer: category (DINING, TRAVEL, SHOPPING), lang (en, ar). country=AE is fixed: API Connect adds it toward the backend.

**Sample Response**

```json
{
  "count": 1,
  "offers": [
    {
      "offerId": "PH-DIN-2041",
      "partnerName": "Mock Dining Group",
      "title": "20% off dinner for two",
      "pointsRequired": 2500,
      "validTill": "2026-12-31"
    }
  ]
}
```

**Sample Error Response**

```json
{
  "error": {
    "code": "PH-429",
    "message": "Rate limit exceeded"
  }
}
```

**Important Response fields**

| Field | Description |
|---|---|
| offers | List shown in the app; empty list when the partner has no offer |
| pointsRequired | Points the customer needs for the offer |
