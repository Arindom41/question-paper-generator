--
-- PostgreSQL database dump
--

\restrict b7BpZIa6KvWthQcmVTBikMotFgv5fe7T6gCtyeWpOYi0mDKni6G8TdaFN94o8iC

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

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
-- Name: course_outcomes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.course_outcomes (
    co_id integer NOT NULL,
    subject_id integer,
    co_code character varying(10),
    description text
);


ALTER TABLE public.course_outcomes OWNER TO postgres;

--
-- Name: course_outcomes_co_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.course_outcomes_co_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.course_outcomes_co_id_seq OWNER TO postgres;

--
-- Name: course_outcomes_co_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.course_outcomes_co_id_seq OWNED BY public.course_outcomes.co_id;


--
-- Name: exam_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exam_questions (
    id integer NOT NULL,
    exam_id integer,
    question_id integer
);


ALTER TABLE public.exam_questions OWNER TO postgres;

--
-- Name: exam_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exam_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exam_questions_id_seq OWNER TO postgres;

--
-- Name: exam_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exam_questions_id_seq OWNED BY public.exam_questions.id;


--
-- Name: exams; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exams (
    exam_id integer NOT NULL,
    subject_id integer,
    total_marks integer,
    exam_date date
);


ALTER TABLE public.exams OWNER TO postgres;

--
-- Name: exams_exam_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exams_exam_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exams_exam_id_seq OWNER TO postgres;

--
-- Name: exams_exam_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exams_exam_id_seq OWNED BY public.exams.exam_id;


--
-- Name: marks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.marks (
    id integer NOT NULL,
    student_id integer,
    exam_id integer,
    question_id integer,
    marks_obtained integer
);


ALTER TABLE public.marks OWNER TO postgres;

--
-- Name: marks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.marks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.marks_id_seq OWNER TO postgres;

--
-- Name: marks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.marks_id_seq OWNED BY public.marks.id;


--
-- Name: question_co_map; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.question_co_map (
    question_id integer NOT NULL,
    co_id integer NOT NULL
);


ALTER TABLE public.question_co_map OWNER TO postgres;

--
-- Name: questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.questions (
    question_id integer NOT NULL,
    subject_id integer,
    unit integer,
    question_text text NOT NULL,
    marks integer,
    bloom_level character varying(20),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    image_path text
);


ALTER TABLE public.questions OWNER TO postgres;

--
-- Name: questions_question_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.questions_question_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.questions_question_id_seq OWNER TO postgres;

--
-- Name: questions_question_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.questions_question_id_seq OWNED BY public.questions.question_id;


--
-- Name: students; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students (
    student_id integer NOT NULL,
    name character varying(100),
    roll_no character varying(20)
);


ALTER TABLE public.students OWNER TO postgres;

--
-- Name: students_student_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.students_student_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.students_student_id_seq OWNER TO postgres;

--
-- Name: students_student_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.students_student_id_seq OWNED BY public.students.student_id;


--
-- Name: subjects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subjects (
    subject_id integer NOT NULL,
    subject_name character varying(100) NOT NULL,
    semester integer
);


ALTER TABLE public.subjects OWNER TO postgres;

--
-- Name: subjects_subject_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subjects_subject_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subjects_subject_id_seq OWNER TO postgres;

--
-- Name: subjects_subject_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subjects_subject_id_seq OWNED BY public.subjects.subject_id;


--
-- Name: course_outcomes co_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_outcomes ALTER COLUMN co_id SET DEFAULT nextval('public.course_outcomes_co_id_seq'::regclass);


--
-- Name: exam_questions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_questions ALTER COLUMN id SET DEFAULT nextval('public.exam_questions_id_seq'::regclass);


--
-- Name: exams exam_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams ALTER COLUMN exam_id SET DEFAULT nextval('public.exams_exam_id_seq'::regclass);


--
-- Name: marks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marks ALTER COLUMN id SET DEFAULT nextval('public.marks_id_seq'::regclass);


--
-- Name: questions question_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions ALTER COLUMN question_id SET DEFAULT nextval('public.questions_question_id_seq'::regclass);


--
-- Name: students student_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students ALTER COLUMN student_id SET DEFAULT nextval('public.students_student_id_seq'::regclass);


--
-- Name: subjects subject_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects ALTER COLUMN subject_id SET DEFAULT nextval('public.subjects_subject_id_seq'::regclass);


--
-- Data for Name: course_outcomes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.course_outcomes (co_id, subject_id, co_code, description) FROM stdin;
1	1	CO1	Understand concepts
2	1	CO2	Apply algorithms
3	1	CO3	Analyze data
\.


--
-- Data for Name: exam_questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exam_questions (id, exam_id, question_id) FROM stdin;
\.


--
-- Data for Name: exams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams (exam_id, subject_id, total_marks, exam_date) FROM stdin;
\.


--
-- Data for Name: marks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.marks (id, student_id, exam_id, question_id, marks_obtained) FROM stdin;
\.


--
-- Data for Name: question_co_map; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.question_co_map (question_id, co_id) FROM stdin;
1	1
2	1
3	2
4	2
5	3
6	1
7	1
8	1
9	2
10	2
11	2
12	2
13	3
14	3
15	3
16	3
17	3
18	3
19	1
20	1
22	1
23	3
\.


