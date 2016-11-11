/*
Created: 1/27/2016
Modified: 1/28/2016
Model: PostgreSQL 9.1
Database: PostgreSQL 9.1
*/

-- Create schemas section -------------------------------------------------



-- Create user data types section -------------------------------------------------


-- Create tables section -------------------------------------------------

-- Table nodes

CREATE TABLE "nodes"(
 "nodeid" UUID NOT NULL,
 "name" Text NOT NULL,
 "description" Text NOT NULL,
 "istopnode" Boolean NOT NULL,
 "crmclass" Text NOT NULL,
 "datatype" Text NOT NULL,
 "validation" Text,
 "label" Text,
 "inputmask" Text,
 "status" Bigint,
 "nodegroupid" UUID,
 "graphid" UUID NOT NULL
)
WITH (OIDS=FALSE)
;

-- Add keys for table nodes

ALTER TABLE "nodes" ADD CONSTRAINT "nodes_pk" PRIMARY KEY ("nodeid")
;

-- Table forms

CREATE TABLE "forms"(
 "formid" UUID NOT NULL,
 "name" Text NOT NULL,
 "title" Text,
 "subtitle" Text
)
WITH (OIDS=FALSE)
;

-- Add keys for table forms

ALTER TABLE "forms" ADD CONSTRAINT "forms_pk" PRIMARY KEY ("formid")
;

-- Table cards

CREATE TABLE "cards"(
 "cardid" UUID NOT NULL,
 "name" Text NOT NULL,
 "htmltemplate" Text NOT NULL,
 "title" Text NOT NULL,
 "subtitle" Text
)
WITH (OIDS=FALSE)
;

-- Add keys for table cards

ALTER TABLE "cards" ADD CONSTRAINT "cards_pk" PRIMARY KEY ("cardid")
;

-- Table cardgroups

CREATE TABLE "cardgroups"(
 "cardgroupid" UUID NOT NULL,
 "name" Text NOT NULL,
 "title" Text NOT NULL,
 "subtitle" Text,
 "nodeid" UUID
)
WITH (OIDS=FALSE)
;

-- Add keys for table cardgroups

ALTER TABLE "cardgroups" ADD CONSTRAINT "cardgroups_pk" PRIMARY KEY ("cardgroupid")
;

-- Table widgets

CREATE TABLE "widgets"(
 "widgetid" UUID NOT NULL,
 "name" Text NOT NULL,
 "component" Text NOT NULL,
 "defaultlabel" Text,
 "defaultmask" Text
)
WITH (OIDS=FALSE)
;

-- Add keys for table widgets

ALTER TABLE "widgets" ADD CONSTRAINT "widgets_pk" PRIMARY KEY ("widgetid")
;

-- Table tileinstances

CREATE TABLE "tileinstances"(
 "tileinstanceid" UUID NOT NULL,
 "resourceinstanceid" UUID NOT NULL,
 "resourceclassid" UUID NOT NULL,
 "cardid" UUID NOT NULL,
 "tileinstancedata" JSONB NOT NULL,
 "parenttileinstanceid" UUID,
 "tilegroupid" UUID NOT NULL
)
WITH (OIDS=FALSE)
;

ALTER TABLE tileinstances DROP COLUMN tileinstancedata;
ALTER TABLE tileinstances ADD COLUMN tileinstancedata jsonb;

-- Add keys for table tileinstances

ALTER TABLE "tileinstances" ADD CONSTRAINT "tileinstances_pk" PRIMARY KEY ("tileinstanceid")
;

-- Table cards_x_cardgroups

CREATE TABLE "cards_x_cardgroups"(
 "cardgroupid" UUID NOT NULL,
 "cardid" UUID NOT NULL,
 "id" Serial NOT NULL
)
WITH (OIDS=FALSE)
;

-- Create indexes for table cards_x_cardgroups

CREATE UNIQUE INDEX "card_x_cardgroups_uk" ON "cards_x_cardgroups" ("cardgroupid","cardid")
;

-- Add keys for table cards_x_cardgroups

ALTER TABLE "cards_x_cardgroups" ADD CONSTRAINT "card_x_cardgroups_pk" PRIMARY KEY ("id")
;

-- Table cards_x_nodes_x_widgets

