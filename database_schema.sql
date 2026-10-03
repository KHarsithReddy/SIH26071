--
-- PostgreSQL database dump
--

\restrict vRfU2ueRK9260boBUmzxoqaUMJnR91PeYedQsffP2BzFOp0fHdGYL1fC2zRBcum

-- Dumped from database version 17.11
-- Dumped by pg_dump version 17.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: prediction_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prediction_history (
    id integer NOT NULL,
    prediction_type character varying(50) NOT NULL,
    risk_level character varying(50) NOT NULL,
    predicted_class integer NOT NULL,
    confidence_score double precision NOT NULL,
    probabilities json,
    overall_status character varying(50),
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.prediction_history OWNER TO postgres;

--
-- Name: prediction_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prediction_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prediction_history_id_seq OWNER TO postgres;

--
-- Name: prediction_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.prediction_history_id_seq OWNED BY public.prediction_history.id;


--
-- Name: prediction_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction_history ALTER COLUMN id SET DEFAULT nextval('public.prediction_history_id_seq'::regclass);


--
-- Name: prediction_history prediction_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prediction_history
    ADD CONSTRAINT prediction_history_pkey PRIMARY KEY (id);


--
-- Name: ix_prediction_history_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_prediction_history_id ON public.prediction_history USING btree (id);


--
-- PostgreSQL database dump complete
--

\unrestrict vRfU2ueRK9260boBUmzxoqaUMJnR91PeYedQsffP2BzFOp0fHdGYL1fC2zRBcum

