# API Connect – System Requirements Specification

**&lt;Project Name&gt;**

- File Name: API-SRS-&lt;Project Name&gt;_V&lt;x.y&gt;.docx
- Author: &lt;author&gt;
- Version: &lt;x.y&gt;
- Creation Date: &lt;dd Mon yyyy&gt;
- Release Date: &lt;dd Mon yyyy&gt;
- Released By: &lt;name&gt;
- Reviewed By: &lt;name&gt;

> This is a mock template prepared by IBM for the IBM Bob pilot. It follows the layout of an API Connect SRS used by a bank. It is not a bank document. Text in &lt;angle brackets&gt; is replaced when the document is filled.

**APPROVAL SIGNATURES**

| Name | Title | Date | Signature |
|---|---|---|---|
| &lt;name&gt; | &lt;title&gt; | &lt;dd Mon yyyy&gt; |   |

**REVISION RECORD**

| Change Number | Date | Section | Notes | Version |
|---|---|---|---|---|
| 1 | &lt;dd Mon yyyy&gt; | All | Initial version | &lt;x.y&gt; |

**TABLE OF CONTENTS**

- 1 Introduction
  - 1.1 Purpose
  - 1.2 Business Requirement
    - 1.2.1 In Scope
    - 1.2.2 Out of Scope
- 2 Project Requirements
  - 2.1 Functional Requirements
    - 2.1.&lt;n&gt; &lt;API Name&gt;   (layout A: new API or changed API)
    - 2.1.&lt;n&gt; &lt;API Name&gt;   (layout B: existing API, no change)

## 1 Introduction

### 1.1 Purpose

This document is to explain the system requirements spec for the API connect interface changes part of Project – &lt;Project Name&gt;.

### 1.2 Business Requirement

**Scope & Functionalities :** &lt;what the project delivers and for whom, in two or three sentences&gt;

#### 1.2.1 In Scope

As per Project – &lt;Project Name&gt;, we are exposing below Rest API's via Cloud Internal API Gateway & External gateway.

| S No | API Name | Product | Existing/New | Backend |
|---|---|---|---|---|
| 1 | &lt;API Name&gt; | &lt;Product&gt; | &lt;Existing / New&gt; | &lt;Backend system&gt; |

#### 1.2.2 Out of Scope

Any other requirements which is not mentioned in the scope.

## 2 Project Requirements

### 2.1 Functional Requirements

> Template note: one section 2.1.&lt;n&gt; per API in the In Scope table, in the same order. A new API, or an existing API that changes, uses layout A. An existing API with no change uses layout B.

#### 2.1.&lt;n&gt; &lt;API Name&gt;   (layout A: new API or changed API)

- **Requirement Serial No.** R-<nn> · **Name** API-Interface-<API Name>
- **Unique Req. Ref. No.** API-<nnn> · **Priority** <High / Medium / Low>

**&lt;API Name&gt;** &lt;what the API does and who calls it&gt;. Exposed via &lt;Cloud Internal API Gateway / External API Gateway&gt;.

**API Details:**

- API Name: **&lt;API Name&gt;**
- API oAuth Scope Name: **&lt;scope&gt;**
- Backend Endpoint: **&lt;backend URL&gt;**
- Backend Timeout: **&lt;seconds&gt;**
- Version: **&lt;x.y.z&gt;**   (for a changed API: current &lt;x.y.z&gt; → new &lt;x.y.z&gt;, and what changes)

| S.No | HTTP Method | OperationName | Path |
|---|---|---|---|
| 1 | &lt;GET / POST / PUT / DELETE&gt; | &lt;OperationName&gt; | &lt;operation path&gt; |

Below are the headers required for API connect security checks. These are common for all operations. Please note, along with API headers these security header parameters need to be passed.

**Input Headers**

| API Header Field | Mandatory | Data Type | Description |
|---|---|---|---|
| **HTTP Header Parameters** |   |   |   |
| ClientId | M | String | Client Id of consumer App |
| Authorization | M | String | Bearer &lt;Token received from get token API with respect to Scope&gt; |
| &lt;backend header&gt; | &lt;M / O&gt; | &lt;Data Type&gt; | &lt;description, or the fixed value&gt; |

The below are the request and response schemas for your reference.

**Request**

```
<sample request JSON; for a GET: No request body, and the query parameters>
```

**Response**

```
<sample success response JSON>
```

| Important Response fields | Description |
|---|---|
| &lt;field&gt; | &lt;what the consumer uses it for&gt; |

#### 2.1.&lt;n&gt; &lt;API Name&gt;   (layout B: existing API, no change)

- **Requirement Serial No.** R-<nn> · **Name** API-Interface-<API Name>
- **Unique Req. Ref. No.** API-<nnn> · **Priority** <High / Medium / Low>

**&lt;API Name&gt;** is an existing API. There is no change in the API. Consumer onboarding only: &lt;consumer application&gt; is subscribed to product &lt;Product&gt;.

**API Details:**

- API Name: **&lt;API Name&gt;**
- API oAuth Scope Name: **&lt;scope&gt;**
- Version: **&lt;x.y.z&gt;** (unchanged)