CREATE TABLE "cards_x_nodes_x_widgets"(
 "nodeid" UUID NOT NULL,
 "cardid" UUID NOT NULL,
 "widgetid" UUID NOT NULL,
 "id" Serial NOT NULL
)
WITH (OIDS=FALSE)
;

-- Create indexes for table cards_x_nodes_x_widgets

CREATE UNIQUE INDEX "cards_x_nodes_x_widgets_uk" ON "cards_x_nodes_x_widgets" ("nodeid","cardid","widgetid")
;

-- Add keys for table cards_x_nodes_x_widgets

ALTER TABLE "cards_x_nodes_x_widgets" ADD CONSTRAINT "card_x_nodes_x_widgets_fk" PRIMARY KEY ("id")
;

-- Table resourceclasses_x_forms

CREATE TABLE "resourceclasses_x_forms"(
 "resourceclassid" UUID,
 "formid" UUID NOT NULL,
 "id" Serial NOT NULL
)
WITH (OIDS=FALSE)
;

-- Create indexes for table resourceclasses_x_forms

CREATE UNIQUE INDEX "resourceclasses_x_forms_uk" ON "resourceclasses_x_forms" ("resourceclassid","formid")
;

-- Add keys for table resourceclasses_x_forms

ALTER TABLE "resourceclasses_x_forms" ADD CONSTRAINT "resourceclasses_x_forms_pk" PRIMARY KEY ("id")
;

-- Table edges

CREATE TABLE "edges"(
 "edgeid" UUID NOT NULL,
 "name" Text NOT NULL,
 "description" Text NOT NULL,
 "crmproperty" Text NOT NULL,
 "domainnodeid" UUID NOT NULL,
 "rangenodeid" UUID NOT NULL,
 "graphid" UUID NOT NULL
)
WITH (OIDS=FALSE)
;

-- Create indexes for table edges

CREATE UNIQUE INDEX "edges_uk" ON "edges" ("rangenodeid","domainnodeid")
;

-- Add keys for table edges

ALTER TABLE "edges" ADD CONSTRAINT "edges_pk" PRIMARY KEY ("edgeid")
;

-- Table forms_x_cards

CREATE TABLE "forms_x_cards"(
 "formid" UUID NOT NULL,
 "cardid" UUID NOT NULL,
 "id" Serial NOT NULL
)
WITH (OIDS=FALSE)
;

-- Create indexes for table forms_x_cards

CREATE UNIQUE INDEX "forms_x_cards_uk" ON "forms_x_cards" ("formid","cardid")
;

-- Add keys for table forms_x_cards

ALTER TABLE "forms_x_cards" ADD CONSTRAINT "forms_x_cards_pk" PRIMARY KEY ("id")
;

-- Table addresses

CREATE TABLE "addresses"(
 "addressnum" Text,
 "addressstreet" Text,
 "vintage" Text,
 "city" Text,
 "postalcode" Text,
 "addressesid" Serial NOT NULL
)
WITH (OIDS=FALSE)
;

SELECT AddGeometryColumn ('public','addresses','geometry',4326,'POINT',2);

-- Create indexes for table addresses

CREATE INDEX "addresses_sidx" ON "addresses" USING gist ("geometry")
;

-- Add keys for table addresses

ALTER TABLE "addresses" ADD CONSTRAINT "addresses_pk" PRIMARY KEY ("addressesid")
;

-- Table overlays

CREATE TABLE "overlays"(
 "overlaytyp" Text,
 "overlayval" Text,
 "overlayid" UUID NOT NULL
)
WITH (OIDS=FALSE)
;
SELECT AddGeometryColumn ('public','overlays','geometry',4326,'POLYGON',2);

-- Create indexes for table overlays

CREATE INDEX "overlays_sidx" ON "overlays" USING gist ("geometry")
;

CREATE INDEX "overlaytype_idx" ON "overlays" ("overlaytyp")
;

CREATE INDEX "overlays_geometry_idx" ON "overlays" USING gist ("geometry")
;

-- Add keys for table overlays

ALTER TABLE "overlays" ADD CONSTRAINT "overlays_pkey" PRIMARY KEY ("overlayid")
;

-- Table parcels

CREATE TABLE "parcels"(
 "parcelapn" Text,
 "vintage" Text,
 "parcelsid" Serial NOT NULL
)
WITH (OIDS=FALSE)
;

