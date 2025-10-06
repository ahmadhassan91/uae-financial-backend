"""Sample Arabic translations for the financial health assessment."""

# Sample Arabic translations for questions
ARABIC_QUESTIONS = {
    "q1_income_stability": {
        "text": "كيف تصف استقرار دخلك الشهري؟",
        "options": [
            {"value": 1, "label": "غير مستقر على الإطلاق"},
            {"value": 2, "label": "غير مستقر إلى حد ما"},
            {"value": 3, "label": "مستقر إلى حد ما"},
            {"value": 4, "label": "مستقر جداً"},
            {"value": 5, "label": "مستقر تماماً"}
        ]
    },
    "q2_income_sources": {
        "text": "كم عدد مصادر الدخل لديك؟",
        "options": [
            {"value": 1, "label": "مصدر واحد فقط"},
            {"value": 2, "label": "مصدران"},
            {"value": 3, "label": "ثلاثة مصادر"},
            {"value": 4, "label": "أربعة مصادر"},
            {"value": 5, "label": "خمسة مصادر أو أكثر"}
        ]
    },
    "q3_budget_tracking": {
        "text": "كم مرة تراجع ميزانيتك الشخصية؟",
        "options": [
            {"value": 1, "label": "لا أراجعها أبداً"},
            {"value": 2, "label": "نادراً"},
            {"value": 3, "label": "أحياناً"},
            {"value": 4, "label": "شهرياً"},
            {"value": 5, "label": "أسبوعياً أو أكثر"}
        ]
    },
    "q4_expense_control": {
        "text": "إلى أي مدى تشعر بالسيطرة على نفقاتك؟",
        "options": [
            {"value": 1, "label": "لا أشعر بالسيطرة على الإطلاق"},
            {"value": 2, "label": "سيطرة قليلة"},
            {"value": 3, "label": "سيطرة متوسطة"},
            {"value": 4, "label": "سيطرة جيدة"},
            {"value": 5, "label": "سيطرة كاملة"}
        ]
    },
    "q5_emergency_fund": {
        "text": "كم شهراً يمكن أن تغطي نفقاتك من مدخراتك الطارئة؟",
        "options": [
            {"value": 1, "label": "أقل من شهر واحد"},
            {"value": 2, "label": "1-2 شهر"},
            {"value": 3, "label": "3-4 أشهر"},
            {"value": 4, "label": "5-6 أشهر"},
            {"value": 5, "label": "أكثر من 6 أشهر"}
        ]
    },
    "q6_savings_habit": {
        "text": "كم مرة تدخر من راتبك الشهري؟",
        "options": [
            {"value": 1, "label": "لا أدخر أبداً"},
            {"value": 2, "label": "نادراً"},
            {"value": 3, "label": "أحياناً"},
            {"value": 4, "label": "معظم الأشهر"},
            {"value": 5, "label": "كل شهر"}
        ]
    },
    "q7_debt_burden": {
        "text": "ما نسبة دخلك الشهري التي تذهب لسداد الديون؟",
        "options": [
            {"value": 5, "label": "لا توجد ديون"},
            {"value": 4, "label": "أقل من 10%"},
            {"value": 3, "label": "10-30%"},
            {"value": 2, "label": "30-50%"},
            {"value": 1, "label": "أكثر من 50%"}
        ]
    },
    "q8_debt_management": {
        "text": "كيف تدير ديونك الحالية؟",
        "options": [
            {"value": 1, "label": "أواجه صعوبة في السداد"},
            {"value": 2, "label": "أسدد الحد الأدنى فقط"},
            {"value": 3, "label": "أسدد أكثر من الحد الأدنى أحياناً"},
            {"value": 4, "label": "أسدد أكثر من الحد الأدنى دائماً"},
            {"value": 5, "label": "لا توجد ديون"}
        ]
    },
    "q9_financial_goals": {
        "text": "هل لديك أهداف مالية واضحة ومكتوبة؟",
        "options": [
            {"value": 1, "label": "لا توجد أهداف محددة"},
            {"value": 2, "label": "أهداف غامضة في ذهني"},
            {"value": 3, "label": "أهداف واضحة لكن غير مكتوبة"},
            {"value": 4, "label": "أهداف مكتوبة لكن بدون خطة"},
            {"value": 5, "label": "أهداف مكتوبة مع خطة واضحة"}
        ]
    },
    "q10_retirement_planning": {
        "text": "كم تدخر شهرياً للتقاعد؟",
        "options": [
            {"value": 1, "label": "لا أدخر للتقاعد"},
            {"value": 2, "label": "أقل من 5% من الراتب"},
            {"value": 3, "label": "5-10% من الراتب"},
            {"value": 4, "label": "10-15% من الراتب"},
            {"value": 5, "label": "أكثر من 15% من الراتب"}
        ]
    },
    "q11_investment_knowledge": {
        "text": "كيف تقيم معرفتك بالاستثمار؟",
        "options": [
            {"value": 1, "label": "لا أعرف شيئاً عن الاستثمار"},
            {"value": 2, "label": "معرفة محدودة جداً"},
            {"value": 3, "label": "معرفة أساسية"},
            {"value": 4, "label": "معرفة جيدة"},
            {"value": 5, "label": "معرفة متقدمة"}
        ]
    },
    "q12_investment_experience": {
        "text": "ما مدى خبرتك في الاستثمار؟",
        "options": [
            {"value": 1, "label": "لا توجد خبرة"},
            {"value": 2, "label": "خبرة قليلة (أقل من سنة)"},
            {"value": 3, "label": "خبرة متوسطة (1-3 سنوات)"},
            {"value": 4, "label": "خبرة جيدة (3-5 سنوات)"},
            {"value": 5, "label": "خبرة واسعة (أكثر من 5 سنوات)"}
        ]
    },
    "q13_risk_tolerance": {
        "text": "ما مدى استعدادك لتحمل المخاطر في الاستثمار؟",
        "options": [
            {"value": 1, "label": "لا أتحمل أي مخاطر"},
            {"value": 2, "label": "مخاطر قليلة جداً"},
            {"value": 3, "label": "مخاطر متوسطة"},
            {"value": 4, "label": "مخاطر عالية"},
            {"value": 5, "label": "مخاطر عالية جداً"}
        ]
    },
    "q14_diversification": {
        "text": "كيف تنوع استثماراتك؟",
        "options": [
            {"value": 1, "label": "لا أستثمر"},
            {"value": 2, "label": "استثمار واحد فقط"},
            {"value": 3, "label": "نوعان من الاستثمار"},
            {"value": 4, "label": "ثلاثة أنواع أو أكثر"},
            {"value": 5, "label": "محفظة متنوعة جداً"}
        ]
    },
    "q15_financial_stress": {
        "text": "كم مرة تشعر بالقلق بشأن وضعك المالي؟",
        "options": [
            {"value": 1, "label": "دائماً"},
            {"value": 2, "label": "غالباً"},
            {"value": 3, "label": "أحياناً"},
            {"value": 4, "label": "نادراً"},
            {"value": 5, "label": "أبداً"}
        ]
    },
    "q16_financial_confidence": {
        "text": "ما مدى ثقتك في قدرتك على اتخاذ قرارات مالية صحيحة؟",
        "options": [
            {"value": 1, "label": "لا أثق في قراراتي المالية"},
            {"value": 2, "label": "ثقة قليلة"},
            {"value": 3, "label": "ثقة متوسطة"},
            {"value": 4, "label": "ثقة عالية"},
            {"value": 5, "label": "ثقة كاملة"}
        ]
    }
}

