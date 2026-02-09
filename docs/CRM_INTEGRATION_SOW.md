# CRM API Integration
## Statement of Work (SOW) & Technical Specification

**Version:** 1.0  
**Date:** February 4, 2026  
**Author:** Clustox Development Team  
**Status:** Draft  

---

## 1. Executive Summary

### 1.1 Purpose
To integrate the Financial Clinic platform with the client's Microsoft Dynamics CRM by exposing a secure, automated API endpoint. This will replace the manual process of exporting and uploading Excel files, ensuring real-time or daily synchronization of financial health assessments and leads.

### 1.2 Business Objectives
- **Automation:** Eliminate manual data handling and reduce human error.
- **Timeliness:** Enable daily or real-time updates of leads to the sales team.
- **Scalability:** Support growing data volumes without operational overhead.
- **Consolidated Data:** Provide a single source of truth matching the "Consolidated Report" logic.

---

## 2. Project Scope

### 2.1 In Scope
- **API Development:** Creation of a secure `GET` endpoint to retrieve consolidated assessment data.
- **Authentication:** Implementation of a secure Bearer Token (API Key) mechanism for the CRM system.
- **Data Mapping:** Ensuring the JSON response strictly matches the existing Consolidated Export CSV format (including new columns like "Unique URL").
- **Filtering:** Supporting query parameters for date ranges (e.g., `today`, `yesterday` to support incremental polling).
- **Documentation:** Technical API specification for the CRM integration team.

### 2.2 Out of Scope
- **CRM-Side Development:** Mapping fields within Microsoft Dynamics or building the ingestion pipeline (Client responsibility).
- **Two-Way Sync:** Writing data back from CRM to Financial Clinic (Read-only API).
- **Historic Data Migration:** The API will support fetching history, but manual migration services are not included.

---

## 3. High-Level Requirements

### 3.1 API Endpoint (FR-1)
**Description:** A RESTful endpoint providing consolidated data.
**Requirements:**
- URL: `/api/v1/crm/consolidated-data`
- Method: `GET`
- Output Format: JSON (Array of objects)
- Pagination: Support `limit` and `offset` for large datasets.

### 3.2 Authentication (FR-2)
**Description:** Secure access control for the API.
**Requirements:**
- API Key / Bearer Token based authentication.
- Long-lived tokens for service-to-service communication.
- Ability to revoke tokens if compromised.

### 3.3 Data Structure (FR-3)
**Description:** JSON representation of the Consolidated Report.
**Requirements:**
- Include all 40+ columns from the CSV export.
- Key mapping: `Snake Case` variants of CSV headers (e.g., "Unique URL" -> `unique_url`).
- Data types: Strict typing (Integer, Float, ISO 8601 Date Strings).

---

## 4. Technical Architecture

### 4.1 Schema Definition
The JSON response will follow a strict schema defined using Pydantic models to ensure stability.

```json
{
  "meta": {
    "total_count": 120,
    "timestamp": "2026-02-04T12:00:00Z"
  },
  "data": [
    {
      "id": 101,
      "type": "Submitted", 
      "name": "Jane Doe",
      "email": "jane@example.com",
      "mobile": "+971501234567",
      "company": "National Bonds",
      "unique_url": "nbc-internal",
      "scores": {
        "total": 85.5,
        "status_band": "Financially Secure"
      },
      "leads_requested": true,
      "submission_date": "2026-02-04T09:30:00Z"
    }
  ]
}
```

### 4.2 Security
- **Transport:** HTTPS only.
- **Auth Storage:** Hashed API keys in `api_keys` table.
- **Rate Limiting:** (Optional Phase 2) 100 requests/minute.

---

## 5. Implementation Plan

### Phase 1: Analysis & Schema (Week 1)
- Finalize API Specification.
- Define JSON Schema (Pydantic models).
- Confirm mapping with CRM team.

### Phase 2: Core Development (Week 1)
- Implement `ApiKey` database model.
- Refactor `ConsolidatedExportService` to decouple data logic.
- Implement API Endpoint and Auth Middleware.

### Phase 3: Testing & Verification (Week 2)
- Unit tests for authentication and data serialization.
- Comparison test: Ensure JSON output matches CSV export exactly.
- Staging deployment and integration test with CRM team.

---

## 6. Effort Estimates

| Phase | Task Group | Est. Effort |
|-------|------------|-------------|
| 1 | Analysis & Design | 4 Hours |
| 2 | Authentication System | 9 Hours |
| 3 | Data Service Refactoring | 10 Hours |
| 4 | API Implementation | 8 Hours |
| 5 | Testing & Deployment | 5 Hours |
| | **Total** | **~36 Hours** |

---

## 7. Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Project Manager | | | |
| Client Technical Lead | | | |