SELECT AddGeometryColumn ('public','parcels','geometry',4326,'POLYGON',2);
-- Create indexes for table parcels

CREATE INDEX "parcels_sidx" ON "parcels" USING gist ("geometry")
;

-- Add keys for table parcels

ALTER TABLE "parcels" ADD CONSTRAINT "parcels_pk" PRIMARY KEY ("parcelsid")
;

-- Table concepts

CREATE TABLE "concepts"(
 "conceptid" UUID NOT NULL,
 "nodetype" Text NOT NULL,
 "legacyoid" Text NOT NULL
)
WITH (OIDS=FALSE)
;

-- Add keys for table concepts

ALTER TABLE "concepts" ADD CONSTRAINT "pk_concepts" PRIMARY KEY ("conceptid")
;

ALTER TABLE "concepts" ADD CONSTRAINT "concpets_legacyoid_uk" UNIQUE ("legacyoid")
;

/*
-- Create triggers for table concepts

CREATE TRIGGER "concepts_ins_tgr"
  BEFORE INSERT
  ON "concepts" FOR EACH ROW
 EXECUTE PROCEDURE "concpets_ins"()
;
*/
-- Table d_languages

CREATE TABLE "d_languages"(
 "languageid" Text NOT NULL,
 "languagename" Text NOT NULL,
 "isdefault" Boolean NOT NULL
)
WITH (OIDS=FALSE)
;

-- Add keys for table d_languages

ALTER TABLE "d_languages" ADD CONSTRAINT "pk_d_languages" PRIMARY KEY ("languageid")
;

-- Table d_node_types

CREATE TABLE "d_node_types"(
 "nodetype" Text NOT NULL,
 "namespace" Text DEFAULT 'arches'::text NOT NULL
)
WITH (OIDS=FALSE)
;

-- Add keys for table d_node_types

ALTER TABLE "d_node_types" ADD CONSTRAINT "pk_d_nodetypes" PRIMARY KEY ("nodetype")
;

-- Table d_relationtypes

CREATE TABLE "d_relationtypes"(
 "relationtype" Text NOT NULL,
 "category" Text NOT NULL,
 "namespace" Text DEFAULT 'arches'::text NOT NULL
)
WITH (OIDS=FALSE)
;

-- Add keys for table d_relationtypes

ALTER TABLE "d_relationtypes" ADD CONSTRAINT "pk_d_relationtypes" PRIMARY KEY ("relationtype")
;

-- Table d_valuetypes

CREATE TABLE "d_valuetypes"(
 "valuetype" Text NOT NULL,
 "category" Text,
 "description" Text,
 "namespace" Text DEFAULT 'arches'::text NOT NULL,
 "datatype" Text
)
WITH (OIDS=FALSE)
;

-- Add keys for table d_valuetypes

ALTER TABLE "d_valuetypes" ADD CONSTRAINT "pk_d_valuetypes" PRIMARY KEY ("valuetype")
;

-- Table relations

CREATE TABLE "relations"(
 "conceptidfrom" UUID NOT NULL,
 "conceptidto" UUID NOT NULL,
 "relationtype" Text NOT NULL,
 "relationid" UUID DEFAULT uuid_generate_v1mc() NOT NULL
)
WITH (OIDS=FALSE)
;

-- Add keys for table relations

ALTER TABLE "relations" ADD CONSTRAINT "pk_relations" PRIMARY KEY ("relationid")
;

-- Table values

CREATE TABLE "values"(
 "valueid" UUID DEFAULT uuid_generate_v1mc() NOT NULL,
 "conceptid" UUID NOT NULL,
 "valuetype" Text NOT NULL,
 "value" Text NOT NULL,
 "languageid" Text
)
WITH (OIDS=FALSE)
;

-- Add keys for table values

ALTER TABLE "values" ADD CONSTRAINT "pk_values" PRIMARY KEY ("valueid")
;

-- Table edit_log

