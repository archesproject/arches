-- Table: data.uniqueids

-- DROP TABLE data.uniqueids;

CREATE TABLE data.uniqueids
(
  entityid uuid NOT NULL,
  val text,
  id_type text,
  order_date timestamp without time zone,
  CONSTRAINT pk_uniqueids PRIMARY KEY (entityid),
  CONSTRAINT fk_entities_uniqueids FOREIGN KEY (entityid)
      REFERENCES data.entities (entityid) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data.uniqueids
  OWNER TO postgres;
