-- Initial data
-- DBL Migration Layer: 2026-01-07 14:27:36.467824
-- From: myapp_dbl_shadow_1767817648 To: myapp
-- 
-- Phases:
--   expand:   Add columns/tables (safe, no data loss)
--   backfill: Update/populate data (optional)
--   contract: Remove/constrain (careful, review)



-- [BACKFILL PHASE - DATA SYNC] --
-- ⚠️  Data operations are destructive (TRUNCATE).
-- Ensure these are lookup/reference tables only.
-- phase: backfill (data-only, optional)
-- Data changed in: orders
TRUNCATE TABLE orders;
--
-- PostgreSQL database dump
--

\restrict 6PUjeYRnraVkjABSlbnpuxe6ZVGAiQNTz8BOvAXIQPwRAPLMNCd3gYUP4h5aB5I

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


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.orders_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

\unrestrict 6PUjeYRnraVkjABSlbnpuxe6ZVGAiQNTz8BOvAXIQPwRAPLMNCd3gYUP4h5aB5I

-- phase: backfill (data-only, optional)
-- Data changed in: products
TRUNCATE TABLE products;
--
-- PostgreSQL database dump
--

\restrict XkcVO7vVsPMedgyw7ty7Ykxw0MOokPn7vW8Dm7ld2YruHDNCSDaDCKXGNHdfMGi

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


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.products_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

\unrestrict XkcVO7vVsPMedgyw7ty7Ykxw0MOokPn7vW8Dm7ld2YruHDNCSDaDCKXGNHdfMGi

-- phase: backfill (data-only, optional)
-- Data changed in: users
TRUNCATE TABLE users;
--
-- PostgreSQL database dump
--

\restrict ju1qGrghO3bbkkYxMOpRd9nhwI9m20aAH03oHkkv30YXzymZRnMJpKNjXny9aTI

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


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

\unrestrict ju1qGrghO3bbkkYxMOpRd9nhwI9m20aAH03oHkkv30YXzymZRnMJpKNjXny9aTI