CREATE TABLE "edit_log"(
 "editlogid" UUID DEFAULT uuid_generate_v1mc() NOT NULL,
 "resourceclassid" UUID,
 "resourceinstanceid" UUID,
 "attributenodeid" UUID,
 "tileinstanceid" UUID,
 "edittype" Text,
 "newvalue" Text,
 "oldvalue" Text,
 "timestamp" Timestamp with time zone,
 "userid" Text,
 "user_firstname" Text,
 "user_lastname" Text,
 "user_email" Text,
 "note" Text
)
WITH (OIDS=FALSE)
;

-- Add keys for table edit_log

ALTER TABLE "edit_log" ADD CONSTRAINT "pk_edit_log" PRIMARY KEY ("editlogid")
;

-- Table resource2resource_constraints

CREATE TABLE "resource2resource_constraints"(
 "resource2resourceid" UUID NOT NULL,
 "resourceclassfrom" UUID,
 "resourceclassto" UUID
)
WITH (OIDS=FALSE)
;

-- Add keys for table resource2resource_constraints

ALTER TABLE "resource2resource_constraints" ADD CONSTRAINT "resource2resource_constraints_pk" PRIMARY KEY ("resource2resourceid")
;

-- Table resource_x_resource

CREATE TABLE "resource_x_resource"(
 "resourcexid" serial NOT NULL,
 "resourceinstanceidfrom" UUID,
 "resourceinstanceidto" UUID,
 "notes" Text,
 "relationshiptype" UUID NOT NULL,
 "datestarted" Date,
 "dateended" Date
)
WITH (OIDS=FALSE)
;

-- Add keys for table resource_x_resource

ALTER TABLE "resource_x_resource" ADD CONSTRAINT "pk_rsrc_x_rsrc" PRIMARY KEY ("resourcexid")
;

-- Table classes

CREATE TABLE "classes"(
 "classid" Text NOT NULL,
 "classname" Text NOT NULL,
 "isactive" Boolean DEFAULT true NOT NULL
)
WITH (OIDS=FALSE)
;

-- Add keys for table classes

ALTER TABLE "classes" ADD CONSTRAINT "pk_classes" PRIMARY KEY ("classid")
;

-- Table properties

CREATE TABLE "properties"(
 "propertyid" Text NOT NULL,
 "classdomain" Text NOT NULL,
 "classrange" Text NOT NULL,
 "propertydisplay" Text
)
WITH (OIDS=FALSE)
;

-- Add keys for table properties

ALTER TABLE "properties" ADD CONSTRAINT "pk_propertyid" PRIMARY KEY ("propertyid")
;

-- Table public.auth_group

CREATE TABLE "public"."auth_group"(
 "id" serial NOT NULL,
 "name" Character varying(80) NOT NULL
)
WITH (OIDS=FALSE)
;

-- Add keys for table public.auth_group

ALTER TABLE "public"."auth_group" ADD CONSTRAINT "auth_group_pkey" PRIMARY KEY ("id")
;

ALTER TABLE "public"."auth_group" ADD CONSTRAINT "auth_group_name_key" UNIQUE ("name")
;

-- Table public.auth_group_permissions

CREATE TABLE "public"."auth_group_permissions"(
 "id"  serial NOT NULL,
 "group_id" Integer NOT NULL,
 "permission_id" Integer NOT NULL
)
WITH (OIDS=FALSE)
;

-- Create indexes for table public.auth_group_permissions

CREATE INDEX "auth_group_permissions_group_id" ON "public"."auth_group_permissions" ("group_id")
;

CREATE INDEX "auth_group_permissions_permission_id" ON "public"."auth_group_permissions" ("permission_id")
;

-- Add keys for table public.auth_group_permissions

ALTER TABLE "public"."auth_group_permissions" ADD CONSTRAINT "auth_group_permissions_pkey" PRIMARY KEY ("id")
;

ALTER TABLE "public"."auth_group_permissions" ADD CONSTRAINT "auth_group_permissions_group_id_permission_id_key" UNIQUE ("group_id","permission_id")
;

-- Table public.auth_message

CREATE TABLE "public"."auth_message"(
 "id"  serial NOT NULL,
 "user_id" Integer NOT NULL,
 "message" Text NOT NULL
)
WITH (OIDS=FALSE)
;

-- Create indexes for table public.auth_message

CREATE INDEX "auth_message_user_id" ON "public"."auth_message" ("user_id")
;

-- Add keys for table public.auth_message

