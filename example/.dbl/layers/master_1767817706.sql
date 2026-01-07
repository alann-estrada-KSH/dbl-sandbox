-- Initial data
-- DBL Migration Layer: 2026-01-07 14:28:20.806997
-- From: myapp_dbl_shadow_1767817692 To: myapp
-- 
-- Phases:
--   expand:   Add columns/tables (safe, no data loss)
--   backfill: Update/populate data (optional)
--   contract: Remove/constrain (careful, review)



-- [BACKFILL PHASE - DATA SYNC] --
-- ⚠️  Data operations are destructive (TRUNCATE).
-- Ensure these are lookup/reference tables only.
-- phase: backfill (data-only, optional)
-- Data changed in: addresses
TRUNCATE TABLE addresses;
--
-- PostgreSQL database dump
--

\restrict vAKvaKwqykxddBJfU1xsyTaIwdoYTUCCn8l5qEYncpL09kXP30LJZ1zs1FKZ4cR

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Data for Name: addresses; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.addresses (id, user_id, street, city, zip) VALUES (1, 1, '123 Main St', 'Anytown', '12345');


--
-- Name: addresses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.addresses_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

\unrestrict vAKvaKwqykxddBJfU1xsyTaIwdoYTUCCn8l5qEYncpL09kXP30LJZ1zs1FKZ4cR

-- phase: backfill (data-only, optional)
-- Data changed in: categories
TRUNCATE TABLE categories;
--
-- PostgreSQL database dump
--

\restrict gD4whbJJnwCfrTpEg2js6eZsHdoKSzZmpeDYGAVLvUcIgfjHsDmJmnhQGk0V4PI

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.categories (id, name) VALUES (1, 'Electronics');
INSERT INTO public.categories (id, name) VALUES (2, 'Tools');
INSERT INTO public.categories (id, name) VALUES (3, 'Accessories');


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.categories_id_seq', 3, true);


--
-- PostgreSQL database dump complete
--

\unrestrict gD4whbJJnwCfrTpEg2js6eZsHdoKSzZmpeDYGAVLvUcIgfjHsDmJmnhQGk0V4PI

-- phase: backfill (data-only, optional)
-- Data changed in: coupons
TRUNCATE TABLE coupons;
--
-- PostgreSQL database dump
--

\restrict CuCOPflbIi6q8EJWRxSAiKbCpmhfo9BFr0LSPMx3TmzehdZyXX7SbzMLmLdARdN

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Data for Name: coupons; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.coupons (id, code, discount) VALUES (1, 'SAVE10', 10.00);
INSERT INTO public.coupons (id, code, discount) VALUES (2, 'NEWUSER', 5.00);


--
-- Name: coupons_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.coupons_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

\unrestrict CuCOPflbIi6q8EJWRxSAiKbCpmhfo9BFr0LSPMx3TmzehdZyXX7SbzMLmLdARdN

-- phase: backfill (data-only, optional)
-- Data changed in: inventory
TRUNCATE TABLE inventory;
--
-- PostgreSQL database dump
--

\restrict lVfNiYefHXLopGg42D0h3EBqTyGdIPBGegHKTZgxe8cRPSUpNkkYaflwMFmDduG

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.inventory (id, product_id, stock) VALUES (1, 1, 100);
INSERT INTO public.inventory (id, product_id, stock) VALUES (2, 2, 50);
INSERT INTO public.inventory (id, product_id, stock) VALUES (3, 3, 75);
INSERT INTO public.inventory (id, product_id, stock) VALUES (4, 4, 25);
INSERT INTO public.inventory (id, product_id, stock) VALUES (5, 5, 200);


--
-- Name: inventory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.inventory_id_seq', 5, true);


--
-- PostgreSQL database dump complete
--

\unrestrict lVfNiYefHXLopGg42D0h3EBqTyGdIPBGegHKTZgxe8cRPSUpNkkYaflwMFmDduG

-- phase: backfill (data-only, optional)
-- Data changed in: logs
TRUNCATE TABLE logs;
--
-- PostgreSQL database dump
--

\restrict 9F6e6q2mCp5c0r0brDrmUhQViPQ52Bl2lIhiLhuuHq0RHpyLzjrcZ2h51rC2Dq4

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Data for Name: logs; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.logs (id, action, "timestamp") VALUES (1, 'User login', '2026-01-07 20:28:04.459794');
INSERT INTO public.logs (id, action, "timestamp") VALUES (2, 'Order placed', '2026-01-07 20:28:04.459794');


--
-- Name: logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.logs_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

\unrestrict 9F6e6q2mCp5c0r0brDrmUhQViPQ52Bl2lIhiLhuuHq0RHpyLzjrcZ2h51rC2Dq4

-- phase: backfill (data-only, optional)
-- Data changed in: notifications
TRUNCATE TABLE notifications;
--
-- PostgreSQL database dump
--

\restrict FUuM3koFRhp8oXepy1eg4BnqfFrVskGKqOCGGdmpTkGexzau2lZPYzPEUDkvSca

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.notifications (id, user_id, message, read) VALUES (1, 1, 'Order shipped', false);
INSERT INTO public.notifications (id, user_id, message, read) VALUES (2, 2, 'Payment received', false);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.notifications_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

\unrestrict FUuM3koFRhp8oXepy1eg4BnqfFrVskGKqOCGGdmpTkGexzau2lZPYzPEUDkvSca

-- phase: backfill (data-only, optional)
-- Data changed in: orders
TRUNCATE TABLE orders;
--
-- PostgreSQL database dump
--

