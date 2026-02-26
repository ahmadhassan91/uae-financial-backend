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
      "scores": {
        "total_score": 85.5,
        "status_band": "Financially Healthy"
      },
      "engagement": {
        "questions_answered": 15,
        "completion_percentage": 100.0,
        "leads_requested": "N"
      },
      "timestamps": {
        "submission_date": "2026-02-26T10:30:00Z"
      }
    }
  ]
}
```

---

## 6. Support Data (Incomplete Surveys)
For surveys marked as `type: "Incomplete"`, the API provides demographic details captured up to the point of abandonment. The `scores` object will be `null` for these records, and `completion_percentage` will indicate how far the user progressed.