ALTER TABLE "public"."auth_message" ADD CONSTRAINT "auth_message_pkey" PRIMARY KEY ("id")
;

-- Table public.auth_permission

CREATE TABLE "public"."auth_permission"(
 "id" serial NOT NULL,
 "name" Text NOT NULL,
 "content_type_id" Integer NOT NULL,
 "codename" Text NOT NULL
)
WITH (OIDS=FALSE)
;

-- Create indexes for table public.auth_permission

CREATE INDEX "auth_permission_content_type_id" ON "public"."auth_permission" ("content_type_id")
;

-- Add keys for table public.auth_permission

ALTER TABLE "public"."auth_permission" ADD CONSTRAINT "auth_permission_pkey" PRIMARY KEY ("id")
;

ALTER TABLE "public"."auth_permission" ADD CONSTRAINT "auth_permission_content_type_id_codename_key" UNIQUE ("content_type_id","codename")
;

-- Table public.auth_user

CREATE TABLE "public"."auth_user"(
 "id" serial NOT NULL,
 "username" Character varying(30) NOT NULL,
 "first_name" Character varying(30) NOT NULL,
 "last_name" Character varying(30) NOT NULL,
 "email" Character varying(75) NOT NULL,
 "password" Character varying(128) NOT NULL,
 "is_staff" Boolean NOT NULL,
 "is_active" Boolean NOT NULL,
 "is_superuser" Boolean NOT NULL,
 "last_login" Timestamp with time zone NOT NULL,
 "date_joined" Timestamp with time zone NOT NULL
)
WITH (OIDS=FALSE)
;

-- Add keys for table public.auth_user

ALTER TABLE "public"."auth_user" ADD CONSTRAINT "auth_user_pkey" PRIMARY KEY ("id")
;

ALTER TABLE "public"."auth_user" ADD CONSTRAINT "auth_user_username_key" UNIQUE ("username")
;

-- Table public.auth_user_groups

CREATE TABLE "public"."auth_user_groups"(
 "id" serial NOT NULL,
 "user_id" Integer NOT NULL,
 "group_id" Integer NOT NULL
)
WITH (OIDS=FALSE)
;

-- Create indexes for table public.auth_user_groups

CREATE INDEX "auth_user_groups_group_id" ON "public"."auth_user_groups" ("group_id")
;

CREATE INDEX "auth_user_groups_user_id" ON "public"."auth_user_groups" ("user_id")
;

-- Add keys for table public.auth_user_groups

ALTER TABLE "public"."auth_user_groups" ADD CONSTRAINT "auth_user_groups_pkey" PRIMARY KEY ("id")
;

ALTER TABLE "public"."auth_user_groups" ADD CONSTRAINT "auth_user_groups_user_id_group_id_key" UNIQUE ("user_id","group_id")
;

-- Table public.auth_user_user_permissions

CREATE TABLE "public"."auth_user_user_permissions"(
 "id" serial NOT NULL,
 "user_id" Integer NOT NULL,
 "permission_id" Integer NOT NULL
)
WITH (OIDS=FALSE)
;

-- Create indexes for table public.auth_user_user_permissions

CREATE INDEX "auth_user_user_permissions_permission_id" ON "public"."auth_user_user_permissions" ("permission_id")
;

CREATE INDEX "auth_user_user_permissions_user_id" ON "public"."auth_user_user_permissions" ("user_id")
;

-- Add keys for table public.auth_user_user_permissions

ALTER TABLE "public"."auth_user_user_permissions" ADD CONSTRAINT "auth_user_user_permissions_pkey" PRIMARY KEY ("id")
;

ALTER TABLE "public"."auth_user_user_permissions" ADD CONSTRAINT "auth_user_user_permissions_user_id_permission_id_key" UNIQUE ("user_id","permission_id")
;

-- Table public.django_admin_log

CREATE TABLE "public"."django_admin_log"(
 "id"  serial NOT NULL,
 "action_time" Timestamp with time zone NOT NULL,
 "user_id" Integer NOT NULL,
 "content_type_id" Integer,
 "object_id" Text,
 "object_repr" Character varying(200) NOT NULL,
 "action_flag" Smallint NOT NULL
        CONSTRAINT "django_admin_log_action_flag_check" CHECK (action_flag >= 0),
 "change_message" Text NOT NULL
)
WITH (OIDS=FALSE)
;

