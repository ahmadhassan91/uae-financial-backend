# Implementation Plan - Leads & Submissions Enhancement

## Date: January 15, 2026

## Issues to Fix

### 1. Profile Update Issue ❗ CRITICAL
**Problem**: When a user submits a survey with the same email but different phone/company, ALL previous submissions get their profile information overwritten.

**Root Cause**: In `financial_clinic_routes.py` lines 451-456, the code updates the existing profile object directly, which affects all submissions linked to that profile.

**Solution**: 
- Do NOT update existing profile records
- Keep profile data immutable once created  
- Each submission should maintain its own snapshot of profile data at submission time
- Alternative: Store profile snapshot in `FinancialClinicResponse` table

### 2. Leads Enhancements
**Requirements**:
- Add insights (action plan columns) to leads export
- Add date range filter to leads API
- Include Unique URL name and Company/Employer name in CSV export

**Files to modify**:
- `app/consultations/routes.py` - Update `/admin/export` endpoint
- Add date range parameters
- Include insights columns in CSV
- Add company tracker information

### 3. Submissions Enhancement
**Requirements**:
- Add "Leads requested" Y/N column to submissions export
- Track if a session requested a lead (consultation request)

**Files to modify**:
- Migration already created ✅
- `app/surveys/financial_clinic_routes.py` - Set `leads_requested` when consultation is requested
- Admin export endpoints to include this column

## Implementation Steps

### Step 1: Fix Profile Update Issue
File: `app/surveys/financial_clinic_routes.py`

Change approach from:
```python
if existing_profile:
    # Update existing profile
    for key, value in profile_data.items():
        setattr(existing_profile, key, value)
```

To:
```python
if existing_profile:
    # DO NOT update profile - keep historical data intact
    profile = existing_profile
    logger.info(f"Using existing profile (ID: {profile.id}) without modification")
```

### Step 2: Add Profile Snapshot to Response
Option A: Store current profile data in FinancialClinicResponse
- Add columns: `profile_snapshot` (JSON field)
- Contains: name, phone, company at time of submission

Option B: Accept that profile is "current" data
- Document that profile shows latest information
- Historical tracking via audit logs

**Decision**: Go with Option A for data integrity

### Step 3: Update Leads Export
Add to CSV:
- Insights columns (top 3-5 action items)
- Unique URL name (from CompanyTracker)
- Date range filters

### Step 4: Update Submissions Export  
Add column:
- "Leads Requested" (Y/N)

## Files to Modify

1. ✅ Migration created: `2026_01_15_1343-51859804e36c_add_leads_requested_to_financial_clinic_responses.py`
2. `app/models.py` - ✅ Already has `leads_requested` field
3. `app/surveys/financial_clinic_routes.py` - Fix profile update logic
4. `app/consultations/routes.py` - Enhance leads export
5. Admin export routes - Add submissions export with leads_requested

## Testing Checklist

- [ ] User submits survey with email A, phone 1, company X
- [ ] Same user submits again with email A, phone 2, company Y
- [ ] Verify first submission still shows phone 1, company X
- [ ] Verify second submission shows phone 2, company Y
- [ ] Leads export includes date range filter
- [ ] Leads export includes insights columns
- [ ] Leads export includes Unique URL and Company name
- [ ] Submissions export includes "Leads Requested" column
