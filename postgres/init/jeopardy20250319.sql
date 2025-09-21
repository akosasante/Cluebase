--
-- PostgreSQL database dump
--

-- Dumped from database version 11.2
-- Dumped by pg_dump version 11.2

\c jeopardy

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;
SET xmloption = content;
SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner:
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: clues; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clues (
    id integer NOT NULL,
    game_id integer,
    value integer NOT NULL,
    daily_double boolean NOT NULL,
    round character varying NOT NULL,
    category character varying NOT NULL,
    clue character varying NOT NULL,
    response character varying NOT NULL,
    has_media boolean
);


ALTER TABLE public.clues OWNER TO postgres;

--
-- Name: clues_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clues_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.clues_id_seq OWNER TO postgres;

--
-- Name: clues_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clues_id_seq OWNED BY public.clues.id;


--
-- Name: contestants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contestants (
    id integer NOT NULL,
    name character varying NOT NULL,
    notes character varying,
    games_played integer,
    total_winnings integer,
    jarchive_id integer,
    alternate_jarchive_ids integer[]
);


ALTER TABLE public.contestants OWNER TO postgres;

--
-- Name: contestants_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.contestants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contestants_id_seq OWNER TO postgres;

--
-- Name: contestants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.contestants_id_seq OWNED BY public.contestants.id;


--
-- Name: games; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.games (
    id integer NOT NULL,
    episode_num integer,
    season_id integer,
    air_date date NOT NULL,
    notes character varying,
    contestant1 integer,
    contestant2 integer,
    contestant3 integer,
    winner integer,
    score1 integer,
    score2 integer,
    score3 integer,
    jarchive_id integer,
    coryat1 integer,
    coryat2 integer,
    coryat3 integer
);


ALTER TABLE public.games OWNER TO postgres;

--
-- Name: games_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.games_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.games_id_seq OWNER TO postgres;

--
-- Name: games_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.games_id_seq OWNED BY public.games.id;


--
-- Name: parsed_games; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parsed_games (
    id integer NOT NULL,
    episode_num integer,
    game_link character varying,
    game_id integer,
    parsed_on timestamp without time zone DEFAULT now()
);


ALTER TABLE public.parsed_games OWNER TO postgres;

--
-- Name: parsed_games_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.parsed_games_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.parsed_games_id_seq OWNER TO postgres;

--
-- Name: parsed_games_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.parsed_games_id_seq OWNED BY public.parsed_games.id;


--
-- Name: seasons; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.seasons (
    id integer NOT NULL,
    season_name character varying(64),
    start_date date,
    end_date date,
    total_games integer
);


ALTER TABLE public.seasons OWNER TO postgres;

--
-- Name: seasons_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.seasons_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seasons_id_seq OWNER TO postgres;

--
-- Name: seasons_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.seasons_id_seq OWNED BY public.seasons.id;


--
-- Name: clues id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clues ALTER COLUMN id SET DEFAULT nextval('public.clues_id_seq'::regclass);


--
-- Name: contestants id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contestants ALTER COLUMN id SET DEFAULT nextval('public.contestants_id_seq'::regclass);


--
-- Name: games id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games ALTER COLUMN id SET DEFAULT nextval('public.games_id_seq'::regclass);


--
-- Name: parsed_games id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parsed_games ALTER COLUMN id SET DEFAULT nextval('public.parsed_games_id_seq'::regclass);


--
-- Name: seasons id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seasons ALTER COLUMN id SET DEFAULT nextval('public.seasons_id_seq'::regclass);

--
-- Name: clues_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clues_id_seq', 2932395, true);


--
-- Name: contestants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.contestants_id_seq', 159415, true);


--
-- Name: games_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.games_id_seq', 49521, true);


--
-- Name: parsed_games_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.parsed_games_id_seq', 49581, true);


--
-- Name: seasons_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.seasons_id_seq', 607, true);


--
-- Name: clues clues_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clues
    ADD CONSTRAINT clues_pkey PRIMARY KEY (id);


--
-- Name: contestants contestants_name_unq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contestants
    ADD CONSTRAINT contestants_name_unq UNIQUE (name);


--
-- Name: contestants contestants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contestants
    ADD CONSTRAINT contestants_pkey PRIMARY KEY (id);


--
-- Name: games games_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games
    ADD CONSTRAINT games_pkey PRIMARY KEY (id);


--
-- Name: parsed_games parsed_games_episode_num_unq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parsed_games
    ADD CONSTRAINT parsed_games_episode_num_unq UNIQUE (episode_num);


--
-- Name: parsed_games parsed_games_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parsed_games
    ADD CONSTRAINT parsed_games_pkey PRIMARY KEY (id);


--
-- Name: seasons seasons_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.seasons
    ADD CONSTRAINT seasons_pkey PRIMARY KEY (id);


--
-- Name: games_season_id_episode_num_air_date_uindex; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX games_season_id_episode_num_air_date_uindex ON public.games USING btree (season_id, episode_num, air_date);


--
-- Name: clues clues_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clues
    ADD CONSTRAINT clues_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.games(id);


--
-- Name: games games_contestant1_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games
    ADD CONSTRAINT games_contestant1_fkey FOREIGN KEY (contestant1) REFERENCES public.contestants(id);


--
-- Name: games games_contestant2_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games
    ADD CONSTRAINT games_contestant2_fkey FOREIGN KEY (contestant2) REFERENCES public.contestants(id);


--
-- Name: games games_contestant3_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games
    ADD CONSTRAINT games_contestant3_fkey FOREIGN KEY (contestant3) REFERENCES public.contestants(id);


--
-- Name: games games_season_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games
    ADD CONSTRAINT games_season_id_fkey FOREIGN KEY (season_id) REFERENCES public.seasons(id);


--
-- Name: games games_winner_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.games
    ADD CONSTRAINT games_winner_fkey FOREIGN KEY (winner) REFERENCES public.contestants(id);


--
-- Name: parsed_games parsed_games_games_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parsed_games
    ADD CONSTRAINT parsed_games_games_id_fk FOREIGN KEY (game_id) REFERENCES public.games(id);


--
-- PostgreSQL database dump complete
--
