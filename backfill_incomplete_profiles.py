import json
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    inc_result = conn.execute(text(
        'SELECT id, email, phone_number, responses FROM incomplete_surveys ORDER BY id DESC'
    ))
    incomplete = inc_result.fetchall()

    updated = 0
    skipped = 0

    for row in incomplete:
        inc_id, email, phone, responses = row
        responses = responses or {}

        if responses.get('name') or responses.get('gender'):
            skipped += 1
            continue

        if not email:
            print(f"  INC-{inc_id}: no email, skipping")
            skipped += 1
            continue

        profile_result = conn.execute(text(
            """SELECT name, date_of_birth, gender, nationality, children,
                      employment_status, income_range, emirate, email, mobile_number
               FROM financial_clinic_profiles
               WHERE LOWER(email) = LOWER(:email)
               ORDER BY updated_at DESC LIMIT 1"""
        ), {'email': email})
        profile = profile_result.fetchone()

        if not profile:
            print(f"  INC-{inc_id} ({email}): no matching profile, skipping")
            skipped += 1
            continue

        updated_responses = {
            **responses,
            'name': profile[0] or '',
            'date_of_birth': str(profile[1]) if profile[1] else '',
            'gender': profile[2] or '',
            'nationality': profile[3] or '',
            'children': profile[4] if profile[4] is not None else '',
            'employment_status': profile[5] or '',
            'income_range': profile[6] or '',
            'emirate': profile[7] or '',
            'email': profile[8] or email,
            'mobile_number': profile[9] or phone or '',
        }

        conn.execute(
            text("UPDATE incomplete_surveys SET responses = cast(:r as jsonb) WHERE id = :id"),
            {'r': json.dumps(updated_responses), 'id': inc_id}
        )

        print(f"  OK INC-{inc_id} ({email}): name={profile[0]}, gender={profile[2]}, nationality={profile[3]}, emirate={profile[7]}")
        updated += 1

    conn.commit()
    print(f"\nResult: {updated} updated, {skipped} skipped")
