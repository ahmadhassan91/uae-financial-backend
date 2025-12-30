--
-- PostgreSQL database dump
--

\restrict LRv3ld1VmtCRePjTjfSbcR6ENKPrn187u3Tjtj44GND4IiYLdOY8xsWVU6o7U6M

-- Dumped from database version 14.19 (Homebrew)
-- Dumped by pg_dump version 14.19 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.survey_responses DROP CONSTRAINT IF EXISTS survey_responses_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.survey_responses DROP CONSTRAINT IF EXISTS survey_responses_customer_profile_id_fkey;
ALTER TABLE IF EXISTS ONLY public.simple_sessions DROP CONSTRAINT IF EXISTS simple_sessions_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.report_deliveries DROP CONSTRAINT IF EXISTS report_deliveries_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.report_deliveries DROP CONSTRAINT IF EXISTS report_deliveries_survey_response_id_fkey;
ALTER TABLE IF EXISTS ONLY public.report_access_logs DROP CONSTRAINT IF EXISTS report_access_logs_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.report_access_logs DROP CONSTRAINT IF EXISTS report_access_logs_report_delivery_id_fkey;
ALTER TABLE IF EXISTS ONLY public.recommendations DROP CONSTRAINT IF EXISTS recommendations_survey_response_id_fkey;
ALTER TABLE IF EXISTS ONLY public.incomplete_surveys DROP CONSTRAINT IF EXISTS incomplete_surveys_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.incomplete_surveys DROP CONSTRAINT IF EXISTS incomplete_surveys_customer_profile_id_fkey;
ALTER TABLE IF EXISTS ONLY public.survey_responses DROP CONSTRAINT IF EXISTS fk_survey_responses_company_tracker;
ALTER TABLE IF EXISTS ONLY public.customer_profiles DROP CONSTRAINT IF EXISTS customer_profiles_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.company_question_sets DROP CONSTRAINT IF EXISTS company_question_sets_company_tracker_id_fkey;
ALTER TABLE IF EXISTS ONLY public.company_assessments DROP CONSTRAINT IF EXISTS company_assessments_company_tracker_id_fkey;
ALTER TABLE IF EXISTS ONLY public.audit_logs DROP CONSTRAINT IF EXISTS audit_logs_user_id_fkey;
DROP INDEX IF EXISTS public.ix_users_username;
DROP INDEX IF EXISTS public.ix_users_id;
DROP INDEX IF EXISTS public.ix_users_email;
DROP INDEX IF EXISTS public.ix_survey_responses_language;
DROP INDEX IF EXISTS public.ix_survey_responses_id;
DROP INDEX IF EXISTS public.ix_survey_responses_company_tracker_id;
DROP INDEX IF EXISTS public.ix_simple_sessions_session_id;
DROP INDEX IF EXISTS public.ix_simple_sessions_id;
DROP INDEX IF EXISTS public.ix_report_deliveries_user_id;
DROP INDEX IF EXISTS public.ix_report_deliveries_survey_response_id;
DROP INDEX IF EXISTS public.ix_report_deliveries_id;
DROP INDEX IF EXISTS public.ix_report_deliveries_delivery_type;
DROP INDEX IF EXISTS public.ix_report_deliveries_delivery_status;
DROP INDEX IF EXISTS public.ix_report_deliveries_created_at;
DROP INDEX IF EXISTS public.ix_report_access_logs_user_id;
DROP INDEX IF EXISTS public.ix_report_access_logs_report_delivery_id;
DROP INDEX IF EXISTS public.ix_report_access_logs_id;
DROP INDEX IF EXISTS public.ix_report_access_logs_accessed_at;
DROP INDEX IF EXISTS public.ix_recommendations_id;
DROP INDEX IF EXISTS public.ix_question_variations_language;
DROP INDEX IF EXISTS public.ix_question_variations_is_active;
DROP INDEX IF EXISTS public.ix_question_variations_id;
DROP INDEX IF EXISTS public.ix_question_variations_base_question_id;
DROP INDEX IF EXISTS public.ix_localized_content_language;
DROP INDEX IF EXISTS public.ix_localized_content_is_active;
DROP INDEX IF EXISTS public.ix_localized_content_id;
DROP INDEX IF EXISTS public.ix_localized_content_content_type;
DROP INDEX IF EXISTS public.ix_localized_content_content_id;
DROP INDEX IF EXISTS public.ix_incomplete_surveys_session_id;
DROP INDEX IF EXISTS public.ix_incomplete_surveys_id;
DROP INDEX IF EXISTS public.ix_demographic_rules_priority;
DROP INDEX IF EXISTS public.ix_demographic_rules_is_active;
DROP INDEX IF EXISTS public.ix_demographic_rules_id;
DROP INDEX IF EXISTS public.ix_customer_profiles_nationality;
DROP INDEX IF EXISTS public.ix_customer_profiles_id;
DROP INDEX IF EXISTS public.ix_customer_profiles_emirate;
DROP INDEX IF EXISTS public.ix_customer_profiles_age;
DROP INDEX IF EXISTS public.ix_company_trackers_unique_url;
DROP INDEX IF EXISTS public.ix_company_trackers_id;
DROP INDEX IF EXISTS public.ix_company_question_sets_is_active;
DROP INDEX IF EXISTS public.ix_company_question_sets_id;
DROP INDEX IF EXISTS public.ix_company_question_sets_company_tracker_id;
DROP INDEX IF EXISTS public.ix_company_assessments_id;
DROP INDEX IF EXISTS public.ix_audit_logs_id;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.survey_responses DROP CONSTRAINT IF EXISTS survey_responses_pkey;
ALTER TABLE IF EXISTS ONLY public.simple_sessions DROP CONSTRAINT IF EXISTS simple_sessions_pkey;
ALTER TABLE IF EXISTS ONLY public.report_deliveries DROP CONSTRAINT IF EXISTS report_deliveries_pkey;
ALTER TABLE IF EXISTS ONLY public.report_access_logs DROP CONSTRAINT IF EXISTS report_access_logs_pkey;
ALTER TABLE IF EXISTS ONLY public.recommendations DROP CONSTRAINT IF EXISTS recommendations_pkey;
ALTER TABLE IF EXISTS ONLY public.question_variations DROP CONSTRAINT IF EXISTS question_variations_pkey;
ALTER TABLE IF EXISTS ONLY public.localized_content DROP CONSTRAINT IF EXISTS localized_content_pkey;
ALTER TABLE IF EXISTS ONLY public.incomplete_surveys DROP CONSTRAINT IF EXISTS incomplete_surveys_pkey;
ALTER TABLE IF EXISTS ONLY public.demographic_rules DROP CONSTRAINT IF EXISTS demographic_rules_pkey;
ALTER TABLE IF EXISTS ONLY public.customer_profiles DROP CONSTRAINT IF EXISTS customer_profiles_pkey;
ALTER TABLE IF EXISTS ONLY public.company_trackers DROP CONSTRAINT IF EXISTS company_trackers_pkey;
ALTER TABLE IF EXISTS ONLY public.company_question_sets DROP CONSTRAINT IF EXISTS company_question_sets_pkey;
ALTER TABLE IF EXISTS ONLY public.company_assessments DROP CONSTRAINT IF EXISTS company_assessments_pkey;
ALTER TABLE IF EXISTS ONLY public.audit_logs DROP CONSTRAINT IF EXISTS audit_logs_pkey;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.survey_responses ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.simple_sessions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.report_deliveries ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.report_access_logs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.recommendations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.question_variations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.localized_content ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.incomplete_surveys ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.demographic_rules ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.customer_profiles ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.company_trackers ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.company_question_sets ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.company_assessments ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.audit_logs ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.survey_responses_id_seq;
DROP TABLE IF EXISTS public.survey_responses;
DROP SEQUENCE IF EXISTS public.simple_sessions_id_seq;
DROP TABLE IF EXISTS public.simple_sessions;
DROP SEQUENCE IF EXISTS public.report_deliveries_id_seq;
DROP TABLE IF EXISTS public.report_deliveries;
DROP SEQUENCE IF EXISTS public.report_access_logs_id_seq;
DROP TABLE IF EXISTS public.report_access_logs;
DROP SEQUENCE IF EXISTS public.recommendations_id_seq;
DROP TABLE IF EXISTS public.recommendations;
DROP SEQUENCE IF EXISTS public.question_variations_id_seq;
DROP TABLE IF EXISTS public.question_variations;
DROP SEQUENCE IF EXISTS public.localized_content_id_seq;
DROP TABLE IF EXISTS public.localized_content;
DROP SEQUENCE IF EXISTS public.incomplete_surveys_id_seq;
DROP TABLE IF EXISTS public.incomplete_surveys;
DROP SEQUENCE IF EXISTS public.demographic_rules_id_seq;
DROP TABLE IF EXISTS public.demographic_rules;
DROP SEQUENCE IF EXISTS public.customer_profiles_id_seq;
DROP TABLE IF EXISTS public.customer_profiles;
DROP SEQUENCE IF EXISTS public.company_trackers_id_seq;
DROP TABLE IF EXISTS public.company_trackers;
DROP SEQUENCE IF EXISTS public.company_question_sets_id_seq;
DROP TABLE IF EXISTS public.company_question_sets;
DROP SEQUENCE IF EXISTS public.company_assessments_id_seq;
DROP TABLE IF EXISTS public.company_assessments;
DROP SEQUENCE IF EXISTS public.audit_logs_id_seq;
DROP TABLE IF EXISTS public.audit_logs;
DROP TABLE IF EXISTS public.alembic_version;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    user_id integer,
    action character varying(100) NOT NULL,
    entity_type character varying(50),
    entity_id integer,
    details json,
    ip_address character varying(45),
    user_agent character varying(500),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: company_assessments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.company_assessments (
    id integer NOT NULL,
    company_tracker_id integer NOT NULL,
    employee_id character varying(100),
    department character varying(100),
    position_level character varying(50),
    responses json NOT NULL,
    overall_score double precision NOT NULL,
    category_scores json NOT NULL,
    completion_time integer,
    ip_address character varying(45),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: company_assessments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.company_assessments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: company_assessments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.company_assessments_id_seq OWNED BY public.company_assessments.id;


--
-- Name: company_question_sets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.company_question_sets (
    id integer NOT NULL,
    company_tracker_id integer NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    base_questions json NOT NULL,
    custom_questions json,
    excluded_questions json,
    question_variations json,
    demographic_rules json,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


--
-- Name: company_question_sets_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.company_question_sets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: company_question_sets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.company_question_sets_id_seq OWNED BY public.company_question_sets.id;


--
-- Name: company_trackers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.company_trackers (
    id integer NOT NULL,
    company_name character varying(200) NOT NULL,
    company_email character varying(255) NOT NULL,
    contact_person character varying(200) NOT NULL,
    phone_number character varying(20),
    unique_url character varying(100) NOT NULL,
    is_active boolean,
    total_assessments integer,
    average_score double precision,
    custom_branding json,
    notification_settings json,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone,
    question_set_config json,
    demographic_rules_config json,
    localization_settings json,
    report_branding json,
    admin_users json
);


--
-- Name: company_trackers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.company_trackers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: company_trackers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.company_trackers_id_seq OWNED BY public.company_trackers.id;


--
-- Name: customer_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customer_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    age integer NOT NULL,
    gender character varying(20) NOT NULL,
    nationality character varying(100) NOT NULL,
    emirate character varying(50) NOT NULL,
    city character varying(100),
    employment_status character varying(50) NOT NULL,
    industry character varying(100),
    "position" character varying(100),
    monthly_income character varying(50) NOT NULL,
    household_size integer NOT NULL,
    phone_number character varying(20),
    preferred_language character varying(10),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone,
    children character varying(3) DEFAULT 'No'::character varying NOT NULL,
    education_level character varying(50),
    years_in_uae integer,
    family_status character varying(50),
    housing_status character varying(50),
    banking_relationship character varying(100),
    investment_experience character varying(50),
    financial_goals json,
    preferred_communication character varying(20) DEFAULT 'email'::character varying,
    islamic_finance_preference boolean DEFAULT false
);


--
-- Name: customer_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.customer_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: customer_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.customer_profiles_id_seq OWNED BY public.customer_profiles.id;


--
-- Name: demographic_rules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.demographic_rules (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    conditions json NOT NULL,
    actions json NOT NULL,
    priority integer,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


--
-- Name: demographic_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.demographic_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: demographic_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.demographic_rules_id_seq OWNED BY public.demographic_rules.id;


--
-- Name: incomplete_surveys; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.incomplete_surveys (
    id integer NOT NULL,
    user_id integer,
    customer_profile_id integer,
    session_id character varying(255) NOT NULL,
    current_step integer,
    total_steps integer NOT NULL,
    responses json,
    started_at timestamp with time zone DEFAULT now(),
    last_activity timestamp with time zone DEFAULT now(),
    abandoned_at timestamp with time zone,
    email character varying(255),
    phone_number character varying(20),
    is_abandoned boolean,
    follow_up_sent boolean,
    follow_up_count integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


--
-- Name: incomplete_surveys_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.incomplete_surveys_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: incomplete_surveys_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.incomplete_surveys_id_seq OWNED BY public.incomplete_surveys.id;


--
-- Name: localized_content; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.localized_content (
    id integer NOT NULL,
    content_type character varying(50) NOT NULL,
    content_id character varying(100) NOT NULL,
    language character varying(5) NOT NULL,
    title character varying(500),
    text text NOT NULL,
    options json,
    extra_data json,
    version character varying(10),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


--
-- Name: localized_content_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.localized_content_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: localized_content_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.localized_content_id_seq OWNED BY public.localized_content.id;


--
-- Name: question_variations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.question_variations (
    id integer NOT NULL,
    base_question_id character varying(50) NOT NULL,
    variation_name character varying(100) NOT NULL,
    language character varying(5) NOT NULL,
    text text NOT NULL,
    options json NOT NULL,
    demographic_rules json,
    company_ids json,
    factor character varying(50) NOT NULL,
    weight integer NOT NULL,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


--
-- Name: question_variations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.question_variations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: question_variations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.question_variations_id_seq OWNED BY public.question_variations.id;


--
-- Name: recommendations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.recommendations (
    id integer NOT NULL,
    survey_response_id integer NOT NULL,
    category character varying(50) NOT NULL,
    title character varying(200) NOT NULL,
    description text NOT NULL,
    priority integer,
    action_steps json,
    resources json,
    expected_impact character varying(20),
    is_active boolean,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone
);


--
-- Name: recommendations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.recommendations_id_seq OWNED BY public.recommendations.id;


--
-- Name: report_access_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.report_access_logs (
    id integer NOT NULL,
    report_delivery_id integer NOT NULL,
    user_id integer,
    access_type character varying(20) NOT NULL,
    ip_address character varying(45),
    user_agent character varying(500),
    access_metadata json,
    accessed_at timestamp with time zone DEFAULT now()
);


--
-- Name: report_access_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.report_access_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: report_access_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.report_access_logs_id_seq OWNED BY public.report_access_logs.id;


--
-- Name: report_deliveries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.report_deliveries (
    id integer NOT NULL,
    survey_response_id integer NOT NULL,
    user_id integer NOT NULL,
    delivery_type character varying(20) NOT NULL,
    delivery_status character varying(20) NOT NULL,
    recipient_email character varying(255),
    file_path character varying(500),
    file_size integer,
    language character varying(5) NOT NULL,
    delivery_metadata json,
    error_message text,
    retry_count integer,
    delivered_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


--
-- Name: report_deliveries_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.report_deliveries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: report_deliveries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.report_deliveries_id_seq OWNED BY public.report_deliveries.id;


--
-- Name: simple_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.simple_sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    session_id character varying(255) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    is_active boolean,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: simple_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.simple_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: simple_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.simple_sessions_id_seq OWNED BY public.simple_sessions.id;


--
-- Name: survey_responses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.survey_responses (
    id integer NOT NULL,
    user_id integer NOT NULL,
    customer_profile_id integer NOT NULL,
    responses json NOT NULL,
    overall_score double precision NOT NULL,
    budgeting_score double precision NOT NULL,
    savings_score double precision NOT NULL,
    debt_management_score double precision NOT NULL,
    financial_planning_score double precision NOT NULL,
    investment_knowledge_score double precision NOT NULL,
    risk_tolerance character varying(20) NOT NULL,
    financial_goals json,
    completion_time integer,
    survey_version character varying(10),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone,
    question_set_id character varying(100),
    question_variations_used json,
    demographic_rules_applied json,
    language character varying(5) DEFAULT 'en'::character varying,
    company_tracker_id integer,
    email_sent boolean DEFAULT false,
    pdf_generated boolean DEFAULT false,
    report_downloads integer DEFAULT 0
);


--
-- Name: survey_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.survey_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: survey_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.survey_responses_id_seq OWNED BY public.survey_responses.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    username character varying(100) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    is_active boolean,
    is_admin boolean,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone,
    date_of_birth timestamp without time zone
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: company_assessments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.company_assessments ALTER COLUMN id SET DEFAULT nextval('public.company_assessments_id_seq'::regclass);


--
-- Name: company_question_sets id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.company_question_sets ALTER COLUMN id SET DEFAULT nextval('public.company_question_sets_id_seq'::regclass);


--
-- Name: company_trackers id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.company_trackers ALTER COLUMN id SET DEFAULT nextval('public.company_trackers_id_seq'::regclass);


--
-- Name: customer_profiles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_profiles ALTER COLUMN id SET DEFAULT nextval('public.customer_profiles_id_seq'::regclass);


--
-- Name: demographic_rules id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.demographic_rules ALTER COLUMN id SET DEFAULT nextval('public.demographic_rules_id_seq'::regclass);


--
-- Name: incomplete_surveys id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incomplete_surveys ALTER COLUMN id SET DEFAULT nextval('public.incomplete_surveys_id_seq'::regclass);


--
-- Name: localized_content id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.localized_content ALTER COLUMN id SET DEFAULT nextval('public.localized_content_id_seq'::regclass);


--
-- Name: question_variations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.question_variations ALTER COLUMN id SET DEFAULT nextval('public.question_variations_id_seq'::regclass);


--
-- Name: recommendations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recommendations ALTER COLUMN id SET DEFAULT nextval('public.recommendations_id_seq'::regclass);


--
-- Name: report_access_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.report_access_logs ALTER COLUMN id SET DEFAULT nextval('public.report_access_logs_id_seq'::regclass);


--
-- Name: report_deliveries id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.report_deliveries ALTER COLUMN id SET DEFAULT nextval('public.report_deliveries_id_seq'::regclass);


--
-- Name: simple_sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.simple_sessions ALTER COLUMN id SET DEFAULT nextval('public.simple_sessions_id_seq'::regclass);


--
-- Name: survey_responses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.survey_responses ALTER COLUMN id SET DEFAULT nextval('public.survey_responses_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
c483380ec75e
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.audit_logs (id, user_id, action, entity_type, entity_id, details, ip_address, user_agent, created_at) FROM stdin;
1	1	user_registered	user	1	{"email": "test@example.com", "username": "testuser"}	\N	\N	2025-10-02 18:07:51.324502+05
2	1	simple_login	user	1	{"email": "test@example.com", "session_id": "fgZfR6Yz16WpZr8FD2i-Klu83iMiUNVVnr-yvw5e20E"}	\N	\N	2025-10-02 18:09:28.613121+05
3	1	simple_login_failed	user	1	{"email": "test@example.com", "reason": "date_mismatch"}	\N	\N	2025-10-02 18:09:28.655357+05
4	\N	simple_login_failed	user	\N	{"email": "nonexistent@example.com", "reason": "user_not_found"}	\N	\N	2025-10-02 18:09:28.852004+05
5	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 0.0, "risk_tolerance": "moderate", "completion_time": 120}	\N	\N	2025-10-02 18:14:40.446868+05
6	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 0.0, "risk_tolerance": "moderate", "completion_time": 120}	\N	\N	2025-10-02 18:15:20.934312+05
7	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 0.0, "risk_tolerance": "moderate", "completion_time": 180}	\N	\N	2025-10-02 18:16:34.794118+05
8	2	user_registered	user	2	{"email": "comprehensive.test@example.com", "username": "comprehensive_test"}	\N	\N	2025-10-02 18:16:35.695174+05
9	2	simple_login	user	2	{"email": "comprehensive.test@example.com", "session_id": "qnlcqbsvvuG0ozUTCqfy92Xv3nsGPDw4J_YTHbHX72Q"}	\N	\N	2025-10-02 18:16:35.908612+05
10	2	simple_login_failed	user	2	{"email": "comprehensive.test@example.com", "reason": "date_mismatch"}	\N	\N	2025-10-02 18:16:36.085449+05
11	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 0.0, "risk_tolerance": "moderate", "completion_time": 180}	\N	\N	2025-10-02 18:19:25.489967+05
12	1	simple_login_failed	user	1	{"email": "test@example.com", "reason": "date_mismatch"}	\N	\N	2025-10-02 18:19:25.533063+05
13	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 0.0, "risk_tolerance": "moderate", "completion_time": 180}	\N	\N	2025-10-02 18:20:10.884309+05
14	1	simple_login_failed	user	1	{"email": "test@example.com", "reason": "date_mismatch"}	\N	\N	2025-10-02 18:20:10.905867+05
15	1	simple_login_failed	user	1	{"email": "test@example.com", "reason": "date_mismatch"}	\N	\N	2025-10-02 18:21:46.61051+05
16	1	simple_login_failed	user	1	{"email": "test@example.com", "reason": "date_mismatch"}	\N	\N	2025-10-02 18:21:46.640831+05
17	\N	guest_survey_started	incomplete_survey	1	{"session_id": "gmsloPLu1Uik9mxtHazXjgYD4--oJe-HtAxZCRreLMk", "total_steps": 10, "email": "test.incomplete@example.com"}	\N	\N	2025-10-02 18:50:41.859079+05
18	3	user_registered	user	3	{"email": "admin@example.com", "username": "admin_user"}	\N	\N	2025-10-02 18:50:42.484125+05
19	3	user_login	user	3	{"email": "admin@example.com"}	\N	\N	2025-10-02 18:50:42.526582+05
20	\N	guest_survey_started	incomplete_survey	2	{"session_id": "R11LNz82UYBLPhOY8HZsaisvMDyUaIc3HBhU7YIlj7A", "total_steps": 10, "email": "test.incomplete@example.com"}	\N	\N	2025-10-02 18:55:39.920014+05
21	3	user_login	user	3	{"email": "admin@example.com"}	\N	\N	2025-10-02 18:55:39.991018+05
22	\N	guest_survey_started	incomplete_survey	3	{"session_id": "cTYEaHNZgHwaX2ti_LfvVM1fCzWRbz8c5FAjpuE-fWc", "total_steps": 10, "email": "test.incomplete@example.com"}	\N	\N	2025-10-02 18:56:24.428753+05
23	3	user_login	user	3	{"email": "admin@example.com"}	\N	\N	2025-10-02 18:56:24.655661+05
24	\N	survey_completed_from_incomplete	incomplete_survey	3	{"session_id": "cTYEaHNZgHwaX2ti_LfvVM1fCzWRbz8c5FAjpuE-fWc"}	\N	\N	2025-10-02 18:56:25.642099+05
25	4	user_registered	user	4	{"email": "admin@nationalbonds.ae", "username": "nb_admin"}	\N	\N	2025-10-02 19:10:00.767932+05
26	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-02 19:10:00.821305+05
27	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-02 19:10:22.6176+05
28	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-02 19:16:07.997427+05
29	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-02 19:29:32.050623+05
30	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-02 19:32:21.522246+05
31	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-02 19:35:46.834299+05
32	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-02 19:56:04.312777+05
33	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-02 20:02:03.387478+05
34	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-02 20:03:31.472796+05
35	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-02 20:05:14.051214+05
36	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-02 20:07:38.325323+05
37	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-02 20:08:03.416092+05
38	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 0.0, "risk_tolerance": "moderate", "completion_time": 120}	\N	\N	2025-10-02 20:50:08.817923+05
39	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 0.0, "risk_tolerance": "moderate", "completion_time": 120}	\N	\N	2025-10-02 20:51:18.845398+05
40	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 0.0, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-02 20:54:50.153674+05
41	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 0.0, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-02 21:05:11.934102+05
42	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 0.0, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-03 00:01:51.56918+05
43	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 0.0, "risk_tolerance": "moderate", "completion_time": 180}	\N	\N	2025-10-03 00:17:42.400201+05
44	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 37.92, "risk_tolerance": "low", "completion_time": 180}	\N	\N	2025-10-03 00:22:50.437488+05
45	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 57.08, "risk_tolerance": "low", "completion_time": 180}	\N	\N	2025-10-03 00:23:52.504225+05
46	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 58.33, "risk_tolerance": "low", "completion_time": 240}	\N	\N	2025-10-03 00:29:57.005833+05
47	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 40.0, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-03 00:44:06.049155+05
48	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 62.51, "risk_tolerance": "low", "completion_time": 240}	\N	\N	2025-10-03 01:06:00.252372+05
49	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 62.51, "risk_tolerance": "low", "completion_time": 240}	\N	\N	2025-10-03 01:07:45.169173+05
50	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 62.67, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-03 17:42:47.062029+05
51	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-04 00:45:11.736372+05
52	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-04 00:45:23.50251+05
53	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-04 00:45:39.340155+05
54	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-04 01:45:30.251561+05
55	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-04 11:25:22.919037+05
56	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-04 23:16:29.763809+05
57	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-05 00:08:04.801533+05
58	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-05 00:30:36.024133+05
59	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-05 01:06:19.747153+05
60	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-05 01:43:58.055602+05
61	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-05 02:22:36.295364+05
62	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-05 02:26:13.220357+05
63	1	list_localized_content	localized_content	\N	{"filters": {"content_type": null, "language": null, "active_only": true}, "total_results": 328}	\N	\N	2025-10-05 13:50:04.812872+05
64	1	list_localized_content	localized_content	\N	{"filters": {"content_type": "ui", "language": "en", "active_only": true}, "total_results": 210}	\N	\N	2025-10-05 13:50:05.12032+05
65	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-05 14:51:17.089589+05
66	4	list_localized_content	localized_content	\N	{"filters": {"content_type": null, "language": null, "active_only": true}, "total_results": 328}	\N	\N	2025-10-05 14:51:18.335285+05
67	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-05 14:52:50.938189+05
68	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 00:41:34.144987+05
69	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 00:43:16.579866+05
70	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 00:43:17.150236+05
71	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 00:50:40.62627+05
72	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 01:07:25.624956+05
73	4	create_localized_content	localized_content	402	{"content_type": "ui", "content_id": "test_admin_content", "language": "en"}	\N	\N	2025-10-06 01:07:27.123726+05
74	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 01:08:56.803938+05
75	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 01:13:34.013994+05
76	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 01:14:12.69181+05
77	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 01:16:00.160111+05
78	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 01:17:27.168477+05
79	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 01:23:55.695552+05
80	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 01:26:44.128061+05
81	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 01:29:53.302944+05
82	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 02:04:34.992378+05
83	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 68.0, "risk_tolerance": "high", "completion_time": null}	\N	\N	2025-10-06 13:04:46.461185+05
84	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 65.33, "risk_tolerance": "high", "completion_time": null}	\N	\N	2025-10-06 13:04:47.79615+05
85	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 61.33, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-06 13:21:42.404949+05
86	6	post_survey_registration	user	6	{"email": "ahmad.hassan@clustox.com", "registration_type": "post_survey", "subscribe_to_updates": true, "has_survey_data": true}	\N	\N	2025-10-06 13:36:31.217409+05
87	6	post_registration_login	user	6	{"email": "ahmad.hassan@clustox.com", "session_id": "edesy0N-qRVvu-nePRVUL1HRL6uJGTxmEg9W5yRlf0w"}	\N	\N	2025-10-06 13:36:33.204558+05
88	6	simple_login	user	6	{"email": "ahmad.hassan@clustox.com", "session_id": "MBaGLc54Fpj4so475Xge75aq_HvF9_TsCLLUrL3SRwA"}	\N	\N	2025-10-06 13:51:30.30172+05
89	6	simple_login	user	6	{"email": "ahmad.hassan@clustox.com", "session_id": "22MvIorSyc6i__rAV-I7bkrsqSRyEQlp46R8bNApdrs"}	\N	\N	2025-10-06 13:52:54.379471+05
90	6	simple_login	user	6	{"email": "ahmad.hassan@clustox.com", "session_id": "KQyrGW-f7g6CuBp20k-lvnG3Bf2lwgiFOgrk466yDRQ"}	\N	\N	2025-10-06 13:55:43.706498+05
91	6	simple_login	user	6	{"email": "ahmad.hassan@clustox.com", "session_id": "bmCbgJLdzxnwHRxi6NB5R5ElurRHeZnmlfCZZigeCGY"}	\N	\N	2025-10-06 13:56:20.417633+05
92	6	simple_login	user	6	{"email": "ahmad.hassan@clustox.com", "session_id": "gDvGwisiqCkU9N05QlHw6nTkeBPTEat4VRKO0Oim3-s"}	\N	\N	2025-10-06 14:02:04.894494+05
93	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 74.67, "risk_tolerance": "high", "completion_time": null}	\N	\N	2025-10-06 14:14:57.241045+05
94	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 74.67, "risk_tolerance": "high", "completion_time": null}	\N	\N	2025-10-06 14:15:00.49043+05
95	6	simple_login	user	6	{"email": "ahmad.hassan@clustox.com", "session_id": "bmU_KDHrWdbVCgZ-WThGEKs1HCRNiX7UVkEs4VUmnNQ"}	\N	\N	2025-10-06 14:48:10.705872+05
96	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 57.33, "risk_tolerance": "low", "completion_time": null}	\N	\N	2025-10-06 14:49:50.02953+05
97	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 57.33, "risk_tolerance": "low", "completion_time": null}	\N	\N	2025-10-06 14:49:50.548875+05
98	6	simple_login	user	6	{"email": "ahmad.hassan@clustox.com", "session_id": "fhSVCGFxXFtcQdWvZiVssrkY_ID-yfHFxeYV_oOyB-8"}	\N	\N	2025-10-06 15:21:53.092013+05
99	6	simple_login	user	6	{"email": "ahmad.hassan@clustox.com", "session_id": "wnRLi9C2ntJbN_xQ6rR_VVjVUS-spXIqAmpjNIbwkHE"}	\N	\N	2025-10-06 15:22:30.859811+05
100	6	simple_login	user	6	{"email": "ahmad.hassan@clustox.com", "session_id": "viRqH0T991sTMSUbtfUTtzaOHKAr2Q8iu1X_KvfeVsY"}	\N	\N	2025-10-06 15:31:48.365306+05
101	6	simple_login	user	6	{"email": "ahmad.hassan@clustox.com", "session_id": "nhRLGDA-aPPWWe77VJP9ZXTsQPVyR7i7dHfaLNxSxt4"}	\N	\N	2025-10-06 15:51:53.097014+05
102	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 66.67, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-06 15:55:08.213151+05
103	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 20.0, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-06 17:36:25.559357+05
104	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 56.0, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-06 17:43:28.097064+05
105	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 18:12:34.751619+05
106	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 70.67, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-06 18:39:29.690644+05
107	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 64.0, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-06 18:49:12.896691+05
108	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 18:51:20.726059+05
109	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 57.33, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-06 18:58:01.973702+05
110	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 64.0, "risk_tolerance": "high", "completion_time": null}	\N	\N	2025-10-06 19:16:48.568541+05
111	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 61.33, "risk_tolerance": "high", "completion_time": null}	\N	\N	2025-10-06 19:19:56.574704+05
112	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 66.67, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-06 20:02:14.578373+05
113	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 66.67, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-06 20:02:14.623819+05
114	\N	guest_survey_completed	guest_survey	\N	{"overall_score": 65.33, "risk_tolerance": "moderate", "completion_time": null}	\N	\N	2025-10-06 20:03:49.770043+05
115	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 20:23:18.052766+05
116	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 20:32:28.319114+05
117	4	user_login	user	4	{"email": "admin@nationalbonds.ae"}	\N	\N	2025-10-06 21:39:17.836141+05
\.


