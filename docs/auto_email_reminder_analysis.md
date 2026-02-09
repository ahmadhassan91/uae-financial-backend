# Auto Email Reminder Feature
## Analysis & Cost Estimate

**Date:** February 4, 2026  
**Status:** Proposal  

---

## 1. Requirement Summary
An automated system to send re-engagement emails to users (employees/leads) who have been inactive for a configurable period (e.g., 6 months).

**Key Features:**
*   **Dynamic Configuration:** Admin can set the inactivity threshold (number of days).
*   **Toggle Switch:** Admin can enable/disable the entire feature.
*   **Tracking:** Prevent spamming by logging when a reminder was sent.
*   **Audience:** All users with a `last_activity` date older than the threshold.

---

## 2. Technical Implementation

### 2.1 Backend (Python/FastAPI)
*   **Database Schema:**
    *   `SystemSettings` table to store configuration (`reminder_days`, `reminder_enabled`).
    *   `EmailLog` table to track `user_id`, `sent_at`, `email_type`.
*   **Scheduled Task:**
    *   A daily cron job (e.g., via `apscheduler` or Heroku Scheduler).
    *   Logic:
        1.  Fetch setting. If disabled, exit.
        2.  Query users where `last_activity < (now - days)`.
        3.  Exclude users who received a reminder recently (e.g., within last 30 days).
        4.  Send email via SMTP/SendGrid.
        5.  Log the event.

### 2.2 Frontend (React)
*   **System Management Tab:**
    *   Add a new card "Auto Email Settings".
    *   Input field: "Inactivity Threshold (Days)".
    *   Switch: "Enable Reminders".
    *   Save button.

### 2.3 Email Template
*   Design a simple HTML template: "We havne't seen you in a while! Check your financial health score again."

---

## 3. Effort Breakdown

| Module | Task | Est. Effort |
|--------|------|-------------|
| Database | Schema migration (`SystemSettings`, `EmailLog`) | 2 Hours |
| Backend | Scheduled Job logic & Email Service integration | 3 Hours |
| Frontend | Admin interface for settings | 2 Hours |
| Q/A | Testing & Verification | 1 Hour |
| **Total** | | **8 Hours** |

---

## 4. Cost Estimate

**Fixed Price:** **$450 - $500**  
*(Separate from CRM Integration)*

---

## 5. Next Steps
If approved:
1.  Approve quote.
2.  Provide email content (Subject, Body text).
3.  We implement and deploy to UAT.