# Sample Arabic translations for UI elements
ARABIC_UI_TRANSLATIONS = {
    "welcome_message": "مرحباً بك في تقييم الصحة المالية",
    "start_survey": "ابدأ التقييم",
    "next_question": "السؤال التالي",
    "previous_question": "السؤال السابق",
    "submit_survey": "إرسال التقييم",
    "your_results": "نتائجك",
    "download_pdf": "تحميل التقرير",
    "send_email": "إرسال بالبريد الإلكتروني",
    "register_account": "إنشاء حساب",
    "language_selector": "اختر اللغة",
    "financial_health_score": "درجة الصحة المالية",
    "recommendations": "التوصيات",
    "budgeting": "إدارة الميزانية",
    "savings": "الادخار",
    "debt_management": "إدارة الديون",
    "financial_planning": "التخطيط المالي",
    "investment_knowledge": "المعرفة الاستثمارية",
    "excellent": "ممتاز",
    "good": "جيد",
    "fair": "مقبول",
    "poor": "ضعيف",
    "very_poor": "ضعيف جداً",
    "personal_information": "المعلومات الشخصية",
    "first_name": "الاسم الأول",
    "last_name": "اسم العائلة",
    "age": "العمر",
    "gender": "الجنس",
    "male": "ذكر",
    "female": "أنثى",
    "nationality": "الجنسية",
    "emirate": "الإمارة",
    "employment_status": "الحالة الوظيفية",
    "monthly_income": "الدخل الشهري",
    "household_size": "عدد أفراد الأسرة",
    "children": "الأطفال",
    "yes": "نعم",
    "no": "لا",
    "email": "البريد الإلكتروني",
    "phone_number": "رقم الهاتف",
    "save": "حفظ",
    "cancel": "إلغاء",
    "edit": "تعديل",
    "delete": "حذف",
    "confirm": "تأكيد",
    "loading": "جاري التحميل...",
    "error": "خطأ",
    "success": "نجح",
    "warning": "تحذير",
    "info": "معلومات"
}