-- Create indexes for table public.django_admin_log

CREATE INDEX "django_admin_log_content_type_id" ON "public"."django_admin_log" ("content_type_id")
;

CREATE INDEX "django_admin_log_user_id" ON "public"."django_admin_log" ("user_id")
;

-- Add keys for table public.django_admin_log

ALTER TABLE "public"."django_admin_log" ADD CONSTRAINT "django_admin_log_pkey" PRIMARY KEY ("id")
;

-- Table public.django_content_type

CREATE TABLE "public"."django_content_type"(
 "id" serial NOT NULL,
 "name" Character varying(100) NOT NULL,
 "app_label" Character varying(100) NOT NULL,
 "model" Character varying(100) NOT NULL
)
WITH (OIDS=FALSE)
;

-- Add keys for table public.django_content_type

ALTER TABLE "public"."django_content_type" ADD CONSTRAINT "django_content_type_pkey" PRIMARY KEY ("id")
;

ALTER TABLE "public"."django_content_type" ADD CONSTRAINT "django_content_type_app_label_model_key" UNIQUE ("app_label","model")
;

-- Table public.django_session

CREATE TABLE "public"."django_session"(
 "session_key" Character varying(40) NOT NULL,
 "session_data" Text NOT NULL,
 "expire_date" Timestamp with time zone NOT NULL
)
WITH (OIDS=FALSE)
;

-- Create indexes for table public.django_session

CREATE INDEX "django_session_expire_date" ON "public"."django_session" ("expire_date")
;

-- Add keys for table public.django_session

ALTER TABLE "public"."django_session" ADD CONSTRAINT "django_session_pkey" PRIMARY KEY ("session_key")
;

-- Table public.django_site

CREATE TABLE "public"."django_site"(
 "id" serial NOT NULL,
 "domain" Character varying(100) NOT NULL,
 "name" Character varying(50) NOT NULL
)
WITH (OIDS=FALSE)
;

-- Add keys for table public.django_site

ALTER TABLE "public"."django_site" ADD CONSTRAINT "django_site_pkey" PRIMARY KEY ("id")
;

-- Table nodegroups

CREATE TABLE "nodegroups"(
 "nodegroupid" UUID NOT NULL,
 "cardinality" Text NOT NULL,
 "legacygroupid" Text
)
WITH (OIDS=FALSE)
;

COMMENT ON TABLE "nodegroups" IS '0:1
0:M
1:1
1:M'
;

-- Add keys for table nodegroups

ALTER TABLE "nodegroups" ADD CONSTRAINT "nodegroups_pk" PRIMARY KEY ("nodegroupid")
;

-- Table graph

CREATE TABLE "graph"(
 "graphid" UUID NOT NULL,
 "name" Bigint,
 "deploymentfile" Text,
 "author" Text,
 "deploymentdate" Timestamp,
 "version" Text,
 "isresource" Boolean NOT NULL,
 "isactive" Boolean NOT NULL,
 "iconclass" Text,
 "subtitle" Text
)
WITH (OIDS=FALSE)
;

-- Add keys for table graph

ALTER TABLE "graph" ADD CONSTRAINT "deploymentmetadata_pk" PRIMARY KEY ("graphid")
;

-- Table resourceinstances

CREATE TABLE "resourceinstances"(
 "resourceinstanceid" UUID NOT NULL,
 "col1" Text
)
WITH (OIDS=FALSE)
;

-- Add keys for table resourceinstances

ALTER TABLE "resourceinstances" ADD CONSTRAINT "resourceinstances_pk" PRIMARY KEY ("resourceinstanceid")
;

-- Table validations
CREATE TABLE "validations"(
 "validationid" UUID NOT NULL,
 "validation" Text,
 "validationtype" Text,
 "name" Text,
 "description" Text
)
WITH (OIDS=FALSE)
;

-- Add keys for table validations

ALTER TABLE "validations" ADD CONSTRAINT "validations_pk" PRIMARY KEY ("validationid")
;

-- Table validations

CREATE TABLE "validations_x_nodes"(
 "id" serial NOT NULL,
 "validationid" UUID NOT NULL,
 "nodeid" UUID NOT NULL
)
WITH (OIDS=FALSE)
;

