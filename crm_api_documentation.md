# Microsoft Dynamics CRM Integration Guide

This document provides the technical details required for the Microsoft Dynamics CRM team to integrate with the Financial Clinic API.

## 1. Authentication
The API uses **Bearer Token Authentication**. Every request must include an `Authorization` header with a valid API Key.

**Header Format:**
`Authorization: Bearer <CRM_API_KEY>`

> [!IMPORTANT]
> API Keys are now dynamic. They can be generated and revoked by administrators in the **Admin Dashboard** under **System Management > CRM Integration**.

---

## 2. API Endpoint
The endpoint is a secure, pull-based JSON API.

**Production URL:**
`https://uae-financial-health-filters-68ab0c8434cb.herokuapp.com/api/v1/crm/consolidated-data`

**Method:** `GET`

---

## 3. Query Parameters
The API supports filtering to allow for "Delta Updates" (syncing only new data).

| Parameter     | Type   | Description                                                                 |
|---------------|--------|-----------------------------------------------------------------------------|
| `date_range`  | String | Options: `today`, `yesterday`, `last_7_days`, `all`. (Default: `today`)   |
| `start_date`  | Date   | Custom start date (YYYY-MM-DD).                                           |
| `end_date`    | Date   | Custom end date (YYYY-MM-DD).                                             |

---

## 4. Key Management & Security

### Managing Keys
Administrators can manage access tokens through the application UI:
1. Navigate to **System Management** tab in the Admin area.
2. Select **CRM Integration**.
3. You can generate new keys with descriptive labels (e.g., "Dynamics Prod") and revoke old keys immediately if compromised.

### Security Best Practices
- **Rate Limiting:** The API is limited to **60 requests per hour** per key to ensure system stability.
- **Audit Logging:** All access attempts and key management actions are logged. Every successful data pull records the key name and filters used.
- **Key Format:** Modern keys are prefixed with `fc_` followed by a secure random string (e.g., `fc_XyZ123...`).

---

## 5. Response Structure
The API returns a JSON object containing metadata and an array of records (Submissions, Leads, and Incomplete surveys).

### Sample Request (curl):
```bash
curl -X GET "https://uae-financial-health-filters-68ab0c8434cb.herokuapp.com/api/v1/crm/consolidated-data?date_range=today" \
     -H "Authorization: Bearer fc_unique_token_here"
```

### Sample JSON Output:
```json
{
  "meta": {
    "total_count": 1,
    "timestamp": "2026-02-26T16:00:00Z"
  },
  "data": [
    {
      "id": 123,
      "type": "Submitted",
      "name": "John Doe",
      "email": "john.doe@example.com",
      "mobile_number": "+971 50 123 4567",
      "age": 34,
      "gender": "Male",
      "nationality": "Emirati",
      "emirate": "Dubai",
      "children": "2",
      "employment_status": "Employed",
      "income_range": "10,000 to 20,000",
      "company": "Example Corp",
      "unique_url": "",
      "scores": {
        "total_score": 85.5,
        "status_band": "Good",
        "income_stream": 20.0,
        "savings_habit": 16.0,
        "debt_management": 18.0,
        "retirement_planning": 14.0,
        "financial_protection": 10.0,
        "financial_knowledge": 7.5
      },
      "engagement": {
        "questions_answered": 15,
        "total_questions": 15,
        "completion_percentage": 100.0,
        "leads_requested": "N"
      },
      "action_plans": {
        "plan_1": "You have strong financial protection in place.",
        "plan_2": "High debt levels may limit your future savings.",
        "plan_3": "You have a stable, consistent income.",
        "plan_4": "You save occasionally, but your savings rate could improve.",
        "plan_5": "You're well-prepared for emergencies."
      },
      "consultation": null,
      "timestamps": {
        "submission_date": "2026-02-26T10:30:00Z"
      }
    }
  ]
}
```

> [!NOTE]
> The `consultation` field will be `null` for the vast majority of records. It is only populated when a user explicitly requested a consultation via the Financial Clinic form (i.e. `engagement.leads_requested = "Y"`) **and** a `ConsultationRequest` record was subsequently created by the backend.

### `consultation` Object (when not null):

| Field              | Type               | Description                                                                 |
|--------------------|--------------------|-----------------------------------------------------------------------------|
| `status`           | String             | `pending`, `contacted`, `scheduled`, `completed`, or `cancelled`            |
| `source`           | String             | Origin of the request (e.g. `financial_clinic`)                             |
| `preferred_method` | String             | `phone`, `email`, or `whatsapp`                                             |
| `preferred_time`   | String             | `morning`, `afternoon`, or `evening`                                        |
| `message`          | String / null      | Optional message from the user                                              |
| `notes`            | String / null      | Admin internal notes                                                        |
| `created_at`       | ISO 8601 datetime  | When the consultation request was submitted                                 |
| `contacted_at`     | ISO 8601 datetime / null | When the user was first contacted                                     |
| `scheduled_at`     | ISO 8601 datetime / null | When a consultation meeting has been scheduled                        |

---

## 6. Support Data (Incomplete Surveys)
For surveys marked as `type: "Incomplete"`, the API provides demographic details captured up to the point of abandonment. The `scores`, `action_plans`, and `consultation` fields will be `null` for these records, and `engagement.completion_percentage` will indicate how far the user progressed.
