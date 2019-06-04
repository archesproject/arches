SELECT pg_terminate_backend(pid) from pg_stat_activity where datname='consultations_prj';

DROP DATABASE IF EXISTS consultations_prj;

CREATE DATABASE consultations_prj
  WITH ENCODING='UTF8'
       CONNECTION LIMIT=-1;
