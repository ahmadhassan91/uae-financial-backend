# White Label Solution - Feature Breakdown

## Overview

Enable corporate clients to have their own branded Financial Clinic experience with custom subdomains, logos, and dedicated admin access.

---

## Feature 1: White Label Management Module

| Item | Description |
|------|-------------|
| **Purpose** | Central hub for creating and managing white-labeled companies |
| **Location** | New tab in Admin Dashboard |
| **Capabilities** | Create, edit, enable/disable white-label companies |

---

## Feature 2: Custom Subdomain/URL Generation

| Item | Description |
|------|-------------|
| **Purpose** | Unique URL for each corporate client |
| **Format Options** | `financialclinic.ae/clustox` OR `clustox.financialclinic.ae` |
| **Auto-generated** | System generates URL based on company name |
| **Editable** | Admin can customize the slug |

---

## Feature 3: Company Logo Upload & Branding

| Item | Description |
|------|-------------|
| **Purpose** | Display client's logo on their white-labeled survey |
| **Placement** | Next to National Bonds logo (design to be confirmed) |
| **Format** | PNG/JPG upload via admin panel |
| **Preview** | Visual preview before activation |

---

## Feature 4: Submission & Lead Tracking

| Item | Description |
|------|-------------|
| **Purpose** | Track all submissions from each white-labeled subdomain |
| **Admin Filter** | New "White Label" filter in admin analytics |
| **Data Captured** | All standard profile + response data |
| **Attribution** | Each submission linked to originating white-label company |

---

## Feature 5: View-Only Company Admin Access

| Item | Description |
|------|-------------|
| **Purpose** | Allow corporate clients to view their own data |
| **Access Level** | View-only (no editing, no exports) |
| **Credentials** | Auto-generated username/password |
| **Dashboard** | Simplified view showing only Overview and Submissions |
| **Scope** | Only data from their subdomain visible |

---

## Feature 6: Question Variations Support

| Item | Description |
|------|-------------|
| **Purpose** | Allow custom question sets per white-label client |
| **Default Option** | Standard Financial Clinic questions available |
| **Custom Option** | Assign specific question variation set |
| **Existing Feature** | Leverages current Question Variations module |

---

## Feature 7: Consolidated CSV Export (Separate Scope)

| Item | Description |
|------|-------------|
| **Purpose** | Single export combining Submissions, Leads, and Incompletes |
| **Status Column** | "Submission" / "Lead" / "Incomplete" |
| **Fields** | Standard profile data + scores |
| **Use Case** | CRM upload preparation for Phase 2 integration |

---

## Summary Table

| Feature | Description | Priority |
|---------|-------------|----------|
| White Label Module | Admin management interface | High |
| Subdomain Generation | Custom URLs per company | High |
| Logo Upload | Company branding on survey | High |
| Tracking & Filtering | Track submissions by white-label | High |
| Company Admin Access | View-only dashboard for clients | High |
| Question Variations | Custom questions per company | Medium |
| Consolidated Export | Combined CSV with status | Medium |

---

## Timeline Estimate

| Phase | Features | Duration |
|-------|----------|----------|
| Phase 1 | Backend setup, database, module | 4-5 days |
| Phase 2 | Subdomain routing, logo display | 3-4 days |
| Phase 3 | Company admin dashboard | 3-4 days |
| Phase 4 | Testing & refinement | 2-3 days |
| **Total** | | **12-16 days** |