\restrict tatT9S4KeIo948Lxg9fhYqaYfOE4TBErYfWH08RlvPADpbajGYAoeT8t9hvtL3t

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.orders (id, user_id, product_id, quantity) VALUES (1, 1, 1, 2);
INSERT INTO public.orders (id, user_id, product_id, quantity) VALUES (2, 2, 2, 1);
INSERT INTO public.orders (id, user_id, product_id, quantity) VALUES (3, 3, 3, 3);
INSERT INTO public.orders (id, user_id, product_id, quantity) VALUES (4, 4, 4, 1);
INSERT INTO public.orders (id, user_id, product_id, quantity) VALUES (5, 5, 5, 2);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.orders_id_seq', 5, true);


--
-- PostgreSQL database dump complete
--

\unrestrict tatT9S4KeIo948Lxg9fhYqaYfOE4TBErYfWH08RlvPADpbajGYAoeT8t9hvtL3t

-- phase: backfill (data-only, optional)
-- Data changed in: payments
TRUNCATE TABLE payments;
--
-- PostgreSQL database dump
--

\restrict Fs7iN7NU3DNPAOniJaT7YCIO1QkcnEGRIGgtIUyDxfm16dKpPanxeio07I0OMrE

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.payments (id, order_id, amount, method) VALUES (1, 1, 21.98, 'Credit Card');


--
-- Name: payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.payments_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

\unrestrict Fs7iN7NU3DNPAOniJaT7YCIO1QkcnEGRIGgtIUyDxfm16dKpPanxeio07I0OMrE

-- phase: backfill (data-only, optional)
-- Data changed in: products
TRUNCATE TABLE products;
--
-- PostgreSQL database dump
--

\restrict HWiGRTuUNfmUEiD8w2hIaqaLNrG1Jdl0azzAh0c6XIJonWJwsadmLx7EDnFlKj7

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.products (id, name, price) VALUES (1, 'Widget', 10.99);
INSERT INTO public.products (id, name, price) VALUES (2, 'Gadget', 25.50);
INSERT INTO public.products (id, name, price) VALUES (3, 'Tool', 15.75);
INSERT INTO public.products (id, name, price) VALUES (4, 'Device', 30.00);
INSERT INTO public.products (id, name, price) VALUES (5, 'Accessory', 5.99);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.products_id_seq', 5, true);


--
-- PostgreSQL database dump complete
--

\unrestrict HWiGRTuUNfmUEiD8w2hIaqaLNrG1Jdl0azzAh0c6XIJonWJwsadmLx7EDnFlKj7

-- phase: backfill (data-only, optional)
-- Data changed in: reviews
TRUNCATE TABLE reviews;
--
-- PostgreSQL database dump
--

\restrict VHcYMRebRMLZRmxzsFELf2VqCdlbhr14aBgeq0yBDaFbc0ZJSopgQ0gnDbgFrf4

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.reviews (id, product_id, user_id, rating, comment) VALUES (1, 1, 1, 5, 'Great!');
INSERT INTO public.reviews (id, product_id, user_id, rating, comment) VALUES (2, 2, 2, 4, 'Good value');


--
-- Name: reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.reviews_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

\unrestrict VHcYMRebRMLZRmxzsFELf2VqCdlbhr14aBgeq0yBDaFbc0ZJSopgQ0gnDbgFrf4

-- phase: backfill (data-only, optional)
-- Data changed in: settings
TRUNCATE TABLE settings;
--
-- PostgreSQL database dump
--

\restrict iD04JMy9BWEePcGO0T6oQITGfcXrse2DX6VsfAVaJ1goPbE8oDPdbQKb215Fr7S

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Data for Name: settings; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.settings (id, key, value) VALUES (1, 'theme', 'dark');
INSERT INTO public.settings (id, key, value) VALUES (2, 'language', 'en');


--
-- Name: settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.settings_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

\unrestrict iD04JMy9BWEePcGO0T6oQITGfcXrse2DX6VsfAVaJ1goPbE8oDPdbQKb215Fr7S

-- phase: backfill (data-only, optional)
-- Data changed in: suppliers
TRUNCATE TABLE suppliers;
--
-- PostgreSQL database dump
--

\restrict Tgok3detSarAymYZmd7xYcUlbq3frf9LRIYCxVGLBff2UgpTsv0bb9gwqaX6N35

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Data for Name: suppliers; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.suppliers (id, name, contact) VALUES (1, 'Supplier A', 'contact@a.com');
INSERT INTO public.suppliers (id, name, contact) VALUES (2, 'Supplier B', 'contact@b.com');


--
-- Name: suppliers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.suppliers_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

\unrestrict Tgok3detSarAymYZmd7xYcUlbq3frf9LRIYCxVGLBff2UgpTsv0bb9gwqaX6N35

-- phase: backfill (data-only, optional)
-- Data changed in: users
TRUNCATE TABLE users;
--
-- PostgreSQL database dump
--

\restrict rBpSZtbti9SusxxGQrXQch6dlFRcnqWiUACCcJvUaAMWIh8hGcvg93LdTlHH2X9

-- Dumped from database version 13.23 (Debian 13.23-1.pgdg13+1)
-- Dumped by pg_dump version 13.23 (Debian 13.23-1.pgdg13+1)

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

--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.users (id, name, email) VALUES (1, 'Alice', 'alice@example.com');
INSERT INTO public.users (id, name, email) VALUES (2, 'Bob', 'bob@example.com');
INSERT INTO public.users (id, name, email) VALUES (3, 'Charlie', 'charlie@example.com');
INSERT INTO public.users (id, name, email) VALUES (4, 'Diana', 'diana@example.com');
INSERT INTO public.users (id, name, email) VALUES (5, 'Eve', 'eve@example.com');


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.users_id_seq', 5, true);


--
-- PostgreSQL database dump complete
--

\unrestrict rBpSZtbti9SusxxGQrXQch6dlFRcnqWiUACCcJvUaAMWIh8hGcvg93LdTlHH2X9