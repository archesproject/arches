--
-- PostgreSQL database dump
--

-- Dumped from database version 9.4.5
-- Dumped by pg_dump version 9.4.0
-- Started on 2015-12-08 11:18:40 PST

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

--
-- TOC entry 2384 (class 0 OID 762113)
-- Dependencies: 179
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_group (id, name) FROM stdin;
\.


--
-- TOC entry 2400 (class 0 OID 0)
-- Dependencies: 178
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_group_id_seq', 1, false);


--
-- TOC entry 2380 (class 0 OID 762093)
-- Dependencies: 175
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_content_type (id, app_label, model) FROM stdin;   
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
\.


--
-- TOC entry 2382 (class 0 OID 762103)
-- Dependencies: 177
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can add permission	2	add_permission
5	Can change permission	2	change_permission
6	Can delete permission	2	delete_permission
7	Can add group	3	add_group
8	Can change group	3	change_group
9	Can delete group	3	delete_group
10	Can add user	4	add_user
11	Can change user	4	change_user
12	Can delete user	4	delete_user
13	Can add content type	5	add_contenttype
14	Can change content type	5	change_contenttype
15	Can delete content type	5	delete_contenttype
16	Can add session	6	add_session
17	Can change session	6	change_session
18	Can delete session	6	delete_session
\.


--
-- TOC entry 2386 (class 0 OID 762123)
-- Dependencies: 181
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- TOC entry 2401 (class 0 OID 0)
-- Dependencies: 180
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_group_permissions_id_seq', 1, false);


--
-- TOC entry 2402 (class 0 OID 0)
-- Dependencies: 176
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_permission_id_seq', 18, true);


--
-- TOC entry 2388 (class 0 OID 762133)
-- Dependencies: 183
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_user (id, username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined) FROM stdin;
1	admin			admin@fargeo.com	sha1$6b2ab$8de142f75873b7d6e180133325fe19eae1163262	t	t	t	2012-03-15 15:29:31.211-07	2012-03-15 15:29:31.211-07
\.


--
-- TOC entry 2390 (class 0 OID 762143)
-- Dependencies: 185
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- TOC entry 2403 (class 0 OID 0)
-- Dependencies: 184
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_user_groups_id_seq', 1, false);


--
-- TOC entry 2404 (class 0 OID 0)
-- Dependencies: 182
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_user_id_seq', 1, true);


--
-- TOC entry 2392 (class 0 OID 762153)
-- Dependencies: 187
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- TOC entry 2405 (class 0 OID 0)
-- Dependencies: 186
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('auth_user_user_permissions_id_seq', 1, false);


--
-- TOC entry 2394 (class 0 OID 762207)
-- Dependencies: 189
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- TOC entry 2406 (class 0 OID 0)
-- Dependencies: 188
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 1, false);


--
-- TOC entry 2407 (class 0 OID 0)
-- Dependencies: 174
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_content_type_id_seq', 6, true);


--
-- TOC entry 2378 (class 0 OID 762082)
-- Dependencies: 173
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2015-12-04 12:02:42.213999-08
2	auth	0001_initial	2015-12-04 12:02:42.27077-08
3	admin	0001_initial	2015-12-04 12:02:42.293039-08
4	contenttypes	0002_remove_content_type_name	2015-12-04 12:02:42.324918-08
5	auth	0002_alter_permission_name_max_length	2015-12-04 12:02:42.335961-08
6	auth	0003_alter_user_email_max_length	2015-12-04 12:02:42.349556-08
7	auth	0004_alter_user_username_opts	2015-12-04 12:02:42.35946-08
8	auth	0005_alter_user_last_login_null	2015-12-04 12:02:42.372508-08
9	auth	0006_require_contenttypes_0002	2015-12-04 12:02:42.374291-08
10	sessions	0001_initial	2015-12-04 12:02:42.383015-08
\.


--
-- TOC entry 2408 (class 0 OID 0)
-- Dependencies: 172
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('django_migrations_id_seq', 10, true);


--
-- TOC entry 2395 (class 0 OID 762229)
-- Dependencies: 190
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY django_session (session_key, session_data, expire_date) FROM stdin;
\.


-- Completed on 2015-12-08 11:18:40 PST

--
-- PostgreSQL database dump complete
--

