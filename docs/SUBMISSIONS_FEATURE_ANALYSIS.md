# Submissions Feature - Complete Technical Analysis

> **Generated:** January 26, 2026  
> **Purpose:** Comprehensive documentation of the Financial Clinic Submissions feature across frontend and backend

---

## Table of Contents

1. [Overview](#overview)
2. [Frontend Implementation](#frontend-implementation)
3. [Backend API Endpoints](#backend-api-endpoints)
4. [Filters Reference](#filters-reference)
5. [CSV/Excel Export](#csvexcel-export)
6. [Helper Functions](#helper-functions)
7. [Implementation Notes](#implementation-notes)

---

## Overview

The Submissions feature allows admin users to view, filter, export, and manage all Financial Clinic survey submissions. The feature consists of:

- **Frontend Component:** `SubmissionsTable.tsx` (925 lines)
- **Backend Routes:** `simple_routes.py` (Endpoints under `/admin/simple/`)

---

## Frontend Implementation

### File Location
```
/frontend/src/components/admin/SubmissionsTable.tsx
```

### Data Structure

```typescript
interface FinancialClinicSubmission {
  id: number;
  profile_id: number;
  profile_name: string;
  profile_email: string;
  profile_mobile: string;
  gender: string;
  nationality: string;
  emirate: string;
  age: number | null;
  employment_status: string;
  income_range: string;
  company_name: string | null;
  company_id: number | null;
  total_score: number;
  status_band: string;
  questions_answered: number;
  total_questions: number;
  category_scores: {
    [key: string]: { score: number; max_score: number };
  };
  created_at: string;
  completed_at: string | null;
  insights?: {
    category: string;
    status_level: string;
    text: string;
    text_ar: string;
    priority: number;
  }[];
}

interface SubmissionStats {
  total: number;
  today: number;
  this_week: number;
  this_month: number;
  average_score: number;
}
```

### Key UI Components

| Component | Description |
|-----------|-------------|
| Stats Cards | Display total, today, week, month counts and average score |
| Filter Bar | Date pickers, search, and dropdown filters |
| Submissions Table | Paginated table with sortable columns |
| Detail Dialog | Modal showing full submission details |
| Action Menu | View details, delete submission |

### Core Functions

| Function | Lines | Description |
|----------|-------|-------------|
| `loadCompanies()` | 163-173 | Fetches company options from `/admin/simple/filter-options` |
| `loadSubmissions()` | 175-216 | Fetches paginated submissions with filters |
| `loadStats()` | 218-241 | Fetches submission statistics |
| `handleDelete()` | 243-259 | Deletes a submission by ID |
| `handleExport()` | 261-305 | Exports filtered data as CSV |
| `getStatusBadge()` | 307-322 | Returns styled badge for status band |
| `formatDate()` | 324-332 | Formats ISO date for display |
| `getCategoryScore()` | 334-349 | Extracts score from category_scores object |

---

## Backend API Endpoints

### Base Path: `/admin/simple`

All endpoints require admin authentication via `get_current_admin_user` dependency.

---

### 1. GET `/submissions`

**Purpose:** Paginated list of all Financial Clinic submissions with filtering

**Location:** Lines 2567-2781

**Query Parameters:**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `page` | int | 1 | No | Page number (≥1) |
| `page_size` | int | 20 | No | Items per page (1-100) |
| `search` | string | null | No | Search by name, email, or phone |
| `status_band` | string | null | No | Filter: Excellent, Good, Needs Improvement, At Risk |
| `nationality` | string | null | No | Filter: Emirati, Non-Emirati |
| `company_id` | int | null | No | Filter by CompanyTracker ID (Unique URL) |
| `company_name` | string | null | No | Filter by CompanyDetails name or 'other' |
| `income_range` | string | null | No | Filter by income bracket |
| `age_group` | string | null | No | Filter: < 18, 18-25, 26-35, 36-45, 46-60, 60+ |
| `date_from` | ISO string | null | No | Start date filter |
| `date_to` | ISO string | null | No | End date filter |

**Response:**

```json
{
  "submissions": [
    {
      "id": 123,
      "profile_id": 456,
      "profile_name": "John Doe",
      "profile_email": "john@example.com",
      "profile_mobile": "+971501234567",
      "gender": "Male",
      "nationality": "Emirati",
      "emirate": "Dubai",
      "age": 32,
      "employment_status": "Employed",
      "income_range": "20,000 to 30,000",
      "company_name": "ABC Corp",
      "total_score": 72.5,
      "status_band": "Good",
      "questions_answered": 25,
      "total_questions": 25,
      "category_scores": {
        "Income Stream": { "score": 15, "max_score": 20 },
        "Savings Habit": { "score": 12, "max_score": 20 }
      },
      "insights": [...],
      "leads_requested": true,
      "created_at": "2026-01-25T10:30:00",
      "completed_at": "2026-01-25T10:45:00"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

---

### 2. GET `/submissions/stats`

**Purpose:** Statistics for submissions (respects same filters)

**Location:** Lines 2784-2959

**Query Parameters:** Same as `/submissions` endpoint (excluding pagination)

**Response:**

```json
{
  "total": 500,
  "today": 12,
  "this_week": 45,
  "this_month": 180,
  "average_score": 65.5
}
```

---

### 3. DELETE `/submissions/{submission_id}`

**Purpose:** Delete a specific submission

**Location:** Lines 2962-2999

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `submission_id` | int | ID of submission to delete |

**Response:**

```json
{
  "success": true,
  "message": "Submission deleted successfully",
  "id": 123
}
```

---

### 4. GET `/export-csv`

**Purpose:** Export filtered financial clinic responses as CSV file

**Location:** Lines 750-1062

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `date_range` | string | Preset: '7d', '30d', '90d', '1y', 'ytd', 'all' |
| `start_date` / `date_from` | string | Custom start date (YYYY-MM-DD) |
| `end_date` / `date_to` | string | Custom end date (YYYY-MM-DD) |
| `search` | string | Text search filter |
| `status_band` | string | Status filter |
| `nationality` | string | Nationality filter |
| `company_name` | string | Company name filter |
| `company_id` | int | Unique URL filter |
| `income_range` | string | Income filter |
| `age_group` / `age_groups` | string | Age group filter(s) |
| `genders` | string | Comma-separated genders |
| `emirates` | string | Comma-separated emirates |
| `employment_statuses` | string | Comma-separated statuses |
| `children` | string | Children count filter |
| `companies` | string | CompanyTracker filter |
| `activeCompanies` | string | CompanyDetails filter |
| `unique_users_only` | bool | Only latest per email |

**Response:** StreamingResponse with CSV file attachment

---

### 5. GET `/export-excel`

**Purpose:** Export as Excel (.xlsx) file

**Location:** Lines 1065-1335

**Parameters:** Same as `/export-csv`

**Response:** StreamingResponse with Excel file attachment

---

### 6. GET `/filter-options`

**Purpose:** Provides all available filter options for dropdowns

**Location:** Lines 1557-1650

**Response:**

```json
{
  "age_groups": ["< 18", "18-25", "26-35", "36-45", "46-60", "60+"],
  "genders": ["Male", "Female"],
  "nationalities": ["Emirati", "Non-Emirati"],
  "emirates": [
    "Dubai",
    "Abu Dhabi",
    "Sharjah",
    "Ajman",
    "Al Ain",
    "Ras Al Khaimah / Fujairah / UAQ / Outside UAE"
  ],
  "employment_statuses": ["Employed", "Self-Employed", "Unemployed"],
  "income_ranges": [
    "Below 5,000",
    "5,000 to 10,000",
    "10,000 to 20,000",
    "20,000 to 30,000",
    "30,000 to 40,000",
    "40,000 to 50,000",
    "50,000 to 100,000",
    "Above 100,000"
  ],
  "children_options": ["0", "1", "2", "3", "4", "5+"],
  "companies": [
    { "id": 1, "name": "Company A", "unique_url": "company-a" }
  ],
  "activeCompanies": [
    { "id": 1, "name": "Active Company", "unique_url": null }
  ]
}
```

---

## Filters Reference

### Frontend Filter State Variables

| State Variable | Filter Target | API Parameter |
|----------------|---------------|---------------|
| `searchTerm` | Name/Email/Phone | `search` |
| `statusFilter` | Status Band | `status_band` |
| `nationalityFilter` | Nationality | `nationality` |
| `companyFilter` | Company Name | `company_name` |
| `uniqueUrlFilter` | Unique URL | `company_id` |
| `incomeFilter` | Income Range | `income_range` |
| `ageGroupFilter` | Age Group | `age_group` |
| `dateFrom` | Start Date | `date_from` |
| `dateTo` | End Date | `date_to` |

### Status Band Values

| Value | Display Label | Badge Color |
|-------|---------------|-------------|
| `Excellent` | Excellent | Green |
| `Good` | Good | Blue |
| `Needs Improvement` | Needs Improvement | Yellow |
| `At Risk` | At Risk | Red |

---

## CSV/Excel Export

### Column Structure (27 columns)

| # | Column Name | Source |
|---|-------------|--------|
| 1 | ID | response.id |
| 2 | Name | profile_data.name |
| 3 | Email | profile_data.email |
| 4 | Mobile Number | profile_data.mobile_number (with +971 prefix) |
| 5 | Age | Calculated from date_of_birth |
| 6 | Gender | profile_data.gender |
| 7 | Nationality | profile_data.nationality |
| 8 | Emirate | profile_data.emirate |
| 9 | Children | profile_data.children |
| 10 | Employment Status | profile_data.employment_status |
| 11 | Income Range | profile_data.income_range |
| 12 | Company* | profile_data.company_name |
| 13 | Total Score | response.total_score |
| 14 | Status Band | response.status_band |
| 15 | Questions Answered | response.questions_answered |
| 16 | Income Stream Score | category_scores['Income Stream'].score |
| 17 | Savings Habit Score | category_scores['Savings Habit'].score |
| 18 | Debt Management Score | category_scores['Debt Management'].score |
| 19 | Retirement Planning Score | category_scores['Retirement Planning'].score |
| 20 | Financial Protection Score | category_scores['Protecting Your Family'].score |
| 21 | Financial Knowledge Score | category_scores['Emergency Savings'].score |
| 22 | Leads Requested | 'Y' or 'N' |
| 23-27 | Action Plan 1-5 | response.insights[0-4].text |
| 28 | Submission Date | response.created_at |

> *Company column only included if `COMPANIES_MODULE_ENABLED=true` environment variable

### Export Filename Format

- **CSV:** `financial_clinic_responses_{YYYYMMDD_HHMMSS}.csv`
- **Excel:** `financial_clinic_responses_{YYYYMMDD_HHMMSS}.xlsx`

---

## Helper Functions

**Location:** Lines 21-269 in `simple_routes.py`

| Function | Lines | Purpose |
|----------|-------|---------|
| `filter_unique_users()` | 21-35 | Returns only the latest submission per email address |
| `calculate_age_from_dob()` | 37-55 | Calculates age from DOB string (DD/MM/YYYY or YYYY-MM-DD) |
| `filter_by_age_groups()` | 57-85 | Python-side filtering by age groups |
| `apply_demographic_filters()` | 87-179 | Applies SQL filters for demographics to query |
| `apply_date_range_filter()` | 181-234 | Applies date range filtering (7d, 30d, etc.) |
| `parse_filter_params()` | 236-269 | Parses comma-separated filter strings into lists |

---

## Implementation Notes

### 1. Profile Snapshot Feature

Submissions use a `profile_snapshot` JSON column to preserve historical profile data at submission time. The system falls back to the current profile table data if no snapshot exists.

```python
# Priority: profile_snapshot > current profile
if response.profile_snapshot:
    profile_data = response.profile_snapshot
else:
    profile_data = {...from profile table...}
```

### 2. Age Filtering Challenge

Date of birth is stored as a string in `DD/MM/YYYY` format, making SQL-based age filtering impossible. Age filtering is performed in Python after fetching results:

```python
if age_group:
    all_results = query.all()
    # Filter in Python
    for response, profile in all_results:
        age = calculate_age(profile.date_of_birth)
        # Apply age group logic
```

### 3. Two Company Systems

| System | Table | Purpose | Filter Parameter |
|--------|-------|---------|------------------|
| CompanyTracker | `company_trackers` | Legacy unique URLs | `company_id` |
| CompanyDetails | `company_details` | New company management | `company_name` |

### 4. Audit Logging

All CSV/Excel exports are logged to the `AuditLog` table:

```python
audit_log = AuditLog(
    user_id=current_user.id,
    action="simple_admin_export_csv",
    entity_type="financial_clinic_responses",
    details={"exported_count": len(responses), "filters": filters}
)
```

### 5. Mobile Number Formatting

CSV export auto-prepends UAE country code to mobile numbers:

```python
if not mobile_number.startswith('+'):
    mobile_number = '+971 ' + mobile_number
```

### 6. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COMPANIES_MODULE_ENABLED` | `"true"` | Controls visibility of Company column in exports |

---

## Database Models Used

- `FinancialClinicResponse` - Main submission data
- `FinancialClinicProfile` - User profile data
- `CompanyTracker` - Unique URL tracking
- `CompanyDetails` - Company management
- `AuditLog` - Export audit trail

---

## Related Frontend Components

- `FinancialClinicAdminDashboard.tsx` - Parent dashboard component
- `DatePickerComponent` - Date filter UI
- Various chart components that display submission analytics

---

*Document generated for internal development reference*