--
-- Data for Name: questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.questions (question_id, subject_id, unit, question_text, marks, bloom_level, created_at, image_path) FROM stdin;
2	1	1	Explain classification.	5	Understand	2026-03-29 01:11:28.97896	\N
3	1	2	Describe clustering algorithms.	5	Understand	2026-03-29 01:11:28.97896	\N
4	1	2	Apply K-means on given dataset.	10	Apply	2026-03-29 01:11:28.97896	\N
5	1	3	Compare supervised and unsupervised learning.	5	Analyze	2026-03-29 01:11:28.97896	\N
6	1	1	Define data mining and its applications.	2	Remember	2026-04-04 15:12:42.917121	\N
7	1	1	Explain the KDD process.	5	Understand	2026-04-04 15:12:42.917121	\N
8	1	1	Differentiate between data mining and data warehousing.	5	Analyze	2026-04-04 15:12:42.917121	\N
9	1	2	What is classification? Explain decision tree.	5	Understand	2026-04-04 15:13:28.002988	\N
10	1	2	Explain Naive Bayes classifier with example.	10	Apply	2026-04-04 15:13:28.002988	\N
11	1	2	What is clustering? Explain K-means algorithm.	5	Understand	2026-04-04 15:13:28.002988	\N
12	1	2	Compare K-means and hierarchical clustering.	5	Analyze	2026-04-04 15:13:28.002988	\N
13	1	3	What are association rules?	2	Remember	2026-04-04 15:13:38.103012	\N
14	1	3	Explain Apriori algorithm.	10	Apply	2026-04-04 15:13:38.103012	\N
15	1	3	Define support and confidence.	5	Understand	2026-04-04 15:13:38.103012	\N
16	1	4	What is outlier detection?	5	Understand	2026-04-04 15:13:48.553008	\N
17	1	4	Explain data preprocessing techniques.	5	Understand	2026-04-04 15:13:48.553008	\N
18	1	4	Discuss challenges in data mining.	5	Analyze	2026-04-04 15:13:48.553008	\N
1	1	1	What is data mining?	2	Remember	2026-03-29 01:11:28.97896	/static/images/q1.jpg
19	1	\N	Construct the FIRST set for the grammar\n\n$$\nE \\rightarrow E+T \\mid T\n$$	5	\N	2026-05-29 23:42:26.365722	\N
20	1	\N	Find the determinant of  $$ \\begin{bmatrix} 1 & 2 & 3\\\\ 4 & 5 & 6\\\\ 7 & 8 & 9 \\end{bmatrix} $$  and comment on its properties.	10	\N	2026-05-30 00:57:02.830792	\N
22	1	\N	what is your name :???	2	\N	2026-06-07 10:20:01.891046	\N
23	1	\N	What is the weather today?	20	\N	2026-06-07 10:28:43.656904	uploads/3043FA76-D5DE-45AF-B565-54E3ACF86968.png
\.


--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students (student_id, name, roll_no) FROM stdin;
\.


--
-- Data for Name: subjects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subjects (subject_id, subject_name, semester) FROM stdin;
1	Data Mining	6
\.


--
-- Name: course_outcomes_co_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.course_outcomes_co_id_seq', 3, true);


--
-- Name: exam_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exam_questions_id_seq', 1, false);


--
-- Name: exams_exam_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_exam_id_seq', 1, false);


--
-- Name: marks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.marks_id_seq', 1, false);


--
-- Name: questions_question_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.questions_question_id_seq', 23, true);


--
-- Name: students_student_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_student_id_seq', 1, false);


--
-- Name: subjects_subject_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subjects_subject_id_seq', 1, true);


--
-- Name: course_outcomes course_outcomes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_outcomes
    ADD CONSTRAINT course_outcomes_pkey PRIMARY KEY (co_id);


--
-- Name: exam_questions exam_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_questions
    ADD CONSTRAINT exam_questions_pkey PRIMARY KEY (id);


--
-- Name: exams exams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams
    ADD CONSTRAINT exams_pkey PRIMARY KEY (exam_id);


--
-- Name: marks marks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marks
    ADD CONSTRAINT marks_pkey PRIMARY KEY (id);


--
-- Name: question_co_map question_co_map_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.question_co_map
    ADD CONSTRAINT question_co_map_pkey PRIMARY KEY (question_id, co_id);


--
-- Name: questions questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (question_id);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (student_id);


--
-- Name: students students_roll_no_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_roll_no_key UNIQUE (roll_no);


--
-- Name: subjects subjects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_pkey PRIMARY KEY (subject_id);


--
-- Name: course_outcomes course_outcomes_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.course_outcomes
    ADD CONSTRAINT course_outcomes_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(subject_id) ON DELETE CASCADE;


--
-- Name: exam_questions exam_questions_exam_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_questions
    ADD CONSTRAINT exam_questions_exam_id_fkey FOREIGN KEY (exam_id) REFERENCES public.exams(exam_id) ON DELETE CASCADE;


--
-- Name: exam_questions exam_questions_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exam_questions
    ADD CONSTRAINT exam_questions_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(question_id) ON DELETE CASCADE;


--
-- Name: exams exams_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams
    ADD CONSTRAINT exams_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(subject_id);


--
-- Name: marks marks_exam_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marks
    ADD CONSTRAINT marks_exam_id_fkey FOREIGN KEY (exam_id) REFERENCES public.exams(exam_id) ON DELETE CASCADE;


--
-- Name: marks marks_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marks
    ADD CONSTRAINT marks_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(question_id);


--
-- Name: marks marks_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marks
    ADD CONSTRAINT marks_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(student_id) ON DELETE CASCADE;


--
-- Name: question_co_map question_co_map_co_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.question_co_map
    ADD CONSTRAINT question_co_map_co_id_fkey FOREIGN KEY (co_id) REFERENCES public.course_outcomes(co_id);


--
-- Name: question_co_map question_co_map_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.question_co_map
    ADD CONSTRAINT question_co_map_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(question_id) ON DELETE CASCADE;


--
-- Name: questions questions_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(subject_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict b7BpZIa6KvWthQcmVTBikMotFgv5fe7T6gCtyeWpOYi0mDKni6G8TdaFN94o8iC