-- Add keys for table validations

ALTER TABLE "validations_x_nodes" ADD CONSTRAINT "validations_x_nodes_pk" PRIMARY KEY ("id")
;

-- Table icons

CREATE TABLE "icons"(
 "id" serial NOT NULL,
 "name" Text,
 "cssclass" Text
)
WITH (OIDS=FALSE)
;

-- Add keys for table icons

ALTER TABLE "icons" ADD CONSTRAINT "icons_pk" PRIMARY KEY ("id")
;

-- Create relationships section -------------------------------------------------

ALTER TABLE "cardgroups" ADD CONSTRAINT "nodes_cardgroups_fk" FOREIGN KEY ("nodeid") REFERENCES "nodes" ("nodeid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "tileinstances" ADD CONSTRAINT "nodes_tilesinstances_fk" FOREIGN KEY ("resourceclassid") REFERENCES "nodes" ("nodeid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "tileinstances" ADD CONSTRAINT "cards_tileinstances_fk" FOREIGN KEY ("cardid") REFERENCES "cards" ("cardid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "tileinstances" ADD CONSTRAINT "tileinstance_parenttileinstance_rfk" FOREIGN KEY ("parenttileinstanceid") REFERENCES "tileinstances" ("tileinstanceid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "cards_x_cardgroups" ADD CONSTRAINT "cards_cards_x_cardgroups_fk" FOREIGN KEY ("cardid") REFERENCES "cards" ("cardid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "cards_x_cardgroups" ADD CONSTRAINT "cardgroups_cards_x_cardgroups_fk" FOREIGN KEY ("cardgroupid") REFERENCES "cardgroups" ("cardgroupid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "cards_x_nodes_x_widgets" ADD CONSTRAINT "cards_cards_x_nodes_x_widgets_fk" FOREIGN KEY ("cardid") REFERENCES "cards" ("cardid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "cards_x_nodes_x_widgets" ADD CONSTRAINT "nodes_cards_x_nodes_x_widgets_fk" FOREIGN KEY ("nodeid") REFERENCES "nodes" ("nodeid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "cards_x_nodes_x_widgets" ADD CONSTRAINT "widgets_cards_x_nodes_x_widgets_fk" FOREIGN KEY ("widgetid") REFERENCES "widgets" ("widgetid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "resourceclasses_x_forms" ADD CONSTRAINT "forms_resourceclasses_x_forms_fk" FOREIGN KEY ("formid") REFERENCES "forms" ("formid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "resourceclasses_x_forms" ADD CONSTRAINT "nodes_resoruceclasses_x_forms_fk" FOREIGN KEY ("resourceclassid") REFERENCES "nodes" ("nodeid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "edges" ADD CONSTRAINT "nodes_edges_fk1" FOREIGN KEY ("domainnodeid") REFERENCES "nodes" ("nodeid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "edges" ADD CONSTRAINT "nodes_edges_fk2" FOREIGN KEY ("rangenodeid") REFERENCES "nodes" ("nodeid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "forms_x_cards" ADD CONSTRAINT "cards_cards_x_forms_fk" FOREIGN KEY ("cardid") REFERENCES "cards" ("cardid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "forms_x_cards" ADD CONSTRAINT "forms_forms_x_cards_fk" FOREIGN KEY ("formid") REFERENCES "forms" ("formid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "concepts" ADD CONSTRAINT "fk_concepts_x_nodetypes" FOREIGN KEY ("nodetype") REFERENCES "d_node_types" ("nodetype") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "relations" ADD CONSTRAINT "fk_relations_x_d_relationtypes" FOREIGN KEY ("relationtype") REFERENCES "d_relationtypes" ("relationtype") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "relations" ADD CONSTRAINT "fk_conceptsfrom_x_relations" FOREIGN KEY ("conceptidfrom") REFERENCES "concepts" ("conceptid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "relations" ADD CONSTRAINT "fk_conceptsto_x_relations" FOREIGN KEY ("conceptidto") REFERENCES "concepts" ("conceptid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "values" ADD CONSTRAINT "fk_concepts_x_values" FOREIGN KEY ("conceptid") REFERENCES "concepts" ("conceptid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "values" ADD CONSTRAINT "fk_d_languages_values" FOREIGN KEY ("languageid") REFERENCES "d_languages" ("languageid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "values" ADD CONSTRAINT "fk_valuetype_d_valuetype" FOREIGN KEY ("valuetype") REFERENCES "d_valuetypes" ("valuetype") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "resource_x_resource" ADD CONSTRAINT "value_x_rsrc_x_rsrc" FOREIGN KEY ("relationshiptype") REFERENCES "values" ("valueid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "properties" ADD CONSTRAINT "fk_classes_properties_classdomain" FOREIGN KEY ("classdomain") REFERENCES "classes" ("classid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "properties" ADD CONSTRAINT "fk_classes_properties_classrange" FOREIGN KEY ("classrange") REFERENCES "classes" ("classid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "public"."auth_group_permissions" ADD CONSTRAINT "group_id_refs_id_3cea63fe" FOREIGN KEY ("group_id") REFERENCES "public"."auth_group" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED
;

ALTER TABLE "public"."auth_group_permissions" ADD CONSTRAINT "auth_group_permissions_permission_id_fkey" FOREIGN KEY ("permission_id") REFERENCES "public"."auth_permission" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED
;

ALTER TABLE "public"."auth_message" ADD CONSTRAINT "auth_message_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED
;

ALTER TABLE "public"."auth_user_groups" ADD CONSTRAINT "user_id_refs_id_7ceef80f" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED
;

ALTER TABLE "public"."auth_user_groups" ADD CONSTRAINT "auth_user_groups_group_id_fkey" FOREIGN KEY ("group_id") REFERENCES "public"."auth_group" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED
;

ALTER TABLE "public"."auth_user_user_permissions" ADD CONSTRAINT "user_id_refs_id_dfbab7d" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED
;

ALTER TABLE "public"."auth_user_user_permissions" ADD CONSTRAINT "auth_user_user_permissions_permission_id_fkey" FOREIGN KEY ("permission_id") REFERENCES "public"."auth_permission" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED
;

ALTER TABLE "public"."auth_permission" ADD CONSTRAINT "content_type_id_refs_id_728de91f" FOREIGN KEY ("content_type_id") REFERENCES "public"."django_content_type" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED
;

ALTER TABLE "nodes" ADD CONSTRAINT "nodegroups_x_nodes_fk" FOREIGN KEY ("nodegroupid") REFERENCES "nodegroups" ("nodegroupid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "nodes" ADD CONSTRAINT "deploymentmetadata_x_nodes_fk" FOREIGN KEY ("graphid") REFERENCES "graph" ("graphid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "tileinstances" ADD CONSTRAINT "resourceinstances_tileinstances_fk" FOREIGN KEY ("resourceinstanceid") REFERENCES "resourceinstances" ("resourceinstanceid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "resource_x_resource" ADD CONSTRAINT "resourceinstances_resrc_x_rsrc_fk1" FOREIGN KEY ("resourceinstanceidfrom") REFERENCES "resourceinstances" ("resourceinstanceid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "resource_x_resource" ADD CONSTRAINT "resourceinstances_resrc_x_rsrc_fk2" FOREIGN KEY ("resourceinstanceidto") REFERENCES "resourceinstances" ("resourceinstanceid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "resource2resource_constraints" ADD CONSTRAINT "nodes_rscr2rsrc_constraints_fk1" FOREIGN KEY ("resourceclassfrom") REFERENCES "nodes" ("nodeid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "resource2resource_constraints" ADD CONSTRAINT "nodes_rscr2rsrc_constraints_fk2" FOREIGN KEY ("resourceclassto") REFERENCES "nodes" ("nodeid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "edges" ADD CONSTRAINT "graph_edges_fk" FOREIGN KEY ("graphid") REFERENCES "graph" ("graphid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "validations_x_nodes" ADD CONSTRAINT "nodes_validations_x_nodes_fk" FOREIGN KEY ("nodeid") REFERENCES "nodes" ("nodeid") ON DELETE NO ACTION ON UPDATE NO ACTION
;

ALTER TABLE "validations_x_nodes" ADD CONSTRAINT "validations_validations_x_nodes_fk" FOREIGN KEY ("validationid") REFERENCES "validations" ("validationid") ON DELETE NO ACTION ON UPDATE NO ACTION
;