# Sample Arabic recommendations
ARABIC_RECOMMENDATIONS = {
    "budgeting_basic": {
        "title": "تحسين إدارة الميزانية",
        "text": "ننصحك بإنشاء ميزانية شهرية مفصلة لتتبع دخلك ونفقاتك. استخدم تطبيقات إدارة المال أو جداول بيانات بسيطة لمراقبة إنفاقك اليومي.",
        "extra_data": {
            "action_steps": [
                "سجل جميع مصادر دخلك الشهري",
                "اكتب جميع نفقاتك الثابتة والمتغيرة",
                "حدد أولويات الإنفاق",
                "راجع ميزانيتك أسبوعياً"
            ],
            "cultural_note": "يُنصح بتخصيص جزء من الدخل للزكاة والصدقات حسب التعاليم الإسلامية"
        }
    },
    "savings_emergency": {
        "title": "بناء صندوق الطوارئ",
        "text": "من المهم جداً أن يكون لديك صندوق طوارئ يغطي نفقاتك لمدة 3-6 أشهر. ابدأ بادخار مبلغ صغير شهرياً حتى تصل للهدف المطلوب.",
        "extra_data": {
            "action_steps": [
                "احسب نفقاتك الشهرية الأساسية",
                "اضرب هذا المبلغ في 6 أشهر",
                "ادخر 10-20% من راتبك شهرياً",
                "ضع المدخرات في حساب منفصل"
            ],
            "local_resources": [
                "حسابات الادخار في البنوك الإماراتية",
                "صناديق الاستثمار قصيرة المدى"
            ]
        }
    },
    "debt_management": {
        "title": "إدارة الديون بفعالية",
        "text": "إذا كان لديك ديون متعددة، ركز على سداد الديون ذات الفوائد العالية أولاً. فكر في توحيد الديون إذا كان ذلك سيقلل من الفوائد الإجمالية.",
        "extra_data": {
            "action_steps": [
                "اكتب قائمة بجميع ديونك ومعدلات الفائدة",
                "رتب الديون حسب معدل الفائدة من الأعلى للأقل",
                "ادفع الحد الأدنى لجميع الديون",
                "ادفع مبلغاً إضافياً للدين ذي الفائدة الأعلى"
            ],
            "islamic_finance_note": "فكر في البدائل المصرفية الإسلامية التي تتوافق مع أحكام الشريعة"
        }
    },
    "investment_basic": {
        "title": "بداية الاستثمار",
        "text": "ابدأ رحلتك الاستثمارية بتعلم الأساسيات أولاً. فكر في الاستثمار في صناديق المؤشرات أو الصناديق المتنوعة كبداية آمنة.",
        "extra_data": {
            "action_steps": [
                "تعلم أساسيات الاستثمار",
                "حدد أهدافك الاستثمارية",
                "ابدأ بمبلغ صغير",
                "نوع استثماراتك تدريجياً"
            ],
            "local_options": [
                "صناديق الاستثمار في البنوك المحلية",
                "سوق دبي المالي",
                "سوق أبوظبي للأوراق المالية"
            ],
            "islamic_finance_note": "تتوفر صناديق استثمارية متوافقة مع الشريعة الإسلامية"
        }
    },
    "retirement_planning": {
        "title": "التخطيط للتقاعد",
        "text": "لم يفت الأوان بعد للبدء في التخطيط للتقاعد. ادخر ما لا يقل عن 10-15% من دخلك للتقاعد واستفد من أي برامج تقاعد تقدمها شركتك.",
        "extra_data": {
            "action_steps": [
                "احسب احتياجاتك المالية عند التقاعد",
                "ادخر نسبة ثابتة من راتبك شهرياً",
                "استفد من برامج التقاعد في العمل",
                "فكر في استثمارات طويلة المدى"
            ],
            "uae_specific": [
                "صندوق المعاشات والتأمينات الاجتماعية",
                "برامج التقاعد في الشركات الحكومية",
                "خطط التقاعد في البنوك المحلية"
            ]
        }
    }
}


def get_sample_arabic_questions():
    """Get sample Arabic question translations."""
    return ARABIC_QUESTIONS


def get_sample_arabic_ui():
    """Get sample Arabic UI translations."""
    return ARABIC_UI_TRANSLATIONS


def get_sample_arabic_recommendations():
    """Get sample Arabic recommendation translations."""
    return ARABIC_RECOMMENDATIONS