--
-- Data for Name: company_assessments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.company_assessments (id, company_tracker_id, employee_id, department, position_level, responses, overall_score, category_scores, completion_time, ip_address, created_at) FROM stdin;
\.


--
-- Data for Name: company_question_sets; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.company_question_sets (id, company_tracker_id, name, description, base_questions, custom_questions, excluded_questions, question_variations, demographic_rules, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: company_trackers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.company_trackers (id, company_name, company_email, contact_person, phone_number, unique_url, is_active, total_assessments, average_score, custom_branding, notification_settings, created_at, updated_at, question_set_config, demographic_rules_config, localization_settings, report_branding, admin_users) FROM stdin;
10	Emirates Bank Ltd	hr1@emiratesbankltd.ae	Contact Person 2	+971 4 123 4561	emiratesbankltd1	t	0	\N	null	{"current_link": {"expires_at": "2025-11-16T15:08:04.358001", "max_responses": 1500, "generated_at": "2025-10-02T15:08:04.358017", "generated_by": 4}}	2025-10-02 19:32:22.32862+05	2025-10-02 20:08:04.330987+05	\N	\N	\N	\N	\N
11	Emirates Bank Group	hr2@emiratesbankgroup.ae	Contact Person 3	+971 4 123 4562	emiratesbankgroup1	t	0	\N	null	null	2025-10-02 19:32:22.383847+05	\N	\N	\N	\N	\N	\N
12	National Bank UAE	hr3@nationalbankuae.ae	Contact Person 4	+971 4 123 4563	nationalbankuae1	t	0	\N	null	null	2025-10-02 19:32:22.43365+05	\N	\N	\N	\N	\N	\N
13	National Bank UAE Ltd	hr4@nationalbankuaeltd.ae	Contact Person 5	+971 4 123 4564	nationalbankuaeltd1	t	0	\N	null	null	2025-10-02 19:32:22.484169+05	\N	\N	\N	\N	\N	\N
7	National Bank UAE	hr3@nationalbankuae.ae	Contact Person 4	+971 4 123 4563	nationalbankuae	t	0	\N	null	{"current_link": {"expires_at": "2025-11-16T15:03:32.859090", "max_responses": 1500, "generated_at": "2025-10-02T15:03:32.859116", "generated_by": 4}}	2025-10-02 19:29:33.243731+05	2025-10-02 20:03:32.792891+05	\N	\N	\N	\N	\N
9	Emirates Bank	hr0@emiratesbank.ae	Contact Person 1	+971 4 123 4560	eb-employees	t	0	\N	null	{"current_link": {"expires_at": "2025-10-09T14:32:22.528526", "max_responses": 100, "generated_at": "2025-10-02T14:32:22.528572", "generated_by": 4}}	2025-10-02 19:32:22.251246+05	2025-10-02 19:32:22.916256+05	\N	\N	\N	\N	\N
14	Renewal Test Company	test@renewal.ae	Test Person	\N	renewaltestcompany	t	0	\N	null	{"current_link": {"expires_at": "2025-10-02T14:35:46.396588", "max_responses": 100, "generated_at": "2025-10-02T14:35:47.396608", "generated_by": 4}}	2025-10-02 19:35:47.356898+05	2025-10-02 19:35:47.389956+05	\N	\N	\N	\N	\N
15	Emirates NBD Bank	hr@emiratesnbd.com	Sarah Al-Mansouri	+971 4 316 0316	emiratesnbdbank	t	0	\N	null	null	2025-10-02 19:56:05.262866+05	\N	\N	\N	\N	\N	\N
16	ADNOC Group	hr@adnoc.ae	Mohammed Al-Jaber	+971 2 202 0000	adnocgroup1	t	0	\N	null	null	2025-10-02 19:56:05.344223+05	\N	\N	\N	\N	\N	\N
17	Dubai Municipality	hr@dm.gov.ae	Fatima Al-Zahra	+971 4 221 5555	dubaimunicipality	t	0	\N	null	null	2025-10-02 19:56:05.478788+05	\N	\N	\N	\N	\N	\N
1	Test Company Ltd	hr@testcompany.ae	Ahmed Al-Rashid	+971 4 123 4567	testcompanyltd	t	0	\N	null	{"current_link": {"expires_at": "2025-11-16T15:02:04.180070", "max_responses": 1500, "generated_at": "2025-10-02T15:02:04.180171", "generated_by": 4}}	2025-10-02 19:16:08.686704+05	2025-10-02 20:02:04.169018+05	\N	\N	\N	\N	\N
2	Emirates NBD	hr@emiratesnbd.com	Sarah Al-Mansouri	+971 4 316 0316	emiratesnbd	t	0	\N	null	{"current_link": {"expires_at": "2025-11-16T15:02:04.301580", "max_responses": 1500, "generated_at": "2025-10-02T15:02:04.301605", "generated_by": 4}}	2025-10-02 19:16:08.917486+05	2025-10-02 20:02:04.201079+05	\N	\N	\N	\N	\N
3	ADNOC Group	hr@adnoc.ae	Mohammed Al-Jaber	+971 2 202 0000	adnocgroup	t	0	\N	null	{"current_link": {"expires_at": "2025-11-16T15:02:04.339379", "max_responses": 1500, "generated_at": "2025-10-02T15:02:04.339403", "generated_by": 4}}	2025-10-02 19:16:08.959244+05	2025-10-02 20:02:04.315352+05	\N	\N	\N	\N	\N
18	National Bank of Ras Al Khaimah	hr@rakbank.ae	Ali Al-Qasimi	+971 7 206 2222	nationalbankofrasalkhaimah	t	0	\N	null	null	2025-10-02 20:02:04.668707+05	\N	\N	\N	\N	\N	\N
19	Union National Bank	hr@unb.ae	Mariam Al-Suwaidi	+971 2 677 2200	unionnationalbank	t	0	\N	null	null	2025-10-02 20:02:04.70939+05	\N	\N	\N	\N	\N	\N
20	Abu Dhabi Commercial Bank	hr@adcb.com	Ahmed Al-Rashid	+971 2 621 2222	abudhabicommercialbank	t	0	\N	null	null	2025-10-02 20:03:32.269508+05	\N	\N	\N	\N	\N	\N
21	First Abu Dhabi Bank	hr@fab.ae	Fatima Al-Zahra	+971 2 610 0000	firstabudhabibank	t	0	\N	null	null	2025-10-02 20:03:32.299565+05	\N	\N	\N	\N	\N	\N
22	Dubai Islamic Bank	hr@dib.ae	Mohammed Al-Maktoum	+971 4 609 2222	dubaiislamicbank	t	0	\N	null	null	2025-10-02 20:03:32.453239+05	\N	\N	\N	\N	\N	\N
23	Mashreq Bank	hr@mashreq.com	Sarah Al-Mansouri	+971 4 424 4444	mashreqbank	t	0	\N	null	null	2025-10-02 20:03:32.482581+05	\N	\N	\N	\N	\N	\N
24	Commercial Bank of Dubai	hr@cbd.ae	Omar Al-Suwaidi	+971 4 230 0000	commercialbankofdubai	t	0	\N	null	null	2025-10-02 20:03:32.617897+05	\N	\N	\N	\N	\N	\N
8	National Bank UAE Ltd	hr4@nationalbankuaeltd.ae	Contact Person 5	+971 4 999 0001	nationalbankuaeltd	t	0	\N	null	{"current_link": {"expires_at": "2025-11-16T15:08:04.270512", "max_responses": 1500, "generated_at": "2025-10-02T15:08:04.270528", "generated_by": 4}}	2025-10-02 19:29:33.271438+05	2025-10-02 20:08:04.396514+05	\N	\N	\N	\N	\N
5	Emirates Bank Ltd	hr1@emiratesbankltd.ae	Contact Person 2	+971 4 999 0001	emiratesbankltd	t	0	\N	null	{"current_link": {"expires_at": "2025-11-16T15:03:32.720816", "max_responses": 1500, "generated_at": "2025-10-02T15:03:32.720845", "generated_by": 4}}	2025-10-02 19:29:33.185982+05	2025-10-02 20:03:32.910704+05	\N	\N	\N	\N	\N
6	Emirates Bank Group	hr2@emiratesbankgroup.ae	Contact Person 3	+971 4 999 0002	emiratesbankgroup	t	0	\N	null	{"current_link": {"expires_at": "2025-11-16T15:03:32.761771", "max_responses": 1500, "generated_at": "2025-10-02T15:03:32.761794", "generated_by": 4}}	2025-10-02 19:29:33.215994+05	2025-10-02 20:03:32.92728+05	\N	\N	\N	\N	\N
25	National Bank of Ras Al Khaimah	hr@rakbank.ae	Ali Al-Qasimi	+971 7 206 2222	nationalbankofrasalkhaimah1	t	0	\N	null	null	2025-10-02 20:03:33.12239+05	\N	\N	\N	\N	\N	\N
26	Union National Bank	hr@unb.ae	Mariam Al-Suwaidi	+971 2 677 2200	unionnationalbank1	t	0	\N	null	null	2025-10-02 20:03:33.14962+05	\N	\N	\N	\N	\N	\N
27	Abu Dhabi Commercial Bank	hr@adcb.com	Ahmed Al-Rashid	+971 2 621 2222	abudhabicommercialbank1	t	0	\N	null	null	2025-10-02 20:08:03.888287+05	\N	\N	\N	\N	\N	\N
28	First Abu Dhabi Bank	hr@fab.ae	Fatima Al-Zahra	+971 2 610 0000	firstabudhabibank1	t	0	\N	null	null	2025-10-02 20:08:03.930383+05	\N	\N	\N	\N	\N	\N
29	Dubai Islamic Bank	hr@dib.ae	Mohammed Al-Maktoum	+971 4 609 2222	dubaiislamicbank1	t	0	\N	null	null	2025-10-02 20:08:04.001201+05	\N	\N	\N	\N	\N	\N
31	Commercial Bank of Dubai	hr@cbd.ae	Omar Al-Suwaidi	+971 4 230 0000	commercialbankofdubai1	t	0	\N	null	null	2025-10-02 20:08:04.061845+05	\N	\N	\N	\N	\N	\N
32	National Bank of Ras Al Khaimah	hr@rakbank.ae	Ali Al-Qasimi	+971 7 206 2222	nationalbankofrasalkhaimah2	t	0	\N	null	null	2025-10-02 20:08:04.572787+05	\N	\N	\N	\N	\N	\N
4	Emirates Bank	hr0@emiratesbank.ae	Contact Person 1	+971 4 999 0002	national-bonds-staff	t	0	\N	null	{"current_link": {"expires_at": "2025-10-09T14:29:33.392435", "max_responses": 100, "generated_at": "2025-10-02T14:29:33.392675", "generated_by": 4}}	2025-10-02 19:29:32.872512+05	2025-10-02 20:08:04.408712+05	\N	\N	\N	\N	\N
30	Mashreq Bank	hr@mashreq.com	Sarah Al-Mansouri	+971 4 424 4444	mashreqbank1	t	0	\N	null	{"current_link": {"expires_at": "2025-11-05T15:28:48.821843", "max_responses": 1000, "generated_at": "2025-10-06T15:28:48.822013", "generated_by": 4}}	2025-10-02 20:08:04.027865+05	2025-10-06 20:28:48.786791+05	\N	\N	\N	\N	\N
\.


--
-- Data for Name: customer_profiles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.customer_profiles (id, user_id, first_name, last_name, age, gender, nationality, emirate, city, employment_status, industry, "position", monthly_income, household_size, phone_number, preferred_language, created_at, updated_at, children, education_level, years_in_uae, family_status, housing_status, banking_relationship, investment_experience, financial_goals, preferred_communication, islamic_finance_preference) FROM stdin;
1	6	Ahmad	Hassan	22	Male	Pakistani	Ras Al Khaimah	\N	Employed Part-time	Technology	\N	30,000 - 50,000	1	\N	en	2025-10-06 13:36:31.217409+05	\N	No	\N	\N	\N	\N	\N	\N	\N	email	f
\.


--
-- Data for Name: demographic_rules; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.demographic_rules (id, name, description, conditions, actions, priority, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: incomplete_surveys; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.incomplete_surveys (id, user_id, customer_profile_id, session_id, current_step, total_steps, responses, started_at, last_activity, abandoned_at, email, phone_number, is_abandoned, follow_up_sent, follow_up_count, created_at, updated_at) FROM stdin;
1	\N	\N	gmsloPLu1Uik9mxtHazXjgYD4--oJe-HtAxZCRreLMk	3	10	{"Q1": 4, "Q2": 3, "Q3": 5}	2025-10-02 18:50:41.832914+05	2025-10-02 13:50:41.904004+05	\N	test.incomplete@example.com	+971501234567	f	f	0	2025-10-02 18:50:41.832914+05	2025-10-02 18:50:41.901909+05
2	\N	\N	R11LNz82UYBLPhOY8HZsaisvMDyUaIc3HBhU7YIlj7A	3	10	{"Q1": 4, "Q2": 3, "Q3": 5}	2025-10-02 18:55:39.907673+05	2025-10-02 13:55:39.948414+05	\N	test.incomplete@example.com	+971501234567	f	f	0	2025-10-02 18:55:39.907673+05	2025-10-02 18:55:39.944304+05
\.


--
-- Data for Name: localized_content; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.localized_content (id, content_type, content_id, language, title, text, options, extra_data, version, is_active, created_at, updated_at) FROM stdin;
13	question	q11_investment_knowledge	ar	\N	كيف تقيم معرفتك بالاستثمار؟	[{"value": 1, "label": "\\u0644\\u0627 \\u0623\\u0639\\u0631\\u0641 \\u0634\\u064a\\u0626\\u0627\\u064b \\u0639\\u0646 \\u0627\\u0644\\u0627\\u0633\\u062a\\u062b\\u0645\\u0627\\u0631"}, {"value": 2, "label": "\\u0645\\u0639\\u0631\\u0641\\u0629 \\u0645\\u062d\\u062f\\u0648\\u062f\\u0629 \\u062c\\u062f\\u0627\\u064b"}, {"value": 3, "label": "\\u0645\\u0639\\u0631\\u0641\\u0629 \\u0623\\u0633\\u0627\\u0633\\u064a\\u0629"}, {"value": 4, "label": "\\u0645\\u0639\\u0631\\u0641\\u0629 \\u062c\\u064a\\u062f\\u0629"}, {"value": 5, "label": "\\u0645\\u0639\\u0631\\u0641\\u0629 \\u0645\\u062a\\u0642\\u062f\\u0645\\u0629"}]	null	1.0	t	2025-10-03 22:36:14.681404+05	\N
5	question	q3_budget_tracking	ar	\N	كم مرة تراجع ميزانيتك الشخصية؟	[{"value": 1, "label": "\\u0644\\u0627 \\u0623\\u0631\\u0627\\u062c\\u0639\\u0647\\u0627 \\u0623\\u0628\\u062f\\u0627\\u064b"}, {"value": 2, "label": "\\u0646\\u0627\\u062f\\u0631\\u0627\\u064b"}, {"value": 3, "label": "\\u0623\\u062d\\u064a\\u0627\\u0646\\u0627\\u064b"}, {"value": 4, "label": "\\u0634\\u0647\\u0631\\u064a\\u0627\\u064b"}, {"value": 5, "label": "\\u0623\\u0633\\u0628\\u0648\\u0639\\u064a\\u0627\\u064b \\u0623\\u0648 \\u0623\\u0643\\u062b\\u0631"}]	null	1.0	t	2025-10-03 22:36:13.787293+05	\N
6	question	q4_expense_control	ar	\N	إلى أي مدى تشعر بالسيطرة على نفقاتك؟	[{"value": 1, "label": "\\u0644\\u0627 \\u0623\\u0634\\u0639\\u0631 \\u0628\\u0627\\u0644\\u0633\\u064a\\u0637\\u0631\\u0629 \\u0639\\u0644\\u0649 \\u0627\\u0644\\u0625\\u0637\\u0644\\u0627\\u0642"}, {"value": 2, "label": "\\u0633\\u064a\\u0637\\u0631\\u0629 \\u0642\\u0644\\u064a\\u0644\\u0629"}, {"value": 3, "label": "\\u0633\\u064a\\u0637\\u0631\\u0629 \\u0645\\u062a\\u0648\\u0633\\u0637\\u0629"}, {"value": 4, "label": "\\u0633\\u064a\\u0637\\u0631\\u0629 \\u062c\\u064a\\u062f\\u0629"}, {"value": 5, "label": "\\u0633\\u064a\\u0637\\u0631\\u0629 \\u0643\\u0627\\u0645\\u0644\\u0629"}]	null	1.0	t	2025-10-03 22:36:13.862423+05	\N
7	question	q5_emergency_fund	ar	\N	كم شهراً يمكن أن تغطي نفقاتك من مدخراتك الطارئة؟	[{"value": 1, "label": "\\u0623\\u0642\\u0644 \\u0645\\u0646 \\u0634\\u0647\\u0631 \\u0648\\u0627\\u062d\\u062f"}, {"value": 2, "label": "1-2 \\u0634\\u0647\\u0631"}, {"value": 3, "label": "3-4 \\u0623\\u0634\\u0647\\u0631"}, {"value": 4, "label": "5-6 \\u0623\\u0634\\u0647\\u0631"}, {"value": 5, "label": "\\u0623\\u0643\\u062b\\u0631 \\u0645\\u0646 6 \\u0623\\u0634\\u0647\\u0631"}]	null	1.0	t	2025-10-03 22:36:13.914555+05	\N
8	question	q6_savings_habit	ar	\N	كم مرة تدخر من راتبك الشهري؟	[{"value": 1, "label": "\\u0644\\u0627 \\u0623\\u062f\\u062e\\u0631 \\u0623\\u0628\\u062f\\u0627\\u064b"}, {"value": 2, "label": "\\u0646\\u0627\\u062f\\u0631\\u0627\\u064b"}, {"value": 3, "label": "\\u0623\\u062d\\u064a\\u0627\\u0646\\u0627\\u064b"}, {"value": 4, "label": "\\u0645\\u0639\\u0638\\u0645 \\u0627\\u0644\\u0623\\u0634\\u0647\\u0631"}, {"value": 5, "label": "\\u0643\\u0644 \\u0634\\u0647\\u0631"}]	null	1.0	t	2025-10-03 22:36:13.974902+05	\N
9	question	q7_debt_burden	ar	\N	ما نسبة دخلك الشهري التي تذهب لسداد الديون؟	[{"value": 5, "label": "\\u0644\\u0627 \\u062a\\u0648\\u062c\\u062f \\u062f\\u064a\\u0648\\u0646"}, {"value": 4, "label": "\\u0623\\u0642\\u0644 \\u0645\\u0646 10%"}, {"value": 3, "label": "10-30%"}, {"value": 2, "label": "30-50%"}, {"value": 1, "label": "\\u0623\\u0643\\u062b\\u0631 \\u0645\\u0646 50%"}]	null	1.0	t	2025-10-03 22:36:14.179953+05	\N
10	question	q8_debt_management	ar	\N	كيف تدير ديونك الحالية؟	[{"value": 1, "label": "\\u0623\\u0648\\u0627\\u062c\\u0647 \\u0635\\u0639\\u0648\\u0628\\u0629 \\u0641\\u064a \\u0627\\u0644\\u0633\\u062f\\u0627\\u062f"}, {"value": 2, "label": "\\u0623\\u0633\\u062f\\u062f \\u0627\\u0644\\u062d\\u062f \\u0627\\u0644\\u0623\\u062f\\u0646\\u0649 \\u0641\\u0642\\u0637"}, {"value": 3, "label": "\\u0623\\u0633\\u062f\\u062f \\u0623\\u0643\\u062b\\u0631 \\u0645\\u0646 \\u0627\\u0644\\u062d\\u062f \\u0627\\u0644\\u0623\\u062f\\u0646\\u0649 \\u0623\\u062d\\u064a\\u0627\\u0646\\u0627\\u064b"}, {"value": 4, "label": "\\u0623\\u0633\\u062f\\u062f \\u0623\\u0643\\u062b\\u0631 \\u0645\\u0646 \\u0627\\u0644\\u062d\\u062f \\u0627\\u0644\\u0623\\u062f\\u0646\\u0649 \\u062f\\u0627\\u0626\\u0645\\u0627\\u064b"}, {"value": 5, "label": "\\u0644\\u0627 \\u062a\\u0648\\u062c\\u062f \\u062f\\u064a\\u0648\\u0646"}]	null	1.0	t	2025-10-03 22:36:14.469446+05	\N
11	question	q9_financial_goals	ar	\N	هل لديك أهداف مالية واضحة ومكتوبة؟	[{"value": 1, "label": "\\u0644\\u0627 \\u062a\\u0648\\u062c\\u062f \\u0623\\u0647\\u062f\\u0627\\u0641 \\u0645\\u062d\\u062f\\u062f\\u0629"}, {"value": 2, "label": "\\u0623\\u0647\\u062f\\u0627\\u0641 \\u063a\\u0627\\u0645\\u0636\\u0629 \\u0641\\u064a \\u0630\\u0647\\u0646\\u064a"}, {"value": 3, "label": "\\u0623\\u0647\\u062f\\u0627\\u0641 \\u0648\\u0627\\u0636\\u062d\\u0629 \\u0644\\u0643\\u0646 \\u063a\\u064a\\u0631 \\u0645\\u0643\\u062a\\u0648\\u0628\\u0629"}, {"value": 4, "label": "\\u0623\\u0647\\u062f\\u0627\\u0641 \\u0645\\u0643\\u062a\\u0648\\u0628\\u0629 \\u0644\\u0643\\u0646 \\u0628\\u062f\\u0648\\u0646 \\u062e\\u0637\\u0629"}, {"value": 5, "label": "\\u0623\\u0647\\u062f\\u0627\\u0641 \\u0645\\u0643\\u062a\\u0648\\u0628\\u0629 \\u0645\\u0639 \\u062e\\u0637\\u0629 \\u0648\\u0627\\u0636\\u062d\\u0629"}]	null	1.0	t	2025-10-03 22:36:14.547977+05	\N
12	question	q10_retirement_planning	ar	\N	كم تدخر شهرياً للتقاعد؟	[{"value": 1, "label": "\\u0644\\u0627 \\u0623\\u062f\\u062e\\u0631 \\u0644\\u0644\\u062a\\u0642\\u0627\\u0639\\u062f"}, {"value": 2, "label": "\\u0623\\u0642\\u0644 \\u0645\\u0646 5% \\u0645\\u0646 \\u0627\\u0644\\u0631\\u0627\\u062a\\u0628"}, {"value": 3, "label": "5-10% \\u0645\\u0646 \\u0627\\u0644\\u0631\\u0627\\u062a\\u0628"}, {"value": 4, "label": "10-15% \\u0645\\u0646 \\u0627\\u0644\\u0631\\u0627\\u062a\\u0628"}, {"value": 5, "label": "\\u0623\\u0643\\u062b\\u0631 \\u0645\\u0646 15% \\u0645\\u0646 \\u0627\\u0644\\u0631\\u0627\\u062a\\u0628"}]	null	1.0	t	2025-10-03 22:36:14.632982+05	\N
14	question	q12_investment_experience	ar	\N	ما مدى خبرتك في الاستثمار؟	[{"value": 1, "label": "\\u0644\\u0627 \\u062a\\u0648\\u062c\\u062f \\u062e\\u0628\\u0631\\u0629"}, {"value": 2, "label": "\\u062e\\u0628\\u0631\\u0629 \\u0642\\u0644\\u064a\\u0644\\u0629 (\\u0623\\u0642\\u0644 \\u0645\\u0646 \\u0633\\u0646\\u0629)"}, {"value": 3, "label": "\\u062e\\u0628\\u0631\\u0629 \\u0645\\u062a\\u0648\\u0633\\u0637\\u0629 (1-3 \\u0633\\u0646\\u0648\\u0627\\u062a)"}, {"value": 4, "label": "\\u062e\\u0628\\u0631\\u0629 \\u062c\\u064a\\u062f\\u0629 (3-5 \\u0633\\u0646\\u0648\\u0627\\u062a)"}, {"value": 5, "label": "\\u062e\\u0628\\u0631\\u0629 \\u0648\\u0627\\u0633\\u0639\\u0629 (\\u0623\\u0643\\u062b\\u0631 \\u0645\\u0646 5 \\u0633\\u0646\\u0648\\u0627\\u062a)"}]	null	1.0	t	2025-10-03 22:36:14.776509+05	\N
80	ui	send_email	en	\N	Send via Email	null	null	1.0	t	2025-10-05 01:03:21.281576+05	\N
15	question	q13_risk_tolerance	ar	\N	ما مدى استعدادك لتحمل المخاطر في الاستثمار؟	[{"value": 1, "label": "\\u0644\\u0627 \\u0623\\u062a\\u062d\\u0645\\u0644 \\u0623\\u064a \\u0645\\u062e\\u0627\\u0637\\u0631"}, {"value": 2, "label": "\\u0645\\u062e\\u0627\\u0637\\u0631 \\u0642\\u0644\\u064a\\u0644\\u0629 \\u062c\\u062f\\u0627\\u064b"}, {"value": 3, "label": "\\u0645\\u062e\\u0627\\u0637\\u0631 \\u0645\\u062a\\u0648\\u0633\\u0637\\u0629"}, {"value": 4, "label": "\\u0645\\u062e\\u0627\\u0637\\u0631 \\u0639\\u0627\\u0644\\u064a\\u0629"}, {"value": 5, "label": "\\u0645\\u062e\\u0627\\u0637\\u0631 \\u0639\\u0627\\u0644\\u064a\\u0629 \\u062c\\u062f\\u0627\\u064b"}]	null	1.0	t	2025-10-03 22:36:14.810394+05	\N
16	question	q14_diversification	ar	\N	كيف تنوع استثماراتك؟	[{"value": 1, "label": "\\u0644\\u0627 \\u0623\\u0633\\u062a\\u062b\\u0645\\u0631"}, {"value": 2, "label": "\\u0627\\u0633\\u062a\\u062b\\u0645\\u0627\\u0631 \\u0648\\u0627\\u062d\\u062f \\u0641\\u0642\\u0637"}, {"value": 3, "label": "\\u0646\\u0648\\u0639\\u0627\\u0646 \\u0645\\u0646 \\u0627\\u0644\\u0627\\u0633\\u062a\\u062b\\u0645\\u0627\\u0631"}, {"value": 4, "label": "\\u062b\\u0644\\u0627\\u062b\\u0629 \\u0623\\u0646\\u0648\\u0627\\u0639 \\u0623\\u0648 \\u0623\\u0643\\u062b\\u0631"}, {"value": 5, "label": "\\u0645\\u062d\\u0641\\u0638\\u0629 \\u0645\\u062a\\u0646\\u0648\\u0639\\u0629 \\u062c\\u062f\\u0627\\u064b"}]	null	1.0	t	2025-10-03 22:36:14.927332+05	\N
17	question	q15_financial_stress	ar	\N	كم مرة تشعر بالقلق بشأن وضعك المالي؟	[{"value": 1, "label": "\\u062f\\u0627\\u0626\\u0645\\u0627\\u064b"}, {"value": 2, "label": "\\u063a\\u0627\\u0644\\u0628\\u0627\\u064b"}, {"value": 3, "label": "\\u0623\\u062d\\u064a\\u0627\\u0646\\u0627\\u064b"}, {"value": 4, "label": "\\u0646\\u0627\\u062f\\u0631\\u0627\\u064b"}, {"value": 5, "label": "\\u0623\\u0628\\u062f\\u0627\\u064b"}]	null	1.0	t	2025-10-03 22:36:15.045973+05	\N
18	question	q16_financial_confidence	ar	\N	ما مدى ثقتك في قدرتك على اتخاذ قرارات مالية صحيحة؟	[{"value": 1, "label": "\\u0644\\u0627 \\u0623\\u062b\\u0642 \\u0641\\u064a \\u0642\\u0631\\u0627\\u0631\\u0627\\u062a\\u064a \\u0627\\u0644\\u0645\\u0627\\u0644\\u064a\\u0629"}, {"value": 2, "label": "\\u062b\\u0642\\u0629 \\u0642\\u0644\\u064a\\u0644\\u0629"}, {"value": 3, "label": "\\u062b\\u0642\\u0629 \\u0645\\u062a\\u0648\\u0633\\u0637\\u0629"}, {"value": 4, "label": "\\u062b\\u0642\\u0629 \\u0639\\u0627\\u0644\\u064a\\u0629"}, {"value": 5, "label": "\\u062b\\u0642\\u0629 \\u0643\\u0627\\u0645\\u0644\\u0629"}]	null	1.0	t	2025-10-03 22:36:15.232294+05	\N
19	ui	welcome_message	ar	\N	مرحباً بك في تقييم الصحة المالية	null	null	1.0	t	2025-10-03 22:36:15.288448+05	\N
20	ui	start_survey	ar	\N	ابدأ التقييم	null	null	1.0	t	2025-10-03 22:36:15.673464+05	\N
21	ui	next_question	ar	\N	السؤال التالي	null	null	1.0	t	2025-10-03 22:36:15.73424+05	\N
22	ui	previous_question	ar	\N	السؤال السابق	null	null	1.0	t	2025-10-03 22:36:15.986843+05	\N
23	ui	submit_survey	ar	\N	إرسال التقييم	null	null	1.0	t	2025-10-03 22:36:16.029126+05	\N
24	ui	your_results	ar	\N	نتائجك	null	null	1.0	t	2025-10-03 22:36:16.047691+05	\N
25	ui	download_pdf	ar	\N	تحميل التقرير	null	null	1.0	t	2025-10-03 22:36:16.06646+05	\N
26	ui	send_email	ar	\N	إرسال بالبريد الإلكتروني	null	null	1.0	t	2025-10-03 22:36:16.15193+05	\N
27	ui	register_account	ar	\N	إنشاء حساب	null	null	1.0	t	2025-10-03 22:36:16.273313+05	\N
28	ui	language_selector	ar	\N	اختر اللغة	null	null	1.0	t	2025-10-03 22:36:16.291652+05	\N
29	ui	financial_health_score	ar	\N	درجة الصحة المالية	null	null	1.0	t	2025-10-03 22:36:16.30599+05	\N
30	ui	recommendations	ar	\N	التوصيات	null	null	1.0	t	2025-10-03 22:36:16.318134+05	\N
31	ui	budgeting	ar	\N	إدارة الميزانية	null	null	1.0	t	2025-10-03 22:36:16.331352+05	\N
32	ui	savings	ar	\N	الادخار	null	null	1.0	t	2025-10-03 22:36:16.673197+05	\N
33	ui	debt_management	ar	\N	إدارة الديون	null	null	1.0	t	2025-10-03 22:36:16.69413+05	\N
34	ui	financial_planning	ar	\N	التخطيط المالي	null	null	1.0	t	2025-10-03 22:36:16.779608+05	\N
35	ui	investment_knowledge	ar	\N	المعرفة الاستثمارية	null	null	1.0	t	2025-10-03 22:36:17.152032+05	\N
36	ui	excellent	ar	\N	ممتاز	null	null	1.0	t	2025-10-03 22:36:17.205911+05	\N
37	ui	good	ar	\N	جيد	null	null	1.0	t	2025-10-03 22:36:17.277438+05	\N
38	ui	fair	ar	\N	مقبول	null	null	1.0	t	2025-10-03 22:36:17.310462+05	\N
39	ui	poor	ar	\N	ضعيف	null	null	1.0	t	2025-10-03 22:36:17.349769+05	\N
40	ui	very_poor	ar	\N	ضعيف جداً	null	null	1.0	t	2025-10-03 22:36:17.443838+05	\N
41	ui	personal_information	ar	\N	المعلومات الشخصية	null	null	1.0	t	2025-10-03 22:36:17.478177+05	\N
42	ui	first_name	ar	\N	الاسم الأول	null	null	1.0	t	2025-10-03 22:36:17.518037+05	\N
43	ui	last_name	ar	\N	اسم العائلة	null	null	1.0	t	2025-10-03 22:36:17.534649+05	\N
44	ui	age	ar	\N	العمر	null	null	1.0	t	2025-10-03 22:36:17.558059+05	\N
45	ui	gender	ar	\N	الجنس	null	null	1.0	t	2025-10-03 22:36:17.580243+05	\N
46	ui	male	ar	\N	ذكر	null	null	1.0	t	2025-10-03 22:36:17.661405+05	\N
47	ui	female	ar	\N	أنثى	null	null	1.0	t	2025-10-03 22:36:17.818003+05	\N
48	ui	nationality	ar	\N	الجنسية	null	null	1.0	t	2025-10-03 22:36:18.223061+05	\N
49	ui	emirate	ar	\N	الإمارة	null	null	1.0	t	2025-10-03 22:36:18.237634+05	\N
50	ui	employment_status	ar	\N	الحالة الوظيفية	null	null	1.0	t	2025-10-03 22:36:18.247688+05	\N
51	ui	monthly_income	ar	\N	الدخل الشهري	null	null	1.0	t	2025-10-03 22:36:18.262507+05	\N
52	ui	household_size	ar	\N	عدد أفراد الأسرة	null	null	1.0	t	2025-10-03 22:36:18.275494+05	\N
53	ui	children	ar	\N	الأطفال	null	null	1.0	t	2025-10-03 22:36:18.284861+05	\N
54	ui	yes	ar	\N	نعم	null	null	1.0	t	2025-10-03 22:36:18.299155+05	\N
55	ui	no	ar	\N	لا	null	null	1.0	t	2025-10-03 22:36:18.312426+05	\N
56	ui	email	ar	\N	البريد الإلكتروني	null	null	1.0	t	2025-10-03 22:36:18.326681+05	\N
57	ui	phone_number	ar	\N	رقم الهاتف	null	null	1.0	t	2025-10-03 22:36:18.463309+05	\N
58	ui	save	ar	\N	حفظ	null	null	1.0	t	2025-10-03 22:36:18.480619+05	\N
59	ui	cancel	ar	\N	إلغاء	null	null	1.0	t	2025-10-03 22:36:18.511181+05	\N
60	ui	edit	ar	\N	تعديل	null	null	1.0	t	2025-10-03 22:36:18.53502+05	\N
61	ui	delete	ar	\N	حذف	null	null	1.0	t	2025-10-03 22:36:18.628346+05	\N
62	ui	confirm	ar	\N	تأكيد	null	null	1.0	t	2025-10-03 22:36:18.693586+05	\N
63	ui	loading	ar	\N	جاري التحميل...	null	null	1.0	t	2025-10-03 22:36:18.72657+05	\N
64	ui	error	ar	\N	خطأ	null	null	1.0	t	2025-10-03 22:36:18.742121+05	\N
65	ui	success	ar	\N	نجح	null	null	1.0	t	2025-10-03 22:36:18.767413+05	\N
66	ui	warning	ar	\N	تحذير	null	null	1.0	t	2025-10-03 22:36:18.827311+05	\N
67	ui	info	ar	\N	معلومات	null	null	1.0	t	2025-10-03 22:36:18.876353+05	\N
81	ui	register_account	en	\N	Create Account	null	null	1.0	t	2025-10-05 01:03:21.301118+05	\N
82	ui	language_selector	en	\N	Select Language	null	null	1.0	t	2025-10-05 01:03:21.318123+05	\N
83	ui	continue_assessment	en	\N	Continue Assessment	null	null	1.0	t	2025-10-05 01:03:21.332434+05	\N
84	ui	begin_assessment_now	en	\N	Begin Assessment Now	null	null	1.0	t	2025-10-05 01:03:21.34396+05	\N
164	ui	strongly_agree	en	\N	Strongly Agree	null	null	1.0	t	2025-10-05 01:03:22.694045+05	\N
69	recommendation	savings_emergency	ar	بناء صندوق الطوارئ	من المهم جداً أن يكون لديك صندوق طوارئ يغطي نفقاتك لمدة 3-6 أشهر. ابدأ بادخار مبلغ صغير شهرياً حتى تصل للهدف المطلوب.	null	{"action_steps": ["\\u0627\\u062d\\u0633\\u0628 \\u0646\\u0641\\u0642\\u0627\\u062a\\u0643 \\u0627\\u0644\\u0634\\u0647\\u0631\\u064a\\u0629 \\u0627\\u0644\\u0623\\u0633\\u0627\\u0633\\u064a\\u0629", "\\u0627\\u0636\\u0631\\u0628 \\u0647\\u0630\\u0627 \\u0627\\u0644\\u0645\\u0628\\u0644\\u063a \\u0641\\u064a 6 \\u0623\\u0634\\u0647\\u0631", "\\u0627\\u062f\\u062e\\u0631 10-20% \\u0645\\u0646 \\u0631\\u0627\\u062a\\u0628\\u0643 \\u0634\\u0647\\u0631\\u064a\\u0627\\u064b", "\\u0636\\u0639 \\u0627\\u0644\\u0645\\u062f\\u062e\\u0631\\u0627\\u062a \\u0641\\u064a \\u062d\\u0633\\u0627\\u0628 \\u0645\\u0646\\u0641\\u0635\\u0644"], "local_resources": ["\\u062d\\u0633\\u0627\\u0628\\u0627\\u062a \\u0627\\u0644\\u0627\\u062f\\u062e\\u0627\\u0631 \\u0641\\u064a \\u0627\\u0644\\u0628\\u0646\\u0648\\u0643 \\u0627\\u0644\\u0625\\u0645\\u0627\\u0631\\u0627\\u062a\\u064a\\u0629", "\\u0635\\u0646\\u0627\\u062f\\u064a\\u0642 \\u0627\\u0644\\u0627\\u0633\\u062a\\u062b\\u0645\\u0627\\u0631 \\u0642\\u0635\\u064a\\u0631\\u0629 \\u0627\\u0644\\u0645\\u062f\\u0649"]}	1.0	t	2025-10-03 22:36:19.599184+05	\N
70	recommendation	debt_management	ar	إدارة الديون بفعالية	إذا كان لديك ديون متعددة، ركز على سداد الديون ذات الفوائد العالية أولاً. فكر في توحيد الديون إذا كان ذلك سيقلل من الفوائد الإجمالية.	null	{"action_steps": ["\\u0627\\u0643\\u062a\\u0628 \\u0642\\u0627\\u0626\\u0645\\u0629 \\u0628\\u062c\\u0645\\u064a\\u0639 \\u062f\\u064a\\u0648\\u0646\\u0643 \\u0648\\u0645\\u0639\\u062f\\u0644\\u0627\\u062a \\u0627\\u0644\\u0641\\u0627\\u0626\\u062f\\u0629", "\\u0631\\u062a\\u0628 \\u0627\\u0644\\u062f\\u064a\\u0648\\u0646 \\u062d\\u0633\\u0628 \\u0645\\u0639\\u062f\\u0644 \\u0627\\u0644\\u0641\\u0627\\u0626\\u062f\\u0629 \\u0645\\u0646 \\u0627\\u0644\\u0623\\u0639\\u0644\\u0649 \\u0644\\u0644\\u0623\\u0642\\u0644", "\\u0627\\u062f\\u0641\\u0639 \\u0627\\u0644\\u062d\\u062f \\u0627\\u0644\\u0623\\u062f\\u0646\\u0649 \\u0644\\u062c\\u0645\\u064a\\u0639 \\u0627\\u0644\\u062f\\u064a\\u0648\\u0646", "\\u0627\\u062f\\u0641\\u0639 \\u0645\\u0628\\u0644\\u063a\\u0627\\u064b \\u0625\\u0636\\u0627\\u0641\\u064a\\u0627\\u064b \\u0644\\u0644\\u062f\\u064a\\u0646 \\u0630\\u064a \\u0627\\u0644\\u0641\\u0627\\u0626\\u062f\\u0629 \\u0627\\u0644\\u0623\\u0639\\u0644\\u0649"], "islamic_finance_note": "\\u0641\\u0643\\u0631 \\u0641\\u064a \\u0627\\u0644\\u0628\\u062f\\u0627\\u0626\\u0644 \\u0627\\u0644\\u0645\\u0635\\u0631\\u0641\\u064a\\u0629 \\u0627\\u0644\\u0625\\u0633\\u0644\\u0627\\u0645\\u064a\\u0629 \\u0627\\u0644\\u062a\\u064a \\u062a\\u062a\\u0648\\u0627\\u0641\\u0642 \\u0645\\u0639 \\u0623\\u062d\\u0643\\u0627\\u0645 \\u0627\\u0644\\u0634\\u0631\\u064a\\u0639\\u0629"}	1.0	t	2025-10-03 22:36:19.611205+05	\N
71	recommendation	investment_basic	ar	بداية الاستثمار	ابدأ رحلتك الاستثمارية بتعلم الأساسيات أولاً. فكر في الاستثمار في صناديق المؤشرات أو الصناديق المتنوعة كبداية آمنة.	null	{"action_steps": ["\\u062a\\u0639\\u0644\\u0645 \\u0623\\u0633\\u0627\\u0633\\u064a\\u0627\\u062a \\u0627\\u0644\\u0627\\u0633\\u062a\\u062b\\u0645\\u0627\\u0631", "\\u062d\\u062f\\u062f \\u0623\\u0647\\u062f\\u0627\\u0641\\u0643 \\u0627\\u0644\\u0627\\u0633\\u062a\\u062b\\u0645\\u0627\\u0631\\u064a\\u0629", "\\u0627\\u0628\\u062f\\u0623 \\u0628\\u0645\\u0628\\u0644\\u063a \\u0635\\u063a\\u064a\\u0631", "\\u0646\\u0648\\u0639 \\u0627\\u0633\\u062a\\u062b\\u0645\\u0627\\u0631\\u0627\\u062a\\u0643 \\u062a\\u062f\\u0631\\u064a\\u062c\\u064a\\u0627\\u064b"], "local_options": ["\\u0635\\u0646\\u0627\\u062f\\u064a\\u0642 \\u0627\\u0644\\u0627\\u0633\\u062a\\u062b\\u0645\\u0627\\u0631 \\u0641\\u064a \\u0627\\u0644\\u0628\\u0646\\u0648\\u0643 \\u0627\\u0644\\u0645\\u062d\\u0644\\u064a\\u0629", "\\u0633\\u0648\\u0642 \\u062f\\u0628\\u064a \\u0627\\u0644\\u0645\\u0627\\u0644\\u064a", "\\u0633\\u0648\\u0642 \\u0623\\u0628\\u0648\\u0638\\u0628\\u064a \\u0644\\u0644\\u0623\\u0648\\u0631\\u0627\\u0642 \\u0627\\u0644\\u0645\\u0627\\u0644\\u064a\\u0629"], "islamic_finance_note": "\\u062a\\u062a\\u0648\\u0641\\u0631 \\u0635\\u0646\\u0627\\u062f\\u064a\\u0642 \\u0627\\u0633\\u062a\\u062b\\u0645\\u0627\\u0631\\u064a\\u0629 \\u0645\\u062a\\u0648\\u0627\\u0641\\u0642\\u0629 \\u0645\\u0639 \\u0627\\u0644\\u0634\\u0631\\u064a\\u0639\\u0629 \\u0627\\u0644\\u0625\\u0633\\u0644\\u0627\\u0645\\u064a\\u0629"}	1.0	t	2025-10-03 22:36:19.623299+05	\N
72	recommendation	retirement_planning	ar	التخطيط للتقاعد	لم يفت الأوان بعد للبدء في التخطيط للتقاعد. ادخر ما لا يقل عن 10-15% من دخلك للتقاعد واستفد من أي برامج تقاعد تقدمها شركتك.	null	{"action_steps": ["\\u0627\\u062d\\u0633\\u0628 \\u0627\\u062d\\u062a\\u064a\\u0627\\u062c\\u0627\\u062a\\u0643 \\u0627\\u0644\\u0645\\u0627\\u0644\\u064a\\u0629 \\u0639\\u0646\\u062f \\u0627\\u0644\\u062a\\u0642\\u0627\\u0639\\u062f", "\\u0627\\u062f\\u062e\\u0631 \\u0646\\u0633\\u0628\\u0629 \\u062b\\u0627\\u0628\\u062a\\u0629 \\u0645\\u0646 \\u0631\\u0627\\u062a\\u0628\\u0643 \\u0634\\u0647\\u0631\\u064a\\u0627\\u064b", "\\u0627\\u0633\\u062a\\u0641\\u062f \\u0645\\u0646 \\u0628\\u0631\\u0627\\u0645\\u062c \\u0627\\u0644\\u062a\\u0642\\u0627\\u0639\\u062f \\u0641\\u064a \\u0627\\u0644\\u0639\\u0645\\u0644", "\\u0641\\u0643\\u0631 \\u0641\\u064a \\u0627\\u0633\\u062a\\u062b\\u0645\\u0627\\u0631\\u0627\\u062a \\u0637\\u0648\\u064a\\u0644\\u0629 \\u0627\\u0644\\u0645\\u062f\\u0649"], "uae_specific": ["\\u0635\\u0646\\u062f\\u0648\\u0642 \\u0627\\u0644\\u0645\\u0639\\u0627\\u0634\\u0627\\u062a \\u0648\\u0627\\u0644\\u062a\\u0623\\u0645\\u064a\\u0646\\u0627\\u062a \\u0627\\u0644\\u0627\\u062c\\u062a\\u0645\\u0627\\u0639\\u064a\\u0629", "\\u0628\\u0631\\u0627\\u0645\\u062c \\u0627\\u0644\\u062a\\u0642\\u0627\\u0639\\u062f \\u0641\\u064a \\u0627\\u0644\\u0634\\u0631\\u0643\\u0627\\u062a \\u0627\\u0644\\u062d\\u0643\\u0648\\u0645\\u064a\\u0629", "\\u062e\\u0637\\u0637 \\u0627\\u0644\\u062a\\u0642\\u0627\\u0639\\u062f \\u0641\\u064a \\u0627\\u0644\\u0628\\u0646\\u0648\\u0643 \\u0627\\u0644\\u0645\\u062d\\u0644\\u064a\\u0629"]}	1.0	t	2025-10-03 22:36:19.64314+05	\N
73	ui	welcome_message	en	\N	Welcome to Financial Health Assessment	null	null	1.0	t	2025-10-05 01:03:21.143509+05	\N
74	ui	start_survey	en	\N	Start Assessment	null	null	1.0	t	2025-10-05 01:03:21.198985+05	\N
75	ui	next_question	en	\N	Next Question	null	null	1.0	t	2025-10-05 01:03:21.213292+05	\N
76	ui	previous_question	en	\N	Previous Question	null	null	1.0	t	2025-10-05 01:03:21.222832+05	\N
77	ui	submit_survey	en	\N	Submit Assessment	null	null	1.0	t	2025-10-05 01:03:21.239054+05	\N
78	ui	your_results	en	\N	Your Results	null	null	1.0	t	2025-10-05 01:03:21.251837+05	\N
79	ui	download_pdf	en	\N	Download Report	null	null	1.0	t	2025-10-05 01:03:21.266099+05	\N
85	ui	access_previous_results	en	\N	Access Previous Results	null	null	1.0	t	2025-10-05 01:03:21.358264+05	\N
86	ui	view_previous_results	en	\N	View Previous Results	null	null	1.0	t	2025-10-05 01:03:21.381407+05	\N
87	ui	financial_health_score	en	\N	Financial Health Score	null	null	1.0	t	2025-10-05 01:03:21.400408+05	\N
88	ui	recommendations	en	\N	Recommendations	null	null	1.0	t	2025-10-05 01:03:21.412488+05	\N
89	ui	budgeting	en	\N	Budgeting	null	null	1.0	t	2025-10-05 01:03:21.420522+05	\N
90	ui	savings	en	\N	Savings	null	null	1.0	t	2025-10-05 01:03:21.429089+05	\N
91	ui	debt_management	en	\N	Debt Management	null	null	1.0	t	2025-10-05 01:03:21.435482+05	\N
92	ui	financial_planning	en	\N	Financial Planning	null	null	1.0	t	2025-10-05 01:03:21.44434+05	\N
93	ui	investment_knowledge	en	\N	Investment Knowledge	null	null	1.0	t	2025-10-05 01:03:21.450902+05	\N
94	ui	income_stream	en	\N	Income Stream	null	null	1.0	t	2025-10-05 01:03:21.462784+05	\N
95	ui	monthly_expenses	en	\N	Monthly Expenses Management	null	null	1.0	t	2025-10-05 01:03:21.469582+05	\N
96	ui	savings_habit	en	\N	Savings Habit	null	null	1.0	t	2025-10-05 01:03:21.480604+05	\N
97	ui	retirement_planning	en	\N	Retirement Planning	null	null	1.0	t	2025-10-05 01:03:21.492459+05	\N
98	ui	protection	en	\N	Protecting Your Assets & Loved Ones	null	null	1.0	t	2025-10-05 01:03:21.535747+05	\N
99	ui	future_planning	en	\N	Planning for Your Future & Siblings	null	null	1.0	t	2025-10-05 01:03:21.547678+05	\N
100	ui	excellent	en	\N	Excellent	null	null	1.0	t	2025-10-05 01:03:21.562465+05	\N
101	ui	good	en	\N	Good	null	null	1.0	t	2025-10-05 01:03:21.572808+05	\N
102	ui	fair	en	\N	Fair	null	null	1.0	t	2025-10-05 01:03:21.58156+05	\N
103	ui	needs_improvement	en	\N	Needs Improvement	null	null	1.0	t	2025-10-05 01:03:21.593435+05	\N
104	ui	poor	en	\N	Poor	null	null	1.0	t	2025-10-05 01:03:21.610382+05	\N
105	ui	at_risk	en	\N	At Risk	null	null	1.0	t	2025-10-05 01:03:21.619947+05	\N
106	ui	personal_information	en	\N	Personal Information	null	null	1.0	t	2025-10-05 01:03:21.745634+05	\N
107	ui	first_name	en	\N	First Name	null	null	1.0	t	2025-10-05 01:03:21.760703+05	\N
108	ui	last_name	en	\N	Last Name	null	null	1.0	t	2025-10-05 01:03:21.775619+05	\N
109	ui	age	en	\N	Age	null	null	1.0	t	2025-10-05 01:03:21.785333+05	\N
110	ui	gender	en	\N	Gender	null	null	1.0	t	2025-10-05 01:03:21.799187+05	\N
111	ui	male	en	\N	Male	null	null	1.0	t	2025-10-05 01:03:21.812102+05	\N
112	ui	female	en	\N	Female	null	null	1.0	t	2025-10-05 01:03:21.84607+05	\N
113	ui	other	en	\N	Other	null	null	1.0	t	2025-10-05 01:03:21.880872+05	\N
114	ui	prefer_not_to_say	en	\N	Prefer not to say	null	null	1.0	t	2025-10-05 01:03:21.919108+05	\N
115	ui	nationality	en	\N	Nationality	null	null	1.0	t	2025-10-05 01:03:21.935773+05	\N
116	ui	emirate	en	\N	Emirate	null	null	1.0	t	2025-10-05 01:03:21.95873+05	\N
117	ui	employment_status	en	\N	Employment Status	null	null	1.0	t	2025-10-05 01:03:21.980629+05	\N
118	ui	employment_sector	en	\N	Employment Sector	null	null	1.0	t	2025-10-05 01:03:22.001555+05	\N
119	ui	monthly_income	en	\N	Monthly Income	null	null	1.0	t	2025-10-05 01:03:22.015417+05	\N
120	ui	income_range	en	\N	Income Range	null	null	1.0	t	2025-10-05 01:03:22.033341+05	\N
121	ui	household_size	en	\N	Household Size	null	null	1.0	t	2025-10-05 01:03:22.047929+05	\N
122	ui	children	en	\N	Children	null	null	1.0	t	2025-10-05 01:03:22.061537+05	\N
123	ui	residence	en	\N	Residence	null	null	1.0	t	2025-10-05 01:03:22.072996+05	\N
124	ui	yes	en	\N	Yes	null	null	1.0	t	2025-10-05 01:03:22.084568+05	\N
125	ui	no	en	\N	No	null	null	1.0	t	2025-10-05 01:03:22.094846+05	\N
126	ui	email	en	\N	Email Address	null	null	1.0	t	2025-10-05 01:03:22.142511+05	\N
127	ui	phone_number	en	\N	Phone Number	null	null	1.0	t	2025-10-05 01:03:22.161619+05	\N
128	ui	save	en	\N	Save	null	null	1.0	t	2025-10-05 01:03:22.174964+05	\N
129	ui	cancel	en	\N	Cancel	null	null	1.0	t	2025-10-05 01:03:22.184998+05	\N
130	ui	edit	en	\N	Edit	null	null	1.0	t	2025-10-05 01:03:22.195116+05	\N
131	ui	delete	en	\N	Delete	null	null	1.0	t	2025-10-05 01:03:22.204839+05	\N
132	ui	confirm	en	\N	Confirm	null	null	1.0	t	2025-10-05 01:03:22.214175+05	\N
133	ui	back	en	\N	Back	null	null	1.0	t	2025-10-05 01:03:22.227461+05	\N
134	ui	continue	en	\N	Continue	null	null	1.0	t	2025-10-05 01:03:22.246205+05	\N
135	ui	complete	en	\N	Complete	null	null	1.0	t	2025-10-05 01:03:22.265358+05	\N
136	ui	skip	en	\N	Skip	null	null	1.0	t	2025-10-05 01:03:22.280243+05	\N
137	ui	loading	en	\N	Loading...	null	null	1.0	t	2025-10-05 01:03:22.328257+05	\N
138	ui	error	en	\N	Error	null	null	1.0	t	2025-10-05 01:03:22.337485+05	\N
139	ui	success	en	\N	Success	null	null	1.0	t	2025-10-05 01:03:22.346573+05	\N
140	ui	warning	en	\N	Warning	null	null	1.0	t	2025-10-05 01:03:22.359988+05	\N
141	ui	info	en	\N	Information	null	null	1.0	t	2025-10-05 01:03:22.369491+05	\N
142	ui	sign_in	en	\N	Sign In	null	null	1.0	t	2025-10-05 01:03:22.379216+05	\N
143	ui	sign_out	en	\N	Sign Out	null	null	1.0	t	2025-10-05 01:03:22.387042+05	\N
144	ui	sign_up	en	\N	Sign Up	null	null	1.0	t	2025-10-05 01:03:22.397428+05	\N
145	ui	welcome_back	en	\N	Welcome back!	null	null	1.0	t	2025-10-05 01:03:22.411099+05	\N
146	ui	date_of_birth	en	\N	Date of Birth	null	null	1.0	t	2025-10-05 01:03:22.418167+05	\N
147	ui	financial_health_assessment	en	\N	Financial Health Assessment	null	null	1.0	t	2025-10-05 01:03:22.428533+05	\N
148	ui	trusted_uae_institution	en	\N	A trusted UAE financial institution providing transparent, science-based financial wellness assessment.	null	null	1.0	t	2025-10-05 01:03:22.444968+05	\N
149	ui	get_personalized_insights	en	\N	Get personalized insights to strengthen your financial future.	null	null	1.0	t	2025-10-05 01:03:22.456006+05	\N
150	ui	transparent_scoring	en	\N	Transparent Scoring	null	null	1.0	t	2025-10-05 01:03:22.465195+05	\N
151	ui	privacy_protected	en	\N	Privacy Protected	null	null	1.0	t	2025-10-05 01:03:22.473698+05	\N
152	ui	personalized_insights	en	\N	Personalized Insights	null	null	1.0	t	2025-10-05 01:03:22.480999+05	\N
153	ui	progress_tracking	en	\N	Progress Tracking	null	null	1.0	t	2025-10-05 01:03:22.489999+05	\N
154	ui	science_based_methodology	en	\N	Science-Based Methodology	null	null	1.0	t	2025-10-05 01:03:22.549431+05	\N
155	ui	uae_specific_insights	en	\N	UAE-Specific Insights	null	null	1.0	t	2025-10-05 01:03:22.579325+05	\N
156	ui	ready_to_improve	en	\N	Ready to Improve Your Financial Health?	null	null	1.0	t	2025-10-05 01:03:22.610573+05	\N
157	ui	join_thousands	en	\N	Join thousands of UAE residents who have strengthened their financial future with our comprehensive assessment.	null	null	1.0	t	2025-10-05 01:03:22.617962+05	\N
158	ui	progress_overview	en	\N	Progress Overview	null	null	1.0	t	2025-10-05 01:03:22.633262+05	\N
159	ui	questions_total	en	\N	questions total	null	null	1.0	t	2025-10-05 01:03:22.645239+05	\N
160	ui	current	en	\N	Current	null	null	1.0	t	2025-10-05 01:03:22.657304+05	\N
161	ui	completed	en	\N	Completed	null	null	1.0	t	2025-10-05 01:03:22.667322+05	\N
162	ui	pending	en	\N	Pending	null	null	1.0	t	2025-10-05 01:03:22.677128+05	\N
163	ui	complete_assessment	en	\N	Complete Assessment	null	null	1.0	t	2025-10-05 01:03:22.685084+05	\N
165	ui	agree	en	\N	Agree	null	null	1.0	t	2025-10-05 01:03:22.70471+05	\N
166	ui	neutral	en	\N	Neutral	null	null	1.0	t	2025-10-05 01:03:22.717953+05	\N
167	ui	disagree	en	\N	Disagree	null	null	1.0	t	2025-10-05 01:03:22.727447+05	\N
168	ui	strongly_disagree	en	\N	Strongly Disagree	null	null	1.0	t	2025-10-05 01:03:22.735653+05	\N
169	ui	overall_score	en	\N	Overall Score	null	null	1.0	t	2025-10-05 01:03:22.742531+05	\N
170	ui	pillar_breakdown	en	\N	Pillar Breakdown	null	null	1.0	t	2025-10-05 01:03:22.754244+05	\N
171	ui	detailed_recommendations	en	\N	Detailed Recommendations	null	null	1.0	t	2025-10-05 01:03:22.766137+05	\N
172	ui	action_plan	en	\N	Action Plan	null	null	1.0	t	2025-10-05 01:03:22.794549+05	\N
173	ui	next_steps	en	\N	Next Steps	null	null	1.0	t	2025-10-05 01:03:22.809489+05	\N
174	ui	download_report	en	\N	Download Report	null	null	1.0	t	2025-10-05 01:03:22.818754+05	\N
175	ui	email_report	en	\N	Email Report	null	null	1.0	t	2025-10-05 01:03:22.829901+05	\N
176	ui	share_results	en	\N	Share Results	null	null	1.0	t	2025-10-05 01:03:22.836646+05	\N
177	ui	error_loading_questions	en	\N	Error loading questions. Please try again.	null	null	1.0	t	2025-10-05 01:03:22.84875+05	\N
178	ui	error_saving_response	en	\N	Error saving response. Please try again.	null	null	1.0	t	2025-10-05 01:03:22.859972+05	\N
179	ui	error_generating_report	en	\N	Error generating report. Please try again.	null	null	1.0	t	2025-10-05 01:03:22.867181+05	\N
180	ui	network_error	en	\N	Network error. Please check your connection.	null	null	1.0	t	2025-10-05 01:03:22.875547+05	\N
181	ui	field_required	en	\N	This field is required	null	null	1.0	t	2025-10-05 01:03:22.882061+05	\N
182	ui	invalid_email	en	\N	Please enter a valid email address	null	null	1.0	t	2025-10-05 01:03:22.889041+05	\N
183	ui	invalid_date	en	\N	Please enter a valid date	null	null	1.0	t	2025-10-05 01:03:22.903643+05	\N
184	ui	please_select_option	en	\N	Please select an option	null	null	1.0	t	2025-10-05 01:03:22.913322+05	\N
185	ui	of	en	\N	of	null	null	1.0	t	2025-10-05 01:03:22.923123+05	\N
186	ui	admin_dashboard	en	\N	Admin Dashboard	null	null	1.0	t	2025-10-05 01:03:22.930959+05	\N
187	ui	localization_management	en	\N	Localization Management	null	null	1.0	t	2025-10-05 01:03:22.938552+05	\N
188	ui	manage_translations	en	\N	Manage translations and localized content for multiple languages	null	null	1.0	t	2025-10-05 01:03:22.946944+05	\N
189	ui	content_type	en	\N	Content Type	null	null	1.0	t	2025-10-05 01:03:22.958759+05	\N
190	ui	language	en	\N	Language	null	null	1.0	t	2025-10-05 01:03:22.966108+05	\N
191	ui	version	en	\N	Version	null	null	1.0	t	2025-10-05 01:03:22.972906+05	\N
192	ui	status	en	\N	Status	null	null	1.0	t	2025-10-05 01:03:22.980925+05	\N
193	ui	actions	en	\N	Actions	null	null	1.0	t	2025-10-05 01:03:22.988028+05	\N
194	ui	active	en	\N	Active	null	null	1.0	t	2025-10-05 01:03:22.996407+05	\N
195	ui	inactive	en	\N	Inactive	null	null	1.0	t	2025-10-05 01:03:23.008532+05	\N
196	ui	add_content	en	\N	Add Content	null	null	1.0	t	2025-10-05 01:03:23.016286+05	\N
197	ui	new_workflow	en	\N	New Workflow	null	null	1.0	t	2025-10-05 01:03:23.024356+05	\N
198	ui	create_translation_workflow	en	\N	Create Translation Workflow	null	null	1.0	t	2025-10-05 01:03:23.031225+05	\N
199	ui	source_language	en	\N	Source Language	null	null	1.0	t	2025-10-05 01:03:23.040313+05	\N
200	ui	target_language	en	\N	Target Language	null	null	1.0	t	2025-10-05 01:03:23.051326+05	\N
201	ui	workflow_type	en	\N	Workflow Type	null	null	1.0	t	2025-10-05 01:03:23.06128+05	\N
202	ui	priority	en	\N	Priority	null	null	1.0	t	2025-10-05 01:03:23.071283+05	\N
203	ui	content_ids	en	\N	Content IDs	null	null	1.0	t	2025-10-05 01:03:23.080134+05	\N
204	ui	notes	en	\N	Notes	null	null	1.0	t	2025-10-05 01:03:23.089208+05	\N
205	ui	create_workflow	en	\N	Create Workflow	null	null	1.0	t	2025-10-05 01:03:23.101317+05	\N
206	ui	add_localized_content	en	\N	Add Localized Content	null	null	1.0	t	2025-10-05 01:03:23.111722+05	\N
207	ui	create_new_localized_content	en	\N	Create new localized content for questions, recommendations, or UI elements	null	null	1.0	t	2025-10-05 01:03:23.119017+05	\N
208	ui	content_id	en	\N	Content ID	null	null	1.0	t	2025-10-05 01:03:23.203169+05	\N
209	ui	title_optional	en	\N	Title (Optional)	null	null	1.0	t	2025-10-05 01:03:23.211345+05	\N
210	ui	text	en	\N	Text	null	null	1.0	t	2025-10-05 01:03:23.217822+05	\N
211	ui	localized_text_content	en	\N	Localized text content	null	null	1.0	t	2025-10-05 01:03:23.229195+05	\N
212	ui	create_content	en	\N	Create Content	null	null	1.0	t	2025-10-05 01:03:23.238383+05	\N
213	ui	filters	en	\N	Filters	null	null	1.0	t	2025-10-05 01:03:23.246295+05	\N
214	ui	all_types	en	\N	All types	null	null	1.0	t	2025-10-05 01:03:23.256459+05	\N
215	ui	all_languages	en	\N	All languages	null	null	1.0	t	2025-10-05 01:03:23.263464+05	\N
216	ui	active_only	en	\N	Active only	null	null	1.0	t	2025-10-05 01:03:23.272979+05	\N
217	ui	localized_content	en	\N	Localized Content	null	null	1.0	t	2025-10-05 01:03:23.282024+05	\N
218	ui	content_items_found	en	\N	content items found	null	null	1.0	t	2025-10-05 01:03:23.288988+05	\N
219	ui	no_localized_content_found	en	\N	No localized content found	null	null	1.0	t	2025-10-05 01:03:23.296797+05	\N
220	ui	translation_workflows	en	\N	Translation Workflows	null	null	1.0	t	2025-10-05 01:03:23.306779+05	\N
221	ui	active_completed_workflows	en	\N	Active and completed translation workflows	null	null	1.0	t	2025-10-05 01:03:23.313814+05	\N
222	ui	no_translation_workflows_found	en	\N	No translation workflows found	null	null	1.0	t	2025-10-05 01:03:23.320251+05	\N
223	ui	analytics	en	\N	Analytics	null	null	1.0	t	2025-10-05 01:03:23.328926+05	\N
224	ui	workflows	en	\N	Workflows	null	null	1.0	t	2025-10-05 01:03:23.335624+05	\N
225	ui	content	en	\N	Content	null	null	1.0	t	2025-10-05 01:03:23.344249+05	\N
226	ui	customer_profile	en	\N	Customer Profile	null	null	1.0	t	2025-10-05 01:03:23.354457+05	\N
227	ui	please_provide_information	en	\N	Please provide your information to get personalized recommendations	null	null	1.0	t	2025-10-05 01:03:23.36647+05	\N
228	ui	uae_national	en	\N	UAE National	null	null	1.0	t	2025-10-05 01:03:23.382026+05	\N
229	ui	expat	en	\N	Expat	null	null	1.0	t	2025-10-05 01:03:23.392406+05	\N
230	ui	abu_dhabi	en	\N	Abu Dhabi	null	null	1.0	t	2025-10-05 01:03:23.408697+05	\N
231	ui	dubai	en	\N	Dubai	null	null	1.0	t	2025-10-05 01:03:23.418159+05	\N
232	ui	sharjah	en	\N	Sharjah	null	null	1.0	t	2025-10-05 01:03:23.430524+05	\N
233	ui	ajman	en	\N	Ajman	null	null	1.0	t	2025-10-05 01:03:23.446651+05	\N
234	ui	ras_al_khaimah	en	\N	Ras Al Khaimah	null	null	1.0	t	2025-10-05 01:03:23.519424+05	\N
235	ui	fujairah	en	\N	Fujairah	null	null	1.0	t	2025-10-05 01:03:23.531987+05	\N
236	ui	umm_al_quwain	en	\N	Umm Al Quwain	null	null	1.0	t	2025-10-05 01:03:23.54716+05	\N
237	ui	employed_full_time	en	\N	Employed (Full-time)	null	null	1.0	t	2025-10-05 01:03:23.559747+05	\N
238	ui	employed_part_time	en	\N	Employed (Part-time)	null	null	1.0	t	2025-10-05 01:03:23.56619+05	\N
239	ui	self_employed	en	\N	Self-employed	null	null	1.0	t	2025-10-05 01:03:23.573678+05	\N
240	ui	unemployed	en	\N	Unemployed	null	null	1.0	t	2025-10-05 01:03:23.580348+05	\N
241	ui	retired	en	\N	Retired	null	null	1.0	t	2025-10-05 01:03:23.586665+05	\N
242	ui	student	en	\N	Student	null	null	1.0	t	2025-10-05 01:03:23.593566+05	\N
243	ui	less_than_5000	en	\N	Less than AED 5,000	null	null	1.0	t	2025-10-05 01:03:23.605788+05	\N
244	ui	5000_to_10000	en	\N	AED 5,000 - 10,000	null	null	1.0	t	2025-10-05 01:03:23.619128+05	\N
245	ui	10000_to_20000	en	\N	AED 10,000 - 20,000	null	null	1.0	t	2025-10-05 01:03:23.633423+05	\N
246	ui	20000_to_50000	en	\N	AED 20,000 - 50,000	null	null	1.0	t	2025-10-05 01:03:23.650185+05	\N
247	ui	more_than_50000	en	\N	More than AED 50,000	null	null	1.0	t	2025-10-05 01:03:23.67544+05	\N
248	ui	your_financial_health_score	en	\N	Your Financial Health Score	null	null	1.0	t	2025-10-05 01:03:23.690995+05	\N
249	ui	score_out_of_100	en	\N	Score: {{score}} out of 100	null	null	1.0	t	2025-10-05 01:03:23.717274+05	\N
250	ui	score_interpretation	en	\N	Score Interpretation	null	null	1.0	t	2025-10-05 01:03:23.748641+05	\N
251	ui	pillar_scores	en	\N	Pillar Scores	null	null	1.0	t	2025-10-05 01:03:23.762262+05	\N
252	ui	personalized_recommendations	en	\N	Personalized Recommendations	null	null	1.0	t	2025-10-05 01:03:23.77712+05	\N
253	ui	download_detailed_report	en	\N	Download Detailed Report	null	null	1.0	t	2025-10-05 01:03:23.784489+05	\N
254	ui	email_results	en	\N	Email Results	null	null	1.0	t	2025-10-05 01:03:23.796173+05	\N
255	ui	retake_assessment	en	\N	Retake Assessment	null	null	1.0	t	2025-10-05 01:03:23.809589+05	\N
256	ui	report_delivery	en	\N	Report Delivery	null	null	1.0	t	2025-10-05 01:03:23.817629+05	\N
257	ui	send_report_email	en	\N	Send Report via Email	null	null	1.0	t	2025-10-05 01:03:23.829943+05	\N
258	ui	enter_email_address	en	\N	Enter your email address to receive the detailed report	null	null	1.0	t	2025-10-05 01:03:23.864966+05	\N
259	ui	send_report	en	\N	Send Report	null	null	1.0	t	2025-10-05 01:03:23.877849+05	\N
260	ui	download_pdf_report	en	\N	Download PDF Report	null	null	1.0	t	2025-10-05 01:03:23.884781+05	\N
261	ui	generating_report	en	\N	Generating your personalized report...	null	null	1.0	t	2025-10-05 01:03:23.901886+05	\N
262	ui	report_sent_successfully	en	\N	Report sent successfully to your email!	null	null	1.0	t	2025-10-05 01:03:23.91857+05	\N
263	ui	report_generation_failed	en	\N	Failed to generate report. Please try again.	null	null	1.0	t	2025-10-05 01:03:23.931907+05	\N
264	ui	email_sending_failed	en	\N	Failed to send email. Please try again.	null	null	1.0	t	2025-10-05 01:03:24.049177+05	\N
265	question	q1_income_stability	en	\N	My income is stable and predictable each month.	[{"value": 5, "label": "Strongly Agree"}, {"value": 4, "label": "Agree"}, {"value": 3, "label": "Neutral"}, {"value": 2, "label": "Disagree"}, {"value": 1, "label": "Strongly Disagree"}]	null	1.0	t	2025-10-05 01:03:24.058615+05	\N
266	question	q2_income_sources	en	\N	I have more than one source of income (e.g., side business, investments).	[{"value": 5, "label": "Multiple consistent income streams"}, {"value": 4, "label": "Multiple inconsistent income streams"}, {"value": 3, "label": "I have a consistent side income"}, {"value": 2, "label": "A non consistent side income"}, {"value": 1, "label": "My Salary"}]	null	1.0	t	2025-10-05 01:03:24.067521+05	\N
267	question	q3_living_expenses	en	\N	I can cover my essential living expenses without financial strain.	[{"value": 5, "label": "Strongly Agree"}, {"value": 4, "label": "Agree"}, {"value": 3, "label": "Neutral"}, {"value": 2, "label": "Disagree"}, {"value": 1, "label": "Strongly Disagree"}]	null	1.0	t	2025-10-05 01:03:24.077057+05	\N
268	question	q4_budget_tracking	en	\N	I follow a monthly budget and track my expenses.	[{"value": 5, "label": "Consistently every month"}, {"value": 4, "label": "Frequently but not consistently"}, {"value": 3, "label": "Occasionally"}, {"value": 2, "label": "Adhoc"}, {"value": 1, "label": "No Tracking"}]	null	1.0	t	2025-10-05 01:03:24.144403+05	\N
269	question	q5_spending_control	en	\N	I spend less than I earn every month.	[{"value": 5, "label": "Consistently every month"}, {"value": 4, "label": "Frequently but not consistently"}, {"value": 3, "label": "Occasionally"}, {"value": 2, "label": "Adhoc"}, {"value": 1, "label": "Greater or all of my earnings"}]	null	1.0	t	2025-10-05 01:03:24.158425+05	\N
270	question	q6_expense_review	en	\N	I regularly review and reduce unnecessary expenses.	[{"value": 5, "label": "Consistently every month"}, {"value": 4, "label": "Frequently but not consistently"}, {"value": 3, "label": "Occasionally"}, {"value": 2, "label": "Adhoc"}, {"value": 1, "label": "No Tracking"}]	null	1.0	t	2025-10-05 01:03:24.173582+05	\N
271	question	q7_savings_rate	en	\N	I save from my income every month.	[{"value": 5, "label": "20% or more"}, {"value": 4, "label": "Less than 20%"}, {"value": 3, "label": "Less than 10%"}, {"value": 2, "label": "5% or less"}, {"value": 1, "label": "0%"}]	null	1.0	t	2025-10-05 01:03:24.185674+05	\N
272	question	q8_emergency_fund	en	\N	I have an emergency fund to cater for my expenses.	[{"value": 5, "label": "6+ months"}, {"value": 4, "label": "3 - 6 months"}, {"value": 3, "label": "2 months"}, {"value": 2, "label": "1 month"}, {"value": 1, "label": "Nil"}]	null	1.0	t	2025-10-05 01:03:24.201823+05	\N
273	question	q9_savings_optimization	en	\N	I keep my savings in safe, return generating accounts or investments.	[{"value": 5, "label": "Safe | Seek for return optimization consistently"}, {"value": 4, "label": "Safe | Seek for return optimization most of the times"}, {"value": 3, "label": "Savings Account with minimal returns"}, {"value": 2, "label": "Current Account"}, {"value": 1, "label": "Cash"}]	null	1.0	t	2025-10-05 01:03:24.216882+05	\N
274	question	q10_payment_history	en	\N	I pay all my bills and loan installments on time.	[{"value": 5, "label": "Consistently every month"}, {"value": 4, "label": "Frequently but not consistently"}, {"value": 3, "label": "Occasionally"}, {"value": 2, "label": "Adhoc"}, {"value": 1, "label": "Missed Payments most of the times"}]	null	1.0	t	2025-10-05 01:03:24.245935+05	\N
275	question	q11_debt_ratio	en	\N	My debt repayments are less than 30% of my monthly income.	[{"value": 5, "label": "No Debt"}, {"value": 4, "label": "20% or less of monthly income"}, {"value": 3, "label": "Less than 30% of monthly income"}, {"value": 2, "label": "30% or more of monthly income"}, {"value": 1, "label": "50% or more of monthly income"}]	null	1.0	t	2025-10-05 01:03:24.25911+05	\N
276	question	q12_credit_score	en	\N	I understand my credit score and actively maintain or improve it.	[{"value": 5, "label": "100% and monitor it consistently"}, {"value": 4, "label": "100% and monitor it frequently"}, {"value": 3, "label": "somewhat understand and frequent monitoring"}, {"value": 2, "label": "somewhat understand and maintain on an adhoc basis"}, {"value": 1, "label": "No Understanding and not maintained"}]	null	1.0	t	2025-10-05 01:03:24.267809+05	\N
277	question	q13_retirement_planning	en	\N	I have a retirement savings plan or pension fund in place to secure a stable income at retirement.	[{"value": 5, "label": "Yes - I have already secured a stable income"}, {"value": 4, "label": "Yes - I am highly confident of having a stable income"}, {"value": 3, "label": "Yes - I am somewhat confident of having a stable income"}, {"value": 2, "label": "No: Planning to have one shortly | adhoc Savings"}, {"value": 1, "label": "No: not for the time being"}]	null	1.0	t	2025-10-05 01:03:24.277668+05	\N
330	ui	get_personalized_insights	ar	\N	احصل على رؤى مخصصة لتعزيز مستقبلك المالي.	null	null	1.0	t	2025-10-05 01:26:39.443562+05	\N
341	ui	score_breakdown	en	\N	Score Breakdown	\N	\N	\N	t	2025-10-06 01:01:53.304327+05	2025-10-06 01:01:53.304333+05
278	question	q14_insurance_coverage	en	\N	I have adequate takaful cover (insurance) - (health, life, motor, property).	[{"value": 5, "label": "100% adequate cover in place for the required protection"}, {"value": 4, "label": "80% cover in place for the required protection"}, {"value": 3, "label": "50% cover in place for the required protection"}, {"value": 2, "label": "25% cover in place for the required protection"}, {"value": 1, "label": "No Coverage"}]	null	1.0	t	2025-10-05 01:03:24.295625+05	\N
279	question	q15_financial_planning	en	\N	I have a written financial plan with goals for the next 3–5 years catering.	[{"value": 5, "label": "Concise Financial plan in place and consistently reviewed"}, {"value": 4, "label": "Broad Financial plan in place and frequently reviewed"}, {"value": 3, "label": "High level objectives set and occasionally reviewed"}, {"value": 2, "label": "Adhoc Plan | reviews"}, {"value": 1, "label": "No Financial Plan in place"}]	null	1.0	t	2025-10-05 01:03:24.309693+05	\N
280	question	q16_children_planning	en	\N	I have adequately planned my children future for his school | University | Career Start Up.	[{"value": 5, "label": "100% adequate savings in place for all 3 Aspects"}, {"value": 4, "label": "80% savings in place for all 3 Aspects"}, {"value": 3, "label": "50% savings in place for all 3 Aspects"}, {"value": 2, "label": "Adhoc plan in place for all 3 Aspects"}, {"value": 1, "label": "No Plan in place"}]	null	1.0	t	2025-10-05 01:03:24.319467+05	\N
281	recommendation	budgeting_basic	en	Improve Budget Management	Create a detailed monthly budget to track your income and expenses. Use money management apps or simple spreadsheets to monitor your daily spending.	null	{"category": "budgeting"}	1.0	t	2025-10-05 01:03:24.334575+05	\N
282	recommendation	savings_emergency	en	Build Emergency Fund	It's crucial to have an emergency fund that covers your expenses for 3-6 months. Start by saving a small amount monthly until you reach your target.	null	{"category": "savings"}	1.0	t	2025-10-05 01:03:24.347293+05	\N
283	recommendation	debt_management	en	Manage Debt Effectively	If you have multiple debts, focus on paying off high-interest debts first. Consider debt consolidation if it reduces your overall interest payments.	null	{"category": "debt_management"}	1.0	t	2025-10-05 01:03:24.362698+05	\N
284	recommendation	investment_basic	en	Start Investing	Begin your investment journey by learning the basics first. Consider investing in index funds or diversified funds as a safe starting point.	null	{"category": "investment"}	1.0	t	2025-10-05 01:03:24.373872+05	\N
285	recommendation	retirement_planning	en	Plan for Retirement	It's never too late to start planning for retirement. Save at least 10-15% of your income for retirement and take advantage of any employer retirement programs.	null	{"category": "retirement_planning"}	1.0	t	2025-10-05 01:03:24.391789+05	\N
286	ui	continue	ar	\N	متابعة	null	null	1.0	t	2025-10-05 01:03:50.481922+05	\N
287	ui	back	ar	\N	رجوع	null	null	1.0	t	2025-10-05 01:03:50.497474+05	\N
288	ui	complete	ar	\N	إكمال	null	null	1.0	t	2025-10-05 01:03:50.507077+05	\N
3	question	q1_income_stability	ar	\N	دخلي مستقر ويمكن التنبؤ به كل شهر.	[{"value": 5, "label": "\\u0623\\u0648\\u0627\\u0641\\u0642 \\u0628\\u0634\\u062f\\u0629"}, {"value": 4, "label": "\\u0623\\u0648\\u0627\\u0641\\u0642"}, {"value": 3, "label": "\\u0645\\u062d\\u0627\\u064a\\u062f"}, {"value": 2, "label": "\\u0644\\u0627 \\u0623\\u0648\\u0627\\u0641\\u0642"}, {"value": 1, "label": "\\u0644\\u0627 \\u0623\\u0648\\u0627\\u0641\\u0642 \\u0628\\u0634\\u062f\\u0629"}]	null	1.0	t	2025-10-03 22:36:12.976311+05	2025-10-05 01:03:50.525298+05
4	question	q2_income_sources	ar	\N	لدي أكثر من مصدر دخل واحد (مثل عمل جانبي، استثمارات).	[{"value": 5, "label": "\\u0645\\u0635\\u0627\\u062f\\u0631 \\u062f\\u062e\\u0644 \\u0645\\u062a\\u0639\\u062f\\u062f\\u0629 \\u0648\\u0645\\u0633\\u062a\\u0642\\u0631\\u0629"}, {"value": 4, "label": "\\u0645\\u0635\\u0627\\u062f\\u0631 \\u062f\\u062e\\u0644 \\u0645\\u062a\\u0639\\u062f\\u062f\\u0629 \\u0648\\u063a\\u064a\\u0631 \\u0645\\u0633\\u062a\\u0642\\u0631\\u0629"}, {"value": 3, "label": "\\u0644\\u062f\\u064a \\u062f\\u062e\\u0644 \\u062c\\u0627\\u0646\\u0628\\u064a \\u0645\\u0633\\u062a\\u0642\\u0631"}, {"value": 2, "label": "\\u062f\\u062e\\u0644 \\u062c\\u0627\\u0646\\u0628\\u064a \\u063a\\u064a\\u0631 \\u0645\\u0633\\u062a\\u0642\\u0631"}, {"value": 1, "label": "\\u0631\\u0627\\u062a\\u0628\\u064a \\u0641\\u0642\\u0637"}]	null	1.0	t	2025-10-03 22:36:13.767284+05	2025-10-05 01:03:50.541638+05
289	question	q3_living_expenses	ar	\N	يمكنني تغطية نفقات المعيشة الأساسية دون ضغط مالي.	[{"value": 5, "label": "\\u0623\\u0648\\u0627\\u0641\\u0642 \\u0628\\u0634\\u062f\\u0629"}, {"value": 4, "label": "\\u0623\\u0648\\u0627\\u0641\\u0642"}, {"value": 3, "label": "\\u0645\\u062d\\u0627\\u064a\\u062f"}, {"value": 2, "label": "\\u0644\\u0627 \\u0623\\u0648\\u0627\\u0641\\u0642"}, {"value": 1, "label": "\\u0644\\u0627 \\u0623\\u0648\\u0627\\u0641\\u0642 \\u0628\\u0634\\u062f\\u0629"}]	null	1.0	t	2025-10-05 01:03:50.553344+05	\N
291	question	q13_retirement_planning	ar	\N	لدي خطة ادخار للتقاعد أو صندوق معاشات لضمان دخل مستقر عند التقاعد.	[{"value": 5, "label": "\\u0646\\u0639\\u0645 - \\u0644\\u0642\\u062f \\u0636\\u0645\\u0646\\u062a \\u062f\\u062e\\u0644\\u0627\\u064b \\u0645\\u0633\\u062a\\u0642\\u0631\\u0627\\u064b \\u0628\\u0627\\u0644\\u0641\\u0639\\u0644"}, {"value": 4, "label": "\\u0646\\u0639\\u0645 - \\u0623\\u0646\\u0627 \\u0648\\u0627\\u062b\\u0642 \\u062c\\u062f\\u0627\\u064b \\u0645\\u0646 \\u0627\\u0644\\u062d\\u0635\\u0648\\u0644 \\u0639\\u0644\\u0649 \\u062f\\u062e\\u0644 \\u0645\\u0633\\u062a\\u0642\\u0631"}, {"value": 3, "label": "\\u0646\\u0639\\u0645 - \\u0623\\u0646\\u0627 \\u0648\\u0627\\u062b\\u0642 \\u0625\\u0644\\u0649 \\u062d\\u062f \\u0645\\u0627 \\u0645\\u0646 \\u0627\\u0644\\u062d\\u0635\\u0648\\u0644 \\u0639\\u0644\\u0649 \\u062f\\u062e\\u0644 \\u0645\\u0633\\u062a\\u0642\\u0631"}, {"value": 2, "label": "\\u0644\\u0627: \\u0623\\u062e\\u0637\\u0637 \\u0644\\u0644\\u062d\\u0635\\u0648\\u0644 \\u0639\\u0644\\u0649 \\u0648\\u0627\\u062d\\u062f\\u0629 \\u0642\\u0631\\u064a\\u0628\\u0627\\u064b | \\u0645\\u062f\\u062e\\u0631\\u0627\\u062a \\u0639\\u0634\\u0648\\u0627\\u0626\\u064a\\u0629"}, {"value": 1, "label": "\\u0644\\u0627: \\u0644\\u064a\\u0633 \\u0641\\u064a \\u0627\\u0644\\u0648\\u0642\\u062a \\u0627\\u0644\\u062d\\u0627\\u0644\\u064a"}]	null	1.0	t	2025-10-05 01:03:50.574994+05	\N
331	ui	assessment_progress	en	\N	Assessment Progress	\N	\N	\N	t	2025-10-06 01:01:53.258333+05	2025-10-06 01:01:53.258351+05
332	ui	assessment_progress	ar	\N	تقدم التقييم	\N	\N	\N	t	2025-10-06 01:01:53.289813+05	2025-10-06 01:01:53.289821+05
333	ui	question_of	en	\N	Question {{current}} of {{total}}	\N	\N	\N	t	2025-10-06 01:01:53.291163+05	2025-10-06 01:01:53.29117+05
334	ui	question_of	ar	\N	السؤال {{current}} من {{total}}	\N	\N	\N	t	2025-10-06 01:01:53.292237+05	2025-10-06 01:01:53.292244+05
335	ui	assessment_complete	en	\N	Assessment Complete	\N	\N	\N	t	2025-10-06 01:01:53.293093+05	2025-10-06 01:01:53.293101+05
336	ui	assessment_complete	ar	\N	اكتمل التقييم	\N	\N	\N	t	2025-10-06 01:01:53.298258+05	2025-10-06 01:01:53.298266+05
337	ui	calculating_results	en	\N	Calculating your results...	\N	\N	\N	t	2025-10-06 01:01:53.299506+05	2025-10-06 01:01:53.299514+05
338	ui	calculating_results	ar	\N	جاري حساب النتائج...	\N	\N	\N	t	2025-10-06 01:01:53.300737+05	2025-10-06 01:01:53.300743+05
339	ui	your_score	en	\N	Your Score	\N	\N	\N	t	2025-10-06 01:01:53.302014+05	2025-10-06 01:01:53.302026+05
340	ui	your_score	ar	\N	درجتك	\N	\N	\N	t	2025-10-06 01:01:53.303248+05	2025-10-06 01:01:53.303255+05
68	recommendation	budgeting_basic	ar	تحسين إدارة الميزانية	أنشئ ميزانية شهرية مفصلة لتتبع دخلك ونفقاتك. استخدم تطبيقات إدارة المال أو جداول بيانات بسيطة لمراقبة إنفاقك اليومي.	null	{"action_steps": ["\\u0633\\u062c\\u0644 \\u062c\\u0645\\u064a\\u0639 \\u0645\\u0635\\u0627\\u062f\\u0631 \\u062f\\u062e\\u0644\\u0643 \\u0627\\u0644\\u0634\\u0647\\u0631\\u064a", "\\u0627\\u0643\\u062a\\u0628 \\u062c\\u0645\\u064a\\u0639 \\u0646\\u0641\\u0642\\u0627\\u062a\\u0643 \\u0627\\u0644\\u062b\\u0627\\u0628\\u062a\\u0629 \\u0648\\u0627\\u0644\\u0645\\u062a\\u063a\\u064a\\u0631\\u0629", "\\u062d\\u062f\\u062f \\u0623\\u0648\\u0644\\u0648\\u064a\\u0627\\u062a \\u0627\\u0644\\u0625\\u0646\\u0641\\u0627\\u0642", "\\u0631\\u0627\\u062c\\u0639 \\u0645\\u064a\\u0632\\u0627\\u0646\\u064a\\u062a\\u0643 \\u0623\\u0633\\u0628\\u0648\\u0639\\u064a\\u0627\\u064b"], "cultural_note": "\\u064a\\u064f\\u0646\\u0635\\u062d \\u0628\\u062a\\u062e\\u0635\\u064a\\u0635 \\u062c\\u0632\\u0621 \\u0645\\u0646 \\u0627\\u0644\\u062f\\u062e\\u0644 \\u0644\\u0644\\u0632\\u0643\\u0627\\u0629 \\u0648\\u0627\\u0644\\u0635\\u062f\\u0642\\u0627\\u062a \\u062d\\u0633\\u0628 \\u0627\\u0644\\u062a\\u0639\\u0627\\u0644\\u064a\\u0645 \\u0627\\u0644\\u0625\\u0633\\u0644\\u0627\\u0645\\u064a\\u0629"}	1.0	t	2025-10-03 22:36:18.914092+05	2025-10-05 01:03:50.612962+05
292	ui	transparent_scoring_description	en	\N	Understand exactly how your score is calculated with clear explanations for each factor.	null	null	1.0	t	2025-10-05 01:13:39.161179+05	\N
293	ui	privacy_protected_description	en	\N	Your data is handled according to UAE PDPL regulations with full consent management.	null	null	1.0	t	2025-10-05 01:13:39.246286+05	\N
294	ui	personalized_insights_description	en	\N	Receive tailored recommendations based on your unique financial situation and goals.	null	null	1.0	t	2025-10-05 01:13:39.263097+05	\N
295	ui	progress_tracking_description	en	\N	Save your results with just email and date of birth. No passwords needed to track your progress over time.	null	null	1.0	t	2025-10-05 01:13:39.280395+05	\N
296	ui	about_financial_health_assessment	en	\N	About Financial Health Assessment	null	null	1.0	t	2025-10-05 01:13:39.29014+05	\N
297	ui	science_based_methodology_description	en	\N	Our assessment uses proven financial wellness metrics adapted specifically for UAE residents. The scoring system evaluates five key pillars of financial health.	null	null	1.0	t	2025-10-05 01:13:39.297033+05	\N
298	ui	budgeting_expense_management	en	\N	Budgeting & Expense Management	null	null	1.0	t	2025-10-05 01:13:39.309719+05	\N
299	ui	savings_emergency_funds	en	\N	Savings & Emergency Funds	null	null	1.0	t	2025-10-05 01:13:39.320255+05	\N
300	ui	financial_planning_goals	en	\N	Financial Planning & Goals	null	null	1.0	t	2025-10-05 01:13:39.327067+05	\N
301	ui	investment_wealth_building	en	\N	Investment & Wealth Building	null	null	1.0	t	2025-10-05 01:13:39.333765+05	\N
302	ui	uae_specific_insights_description	en	\N	Tailored for the UAE market with localized recommendations that consider Emirates-specific financial products, regulations, and cultural factors.	null	null	1.0	t	2025-10-05 01:13:39.341942+05	\N
303	ui	uae_banking_products_services	en	\N	UAE banking products & services	null	null	1.0	t	2025-10-05 01:13:39.347649+05	\N
304	ui	adcb_emirates_nbd_partnerships	en	\N	ADCB & Emirates NBD partnerships	null	null	1.0	t	2025-10-05 01:13:39.354393+05	\N
305	ui	sharia_compliant_options	en	\N	Sharia-compliant options	null	null	1.0	t	2025-10-05 01:13:39.362159+05	\N
306	ui	expat_specific_considerations	en	\N	Expat-specific considerations	null	null	1.0	t	2025-10-05 01:13:39.369361+05	\N
307	ui	local_investment_opportunities	en	\N	Local investment opportunities	null	null	1.0	t	2025-10-05 01:13:39.3748+05	\N
308	ui	save_results_no_passwords	en	\N	Save your results with just your email and date of birth - no passwords required!	null	null	1.0	t	2025-10-05 01:13:39.380104+05	\N
309	ui	continue_your_journey	en	\N	Continue Your Journey	null	null	1.0	t	2025-10-05 01:13:39.401919+05	\N
310	ui	transparent_scoring_description	ar	\N	افهم بالضبط كيف يتم حساب درجتك مع شرح واضح لكل عامل.	null	null	1.0	t	2025-10-05 01:13:39.407972+05	\N
311	ui	privacy_protected_description	ar	\N	يتم التعامل مع بياناتك وفقاً لقانون حماية البيانات الإماراتي مع إدارة كاملة للموافقة.	null	null	1.0	t	2025-10-05 01:13:39.414157+05	\N
312	ui	personalized_insights_description	ar	\N	احصل على توصيات مخصصة بناءً على وضعك المالي وأهدافك الفريدة.	null	null	1.0	t	2025-10-05 01:13:39.423807+05	\N
313	ui	progress_tracking_description	ar	\N	احفظ نتائجك بمجرد البريد الإلكتروني وتاريخ الميلاد. لا حاجة لكلمات مرور لتتبع تقدمك عبر الزمن.	null	null	1.0	t	2025-10-05 01:13:39.430363+05	\N
314	ui	about_financial_health_assessment	ar	\N	حول تقييم الصحة المالية	null	null	1.0	t	2025-10-05 01:13:39.438812+05	\N
315	ui	science_based_methodology_description	ar	\N	يستخدم تقييمنا مقاييس العافية المالية المثبتة والمكيفة خصيصاً لسكان دولة الإمارات. يقيم نظام التسجيل خمسة أركان رئيسية للصحة المالية.	null	null	1.0	t	2025-10-05 01:13:39.448595+05	\N
316	ui	budgeting_expense_management	ar	\N	إدارة الميزانية والنفقات	null	null	1.0	t	2025-10-05 01:13:39.457312+05	\N
317	ui	savings_emergency_funds	ar	\N	المدخرات وصناديق الطوارئ	null	null	1.0	t	2025-10-05 01:13:39.462363+05	\N
318	ui	financial_planning_goals	ar	\N	التخطيط المالي والأهداف	null	null	1.0	t	2025-10-05 01:13:39.471174+05	\N
319	ui	investment_wealth_building	ar	\N	الاستثمار وبناء الثروة	null	null	1.0	t	2025-10-05 01:13:39.503864+05	\N
320	ui	uae_specific_insights_description	ar	\N	مصمم خصيصاً للسوق الإماراتي مع توصيات محلية تأخذ في الاعتبار المنتجات المالية واللوائح والعوامل الثقافية الخاصة بالإمارات.	null	null	1.0	t	2025-10-05 01:13:39.508929+05	\N
321	ui	uae_banking_products_services	ar	\N	المنتجات والخدمات المصرفية الإماراتية	null	null	1.0	t	2025-10-05 01:13:39.514688+05	\N
322	ui	adcb_emirates_nbd_partnerships	ar	\N	شراكات بنك أبوظبي التجاري وبنك الإمارات دبي الوطني	null	null	1.0	t	2025-10-05 01:13:39.523629+05	\N
323	ui	sharia_compliant_options	ar	\N	خيارات متوافقة مع الشريعة	null	null	1.0	t	2025-10-05 01:13:39.53489+05	\N
324	ui	expat_specific_considerations	ar	\N	اعتبارات خاصة بالمغتربين	null	null	1.0	t	2025-10-05 01:13:39.542881+05	\N
325	ui	local_investment_opportunities	ar	\N	فرص الاستثمار المحلية	null	null	1.0	t	2025-10-05 01:13:39.549225+05	\N
326	ui	save_results_no_passwords	ar	\N	احفظ نتائجك بمجرد بريدك الإلكتروني وتاريخ ميلادك - لا حاجة لكلمات مرور!	null	null	1.0	t	2025-10-05 01:13:39.556414+05	\N
327	ui	continue_your_journey	ar	\N	تابع رحلتك	null	null	1.0	t	2025-10-05 01:13:39.562782+05	\N
328	ui	financial_health_assessment	ar	\N	تقييم الصحة المالية	null	null	1.0	t	2025-10-05 01:24:04.499436+05	\N
329	ui	trusted_uae_institution	ar	\N	مؤسسة مالية إماراتية موثوقة تقدم تقييماً شفافاً ومبنياً على العلم للعافية المالية.	null	null	1.0	t	2025-10-05 01:26:39.42609+05	\N
342	ui	score_breakdown	ar	\N	تفصيل الدرجات	\N	\N	\N	t	2025-10-06 01:01:53.30529+05	2025-10-06 01:01:53.305297+05
343	ui	improvement_areas	en	\N	Areas for Improvement	\N	\N	\N	t	2025-10-06 01:01:53.306441+05	2025-10-06 01:01:53.306449+05
344	ui	improvement_areas	ar	\N	مجالات التحسين	\N	\N	\N	t	2025-10-06 01:01:53.307481+05	2025-10-06 01:01:53.307487+05
345	ui	strengths	en	\N	Your Strengths	\N	\N	\N	t	2025-10-06 01:01:53.308738+05	2025-10-06 01:01:53.308814+05
346	ui	strengths	ar	\N	نقاط قوتك	\N	\N	\N	t	2025-10-06 01:01:53.310012+05	2025-10-06 01:01:53.310019+05
347	ui	next_steps_title	en	\N	Recommended Next Steps	\N	\N	\N	t	2025-10-06 01:01:53.311118+05	2025-10-06 01:01:53.311125+05
348	ui	next_steps_title	ar	\N	الخطوات التالية الموصى بها	\N	\N	\N	t	2025-10-06 01:01:53.312288+05	2025-10-06 01:01:53.312297+05
349	ui	score_excellent_desc	en	\N	Outstanding financial health! You have strong financial habits and planning.	\N	\N	\N	t	2025-10-06 01:01:53.313264+05	2025-10-06 01:01:53.31327+05
350	ui	score_excellent_desc	ar	\N	صحة مالية ممتازة! لديك عادات مالية قوية وتخطيط جيد.	\N	\N	\N	t	2025-10-06 01:01:53.314176+05	2025-10-06 01:01:53.314183+05
351	ui	score_good_desc	en	\N	Good financial health with room for improvement in some areas.	\N	\N	\N	t	2025-10-06 01:01:53.315268+05	2025-10-06 01:01:53.315275+05
352	ui	score_good_desc	ar	\N	صحة مالية جيدة مع مجال للتحسين في بعض المناطق.	\N	\N	\N	t	2025-10-06 01:01:53.316364+05	2025-10-06 01:01:53.31637+05
353	ui	score_fair_desc	en	\N	Fair financial health. Focus on building better financial habits.	\N	\N	\N	t	2025-10-06 01:01:53.317448+05	2025-10-06 01:01:53.317454+05
354	ui	score_fair_desc	ar	\N	صحة مالية مقبولة. ركز على بناء عادات مالية أفضل.	\N	\N	\N	t	2025-10-06 01:01:53.318708+05	2025-10-06 01:01:53.318716+05
355	ui	score_poor_desc	en	\N	Your financial health needs attention. Consider seeking financial advice.	\N	\N	\N	t	2025-10-06 01:01:53.319748+05	2025-10-06 01:01:53.31978+05
356	ui	score_poor_desc	ar	\N	صحتك المالية تحتاج إلى اهتمام. فكر في طلب المشورة المالية.	\N	\N	\N	t	2025-10-06 01:01:53.321011+05	2025-10-06 01:01:53.321019+05
357	ui	budgeting_pillar_desc	en	\N	How well you manage your monthly income and expenses	\N	\N	\N	t	2025-10-06 01:01:53.321963+05	2025-10-06 01:01:53.321969+05
358	ui	budgeting_pillar_desc	ar	\N	مدى جودة إدارتك لدخلك ونفقاتك الشهرية	\N	\N	\N	t	2025-10-06 01:01:53.322692+05	2025-10-06 01:01:53.322698+05
359	ui	savings_pillar_desc	en	\N	Your ability to save money and build emergency funds	\N	\N	\N	t	2025-10-06 01:01:53.32384+05	2025-10-06 01:01:53.323846+05
360	ui	savings_pillar_desc	ar	\N	قدرتك على توفير المال وبناء صناديق الطوارئ	\N	\N	\N	t	2025-10-06 01:01:53.32524+05	2025-10-06 01:01:53.325248+05
361	ui	debt_pillar_desc	en	\N	How effectively you manage and reduce your debts	\N	\N	\N	t	2025-10-06 01:01:53.32599+05	2025-10-06 01:01:53.325995+05
362	ui	debt_pillar_desc	ar	\N	مدى فعالية إدارتك وتقليل ديونك	\N	\N	\N	t	2025-10-06 01:01:53.326644+05	2025-10-06 01:01:53.32665+05
363	ui	planning_pillar_desc	en	\N	Your long-term financial planning and goal setting	\N	\N	\N	t	2025-10-06 01:01:53.327591+05	2025-10-06 01:01:53.327598+05
364	ui	planning_pillar_desc	ar	\N	تخطيطك المالي طويل المدى ووضع الأهداف	\N	\N	\N	t	2025-10-06 01:01:53.338248+05	2025-10-06 01:01:53.338254+05
365	ui	investment_pillar_desc	en	\N	Your knowledge and experience with investments	\N	\N	\N	t	2025-10-06 01:01:53.373028+05	2025-10-06 01:01:53.373039+05
366	ui	investment_pillar_desc	ar	\N	معرفتك وخبرتك في الاستثمارات	\N	\N	\N	t	2025-10-06 01:01:53.40025+05	2025-10-06 01:01:53.400259+05
367	ui	take_action	en	\N	Take Action	\N	\N	\N	t	2025-10-06 01:01:53.417453+05	2025-10-06 01:01:53.417463+05
368	ui	take_action	ar	\N	اتخذ إجراء	\N	\N	\N	t	2025-10-06 01:01:53.462127+05	2025-10-06 01:01:53.462147+05
369	ui	learn_more	en	\N	Learn More	\N	\N	\N	t	2025-10-06 01:01:53.486239+05	2025-10-06 01:01:53.486247+05
370	ui	learn_more	ar	\N	تعلم المزيد	\N	\N	\N	t	2025-10-06 01:01:53.487489+05	2025-10-06 01:01:53.487496+05
371	ui	get_advice	en	\N	Get Professional Advice	\N	\N	\N	t	2025-10-06 01:01:53.489617+05	2025-10-06 01:01:53.489626+05
372	ui	get_advice	ar	\N	احصل على مشورة مهنية	\N	\N	\N	t	2025-10-06 01:01:53.491495+05	2025-10-06 01:01:53.491502+05
373	ui	generating_pdf	en	\N	Generating PDF report...	\N	\N	\N	t	2025-10-06 01:01:53.49322+05	2025-10-06 01:01:53.493226+05
374	ui	generating_pdf	ar	\N	جاري إنشاء تقرير PDF...	\N	\N	\N	t	2025-10-06 01:01:53.495319+05	2025-10-06 01:01:53.495326+05
375	ui	report_ready	en	\N	Your report is ready!	\N	\N	\N	t	2025-10-06 01:01:53.497334+05	2025-10-06 01:01:53.497406+05
376	ui	report_ready	ar	\N	تقريرك جاهز!	\N	\N	\N	t	2025-10-06 01:01:53.498724+05	2025-10-06 01:01:53.49873+05
377	ui	email_sent	en	\N	Report sent to your email	\N	\N	\N	t	2025-10-06 01:01:53.501536+05	2025-10-06 01:01:53.501543+05
378	ui	email_sent	ar	\N	تم إرسال التقرير إلى بريدك الإلكتروني	\N	\N	\N	t	2025-10-06 01:01:53.502463+05	2025-10-06 01:01:53.502468+05
379	ui	multiple_choice	en	\N	Multiple Choice	\N	\N	\N	t	2025-10-06 01:01:53.504905+05	2025-10-06 01:01:53.504913+05
380	ui	multiple_choice	ar	\N	اختيار متعدد	\N	\N	\N	t	2025-10-06 01:01:53.506986+05	2025-10-06 01:01:53.506992+05
381	ui	select_one	en	\N	Select one option	\N	\N	\N	t	2025-10-06 01:01:53.508673+05	2025-10-06 01:01:53.508679+05
382	ui	select_one	ar	\N	اختر خياراً واحداً	\N	\N	\N	t	2025-10-06 01:01:53.510368+05	2025-10-06 01:01:53.510376+05
383	ui	required_question	en	\N	This question is required	\N	\N	\N	t	2025-10-06 01:01:53.512347+05	2025-10-06 01:01:53.512355+05
384	ui	required_question	ar	\N	هذا السؤال مطلوب	\N	\N	\N	t	2025-10-06 01:01:53.513575+05	2025-10-06 01:01:53.513583+05
385	ui	go_back	en	\N	Go Back	\N	\N	\N	t	2025-10-06 01:01:53.5154+05	2025-10-06 01:01:53.515408+05
386	ui	go_back	ar	\N	العودة	\N	\N	\N	t	2025-10-06 01:01:53.517873+05	2025-10-06 01:01:53.51788+05
387	ui	finish_assessment	en	\N	Finish Assessment	\N	\N	\N	t	2025-10-06 01:01:53.519429+05	2025-10-06 01:01:53.519439+05
388	ui	finish_assessment	ar	\N	إنهاء التقييم	\N	\N	\N	t	2025-10-06 01:01:53.520893+05	2025-10-06 01:01:53.5209+05
389	ui	restart_assessment	en	\N	Restart Assessment	\N	\N	\N	t	2025-10-06 01:01:53.523651+05	2025-10-06 01:01:53.523663+05
390	ui	restart_assessment	ar	\N	إعادة بدء التقييم	\N	\N	\N	t	2025-10-06 01:01:53.524576+05	2025-10-06 01:01:53.524585+05
402	ui	test_admin_content	en	\N	Test content from admin API	null	null	1.0	t	2025-10-06 01:07:27.050788+05	\N
394	question	q8_emergency_fund	ar	\N	لدي صندوق طوارئ لتغطية نفقاتي.	[{"value": 5, "label": "6+ \\u0623\\u0634\\u0647\\u0631"}, {"value": 4, "label": "3 - 6 \\u0623\\u0634\\u0647\\u0631"}, {"value": 3, "label": "\\u0634\\u0647\\u0631\\u064a\\u0646"}, {"value": 2, "label": "\\u0634\\u0647\\u0631 \\u0648\\u0627\\u062d\\u062f"}, {"value": 1, "label": "\\u0644\\u0627 \\u064a\\u0648\\u062c\\u062f"}]	\N	\N	t	2025-10-06 01:03:24.63926+05	2025-10-06 01:03:24.639269+05
400	question	q15_financial_planning	ar	\N	لدي خطة مالية مكتوبة بأهداف للسنوات الـ 3-5 القادمة.	[{"value": 5, "label": "\\u062e\\u0637\\u0629 \\u0645\\u0627\\u0644\\u064a\\u0629 \\u0645\\u062e\\u062a\\u0635\\u0631\\u0629 \\u0648\\u0645\\u0631\\u0627\\u062c\\u0639\\u0629 \\u0628\\u0627\\u0633\\u062a\\u0645\\u0631\\u0627\\u0631"}, {"value": 4, "label": "\\u062e\\u0637\\u0629 \\u0645\\u0627\\u0644\\u064a\\u0629 \\u0648\\u0627\\u0633\\u0639\\u0629 \\u0648\\u0645\\u0631\\u0627\\u062c\\u0639\\u0629 \\u0628\\u0634\\u0643\\u0644 \\u0645\\u062a\\u0643\\u0631\\u0631"}, {"value": 3, "label": "\\u0623\\u0647\\u062f\\u0627\\u0641 \\u0639\\u0627\\u0644\\u064a\\u0629 \\u0627\\u0644\\u0645\\u0633\\u062a\\u0648\\u0649 \\u0648\\u0645\\u0631\\u0627\\u062c\\u0639\\u0629 \\u0623\\u062d\\u064a\\u0627\\u0646\\u0627\\u064b"}, {"value": 2, "label": "\\u062e\\u0637\\u0629 \\u0639\\u0634\\u0648\\u0627\\u0626\\u064a\\u0629 | \\u0645\\u0631\\u0627\\u062c\\u0639\\u0627\\u062a"}, {"value": 1, "label": "\\u0644\\u0627 \\u062a\\u0648\\u062c\\u062f \\u062e\\u0637\\u0629 \\u0645\\u0627\\u0644\\u064a\\u0629"}]	\N	\N	t	2025-10-06 01:03:24.672956+05	2025-10-06 01:03:24.672964+05
391	question	q4_budget_tracking	ar	\N	أتبع ميزانية شهرية وأتتبع نفقاتي.	[{"value": 5, "label": "\\u0628\\u0627\\u0633\\u062a\\u0645\\u0631\\u0627\\u0631 \\u0643\\u0644 \\u0634\\u0647\\u0631"}, {"value": 4, "label": "\\u0628\\u0634\\u0643\\u0644 \\u0645\\u062a\\u0643\\u0631\\u0631 \\u0648\\u0644\\u0643\\u0646 \\u0644\\u064a\\u0633 \\u0628\\u0627\\u0633\\u062a\\u0645\\u0631\\u0627\\u0631"}, {"value": 3, "label": "\\u0623\\u062d\\u064a\\u0627\\u0646\\u0627\\u064b"}, {"value": 2, "label": "\\u0628\\u0634\\u0643\\u0644 \\u0639\\u0634\\u0648\\u0627\\u0626\\u064a"}, {"value": 1, "label": "\\u0644\\u0627 \\u0623\\u062a\\u062a\\u0628\\u0639"}]	\N	\N	t	2025-10-06 01:03:24.550709+05	2025-10-06 01:03:24.550728+05
392	question	q5_spending_control	ar	\N	أنفق أقل مما أكسب كل شهر.	[{"value": 5, "label": "\\u0628\\u0627\\u0633\\u062a\\u0645\\u0631\\u0627\\u0631 \\u0643\\u0644 \\u0634\\u0647\\u0631"}, {"value": 4, "label": "\\u0628\\u0634\\u0643\\u0644 \\u0645\\u062a\\u0643\\u0631\\u0631 \\u0648\\u0644\\u0643\\u0646 \\u0644\\u064a\\u0633 \\u0628\\u0627\\u0633\\u062a\\u0645\\u0631\\u0627\\u0631"}, {"value": 3, "label": "\\u0623\\u062d\\u064a\\u0627\\u0646\\u0627\\u064b"}, {"value": 2, "label": "\\u0628\\u0634\\u0643\\u0644 \\u0639\\u0634\\u0648\\u0627\\u0626\\u064a"}, {"value": 1, "label": "\\u0623\\u0643\\u062b\\u0631 \\u0645\\u0646 \\u0623\\u0648 \\u0643\\u0644 \\u0623\\u0631\\u0628\\u0627\\u062d\\u064a"}]	\N	\N	t	2025-10-06 01:03:24.598402+05	2025-10-06 01:03:24.598411+05
393	question	q6_expense_review	ar	\N	أراجع وأقلل النفقات غير الضرورية بانتظام.	[{"value": 5, "label": "\\u0628\\u0627\\u0633\\u062a\\u0645\\u0631\\u0627\\u0631 \\u0643\\u0644 \\u0634\\u0647\\u0631"}, {"value": 4, "label": "\\u0628\\u0634\\u0643\\u0644 \\u0645\\u062a\\u0643\\u0631\\u0631 \\u0648\\u0644\\u0643\\u0646 \\u0644\\u064a\\u0633 \\u0628\\u0627\\u0633\\u062a\\u0645\\u0631\\u0627\\u0631"}, {"value": 3, "label": "\\u0623\\u062d\\u064a\\u0627\\u0646\\u0627\\u064b"}, {"value": 2, "label": "\\u0628\\u0634\\u0643\\u0644 \\u0639\\u0634\\u0648\\u0627\\u0626\\u064a"}, {"value": 1, "label": "\\u0644\\u0627 \\u0623\\u062a\\u062a\\u0628\\u0639"}]	\N	\N	t	2025-10-06 01:03:24.629304+05	2025-10-06 01:03:24.629313+05
290	question	q7_savings_rate	ar	\N	أدخر من دخلي كل شهر.	[{"value": 5, "label": "20% \\u0623\\u0648 \\u0623\\u0643\\u062b\\u0631"}, {"value": 4, "label": "\\u0623\\u0642\\u0644 \\u0645\\u0646 20%"}, {"value": 3, "label": "\\u0623\\u0642\\u0644 \\u0645\\u0646 10%"}, {"value": 2, "label": "5% \\u0623\\u0648 \\u0623\\u0642\\u0644"}, {"value": 1, "label": "0%"}]	null	1.0	t	2025-10-05 01:03:50.561015+05	\N
395	question	q9_savings_optimization	ar	\N	أحتفظ بمدخراتي في حسابات آمنة ومربحة أو استثمارات.	[{"value": 5, "label": "\\u0622\\u0645\\u0646 | \\u0623\\u0633\\u0639\\u0649 \\u0644\\u062a\\u062d\\u0633\\u064a\\u0646 \\u0627\\u0644\\u0639\\u0627\\u0626\\u062f \\u0628\\u0627\\u0633\\u062a\\u0645\\u0631\\u0627\\u0631"}, {"value": 4, "label": "\\u0622\\u0645\\u0646 | \\u0623\\u0633\\u0639\\u0649 \\u0644\\u062a\\u062d\\u0633\\u064a\\u0646 \\u0627\\u0644\\u0639\\u0627\\u0626\\u062f \\u0645\\u0639\\u0638\\u0645 \\u0627\\u0644\\u0623\\u0648\\u0642\\u0627\\u062a"}, {"value": 3, "label": "\\u062d\\u0633\\u0627\\u0628 \\u062a\\u0648\\u0641\\u064a\\u0631 \\u0628\\u0639\\u0648\\u0627\\u0626\\u062f \\u0642\\u0644\\u064a\\u0644\\u0629"}, {"value": 2, "label": "\\u062d\\u0633\\u0627\\u0628 \\u062c\\u0627\\u0631\\u064a"}, {"value": 1, "label": "\\u0646\\u0642\\u062f"}]	\N	\N	t	2025-10-06 01:03:24.643478+05	2025-10-06 01:03:24.643486+05
396	question	q10_payment_history	ar	\N	أدفع جميع فواتيري وأقساط القروض في الوقت المحدد.	[{"value": 5, "label": "\\u0628\\u0627\\u0633\\u062a\\u0645\\u0631\\u0627\\u0631 \\u0643\\u0644 \\u0634\\u0647\\u0631"}, {"value": 4, "label": "\\u0628\\u0634\\u0643\\u0644 \\u0645\\u062a\\u0643\\u0631\\u0631 \\u0648\\u0644\\u0643\\u0646 \\u0644\\u064a\\u0633 \\u0628\\u0627\\u0633\\u062a\\u0645\\u0631\\u0627\\u0631"}, {"value": 3, "label": "\\u0623\\u062d\\u064a\\u0627\\u0646\\u0627\\u064b"}, {"value": 2, "label": "\\u0628\\u0634\\u0643\\u0644 \\u0639\\u0634\\u0648\\u0627\\u0626\\u064a"}, {"value": 1, "label": "\\u0641\\u0648\\u062a \\u0627\\u0644\\u0645\\u062f\\u0641\\u0648\\u0639\\u0627\\u062a \\u0645\\u0639\\u0638\\u0645 \\u0627\\u0644\\u0623\\u0648\\u0642\\u0627\\u062a"}]	\N	\N	t	2025-10-06 01:03:24.647371+05	2025-10-06 01:03:24.647379+05
397	question	q11_debt_ratio	ar	\N	مدفوعات ديوني أقل من 30% من دخلي الشهري.	[{"value": 5, "label": "\\u0644\\u0627 \\u064a\\u0648\\u062c\\u062f \\u062f\\u064a\\u0646"}, {"value": 4, "label": "20% \\u0623\\u0648 \\u0623\\u0642\\u0644 \\u0645\\u0646 \\u0627\\u0644\\u062f\\u062e\\u0644 \\u0627\\u0644\\u0634\\u0647\\u0631\\u064a"}, {"value": 3, "label": "\\u0623\\u0642\\u0644 \\u0645\\u0646 30% \\u0645\\u0646 \\u0627\\u0644\\u062f\\u062e\\u0644 \\u0627\\u0644\\u0634\\u0647\\u0631\\u064a"}, {"value": 2, "label": "30% \\u0623\\u0648 \\u0623\\u0643\\u062b\\u0631 \\u0645\\u0646 \\u0627\\u0644\\u062f\\u062e\\u0644 \\u0627\\u0644\\u0634\\u0647\\u0631\\u064a"}, {"value": 1, "label": "50% \\u0623\\u0648 \\u0623\\u0643\\u062b\\u0631 \\u0645\\u0646 \\u0627\\u0644\\u062f\\u062e\\u0644 \\u0627\\u0644\\u0634\\u0647\\u0631\\u064a"}]	\N	\N	t	2025-10-06 01:03:24.654979+05	2025-10-06 01:03:24.654987+05
398	question	q12_credit_score	ar	\N	أفهم درجة ائتماني وأحافظ عليها أو أحسنها بنشاط.	[{"value": 5, "label": "100% \\u0648\\u0623\\u0631\\u0627\\u0642\\u0628\\u0647\\u0627 \\u0628\\u0627\\u0633\\u062a\\u0645\\u0631\\u0627\\u0631"}, {"value": 4, "label": "100% \\u0648\\u0623\\u0631\\u0627\\u0642\\u0628\\u0647\\u0627 \\u0628\\u0634\\u0643\\u0644 \\u0645\\u062a\\u0643\\u0631\\u0631"}, {"value": 3, "label": "\\u0623\\u0641\\u0647\\u0645 \\u0625\\u0644\\u0649 \\u062d\\u062f \\u0645\\u0627 \\u0648\\u0645\\u0631\\u0627\\u0642\\u0628\\u0629 \\u0645\\u062a\\u0643\\u0631\\u0631\\u0629"}, {"value": 2, "label": "\\u0623\\u0641\\u0647\\u0645 \\u0625\\u0644\\u0649 \\u062d\\u062f \\u0645\\u0627 \\u0648\\u0623\\u062d\\u0627\\u0641\\u0638 \\u0639\\u0644\\u064a\\u0647\\u0627 \\u0628\\u0634\\u0643\\u0644 \\u0639\\u0634\\u0648\\u0627\\u0626\\u064a"}, {"value": 1, "label": "\\u0644\\u0627 \\u0623\\u0641\\u0647\\u0645 \\u0648\\u0644\\u0627 \\u0623\\u062d\\u0627\\u0641\\u0638 \\u0639\\u0644\\u064a\\u0647\\u0627"}]	\N	\N	t	2025-10-06 01:03:24.66015+05	2025-10-06 01:03:24.660158+05
399	question	q14_insurance_coverage	ar	\N	لدي تغطية تكافل (تأمين) كافية - (صحي، حياة، سيارة، ممتلكات).	[{"value": 5, "label": "100% \\u062a\\u063a\\u0637\\u064a\\u0629 \\u0643\\u0627\\u0641\\u064a\\u0629 \\u0644\\u0644\\u062d\\u0645\\u0627\\u064a\\u0629 \\u0627\\u0644\\u0645\\u0637\\u0644\\u0648\\u0628\\u0629"}, {"value": 4, "label": "80% \\u062a\\u063a\\u0637\\u064a\\u0629 \\u0644\\u0644\\u062d\\u0645\\u0627\\u064a\\u0629 \\u0627\\u0644\\u0645\\u0637\\u0644\\u0648\\u0628\\u0629"}, {"value": 3, "label": "50% \\u062a\\u063a\\u0637\\u064a\\u0629 \\u0644\\u0644\\u062d\\u0645\\u0627\\u064a\\u0629 \\u0627\\u0644\\u0645\\u0637\\u0644\\u0648\\u0628\\u0629"}, {"value": 2, "label": "25% \\u062a\\u063a\\u0637\\u064a\\u0629 \\u0644\\u0644\\u062d\\u0645\\u0627\\u064a\\u0629 \\u0627\\u0644\\u0645\\u0637\\u0644\\u0648\\u0628\\u0629"}, {"value": 1, "label": "\\u0644\\u0627 \\u062a\\u0648\\u062c\\u062f \\u062a\\u063a\\u0637\\u064a\\u0629"}]	\N	\N	t	2025-10-06 01:03:24.670017+05	2025-10-06 01:03:24.670026+05
401	question	q16_children_planning	ar	\N	لقد خططت بشكل كافٍ لمستقبل أطفالي للمدرسة | الجامعة | بداية المهنة.	[{"value": 5, "label": "100% \\u0645\\u062f\\u062e\\u0631\\u0627\\u062a \\u0643\\u0627\\u0641\\u064a\\u0629 \\u0644\\u0644\\u062c\\u0648\\u0627\\u0646\\u0628 \\u0627\\u0644\\u062b\\u0644\\u0627\\u062b\\u0629"}, {"value": 4, "label": "80% \\u0645\\u062f\\u062e\\u0631\\u0627\\u062a \\u0644\\u0644\\u062c\\u0648\\u0627\\u0646\\u0628 \\u0627\\u0644\\u062b\\u0644\\u0627\\u062b\\u0629"}, {"value": 3, "label": "50% \\u0645\\u062f\\u062e\\u0631\\u0627\\u062a \\u0644\\u0644\\u062c\\u0648\\u0627\\u0646\\u0628 \\u0627\\u0644\\u062b\\u0644\\u0627\\u062b\\u0629"}, {"value": 2, "label": "\\u062e\\u0637\\u0629 \\u0639\\u0634\\u0648\\u0627\\u0626\\u064a\\u0629 \\u0644\\u0644\\u062c\\u0648\\u0627\\u0646\\u0628 \\u0627\\u0644\\u062b\\u0644\\u0627\\u062b\\u0629"}, {"value": 1, "label": "\\u0644\\u0627 \\u062a\\u0648\\u062c\\u062f \\u062e\\u0637\\u0629"}]	\N	\N	t	2025-10-06 01:03:24.675973+05	2025-10-06 01:03:24.67598+05
403	ui	transparent_scoring	ar	\N	تسجيل شفاف	null	null	1.0	t	2025-10-06 21:36:03.901503+05	\N
404	ui	privacy_protected	ar	\N	حماية الخصوصية	null	null	1.0	t	2025-10-06 21:36:03.988742+05	\N
405	ui	personalized_insights	ar	\N	رؤى مخصصة	null	null	1.0	t	2025-10-06 21:36:04.104579+05	\N
406	ui	progress_tracking	ar	\N	تتبع التقدم	null	null	1.0	t	2025-10-06 21:36:04.1921+05	\N
407	ui	science_based_methodology	ar	\N	منهجية علمية	null	null	1.0	t	2025-10-06 21:36:04.322452+05	\N
408	ui	uae_specific_insights	ar	\N	رؤى خاصة بدولة الإمارات	null	null	1.0	t	2025-10-06 21:36:04.473552+05	\N
409	ui	ready_to_improve	ar	\N	هل أنت مستعد لتحسين صحتك المالية؟	null	null	1.0	t	2025-10-06 21:36:04.543296+05	\N
410	ui	join_thousands	ar	\N	انضم إلى آلاف المقيمين في دولة الإمارات الذين عززوا مستقبلهم المالي من خلال تقييمنا الشامل.	null	null	1.0	t	2025-10-06 21:36:04.564783+05	\N
411	ui	begin_assessment_now	ar	\N	ابدأ التقييم الآن	null	null	1.0	t	2025-10-06 21:36:04.600177+05	\N
412	ui	overall_score	ar	\N	النتيجة الإجمالية	null	null	1.0	t	2025-10-06 21:36:04.788716+05	\N
413	ui	pillar_breakdown	ar	\N	تفصيل الأركان	null	null	1.0	t	2025-10-06 21:36:04.876571+05	\N
414	ui	detailed_recommendations	ar	\N	توصيات مفصلة	null	null	1.0	t	2025-10-06 21:36:04.961023+05	\N
415	ui	action_plan	ar	\N	خطة العمل	null	null	1.0	t	2025-10-06 21:36:05.12292+05	\N
416	ui	next_steps	ar	\N	الخطوات التالية	null	null	1.0	t	2025-10-06 21:36:05.135391+05	\N
417	ui	download_report	ar	\N	تحميل التقرير	null	null	1.0	t	2025-10-06 21:36:05.150933+05	\N
418	ui	email_report	ar	\N	إرسال التقرير بالبريد الإلكتروني	null	null	1.0	t	2025-10-06 21:36:05.166054+05	\N
419	ui	share_results	ar	\N	مشاركة النتائج	null	null	1.0	t	2025-10-06 21:36:05.179695+05	\N
420	ui	generate_report	ar	\N	إنشاء التقرير	null	null	1.0	t	2025-10-06 21:36:05.191502+05	\N
421	ui	understanding_your_score	ar	\N	فهم درجتك	null	null	1.0	t	2025-10-06 21:36:05.204997+05	\N
422	ui	score_ranges	ar	\N	نطاقات الدرجات	null	null	1.0	t	2025-10-06 21:36:05.21394+05	\N
423	ui	save_your_results	ar	\N	احفظ نتائجك	null	null	1.0	t	2025-10-06 21:36:05.228278+05	\N
424	ui	create_account	ar	\N	إنشاء حساب	null	null	1.0	t	2025-10-06 21:36:05.24357+05	\N
425	ui	view_score_history	ar	\N	عرض تاريخ النتائج	null	null	1.0	t	2025-10-06 21:36:05.264807+05	\N
426	ui	retake_assessment	ar	\N	إعادة التقييم	null	null	1.0	t	2025-10-06 21:36:05.290738+05	\N
427	ui	personalized_recommendations	ar	\N	توصيات مخصصة	null	null	1.0	t	2025-10-06 21:36:05.318668+05	\N
428	ui	educational_guidance	ar	\N	إرشادات تعليمية	null	null	1.0	t	2025-10-06 21:36:05.351338+05	\N
429	ui	financial_pillar_scores	ar	\N	درجات الأركان المالية	null	null	1.0	t	2025-10-06 21:36:05.388976+05	\N
430	ui	performance_across_areas	ar	\N	أداؤك عبر المجالات الرئيسية	null	null	1.0	t	2025-10-06 21:36:05.452154+05	\N
431	ui	no_results_available	ar	\N	لا توجد نتائج متاحة	null	null	1.0	t	2025-10-06 21:36:05.496645+05	\N
432	ui	complete_assessment_first	ar	\N	تحتاج إلى إكمال تقييم الصحة المالية أولاً لرؤية نتائجك.	null	null	1.0	t	2025-10-06 21:36:05.524262+05	\N
433	ui	error_loading_results	ar	\N	خطأ في تحميل النتائج	null	null	1.0	t	2025-10-06 21:36:05.553102+05	\N
434	ui	unable_to_load_score	ar	\N	غير قادر على تحميل نتائج درجتك. يرجى المحاولة مرة أخرى.	null	null	1.0	t	2025-10-06 21:36:05.571033+05	\N
435	ui	needs_improvement	ar	\N	يحتاج تحسين	null	null	1.0	t	2025-10-06 21:36:05.635312+05	\N
436	ui	at_risk	ar	\N	في خطر	null	null	1.0	t	2025-10-06 21:36:05.689364+05	\N
437	ui	income_stream	ar	\N	مصدر الدخل	null	null	1.0	t	2025-10-06 21:36:05.772475+05	\N
438	ui	monthly_expenses	ar	\N	إدارة النفقات الشهرية	null	null	1.0	t	2025-10-06 21:36:05.811432+05	\N
439	ui	savings_habit	ar	\N	عادة الادخار	null	null	1.0	t	2025-10-06 21:36:05.861247+05	\N
440	ui	retirement_planning	ar	\N	التخطيط للتقاعد	null	null	1.0	t	2025-10-06 21:36:05.885529+05	\N
441	ui	protection	ar	\N	حماية الأصول والأحباء	null	null	1.0	t	2025-10-06 21:36:05.942218+05	\N
442	ui	future_planning	ar	\N	التخطيط للمستقبل والأشقاء	null	null	1.0	t	2025-10-06 21:36:05.954253+05	\N
443	ui	focus_on_building_basic_habits	ar	\N	ركز على بناء العادات المالية الأساسية	null	null	1.0	t	2025-10-06 21:36:05.976567+05	\N
444	ui	good_foundation_room_for_growth	ar	\N	أساس جيد، مجال للنمو	null	null	1.0	t	2025-10-06 21:36:05.994279+05	\N
445	ui	strong_financial_health	ar	\N	صحة مالية قوية	null	null	1.0	t	2025-10-06 21:36:06.027594+05	\N
446	ui	outstanding_financial_wellness	ar	\N	عافية مالية متميزة	null	null	1.0	t	2025-10-06 21:36:06.058981+05	\N
447	ui	educational_content_only	ar	\N	هذا محتوى تعليمي فقط ولا يشكل نصيحة مالية.	null	null	1.0	t	2025-10-06 21:36:06.078137+05	\N
448	ui	consult_qualified_professionals	ar	\N	استشر المهنيين المؤهلين للحصول على إرشادات مخصصة.	null	null	1.0	t	2025-10-06 21:36:06.100921+05	\N
449	ui	track_progress_download_reports	ar	\N	تتبع تقدمك، وحمل التقارير، والوصول إلى تاريخ تقييماتك.	null	null	1.0	t	2025-10-06 21:36:06.144039+05	\N
450	ui	personalized_recommendations_generated	ar	\N	سيتم إنشاء توصيات مخصصة بناءً على نتائج تقييمك.	null	null	1.0	t	2025-10-06 21:36:06.192838+05	\N
451	ui	detailed_breakdown_available	ar	\N	سيكون التفصيل المفصل متاحاً بعد إكمال التقييم.	null	null	1.0	t	2025-10-06 21:36:06.242607+05	\N
452	ui	welcome_back	ar	\N	مرحباً بعودتك!	null	null	1.0	t	2025-10-06 21:36:06.260364+05	\N
453	ui	sign_out	ar	\N	تسجيل الخروج	null	null	1.0	t	2025-10-06 21:36:06.284475+05	\N
454	ui	access_previous_results	ar	\N	الوصول إلى النتائج السابقة	null	null	1.0	t	2025-10-06 21:36:06.303219+05	\N
455	ui	view_previous_results	ar	\N	عرض النتائج السابقة	null	null	1.0	t	2025-10-06 21:36:06.318997+05	\N
456	ui	admin_dashboard	ar	\N	لوحة الإدارة	null	null	1.0	t	2025-10-06 21:36:06.342384+05	\N
457	ui	start_assessment	ar	\N	ابدأ التقييم	null	null	1.0	t	2025-10-06 21:36:06.362383+05	\N
458	ui	go_to_home	ar	\N	اذهب إلى الصفحة الرئيسية	null	null	1.0	t	2025-10-06 21:36:06.385159+05	\N
459	ui	home	ar	\N	الرئيسية	null	null	1.0	t	2025-10-06 21:36:06.42058+05	\N
460	ui	generate_report	en	\N	Generate Report	null	null	1.0	t	2025-10-06 21:36:07.118237+05	\N
461	ui	understanding_your_score	en	\N	Understanding Your Score	null	null	1.0	t	2025-10-06 21:36:07.220563+05	\N
462	ui	score_ranges	en	\N	Score Ranges	null	null	1.0	t	2025-10-06 21:36:07.235688+05	\N
463	ui	save_your_results	en	\N	Save Your Results	null	null	1.0	t	2025-10-06 21:36:07.257939+05	\N
464	ui	create_account	en	\N	Create Account	null	null	1.0	t	2025-10-06 21:36:07.293651+05	\N
465	ui	view_score_history	en	\N	View Score History	null	null	1.0	t	2025-10-06 21:36:07.367811+05	\N
466	ui	educational_guidance	en	\N	Educational guidance to improve your financial health	null	null	1.0	t	2025-10-06 21:36:07.454091+05	\N
467	ui	financial_pillar_scores	en	\N	Financial Pillar Scores	null	null	1.0	t	2025-10-06 21:36:07.474199+05	\N
468	ui	performance_across_areas	en	\N	Your performance across the 7 key areas of financial health	null	null	1.0	t	2025-10-06 21:36:07.519835+05	\N
469	ui	no_results_available	en	\N	No Results Available	null	null	1.0	t	2025-10-06 21:36:07.554351+05	\N
470	ui	complete_assessment_first	en	\N	You need to complete the financial health assessment first to see your results.	null	null	1.0	t	2025-10-06 21:36:07.592721+05	\N
471	ui	error_loading_results	en	\N	Error Loading Results	null	null	1.0	t	2025-10-06 21:36:07.636277+05	\N
472	ui	unable_to_load_score	en	\N	Unable to load your score results. Please try the assessment again.	null	null	1.0	t	2025-10-06 21:36:07.665072+05	\N
473	ui	focus_on_building_basic_habits	en	\N	Focus on building basic financial habits	null	null	1.0	t	2025-10-06 21:36:07.823642+05	\N
474	ui	good_foundation_room_for_growth	en	\N	Good foundation, room for growth	null	null	1.0	t	2025-10-06 21:36:07.834629+05	\N
475	ui	strong_financial_health	en	\N	Strong financial health	null	null	1.0	t	2025-10-06 21:36:07.845607+05	\N
476	ui	outstanding_financial_wellness	en	\N	Outstanding financial wellness	null	null	1.0	t	2025-10-06 21:36:07.859422+05	\N
477	ui	educational_content_only	en	\N	This is educational content only and does not constitute financial advice.	null	null	1.0	t	2025-10-06 21:36:07.872833+05	\N
478	ui	consult_qualified_professionals	en	\N	Consult qualified professionals for personalized guidance.	null	null	1.0	t	2025-10-06 21:36:07.890778+05	\N
479	ui	track_progress_download_reports	en	\N	Track your progress, download reports, and access your assessment history.	null	null	1.0	t	2025-10-06 21:36:07.924751+05	\N
480	ui	personalized_recommendations_generated	en	\N	Personalized recommendations will be generated based on your assessment results.	null	null	1.0	t	2025-10-06 21:36:07.935198+05	\N
481	ui	detailed_breakdown_available	en	\N	Detailed pillar breakdown will be available after completing the assessment.	null	null	1.0	t	2025-10-06 21:36:07.943489+05	\N
482	ui	start_assessment	en	\N	Start Assessment	null	null	1.0	t	2025-10-06 21:36:07.979222+05	\N
483	ui	go_to_home	en	\N	Go to Home	null	null	1.0	t	2025-10-06 21:36:07.988492+05	\N
484	ui	home	en	\N	Home	null	null	1.0	t	2025-10-06 21:36:08.002514+05	\N
\.


--
-- Data for Name: question_variations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.question_variations (id, base_question_id, variation_name, language, text, options, demographic_rules, company_ids, factor, weight, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: recommendations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.recommendations (id, survey_response_id, category, title, description, priority, action_steps, resources, expected_impact, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: report_access_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.report_access_logs (id, report_delivery_id, user_id, access_type, ip_address, user_agent, access_metadata, accessed_at) FROM stdin;
\.


--
-- Data for Name: report_deliveries; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.report_deliveries (id, survey_response_id, user_id, delivery_type, delivery_status, recipient_email, file_path, file_size, language, delivery_metadata, error_message, retry_count, delivered_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: simple_sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.simple_sessions (id, user_id, session_id, expires_at, is_active, created_at) FROM stdin;
1	1	fgZfR6Yz16WpZr8FD2i-Klu83iMiUNVVnr-yvw5e20E	2025-10-03 13:09:28.613968+05	t	2025-10-02 18:09:28.613121+05
2	2	qnlcqbsvvuG0ozUTCqfy92Xv3nsGPDw4J_YTHbHX72Q	2025-10-03 13:16:35.909747+05	t	2025-10-02 18:16:35.908612+05
3	6	edesy0N-qRVvu-nePRVUL1HRL6uJGTxmEg9W5yRlf0w	2025-10-07 08:36:33.227624+05	t	2025-10-06 13:36:33.204558+05
4	6	MBaGLc54Fpj4so475Xge75aq_HvF9_TsCLLUrL3SRwA	2025-10-07 08:51:30.603898+05	t	2025-10-06 13:51:30.30172+05
5	6	22MvIorSyc6i__rAV-I7bkrsqSRyEQlp46R8bNApdrs	2025-10-07 08:52:56.661684+05	t	2025-10-06 13:52:54.379471+05
6	6	KQyrGW-f7g6CuBp20k-lvnG3Bf2lwgiFOgrk466yDRQ	2025-10-07 08:55:44.336804+05	t	2025-10-06 13:55:43.706498+05
7	6	bmCbgJLdzxnwHRxi6NB5R5ElurRHeZnmlfCZZigeCGY	2025-10-07 08:56:20.435509+05	t	2025-10-06 13:56:20.417633+05
8	6	gDvGwisiqCkU9N05QlHw6nTkeBPTEat4VRKO0Oim3-s	2025-10-07 09:02:05.32037+05	t	2025-10-06 14:02:04.894494+05
9	6	bmU_KDHrWdbVCgZ-WThGEKs1HCRNiX7UVkEs4VUmnNQ	2025-10-07 09:48:10.797123+05	t	2025-10-06 14:48:10.705872+05
10	6	fhSVCGFxXFtcQdWvZiVssrkY_ID-yfHFxeYV_oOyB-8	2025-10-07 10:21:53.130543+05	t	2025-10-06 15:21:53.092013+05
11	6	wnRLi9C2ntJbN_xQ6rR_VVjVUS-spXIqAmpjNIbwkHE	2025-10-07 10:22:30.86978+05	t	2025-10-06 15:22:30.859811+05
12	6	viRqH0T991sTMSUbtfUTtzaOHKAr2Q8iu1X_KvfeVsY	2025-10-07 10:31:48.403176+05	t	2025-10-06 15:31:48.365306+05
13	6	nhRLGDA-aPPWWe77VJP9ZXTsQPVyR7i7dHfaLNxSxt4	2025-10-07 10:51:53.140861+05	t	2025-10-06 15:51:53.097014+05
\.


--
-- Data for Name: survey_responses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.survey_responses (id, user_id, customer_profile_id, responses, overall_score, budgeting_score, savings_score, debt_management_score, financial_planning_score, investment_knowledge_score, risk_tolerance, financial_goals, completion_time, survey_version, created_at, updated_at, question_set_id, question_variations_used, demographic_rules_applied, language, company_tracker_id, email_sent, pdf_generated, report_downloads) FROM stdin;
1	6	1	{"q1_income_stability": 3, "q2_income_sources": 2, "q3_living_expenses": 3, "q4_budget_tracking": 4, "q5_spending_control": 2, "q6_expense_review": 3, "q7_savings_rate": 3, "q8_emergency_fund": 3, "q9_savings_optimization": 4, "q10_payment_history": 3, "q11_debt_ratio": 3, "q12_credit_score": 3, "q13_retirement_planning": 4, "q14_insurance_coverage": 3, "q15_financial_planning": 3}	61.33	55	66.6	60	66.67	0	moderate	null	\N	2.0	2025-10-06 13:36:31.217409+05	\N	\N	\N	\N	en	\N	f	f	0
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, email, username, hashed_password, is_active, is_admin, created_at, updated_at, date_of_birth) FROM stdin;
1	test@example.com	testuser	$2b$12$hSvtM302hsfPylzS5cU0eOh.agqROcipDwXXohlj0brIRjGiWIgJu	t	f	2025-10-02 18:07:50.826409+05	2025-10-02 18:09:28.587282+05	1990-01-01 00:00:00
2	comprehensive.test@example.com	comprehensive_test	$2b$12$0pvGZgvqmmkoxtAkvCXW0OS/SqR7da1SfzcpGDeVjzCwbwccJRb4i	t	f	2025-10-02 18:16:34.848865+05	2025-10-02 18:16:35.863628+05	1985-06-15 00:00:00
3	admin@example.com	admin_user	$2b$12$U8KU97lQoGl3nUhZdo5Qu.RJ/2WDRYsmCTT/918cLt/wF7PZ6zy2W	t	t	2025-10-02 18:50:41.933417+05	2025-10-02 18:55:22.95019+05	\N
4	admin@nationalbonds.ae	nb_admin	$2b$12$7PZlkI05YAKjSehqCMtZcuxiIbFmxNyjKANNfdZ7zZzZLlB/M0Esq	t	t	2025-10-02 19:10:00.096954+05	\N	\N
6	ahmad.hassan@clustox.com	ahmadhassan		t	f	2025-10-06 13:36:31.217409+05	\N	1993-01-29 00:00:00
\.


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 117, true);


--
-- Name: company_assessments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.company_assessments_id_seq', 1, false);


--
-- Name: company_question_sets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.company_question_sets_id_seq', 1, false);


--
-- Name: company_trackers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.company_trackers_id_seq', 33, true);


--
-- Name: customer_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.customer_profiles_id_seq', 1, true);


--
-- Name: demographic_rules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.demographic_rules_id_seq', 1, false);


--
-- Name: incomplete_surveys_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.incomplete_surveys_id_seq', 3, true);


--
-- Name: localized_content_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.localized_content_id_seq', 484, true);


--
-- Name: question_variations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.question_variations_id_seq', 1, false);


--
-- Name: recommendations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.recommendations_id_seq', 1, false);


--
-- Name: report_access_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.report_access_logs_id_seq', 1, false);


--
-- Name: report_deliveries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.report_deliveries_id_seq', 1, false);


--
-- Name: simple_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.simple_sessions_id_seq', 13, true);


--
-- Name: survey_responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.survey_responses_id_seq', 2, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: company_assessments company_assessments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.company_assessments
    ADD CONSTRAINT company_assessments_pkey PRIMARY KEY (id);


--
-- Name: company_question_sets company_question_sets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.company_question_sets
    ADD CONSTRAINT company_question_sets_pkey PRIMARY KEY (id);


--
-- Name: company_trackers company_trackers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.company_trackers
    ADD CONSTRAINT company_trackers_pkey PRIMARY KEY (id);


--
-- Name: customer_profiles customer_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_profiles
    ADD CONSTRAINT customer_profiles_pkey PRIMARY KEY (id);


--
-- Name: demographic_rules demographic_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.demographic_rules
    ADD CONSTRAINT demographic_rules_pkey PRIMARY KEY (id);


--
-- Name: incomplete_surveys incomplete_surveys_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incomplete_surveys
    ADD CONSTRAINT incomplete_surveys_pkey PRIMARY KEY (id);


--
-- Name: localized_content localized_content_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.localized_content
    ADD CONSTRAINT localized_content_pkey PRIMARY KEY (id);


--
-- Name: question_variations question_variations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.question_variations
    ADD CONSTRAINT question_variations_pkey PRIMARY KEY (id);


--
-- Name: recommendations recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recommendations
    ADD CONSTRAINT recommendations_pkey PRIMARY KEY (id);


--
-- Name: report_access_logs report_access_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.report_access_logs
    ADD CONSTRAINT report_access_logs_pkey PRIMARY KEY (id);


--
-- Name: report_deliveries report_deliveries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.report_deliveries
    ADD CONSTRAINT report_deliveries_pkey PRIMARY KEY (id);


--
-- Name: simple_sessions simple_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.simple_sessions
    ADD CONSTRAINT simple_sessions_pkey PRIMARY KEY (id);


--
-- Name: survey_responses survey_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.survey_responses
    ADD CONSTRAINT survey_responses_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_audit_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_id ON public.audit_logs USING btree (id);


--
-- Name: ix_company_assessments_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_company_assessments_id ON public.company_assessments USING btree (id);


--
-- Name: ix_company_question_sets_company_tracker_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_company_question_sets_company_tracker_id ON public.company_question_sets USING btree (company_tracker_id);


--
-- Name: ix_company_question_sets_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_company_question_sets_id ON public.company_question_sets USING btree (id);


--
-- Name: ix_company_question_sets_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_company_question_sets_is_active ON public.company_question_sets USING btree (is_active);


--
-- Name: ix_company_trackers_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_company_trackers_id ON public.company_trackers USING btree (id);


--
-- Name: ix_company_trackers_unique_url; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_company_trackers_unique_url ON public.company_trackers USING btree (unique_url);


--
-- Name: ix_customer_profiles_age; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_customer_profiles_age ON public.customer_profiles USING btree (age);


--
-- Name: ix_customer_profiles_emirate; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_customer_profiles_emirate ON public.customer_profiles USING btree (emirate);


--
-- Name: ix_customer_profiles_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_customer_profiles_id ON public.customer_profiles USING btree (id);


--
-- Name: ix_customer_profiles_nationality; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_customer_profiles_nationality ON public.customer_profiles USING btree (nationality);


--
-- Name: ix_demographic_rules_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_demographic_rules_id ON public.demographic_rules USING btree (id);


--
-- Name: ix_demographic_rules_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_demographic_rules_is_active ON public.demographic_rules USING btree (is_active);


--
-- Name: ix_demographic_rules_priority; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_demographic_rules_priority ON public.demographic_rules USING btree (priority);


--
-- Name: ix_incomplete_surveys_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_incomplete_surveys_id ON public.incomplete_surveys USING btree (id);


--
-- Name: ix_incomplete_surveys_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_incomplete_surveys_session_id ON public.incomplete_surveys USING btree (session_id);


--
-- Name: ix_localized_content_content_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_localized_content_content_id ON public.localized_content USING btree (content_id);


--
-- Name: ix_localized_content_content_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_localized_content_content_type ON public.localized_content USING btree (content_type);


--
-- Name: ix_localized_content_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_localized_content_id ON public.localized_content USING btree (id);


--
-- Name: ix_localized_content_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_localized_content_is_active ON public.localized_content USING btree (is_active);


--
-- Name: ix_localized_content_language; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_localized_content_language ON public.localized_content USING btree (language);


--
-- Name: ix_question_variations_base_question_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_question_variations_base_question_id ON public.question_variations USING btree (base_question_id);


--
-- Name: ix_question_variations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_question_variations_id ON public.question_variations USING btree (id);


--
-- Name: ix_question_variations_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_question_variations_is_active ON public.question_variations USING btree (is_active);


--
-- Name: ix_question_variations_language; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_question_variations_language ON public.question_variations USING btree (language);


--
-- Name: ix_recommendations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_recommendations_id ON public.recommendations USING btree (id);


--
-- Name: ix_report_access_logs_accessed_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_report_access_logs_accessed_at ON public.report_access_logs USING btree (accessed_at);


--
-- Name: ix_report_access_logs_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_report_access_logs_id ON public.report_access_logs USING btree (id);


--
-- Name: ix_report_access_logs_report_delivery_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_report_access_logs_report_delivery_id ON public.report_access_logs USING btree (report_delivery_id);


--
-- Name: ix_report_access_logs_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_report_access_logs_user_id ON public.report_access_logs USING btree (user_id);


--
-- Name: ix_report_deliveries_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_report_deliveries_created_at ON public.report_deliveries USING btree (created_at);


--
-- Name: ix_report_deliveries_delivery_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_report_deliveries_delivery_status ON public.report_deliveries USING btree (delivery_status);


--
-- Name: ix_report_deliveries_delivery_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_report_deliveries_delivery_type ON public.report_deliveries USING btree (delivery_type);


--
-- Name: ix_report_deliveries_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_report_deliveries_id ON public.report_deliveries USING btree (id);


--
-- Name: ix_report_deliveries_survey_response_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_report_deliveries_survey_response_id ON public.report_deliveries USING btree (survey_response_id);


--
-- Name: ix_report_deliveries_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_report_deliveries_user_id ON public.report_deliveries USING btree (user_id);


--
-- Name: ix_simple_sessions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_simple_sessions_id ON public.simple_sessions USING btree (id);


--
-- Name: ix_simple_sessions_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_simple_sessions_session_id ON public.simple_sessions USING btree (session_id);


--
-- Name: ix_survey_responses_company_tracker_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_survey_responses_company_tracker_id ON public.survey_responses USING btree (company_tracker_id);


--
-- Name: ix_survey_responses_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_survey_responses_id ON public.survey_responses USING btree (id);


--
-- Name: ix_survey_responses_language; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_survey_responses_language ON public.survey_responses USING btree (language);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: company_assessments company_assessments_company_tracker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.company_assessments
    ADD CONSTRAINT company_assessments_company_tracker_id_fkey FOREIGN KEY (company_tracker_id) REFERENCES public.company_trackers(id);


--
-- Name: company_question_sets company_question_sets_company_tracker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.company_question_sets
    ADD CONSTRAINT company_question_sets_company_tracker_id_fkey FOREIGN KEY (company_tracker_id) REFERENCES public.company_trackers(id);


--
-- Name: customer_profiles customer_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_profiles
    ADD CONSTRAINT customer_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: survey_responses fk_survey_responses_company_tracker; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.survey_responses
    ADD CONSTRAINT fk_survey_responses_company_tracker FOREIGN KEY (company_tracker_id) REFERENCES public.company_trackers(id);


--
-- Name: incomplete_surveys incomplete_surveys_customer_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incomplete_surveys
    ADD CONSTRAINT incomplete_surveys_customer_profile_id_fkey FOREIGN KEY (customer_profile_id) REFERENCES public.customer_profiles(id);


--
-- Name: incomplete_surveys incomplete_surveys_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incomplete_surveys
    ADD CONSTRAINT incomplete_surveys_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: recommendations recommendations_survey_response_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.recommendations
    ADD CONSTRAINT recommendations_survey_response_id_fkey FOREIGN KEY (survey_response_id) REFERENCES public.survey_responses(id);


--
-- Name: report_access_logs report_access_logs_report_delivery_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.report_access_logs
    ADD CONSTRAINT report_access_logs_report_delivery_id_fkey FOREIGN KEY (report_delivery_id) REFERENCES public.report_deliveries(id);


--
-- Name: report_access_logs report_access_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.report_access_logs
    ADD CONSTRAINT report_access_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: report_deliveries report_deliveries_survey_response_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.report_deliveries
    ADD CONSTRAINT report_deliveries_survey_response_id_fkey FOREIGN KEY (survey_response_id) REFERENCES public.survey_responses(id);


--
-- Name: report_deliveries report_deliveries_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.report_deliveries
    ADD CONSTRAINT report_deliveries_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: simple_sessions simple_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.simple_sessions
    ADD CONSTRAINT simple_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: survey_responses survey_responses_customer_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.survey_responses
    ADD CONSTRAINT survey_responses_customer_profile_id_fkey FOREIGN KEY (customer_profile_id) REFERENCES public.customer_profiles(id);


--
-- Name: survey_responses survey_responses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.survey_responses
    ADD CONSTRAINT survey_responses_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict LRv3ld1VmtCRePjTjfSbcR6ENKPrn187u3Tjtj44GND4IiYLdOY8xsWVU6o7U6M

