--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.1
-- Dumped by pg_dump version 9.5.1

-- Started on 2016-05-09 13:31:44 PDT

-- SET statement_timeout = 0;
-- SET lock_timeout = 0;
-- SET client_encoding = 'UTF8';
-- SET standard_conforming_strings = on;
-- SET check_function_bodies = false;
-- SET client_min_messages = warning;
-- SET row_security = off;

-- SET search_path = public, pg_catalog;

--
-- TOC entry 3855 (class 0 OID 491493)
-- Dependencies: 221
-- Data for Name: concepts; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO concepts VALUES ('c03db431-4564-34eb-ba86-4c8169e4276c', 'E1_CRM_Entity', 'Concept');
INSERT INTO concepts VALUES ('70064b58-4490-3d09-b463-fd18defae21f', 'E2_Temporal_Entity', 'Concept');
INSERT INTO concepts VALUES ('12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'E3_Condition_State', 'Concept');
INSERT INTO concepts VALUES ('0cc20557-978d-31ae-bee8-b3939398b1c8', 'E4_Period', 'Concept');
INSERT INTO concepts VALUES ('a6ef9479-248e-3847-bf68-9c9017b0add8', 'E5_Event', 'Concept');
INSERT INTO concepts VALUES ('94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'E6_Destruction', 'Concept');
INSERT INTO concepts VALUES ('6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'E7_Activity', 'Concept');
INSERT INTO concepts VALUES ('d0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'E8_Acquisition', 'Concept');
INSERT INTO concepts VALUES ('8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'E9_Move', 'Concept');
INSERT INTO concepts VALUES ('2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'E10_Transfer_of_Custody', 'Concept');
INSERT INTO concepts VALUES ('ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'E11_Modification', 'Concept');
INSERT INTO concepts VALUES ('f27afcc0-7657-3c5e-8314-b913c562759e', 'E12_Production', 'Concept');
INSERT INTO concepts VALUES ('fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'E13_Attribute_Assignment', 'Concept');
INSERT INTO concepts VALUES ('c411cc1b-d477-3619-a63b-d1566635ead7', 'E14_Condition_Assessment', 'Concept');
INSERT INTO concepts VALUES ('09c85414-85f5-336b-87e7-9e3f1a14faeb', 'E15_Identifier_Assignment', 'Concept');
INSERT INTO concepts VALUES ('a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'E16_Measurement', 'Concept');
INSERT INTO concepts VALUES ('d4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'E17_Type_Assignment', 'Concept');
INSERT INTO concepts VALUES ('4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'E18_Physical_Thing', 'Concept');
INSERT INTO concepts VALUES ('3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'E19_Physical_Object', 'Concept');
INSERT INTO concepts VALUES ('2c287084-c289-36b2-8328-853e381f0ed4', 'E20_Biological_Object', 'Concept');
INSERT INTO concepts VALUES ('9ff08a71-8094-35ed-9005-d94abddefdfe', 'E21_Person', 'Concept');
INSERT INTO concepts VALUES ('fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'E22_Man-Made_Object', 'Concept');
INSERT INTO concepts VALUES ('a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'E24_Physical_Man-Made_Thing', 'Concept');
INSERT INTO concepts VALUES ('4bb246c3-e51e-32f9-a466-3003a17493c5', 'E25_Man-Made_Feature', 'Concept');
INSERT INTO concepts VALUES ('2bc61bb4-384d-3427-bc89-2320be9896f2', 'E26_Physical_Feature', 'Concept');
INSERT INTO concepts VALUES ('a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'E27_Site', 'Concept');
INSERT INTO concepts VALUES ('0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'E28_Conceptual_Object', 'Concept');
INSERT INTO concepts VALUES ('3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'E29_Design_or_Procedure', 'Concept');
INSERT INTO concepts VALUES ('e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'E30_Right', 'Concept');
INSERT INTO concepts VALUES ('84a17c0c-78f2-3607-ba85-da1fc47def5a', 'E31_Document', 'Concept');
INSERT INTO concepts VALUES ('0df9cb10-1203-3efd-8d9e-448f5b02506b', 'E32_Authority_Document', 'Concept');
INSERT INTO concepts VALUES ('fa1b039d-00cd-36e8-b03c-247176a6368d', 'E33_Linguistic_Object', 'Concept');
INSERT INTO concepts VALUES ('21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'E34_Inscription', 'Concept');
INSERT INTO concepts VALUES ('48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'E35_Title', 'Concept');
INSERT INTO concepts VALUES ('675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'E36_Visual_Item', 'Concept');
INSERT INTO concepts VALUES ('7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'E37_Mark', 'Concept');
INSERT INTO concepts VALUES ('9cc69985-2a19-3fa6-abf5-addf02a52b90', 'E38_Image', 'Concept');
INSERT INTO concepts VALUES ('af051b0a-be2f-39da-8f46-429a714e242c', 'E39_Actor', 'Concept');
INSERT INTO concepts VALUES ('40a8beed-541b-35cd-b287-b7c345f998fe', 'E40_Legal_Body', 'Concept');
INSERT INTO concepts VALUES ('b43d4537-6674-37cb-af6e-834b5d63c978', 'E41_Appellation', 'Concept');
INSERT INTO concepts VALUES ('fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'E42_Identifier', 'Concept');
INSERT INTO concepts VALUES ('19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'E44_Place_Appellation', 'Concept');
INSERT INTO concepts VALUES ('ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'E45_Address', 'Concept');
INSERT INTO concepts VALUES ('4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'E46_Section_Definition', 'Concept');
INSERT INTO concepts VALUES ('35bfed01-08dc-34b9-94a0-42facd1291ac', 'E47_Spatial_Coordinates', 'Concept');
INSERT INTO concepts VALUES ('e276711d-008c-3380-934b-e048a6a0d665', 'E48_Place_Name', 'Concept');
INSERT INTO concepts VALUES ('9ca9a75f-0eca-378a-a095-91574ad77a30', 'E49_Time_Appellation', 'Concept');
INSERT INTO concepts VALUES ('c8b36269-f507-32fc-8624-2a9404390719', 'E50_Date', 'Concept');
INSERT INTO concepts VALUES ('7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'E51_Contact_Point', 'Concept');
INSERT INTO concepts VALUES ('9d55628a-0085-3b88-a939-b7a327263f53', 'E52_Time-Span', 'Concept');
INSERT INTO concepts VALUES ('12f08da7-e25c-3e10-8179-62ed76da5da0', 'E53_Place', 'Concept');
INSERT INTO concepts VALUES ('bdf5f93e-589c-3c63-baad-e108520c4072', 'E54_Dimension', 'Concept');
INSERT INTO concepts VALUES ('a8f7cd0b-8771-3b91-a827-422ff7a15250', 'E55_Type', 'Concept');
INSERT INTO concepts VALUES ('4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'E56_Language', 'Concept');
INSERT INTO concepts VALUES ('15afdb47-2e96-3076-8a28-ec86a8fe4674', 'E57_Material', 'Concept');
INSERT INTO concepts VALUES ('c1f0e36c-770f-30f9-8241-30d44921c6c8', 'E58_Measurement_Unit', 'Concept');
INSERT INTO concepts VALUES ('8471e471-3045-3269-a9b8-86d0e6065176', 'E59_Primitive_Value', 'Concept');
INSERT INTO concepts VALUES ('30c58f1c-03f4-36f8-9f50-4fefc84bb0a6', 'E60_Number', 'Concept');
INSERT INTO concepts VALUES ('fd8302b4-921b-300c-a9bf-c50d92418797', 'E61_Time_Primitive', 'Concept');
INSERT INTO concepts VALUES ('6e30fbe8-5a0d-3de8-be79-4ec6ebf4db39', 'E62_String', 'Concept');
INSERT INTO concepts VALUES ('255bba42-8ffb-3796-9caa-807179a20d9a', 'E63_Beginning_of_Existence', 'Concept');
INSERT INTO concepts VALUES ('064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'E64_End_of_Existence', 'Concept');
INSERT INTO concepts VALUES ('ec30d38a-0102-3a93-a31a-d596fb6def0b', 'E65_Creation', 'Concept');
INSERT INTO concepts VALUES ('5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'E66_Formation', 'Concept');
INSERT INTO concepts VALUES ('07fcf604-d28f-3993-90fa-d301c4004913', 'E67_Birth', 'Concept');
INSERT INTO concepts VALUES ('8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'E68_Dissolution', 'Concept');
INSERT INTO concepts VALUES ('725afd13-ebc5-38a8-815b-d3a1e5510698', 'E69_Death', 'Concept');
INSERT INTO concepts VALUES ('8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'E70_Thing', 'Concept');
INSERT INTO concepts VALUES ('558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'E71_Man-Made_Thing', 'Concept');
INSERT INTO concepts VALUES ('78b224a2-9271-3716-8c2e-c82302cdae9c', 'E72_Legal_Object', 'Concept');
INSERT INTO concepts VALUES ('31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'E73_Information_Object', 'Concept');
INSERT INTO concepts VALUES ('211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'E74_Group', 'Concept');
INSERT INTO concepts VALUES ('ae27d5a7-abfc-32e3-9927-99795abc53a4', 'E75_Conceptual_Object_Appellation', 'Concept');
INSERT INTO concepts VALUES ('af1d24cc-428c-3689-bbd1-726d62ec5595', 'E77_Persistent_Item', 'Concept');
INSERT INTO concepts VALUES ('a9888169-3160-3403-a8a2-3fa260b1ad16', 'E78_Collection', 'Concept');
INSERT INTO concepts VALUES ('048fe43e-349a-3dda-9524-7046dcbf7287', 'E79_Part_Addition', 'Concept');
INSERT INTO concepts VALUES ('92a38250-9b25-3bc0-881b-89e778c0ac43', 'E80_Part_Removal', 'Concept');
INSERT INTO concepts VALUES ('32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'E81_Transformation', 'Concept');
INSERT INTO concepts VALUES ('6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'E82_Actor_Appellation', 'Concept');
INSERT INTO concepts VALUES ('70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'E83_Type_Creation', 'Concept');
INSERT INTO concepts VALUES ('b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'E84_Information_Carrier', 'Concept');
INSERT INTO concepts VALUES ('b4f509a5-bf1f-3b1b-875f-e4dade14f862', 'E85_Joining', 'Concept');
INSERT INTO concepts VALUES ('2c5fbf8d-b6ca-39f4-8ee7-5522732fe77e', 'E86_Leaving', 'Concept');
INSERT INTO concepts VALUES ('de74c0db-a5fa-3f45-8684-344c379e6b0d', 'E87_Curation_Activity', 'Concept');
INSERT INTO concepts VALUES ('18a02c1c-38df-3f50-baf5-fc0b5bf2732d', 'E89_Propositional_Object', 'Concept');
INSERT INTO concepts VALUES ('5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'E90_Symbolic_Object', 'Concept');
INSERT INTO concepts VALUES ('94ffd715-18f7-310a-bee2-010d800be058', 'E92_Spacetime_Volume', 'Concept');
INSERT INTO concepts VALUES ('b9af2b98-3c9d-34f1-9a87-f5eb071fb53d', 'E93_Presence', 'Concept');
INSERT INTO concepts VALUES ('1036c7f1-ea95-3ad8-886f-849ca10f9584', 'E94_Space', 'Concept');
INSERT INTO concepts VALUES ('9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'P1_is_identified_by', 'Concept');
INSERT INTO concepts VALUES ('2f8fd82d-2679-3d69-b697-7efe545e76ab', 'P2_has_type', 'Concept');
INSERT INTO concepts VALUES ('fd06e07d-057b-38aa-99ac-1add45f9f217', 'P3_has_note', 'Concept');
INSERT INTO concepts VALUES ('fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'P4_has_time-span', 'Concept');
INSERT INTO concepts VALUES ('e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'P5_consists_of', 'Concept');
INSERT INTO concepts VALUES ('d2a09554-6718-3230-8f6f-10ff2daab9b3', 'P7_took_place_at', 'Concept');
INSERT INTO concepts VALUES ('9f10aa95-ba46-3601-bac2-3ea828c154e6', 'P8_took_place_on_or_within', 'Concept');
INSERT INTO concepts VALUES ('6909b643-03f7-3606-b276-2be0e8773207', 'P9_consists_of', 'Concept');
INSERT INTO concepts VALUES ('b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'P10_falls_within', 'Concept');
INSERT INTO concepts VALUES ('338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'P11_had_participant', 'Concept');
INSERT INTO concepts VALUES ('99e8de0f-fa06-381d-8406-9d467d3f96b5', 'P12_occurred_in_the_presence_of', 'Concept');
INSERT INTO concepts VALUES ('0d61e94e-8834-3ba5-b51b-d55951a84fae', 'P13_destroyed', 'Concept');
INSERT INTO concepts VALUES ('f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'P14_carried_out_by', 'Concept');
INSERT INTO concepts VALUES ('b9ec13a4-02ec-39f2-892d-970762c3f25d', 'P15_was_influenced_by', 'Concept');
INSERT INTO concepts VALUES ('b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'P16_used_specific_object', 'Concept');
INSERT INTO concepts VALUES ('2e24daa3-5793-30a8-a96e-3710c3862af4', 'P17_was_motivated_by', 'Concept');
INSERT INTO concepts VALUES ('8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'P19_was_intended_use_of', 'Concept');
INSERT INTO concepts VALUES ('50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'P20_had_specific_purpose', 'Concept');
INSERT INTO concepts VALUES ('9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'P21_had_general_purpose', 'Concept');
INSERT INTO concepts VALUES ('5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'P22_transferred_title_to', 'Concept');
INSERT INTO concepts VALUES ('345681a7-8324-331c-94d4-1777c36538b5', 'P23_transferred_title_from', 'Concept');
INSERT INTO concepts VALUES ('3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'P24_transferred_title_of', 'Concept');
INSERT INTO concepts VALUES ('f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'P25_moved', 'Concept');
INSERT INTO concepts VALUES ('fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'P26_moved_to', 'Concept');
INSERT INTO concepts VALUES ('e94e9966-e05b-3b5a-a5f0-893166474b80', 'P27_moved_from', 'Concept');
INSERT INTO concepts VALUES ('aad29816-af79-36cf-919e-80980f7c41a3', 'P28_custody_surrendered_by', 'Concept');
INSERT INTO concepts VALUES ('8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'P29_custody_received_by', 'Concept');
INSERT INTO concepts VALUES ('f24070b3-fc3b-3838-8765-87350b40ba84', 'P30_transferred_custody_of', 'Concept');
INSERT INTO concepts VALUES ('439f0684-5ebc-3227-93a5-ae9ebca7e015', 'P31_has_modified', 'Concept');
INSERT INTO concepts VALUES ('1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'P32_used_general_technique', 'Concept');
INSERT INTO concepts VALUES ('f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'P33_used_specific_technique', 'Concept');
INSERT INTO concepts VALUES ('d9f02df8-6676-371e-8114-1f37700639b5', 'P34_concerned', 'Concept');
INSERT INTO concepts VALUES ('79183fdd-7275-32a2-a48d-bb70fe683efd', 'P35_has_identified', 'Concept');
INSERT INTO concepts VALUES ('d35815f0-0426-3ac0-b396-7ce2959ebf77', 'P37_assigned', 'Concept');
INSERT INTO concepts VALUES ('caf4c608-3653-397c-a26e-6cc5135274f8', 'P38_deassigned', 'Concept');
INSERT INTO concepts VALUES ('736d6bff-30b8-34d9-aeb7-24f012968ecc', 'P39_measured', 'Concept');
INSERT INTO concepts VALUES ('5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'P40_observed_dimension', 'Concept');
INSERT INTO concepts VALUES ('8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'P41_classified', 'Concept');
INSERT INTO concepts VALUES ('f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'P42_assigned', 'Concept');
INSERT INTO concepts VALUES ('167c0167-35fd-3c57-b90e-20715fd2c200', 'P43_has_dimension', 'Concept');
INSERT INTO concepts VALUES ('ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'P44_has_condition', 'Concept');
INSERT INTO concepts VALUES ('c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'P45_consists_of', 'Concept');
INSERT INTO concepts VALUES ('e37e8cfe-e1b7-3335-818b-d56090f2974e', 'P46_is_composed_of', 'Concept');
INSERT INTO concepts VALUES ('356c8ba7-0114-32c3-861f-8432bc46e963', 'P48_has_preferred_identifier', 'Concept');
INSERT INTO concepts VALUES ('7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'P49_has_former_or_current_keeper', 'Concept');
INSERT INTO concepts VALUES ('2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'P50_has_current_keeper', 'Concept');
INSERT INTO concepts VALUES ('6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'P51_has_former_or_current_owner', 'Concept');
INSERT INTO concepts VALUES ('954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'P52_has_current_owner', 'Concept');
INSERT INTO concepts VALUES ('a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'P53_has_former_or_current_location', 'Concept');
INSERT INTO concepts VALUES ('e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'P54_has_current_permanent_location', 'Concept');
INSERT INTO concepts VALUES ('f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'P55_has_current_location', 'Concept');
INSERT INTO concepts VALUES ('e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'P56_bears_feature', 'Concept');
INSERT INTO concepts VALUES ('5afb86ba-c943-367b-857c-d7aaec92b5e3', 'P57_has_number_of_parts', 'Concept');
INSERT INTO concepts VALUES ('89cad4c1-914c-3675-9d66-83eed1c61e3e', 'P58_has_section_definition', 'Concept');
INSERT INTO concepts VALUES ('21f8fc78-e937-3048-95e9-e69404b1d3f1', 'P59_has_section', 'Concept');
INSERT INTO concepts VALUES ('05804845-b0d6-3634-a977-a5c7785d2dde', 'P62_depicts', 'Concept');
INSERT INTO concepts VALUES ('15f83f67-48e0-3afd-b693-605172ea3fd2', 'P65_shows_visual_item', 'Concept');
INSERT INTO concepts VALUES ('629ed771-13e7-397e-8345-69f6cfb3db30', 'P67_refers_to', 'Concept');
INSERT INTO concepts VALUES ('037c3de7-65ae-3002-8328-18cc33572501', 'P68_foresees_use_of', 'Concept');
INSERT INTO concepts VALUES ('b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'P69_is_associated_with', 'Concept');
INSERT INTO concepts VALUES ('3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'P70_documents', 'Concept');
INSERT INTO concepts VALUES ('549c04f2-465b-3af6-ba22-8d21aacfe0af', 'P71_lists', 'Concept');
INSERT INTO concepts VALUES ('e4096768-5cad-36ca-8ee7-d5b928a0045a', 'P72_has_language', 'Concept');
INSERT INTO concepts VALUES ('8a9489d3-6c67-3b70-9b4d-64980efa0879', 'P73_has_translation', 'Concept');
INSERT INTO concepts VALUES ('5869a9ed-ebe5-3613-acc2-29c184737885', 'P74_has_current_or_former_residence', 'Concept');
INSERT INTO concepts VALUES ('44813770-321a-370d-bb8f-ba619bcb4334', 'P75_possesses', 'Concept');
INSERT INTO concepts VALUES ('e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'P76_has_contact_point', 'Concept');
INSERT INTO concepts VALUES ('5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'P78_is_identified_by', 'Concept');
INSERT INTO concepts VALUES ('2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'P79_beginning_is_qualified_by', 'Concept');
INSERT INTO concepts VALUES ('b1c4e551-2f6e-327b-8905-191228330e2f', 'P80_end_is_qualified_by', 'Concept');
INSERT INTO concepts VALUES ('6a998971-7a85-3615-9929-d613fe90391c', 'P81_ongoing_throughout', 'Concept');
INSERT INTO concepts VALUES ('890ddf47-6e5e-32f7-b3a8-ecd251002877', 'P82_at_some_time_within', 'Concept');
INSERT INTO concepts VALUES ('b38666a2-59fd-3154-85c3-90edaa812979', 'P83_had_at_least_duration', 'Concept');
INSERT INTO concepts VALUES ('86caed02-d112-3cd7-8f21-4836e4997850', 'P84_had_at_most_duration', 'Concept');
INSERT INTO concepts VALUES ('014fefdb-ddad-368b-b69c-951a0763824d', 'P86_falls_within', 'Concept');
INSERT INTO concepts VALUES ('697dc6cc-0da6-301c-9703-78edbf812fac', 'P87_is_identified_by', 'Concept');
INSERT INTO concepts VALUES ('900165c3-a630-3b9c-bb0b-572df34ea3e6', 'P89_falls_within', 'Concept');
INSERT INTO concepts VALUES ('26af9ec1-e169-3486-9bb5-3c8187784c8e', 'P90_has_value', 'Concept');
INSERT INTO concepts VALUES ('166f17e8-15b8-3abc-bba7-7a56c364bf42', 'P91_has_unit', 'Concept');
INSERT INTO concepts VALUES ('c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'P92_brought_into_existence', 'Concept');
INSERT INTO concepts VALUES ('f865c72a-09dd-386f-a9eb-385176727d94', 'P93_took_out_of_existence', 'Concept');
INSERT INTO concepts VALUES ('3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'P94_has_created', 'Concept');
INSERT INTO concepts VALUES ('9623a310-4d14-33dc-ae6e-10fb48062af5', 'P95_has_formed', 'Concept');
INSERT INTO concepts VALUES ('9e806e49-e728-32cf-821e-504ca9916afc', 'P96_by_mother', 'Concept');
INSERT INTO concepts VALUES ('19c3c1bf-e443-3f89-a366-d3e8c645a546', 'P97_from_father', 'Concept');
INSERT INTO concepts VALUES ('c511a177-3e0b-3a90-babe-e951f56f18d1', 'P98_brought_into_life', 'Concept');
INSERT INTO concepts VALUES ('9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'P99_dissolved', 'Concept');
INSERT INTO concepts VALUES ('b0ed382c-8dcc-3b98-845b-c22620d5633f', 'P100_was_death_of', 'Concept');
INSERT INTO concepts VALUES ('f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'P101_had_as_general_use', 'Concept');
INSERT INTO concepts VALUES ('8c69765e-7827-371f-9db3-fea290f87739', 'P102_has_title', 'Concept');
INSERT INTO concepts VALUES ('0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'P103_was_intended_for', 'Concept');
INSERT INTO concepts VALUES ('e091bc5e-86c9-328a-8c1c-deabe778c821', 'P104_is_subject_to', 'Concept');
INSERT INTO concepts VALUES ('140073c4-60b5-352d-a5f7-244072fc4086', 'P105_right_held_by', 'Concept');
INSERT INTO concepts VALUES ('f677091c-aa91-3851-8aa1-1225980d5e02', 'P106_is_composed_of', 'Concept');
INSERT INTO concepts VALUES ('f24003c3-0d20-3703-b044-9ed3ee42da07', 'P107_has_current_or_former_member', 'Concept');
INSERT INTO concepts VALUES ('632197f8-15a2-32b6-9886-c93e587f5b64', 'P108_has_produced', 'Concept');
INSERT INTO concepts VALUES ('4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'P109_has_current_or_former_curator', 'Concept');
INSERT INTO concepts VALUES ('41f65567-9d44-371a-8806-03e08d332918', 'P110_augmented', 'Concept');
INSERT INTO concepts VALUES ('a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'P111_added', 'Concept');
INSERT INTO concepts VALUES ('87e930ce-8aef-3700-af96-dd4d420fdc0f', 'P112_diminished', 'Concept');
INSERT INTO concepts VALUES ('f887076f-2375-38bd-b11c-e2511a59e0a2', 'P113_removed', 'Concept');
INSERT INTO concepts VALUES ('a9837ed9-5ff8-34ae-907d-2dba6012e877', 'P114_is_equal_in_time_to', 'Concept');
INSERT INTO concepts VALUES ('8687cd99-3201-3f8f-bb1c-241732242a8f', 'P115_finishes', 'Concept');
INSERT INTO concepts VALUES ('61861fca-6102-3151-af0c-599e14e7a93a', 'P116_starts', 'Concept');
INSERT INTO concepts VALUES ('740ab790-feb0-3700-8922-f152320272a5', 'P117_occurs_during', 'Concept');
INSERT INTO concepts VALUES ('b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'P118_overlaps_in_time_with', 'Concept');
INSERT INTO concepts VALUES ('8b7a9392-ce48-360e-b28a-c01d70eaf672', 'P119_meets_in_time_with', 'Concept');
INSERT INTO concepts VALUES ('911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'P120_occurs_before', 'Concept');
INSERT INTO concepts VALUES ('74e69af6-6a10-32be-91d3-50dd33b7876b', 'P121_overlaps_with', 'Concept');
INSERT INTO concepts VALUES ('da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'P122_borders_with', 'Concept');
INSERT INTO concepts VALUES ('50bbc81a-fe17-3469-a055-6c821ed66db1', 'P123_resulted_in', 'Concept');
INSERT INTO concepts VALUES ('98e3e69e-6101-3510-9a8c-7c11e279fd95', 'P124_transformed', 'Concept');
INSERT INTO concepts VALUES ('c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'P125_used_object_of_type', 'Concept');
INSERT INTO concepts VALUES ('8bfff662-9024-325a-a23a-b3c9bf509031', 'P126_employed', 'Concept');
INSERT INTO concepts VALUES ('7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'P127_has_broader_term', 'Concept');
INSERT INTO concepts VALUES ('007dac32-df80-366b-88ce-02f4c1928537', 'P128_carries', 'Concept');
INSERT INTO concepts VALUES ('c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'P129_is_about', 'Concept');
INSERT INTO concepts VALUES ('d6d729ca-ad20-3897-afaa-8427d5771c3f', 'P130_shows_features_of', 'Concept');
INSERT INTO concepts VALUES ('68dd1374-d854-3b4e-bca3-95d41675fb2f', 'P131_is_identified_by', 'Concept');
INSERT INTO concepts VALUES ('50060723-772d-3974-864e-8f8c326f169d', 'P132_overlaps_with', 'Concept');
INSERT INTO concepts VALUES ('95473150-07f2-3967-88f3-20b803dd239d', 'P133_is_separated_from', 'Concept');
INSERT INTO concepts VALUES ('1051349b-b0bf-3d88-8ab7-302c5c969197', 'P134_continued', 'Concept');
INSERT INTO concepts VALUES ('a84f68c6-b6c4-3a37-b069-e85b0b286489', 'P135_created_type', 'Concept');
INSERT INTO concepts VALUES ('ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'P136_was_based_on', 'Concept');
INSERT INTO concepts VALUES ('ada26737-46ff-3a34-8aed-7b70117c34aa', 'P137_exemplifies', 'Concept');
INSERT INTO concepts VALUES ('bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'P138_represents', 'Concept');
INSERT INTO concepts VALUES ('b13335f9-b208-3363-af5a-2e79fb56f7cc', 'P139_has_alternative_form', 'Concept');
INSERT INTO concepts VALUES ('839c9e24-c1ab-34b4-94da-2efb1d32af01', 'P140_assigned_attribute_to', 'Concept');
INSERT INTO concepts VALUES ('90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'P141_assigned', 'Concept');
INSERT INTO concepts VALUES ('f4734d6b-f54c-3ec2-8c0e-5f98211b13bc', 'P142_used_constituent', 'Concept');
INSERT INTO concepts VALUES ('aac583c1-05e4-34fe-aac2-e9bbc9c6d8fd', 'P143_joined', 'Concept');
INSERT INTO concepts VALUES ('406ee11a-a430-386f-9087-30c28c677da6', 'P144_joined_with', 'Concept');
INSERT INTO concepts VALUES ('7722c7a7-c2ff-3a33-8dd6-829c5b108191', 'P145_separated', 'Concept');
INSERT INTO concepts VALUES ('5bea9c01-5e34-32ce-a1b2-cddc51a6bc7c', 'P146_separated_from', 'Concept');
INSERT INTO concepts VALUES ('9c8d34b1-0379-35d6-9470-9ad11efdef5a', 'P147_curated', 'Concept');
INSERT INTO concepts VALUES ('df779f07-03dd-3ed7-91aa-025a71c95957', 'P148_has_component', 'Concept');
INSERT INTO concepts VALUES ('c6888cc6-3b5e-373c-a6ba-6e6bc24773c6', 'P149_is_identified_by', 'Concept');
INSERT INTO concepts VALUES ('75825fa7-ab9a-3b62-b7e8-250712914631', 'P150_defines_typical_parts_of', 'Concept');
INSERT INTO concepts VALUES ('63c5d303-2789-3999-8496-297343edf6dc', 'P151_was_formed_from', 'Concept');
INSERT INTO concepts VALUES ('e28841b2-0d53-3f91-afbf-3694a6236a5d', 'P152_has_parent', 'Concept');
INSERT INTO concepts VALUES ('222f5899-aa3f-3d52-a784-e5a0a68722f2', 'P156_occupies', 'Concept');
INSERT INTO concepts VALUES ('be7f5fbc-6abd-33cd-8cb0-a7e447068b20', 'P157_is_at_rest_relative_to', 'Concept');
INSERT INTO concepts VALUES ('6f3ce351-dc26-30bf-8c50-9392f873968d', 'P160_has_temporal_projection', 'Concept');
INSERT INTO concepts VALUES ('db25f50b-28f3-3041-b091-8bb7d2557856', 'P161_has_spatial_projection', 'Concept');
INSERT INTO concepts VALUES ('68633428-a835-3af2-9e8e-ac1ba713d4c8', 'P164_during', 'Concept');
INSERT INTO concepts VALUES ('a5a812b2-d786-38db-928f-1df9f416ab59', 'P165_incorporates', 'Concept');
INSERT INTO concepts VALUES ('6560a44c-f6b7-3c67-bbaf-c60585bc56d9', 'P166_was_a_presence_of', 'Concept');
INSERT INTO concepts VALUES ('da115774-50f3-3292-97dc-da1cbb527ca5', 'P167_was_at', 'Concept');
INSERT INTO concepts VALUES ('81fd2793-2d69-37fe-8027-ff705a54ce3d', 'P168_place_is_defined_by', 'Concept');
INSERT INTO concepts VALUES ('7cd91c49-743e-3eed-ad91-d993b09af867', 'BM.PX_is_related_to', 'Concept');


-- Completed on 2016-05-09 13:31:44 PDT

--
-- PostgreSQL database dump complete
--



--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.1
-- Dumped by pg_dump version 9.5.1

-- Started on 2016-05-09 13:33:50 PDT

-- SET statement_timeout = 0;
-- SET lock_timeout = 0;
-- SET client_encoding = 'UTF8';
-- SET standard_conforming_strings = on;
-- SET check_function_bodies = false;
-- SET client_min_messages = warning;
-- SET row_security = off;

-- SET search_path = public, pg_catalog;

--
-- TOC entry 3858 (class 0 OID 491690)
-- Dependencies: 248
-- Data for Name: values; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "values" VALUES ('94cb14a1-b729-30a1-89ac-be47bb7916ae', 'E1 Οντότητα CIDOC CRM', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('e90ac5a6-db9b-3ce3-8659-5ba6550551a9', 'Οντότητα CIDOC CRM', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'el', 'altLabel');
INSERT INTO "values" VALUES ('ad8ced6f-f7c0-382f-b2f4-33252843b392', 'E1 CRM Entity', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('05d939c3-12f0-3222-a77a-6d32e4603075', 'CRM Entity', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'en', 'altLabel');
INSERT INTO "values" VALUES ('10fe82dd-fc8d-3692-8387-6eeb66f9e4fb', 'E1 CRM Entität', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('47627785-ec73-3322-b605-0bebe81706b5', 'CRM Entität', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'de', 'altLabel');
INSERT INTO "values" VALUES ('6a97c3aa-bbc5-35f3-8d07-793140b3542c', 'E1 CRM Сущность', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('d24472ae-fd04-3b3c-ad81-ba23ce2170c3', 'CRM Сущность', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('311949cd-ced1-37a3-859d-23a2d4efd8ba', 'E1 Entité CRM', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('92386df0-e40e-3b18-b8cd-148cc2f50cf1', 'Entité CRM', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('ca3b03db-a820-3335-b211-1b05aed7b2de', 'E1 Entidade CRM', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('0a42be9f-f200-3b60-bdc1-e5931c4c3488', 'Entidade CRM', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('fe33b8f7-3a2a-30c3-a6a7-338bd013d798', 'E1 CRM实体', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('67839a2c-7714-3b88-98ac-77c0917487eb', 'CRM实体', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('74212357-f3cf-350d-b971-a77769cdc456', 'This class comprises all things in the universe of discourse of the CIDOC Conceptual Reference Model. 
It is an abstract concept providing for three general properties:
1.	Identification by name or appellation, and in particular by a preferred identifier
2.	Classification by type, allowing further refinement of the specific subclass an instance belongs to 
3.	Attachment of free text for the expression of anything not captured by formal properties
With the exception of E59 Primitive Value, all other classes within the CRM are directly or indirectly specialisations of E1 CRM Entity. 
', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('338bc65d-8538-3031-bf3e-4c8b25d85ea3', 'E2 Entité temporelle', '70064b58-4490-3d09-b463-fd18defae21f', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('23500219-bac3-3988-8592-9589665528ab', 'Entité temporelle', '70064b58-4490-3d09-b463-fd18defae21f', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('34fd3c38-729f-3706-8451-3fa0d33eebfc', 'E2 Temporal Entity', '70064b58-4490-3d09-b463-fd18defae21f', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('9f8ee6f5-0028-3e11-8f32-dc7b37605093', 'Temporal Entity', '70064b58-4490-3d09-b463-fd18defae21f', 'en', 'altLabel');
INSERT INTO "values" VALUES ('f8d5ee4f-0c25-3218-b2d0-d2746159b0cb', 'E2 Временная Сущность', '70064b58-4490-3d09-b463-fd18defae21f', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('f35811c4-4b20-38d0-8529-04e763b5e381', 'Временная Сущность', '70064b58-4490-3d09-b463-fd18defae21f', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('abd0583e-f295-3959-b8fe-ccee9e58b8c4', 'E2 Έγχρονη  Οντότητα', '70064b58-4490-3d09-b463-fd18defae21f', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('4ca90367-8dd3-3d4e-83ad-f28ad5290791', 'Έγχρονη  Οντότητα', '70064b58-4490-3d09-b463-fd18defae21f', 'el', 'altLabel');
INSERT INTO "values" VALUES ('a83275b6-1371-3cc2-9fa7-39f25c262fba', 'E2 Geschehendes', '70064b58-4490-3d09-b463-fd18defae21f', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('cc7ecd77-f0fb-3835-b561-94b815b8ded3', 'Geschehendes', '70064b58-4490-3d09-b463-fd18defae21f', 'de', 'altLabel');
INSERT INTO "values" VALUES ('c5b7aa62-f791-33fa-84dd-1af9c3ef5350', 'E2 Entidade Temporal', '70064b58-4490-3d09-b463-fd18defae21f', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('5c30dc01-bc57-378e-a9ad-180f7de6af0f', 'Entidade Temporal', '70064b58-4490-3d09-b463-fd18defae21f', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b45e4eec-0ff6-3ccc-a2a9-9b777b3e455b', 'E2 时间实体', '70064b58-4490-3d09-b463-fd18defae21f', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('a872ff72-330d-32b3-9140-23bd8749b159', '时间实体', '70064b58-4490-3d09-b463-fd18defae21f', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('51cf3ee2-0c63-3a5f-b0d7-5879b610bf76', 'This class comprises all phenomena, such as the instances of E4 Periods, E5 Events and states, which happen over a limited extent in time. 
	In some contexts, these are also called perdurants. This class is disjoint from E77 Persistent Item. This is an abstract class and has no direct instances. E2 Temporal Entity is specialized into E4 Period, which applies to a particular geographic area (defined with a greater or lesser degree of precision), and E3 Condition State, which applies to instances of E18 Physical Thing.
', '70064b58-4490-3d09-b463-fd18defae21f', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('66e0f9a1-d9b9-392a-a0ab-c6b2f7c1a958', 'E3 Состояние', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('9e06887e-e144-3121-a239-1bc50787e1a9', 'Состояние', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('eb871294-fdde-3cb4-9b8c-7d704f2cab36', 'E3 Condition State', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b062c263-03a9-3411-b222-f81a339214cc', 'Condition State', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'en', 'altLabel');
INSERT INTO "values" VALUES ('5ba01694-e704-358e-8a08-b4126b73b98d', 'E3 Zustandsphase', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('0b543304-a90c-324f-b68a-2040c735c5a4', 'Zustandsphase', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'de', 'altLabel');
INSERT INTO "values" VALUES ('7956747e-4734-325e-a46e-3cd74d898a55', 'E3 État matériel', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('0421ae0e-d627-33b5-81fc-dd3e4dfac09a', 'État matériel', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('13a72e4b-8920-364b-a7ba-bf2ab1c94f8c', 'E3 Κατάσταση', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('219afaf4-c482-378e-81b2-78282ea6dd0d', 'Κατάσταση', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'el', 'altLabel');
INSERT INTO "values" VALUES ('2a8b09af-0295-3ff1-b90b-781349ab7edb', 'E3 Estado Material', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('7b20a2cb-6949-3802-a0e3-9e275b876751', 'Estado Material', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('05e62809-23b1-3a45-ae51-204d52c2cc72', 'E3 状态', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('68a1e3ba-1dad-3589-8d41-5e6edc531a2c', '状态', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('053ee325-ba95-351a-b176-115fa306fa94', 'This class comprises the states of objects characterised by a certain condition over a time-span. 
An instance of this class describes the prevailing physical condition of any material object or feature during a specific E52 Time Span. In general, the time-span for which a certain condition can be asserted may be shorter than the real time-span, for which this condition held.
 The nature of that condition can be described using P2 has type. For example, the E3 Condition State “condition of the SS Great Britain between 22 September 1846 and 27 August 1847” can be characterized as E55 Type “wrecked”. 
', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('0cfe81ac-4d75-3b37-801b-eed0ef4730bc', 'E4 Phase', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('87e87c9d-b6b8-36e1-9bc5-b29535274684', 'Phase', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'de', 'altLabel');
INSERT INTO "values" VALUES ('2f654149-22d3-33e0-9195-46a9f671f6e1', 'E4 Period', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('c7422577-f859-3f11-a7d5-a9920b622647', 'Period', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'en', 'altLabel');
INSERT INTO "values" VALUES ('b3a87dca-f2c2-3d7a-a29a-f217dc97f8e1', 'E4 Période', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('86e481b1-b48d-38bc-8414-f07c9b426b0f', 'Période', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('fb6a03b6-9e1e-3b72-99be-5a262390f069', 'E4 Период', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('9f2b639d-97b1-3d7f-be46-e000ba44a501', 'Период', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('357b1376-ee1a-3142-9388-edda40a18d82', 'E4 Περίοδος', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('902ea3d2-1bd3-32b3-b6c1-9927773732e7', 'Περίοδος', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'el', 'altLabel');
INSERT INTO "values" VALUES ('fb501583-470e-3495-83f9-95b366ce6a2e', 'E4 Período', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('f40e3441-1ca0-3a4f-a590-499f5cfd661d', 'Período', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('28d129b4-01ff-33dd-a00e-1f0e5eb72aed', 'E4 期间', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('e3dea2b3-216c-34cc-b447-fc3115d8db98', '期间', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('5f07323c-556e-356c-90f0-548007630817', 'This class comprises sets of coherent phenomena or cultural manifestations occurring in time and space.

It is the social or physical coherence of these phenomena that identify an E4 Period and not the associated spatiotemporal extent. This extent is only the "ground" or space in an abstract physical sense that the actual process of growth, spread and retreat has covered. Consequently, different periods can overlap and coexist in time and space, such as when a nomadic culture exists in the same area and time as a sedentary culture. This also means that overlapping land use rights, common among first nations, amounts to overlapping periods.

Often, this class is used to describe prehistoric or historic periods such as the "Neolithic Period", the "Ming Dynasty" or the "McCarthy Era", but also geopolitical units and activities of settlements are regarded as special cases of E4 Period. However, there are no assumptions about the scale of the associated phenomena. In particular all events are seen as synthetic processes consisting of coherent phenomena. Therefore E4 Period is a superclass of E5 Event. For example, a modern clinical E67 Birth can be seen as both an atomic E5 Event and as an E4 Period that consists of multiple activities performed by multiple instances of E39 Actor.

As the actual extent of an E4 Period in spacetime we regard the trajectories of the participating physical things during their participation in an instance of E4 Period. This includes the open spaces via which these things have interacted and the spaces by which they had the potential to interact during that period or event in the way defined by the type of the respective period or event. Examples include the air in a meeting room transferring the voices of the participants. Since these phenomena are fuzzy, we assume the spatiotemporal extent to be contiguous, except for cases of phenomena spreading out over islands or other separated areas, including geopolitical units distributed over disconnected areas such as islands or colonies.

Whether the trajectories necessary for participants to travel between these areas are regarded as part of the spatiotemporal extent or not has to be decided in each case based on a concrete analysis, taking use of the sea for other purposes than travel, such as fishing, into consideration. One may also argue that the activities to govern disconnected areas imply travelling through spaces connecting them and that these areas hence are spatially connected in a way, but it appears counterintuitive to consider for instance travel routes in international waters as extensions of geopolitical units.

Consequently, an instance of E4 Period may occupy a number of disjoint spacetime volumes, however there must not be a discontinuity in the  timespan covered by these spacetime volumes. This means that an instance of E4 Period must be contiguous in time. If it has ended in all areas, it has ended as a whole. However it may end in one area before another, such as in the Polynesian migration, and it continues as long as it is ongoing in at least  one area.

We model E4 Period as a subclass of E2 Temporal Entity and of E92 Spacetime volume. The latter is intended as a phenomenal spacetime volume as defined in CRMgeo (Doerr and Hiebel 2013). By virtue of this multiple inheritance we can discuss the physical extent of an E4 Period without representing each instance of it together with an instance of its associated spacetime volume. This model combines two quite different kinds of substance: an instance of E4 Period is a phenomena while a space-time volume is an aggregation of points in spacetime. However, the real spatiotemporal extent of an instance of E4 Period is regarded to be unique to it due to all its details and fuzziness; its identity and existence depends uniquely on the identity of the instance of E4 Period. Therefore this multiple inheritance is unambiguous and effective and furthermore corresponds to the intuitions of natural language.

There are two different conceptualisations of ''artistic style'', defined either by physical features or by historical context. For example, “Impressionism” can be viewed as a period lasting from approximately 1870 to 1905 during which paintings with particular characteristics were produced by a group of artists that included (among others) Monet, Renoir, Pissarro, Sisley and Degas. Alternatively, it can be regarded as a style applicable to all paintings sharing the characteristics of the works produced by the Impressionist painters, regardless of historical context. The first interpretation is an instance of E4 Period, and the second defines morphological object types that fall under E55 Type.

Another specific case of an E4 Period is the set of activities and phenomena associated with a settlement, such as the populated period of Nineveh.
', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('460e77d7-5565-352b-bdc9-073815cd8bc1', 'E5 Συμβάν', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('db10c99c-aa7c-3585-832f-1bd9017ae83e', 'Συμβάν', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'el', 'altLabel');
INSERT INTO "values" VALUES ('0602f045-ff7a-34d2-a5d8-474e5d96dc57', 'E5 Événement', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('ec59441c-0b81-3d7d-8c6b-89c756b7b470', 'Événement', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('75740cfd-5bdb-36f7-8941-9fe0161544f3', 'E5 Событие', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('718aa281-1cb2-3c2b-b96b-5b0a770ee698', 'Событие', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('d5032a11-ee11-30d6-80c6-9f3007ff0b5a', 'E5 Event', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('839e3e33-fa28-37d3-a0f7-a3cf293a1dbc', 'Event', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'en', 'altLabel');
INSERT INTO "values" VALUES ('0257c2c6-81b6-3c6d-b50b-e69a804b5ea3', 'E5 Ereignis', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('bae9d6ae-b077-3e56-85a7-96086c0f1885', 'Ereignis', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'de', 'altLabel');
INSERT INTO "values" VALUES ('734b2f56-972c-3d63-bd58-a0faea049980', 'E5 Evento', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('594c77d4-c58f-332e-8cb5-4089d6a3ce60', 'Evento', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('45bce702-6b7c-3e47-a4d8-0111af8ce239', 'E5 事件', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('d7a8b7ca-4d1b-3c5d-936d-857ca250d42d', '事件', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('5251c166-221c-3184-b155-4e6f5a3d00d1', 'This class comprises changes of states in cultural, social or physical systems, regardless of scale, brought about by a series or group of coherent physical, cultural, technological or legal phenomena. Such changes of state will affect instances of E77 Persistent Item or its subclasses.
The distinction between an E5 Event and an E4 Period is partly a question of the scale of observation. Viewed at a coarse level of detail, an E5 Event is an ‘instantaneous’ change of state. At a fine level, the E5 Event can be analysed into its component phenomena within a space and time frame, and as such can be seen as an E4 Period. The reverse is not necessarily the case: not all instances of E4 Period give rise to a noteworthy change of state.
', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('28fe5229-602d-3039-8f4c-0b0b276339eb', 'E6 Разрушение', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('bb81b0fb-6bf4-3439-8c62-c0172fc8d2b8', 'Разрушение', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('209f1a78-1416-37c8-a40b-9f62ceeabb49', 'E6 Destruction', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('76e10f5a-09e6-32d4-8879-00ce4b801f0b', 'Destruction', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'en', 'altLabel');
INSERT INTO "values" VALUES ('10118831-9c15-34d6-be3d-b279f2de5d4d', 'E6 Destruction', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('b7f4fe1f-c612-3e4f-a95f-82826f0cbc07', 'Destruction', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('bb758535-5031-31b3-8b4e-91ab8db2756d', 'E6 Zerstörung', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f6c9afc4-3197-3733-b89f-b7cfba5e5267', 'Zerstörung', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'de', 'altLabel');
INSERT INTO "values" VALUES ('6fc2d252-1213-3462-a273-5c14876f5f81', 'E6 Καταστροφή', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('9aeb7781-6698-3a39-806f-1b574bdd1a96', 'Καταστροφή', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'el', 'altLabel');
INSERT INTO "values" VALUES ('599c0839-20d0-32eb-8b1d-083ebcfa808c', 'E6 Destruição', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('a6633278-0e4c-38c2-86a5-e9a67d76190a', 'Destruição', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('a5fd7f32-636c-3b4b-b668-9e05e0368dee', 'E6 摧毁', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('c184d6eb-99c5-37d1-85af-faa00154d073', '摧毁', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('35d5923b-abf8-3f79-82b2-e448999b26cd', 'This class comprises events that destroy one or more instances of E18 Physical Thing such that they lose their identity as the subjects of documentation.  
Some destruction events are intentional, while others are independent of human activity. Intentional destruction may be documented by classifying the event as both an E6 Destruction and E7 Activity. 
The decision to document an object as destroyed, transformed or modified is context sensitive: 
1.  If the matter remaining from the destruction is not documented, the event is modelled solely as E6 Destruction. 
2. An event should also be documented using E81 Transformation if it results in the destruction of one or more objects and the simultaneous production of others using parts or material from the original. In this case, the new items have separate identities. Matter is preserved, but identity is not.
3. When the initial identity of the changed instance of E18 Physical Thing is preserved, the event should be documented as E11 Modification. 
', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('7f3e87f2-ae69-342b-9bbb-8960cbeb0480', 'E7 Activity', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('37f13ae1-701b-34ab-811b-b953abd3779a', 'Activity', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'en', 'altLabel');
INSERT INTO "values" VALUES ('8065eab4-96a4-3114-8b60-fd28d32f1842', 'E7 Activité', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('03b32082-e73e-3592-b720-5cf0f0f8fe55', 'Activité', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('5ede2489-6bdf-39a6-a7b1-351bf2defa10', 'E7 Handlung', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('43422d80-ec9c-31bb-8e25-541564c34d6e', 'Handlung', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'de', 'altLabel');
INSERT INTO "values" VALUES ('05953c8c-da6d-3e3c-aad1-6c80ecb47063', 'E7 Деятельность', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('408c1bda-a899-33ce-ba39-11a41b6bedd1', 'Деятельность', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('edd77bc0-20d0-3c60-9a73-2b90c2d2e670', 'E7 Δράση', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('b458bd03-f49f-3656-8833-60a290437aa8', 'Δράση', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'el', 'altLabel');
INSERT INTO "values" VALUES ('ee8720c6-f213-3897-8560-405f49ccfbc7', 'E7 Atividade', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('e1666624-bf6e-376c-810c-40d2f8424f4b', 'Atividade', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('e7b0235a-b271-31cd-895c-3794a7ee3400', 'E7 活动', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('b5750f23-b321-3e70-8d89-1707841d4238', '活动', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('c7b0b7b2-7830-33f4-bcf2-11e6f8bcfcb1', 'This class comprises actions intentionally carried out by instances of E39 Actor that result in changes of state in the cultural, social, or physical systems documented. 
This notion includes complex, composite and long-lasting actions such as the building of a settlement or a war, as well as simple, short-lived actions such as the opening of a door.
', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('497388f4-c884-31d1-9412-1013b911a8ad', 'E8 Acquisition', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('96e59424-44c1-3687-9e4d-f1e9abf12296', 'Acquisition', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('959144bb-16e2-3e8d-b966-8324d4d16138', 'E8 Απόκτηση', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('fe8d40ce-69f5-3302-83e8-755a183a5ac5', 'Απόκτηση', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'el', 'altLabel');
INSERT INTO "values" VALUES ('1c7fd1b8-3168-3582-94ef-3bf5bac68dc3', 'E8 Событие Приобретения', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('92cfa5c1-1c35-399d-af98-1cfb42db491d', 'Событие Приобретения', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('bc4bebb3-821e-3d7a-a38c-01d7f0f2d4c9', 'E8 Acquisition', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('0ee14804-01ad-3949-be8e-934e64324895', 'Acquisition', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'en', 'altLabel');
INSERT INTO "values" VALUES ('943a072c-9feb-3363-adee-8fb3f52a9c9d', 'E8 Erwerb', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('722ff6d5-5c70-3325-a806-6e8aa76bfb7e', 'Erwerb', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'de', 'altLabel');
INSERT INTO "values" VALUES ('7d950f21-1c73-37d1-b213-e72e19b0bb8c', 'E8 Aquisição', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('dffa4e7d-f27d-3bcc-9e84-261177807b8e', 'Aquisição', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('9ca57ec9-7f96-3443-a028-c170487e0d7b', 'E8 征集取得', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('d1fc8237-d697-3996-9adb-6587fb1de285', '征集取得', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('11257c21-db73-385c-974b-4e5e377fb5ff', 'This class comprises transfers of legal ownership from one or more instances of E39 Actor to one or more other instances of E39 Actor. 
The class also applies to the establishment or loss of ownership of instances of E18 Physical Thing. It does not, however, imply changes of any other kinds of right. The recording of the donor and/or recipient is optional. It is possible that in an instance of E8 Acquisition there is either no donor or no recipient. Depending on the circumstances, it may describe:
1.	the beginning of ownership
2.	the end of ownership
3.	the transfer of ownership
4.	the acquisition from an unknown source 
5.	the loss of title due to destruction of the item
It may also describe events where a collector appropriates legal title, for example by annexation or field collection. The interpretation of the museum notion of "accession" differs between institutions. The CRM therefore models legal ownership (E8 Acquisition) and physical custody (E10 Transfer of Custody) separately. Institutions will then model their specific notions of accession and deaccession as combinations of these.
', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('14a8048a-a56c-33c7-8dec-65a6e2c04d9a', 'E9 Move', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('9f8ddf47-1d7c-379e-b2af-e751f31aedb2', 'Move', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'en', 'altLabel');
INSERT INTO "values" VALUES ('5c3cf61e-42ca-3cd2-9c1c-66f48d768be5', 'E9 Μετακίνηση', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('aa993fc9-d1a2-3177-b977-2bc00ceb3fd5', 'Μετακίνηση', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'el', 'altLabel');
INSERT INTO "values" VALUES ('7a33096f-4f71-3a1b-9848-e31f6343ecab', 'E9 Objektbewegung', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('5a966ffa-b4e0-33fd-a010-7a246f1369ca', 'Objektbewegung', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'de', 'altLabel');
INSERT INTO "values" VALUES ('fc741a06-b810-36db-b350-d1d024a9b549', 'E9 Перемещение', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('b85e24b5-a670-31f4-b085-fa7da3cd379c', 'Перемещение', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('33ff3de7-57e0-3fc8-8b0c-1a92e59b587b', 'E9 Déplacement', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('1234f997-d973-3f95-9687-513eaa8aac82', 'Déplacement', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('77a42391-ad24-34be-8c4b-3f936e82240c', 'E9 Locomoção', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('0d5c7167-f99a-390f-88e2-a1783456918f', 'Locomoção', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('babcaaea-2d91-31bf-9cfe-deed67fb74d9', 'E9 移动', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('be4831f0-55fe-36fc-bfb9-c7330cedc19a', '移动', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('ed3e95ba-1ac2-378e-a348-00221098f7d4', 'This class comprises changes of the physical location of the instances of E19 Physical Object. 
Note, that the class E9 Move inherits the property P7 took place at (witnessed): E53 Place. This property should be used to describe the trajectory or a larger area within which a move takes place, whereas the properties P26 moved to (was destination of), P27 moved from (was origin of) describe the start and end points only. Moves may also be documented to consist of other moves (via P9 consists of (forms part of)), in order to describe intermediate stages on a trajectory. In that case, start and end points of the partial moves should match appropriately between each other and with the overall event.
', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('000f02d7-3a13-3127-a4fa-d7a7a0370b1d', 'E10 Changement de détenteur', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('4dde06b4-7c00-3040-ab55-86841a1de027', 'Changement de détenteur', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('70d6fc2c-0f6d-38f2-b906-65624ae7a720', 'E10 Transfer of Custody', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('33bf1d7e-2fab-3fa6-8ce4-1be795a783ad', 'Transfer of Custody', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c85bc8bc-480f-3eba-9349-55f72c8871c0', 'E10 Übertragung des Gewahrsams', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('0584d41d-1a48-3b66-b426-cb0c07dfcc74', 'Übertragung des Gewahrsams', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'de', 'altLabel');
INSERT INTO "values" VALUES ('b05590bc-fbd3-3f82-862e-2ac29eeb9ca8', 'E10 Μεταβίβαση  Κατοχής', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('c743b581-c40e-3b21-b192-7806452f280b', 'Μεταβίβαση  Κατοχής', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'el', 'altLabel');
INSERT INTO "values" VALUES ('c322cf55-5997-3953-8e2c-aa61986aeb36', 'E10 Передача Опеки', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('c3361988-9f3f-3ab8-83f0-33f91a2bf136', 'Передача Опеки', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('68db6e02-45f8-340f-9efe-52bd475d6fad', 'E10 Transferência de Custódia', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('69f20177-419f-38e7-82cb-f1528aa28c83', 'Transferência de Custódia', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('6b3062c3-5dbf-368e-a15d-81e988baf226', 'E10 保管作业转移', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('8bb08eec-e1ee-3be9-a182-3a15f052e404', '保管作业转移', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('57c637d9-207a-3f38-84c4-c238b2d13d36', 'This class comprises transfers of physical custody of objects between instances of E39 Actor. 
The recording of the donor and/or recipient is optional. It is possible that in an instance of E10 Transfer of Custody there is either no donor or no recipient. Depending on the circumstances it may describe:
1.	the beginning of custody 
2.	the end of custody 
3.	the transfer of custody 
4.	the receipt of custody from an unknown source
5.	the declared loss of an object
The distinction between the legal responsibility for custody and the actual physical possession of the object should be expressed using the property P2 has type (is type of). A specific case of transfer of custody is theft.
The interpretation of the museum notion of "accession" differs between institutions. The CRM therefore models legal ownership and physical custody separately. Institutions will then model their specific notions of accession and deaccession as combinations of these.
', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('99268503-e7cd-3685-bbfe-1afca0cb6d7b', 'E11 Событие Изменения', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('e7b1172d-c038-33f4-a205-9bf74f644e31', 'Событие Изменения', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('30f22c9b-f3ab-3309-a7ca-efc34b7ca663', 'E11 Modification', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('22eecf88-2d87-366e-8290-dcf9ae15b2eb', 'Modification', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'en', 'altLabel');
INSERT INTO "values" VALUES ('99638195-ec93-3885-82f5-e378ba514eac', 'E11 Τροποποίηση', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('c8b99aab-d9f1-3195-9331-f500a59bd723', 'Τροποποίηση', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'el', 'altLabel');
INSERT INTO "values" VALUES ('ffec40f0-2d49-3bfb-adbf-5dade6f6f9f6', 'E11 Modification', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('36176d25-f098-393c-9ed3-eb1e23b179a4', 'Modification', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('70a6e346-85bb-3ae8-a41e-d37c5a7d8902', 'E11 Bearbeitung', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('7bd9481f-5f32-3f30-be92-5afd524dfbd5', 'Bearbeitung', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'de', 'altLabel');
INSERT INTO "values" VALUES ('2838561a-a297-3508-8bb0-703acabef726', 'E11 Modificação', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('890c1927-86f0-3b2d-a49b-5cb9d6358b09', 'Modificação', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('a463cb4f-7e7d-3ff5-83aa-f916a1df088f', 'E11 修改', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('056a6c78-5a23-3f02-9ec5-ef28e4562370', '修改', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('f808a711-f65d-3d42-8639-8117090df237', 'This class comprises all instances of E7 Activity that create, alter or change E24 Physical Man-Made Thing. 
This class includes the production of an item from raw materials, and other so far undocumented objects, and the preventive treatment or restoration of an object for conservation. 
Since the distinction between modification and production is not always clear, modification is regarded as the more generally applicable concept. This implies that some items may be consumed or destroyed in a Modification, and that others may be produced as a result of it. An event should also be documented using E81 Transformation if it results in the destruction of one or more objects and the simultaneous production of others using parts or material from the originals. In this case, the new items have separate identities. 
If the instance of the E29 Design or Procedure utilized for the modification prescribes the use of specific materials, they should be documented using property P68 foresees use of (use foreseen by): E57 Material of E29 Design or Procedure, rather than via P126 employed (was employed in): E57 Material.
', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('bfe0d961-4840-364f-87ec-f0b8798add58', 'E12 Production', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('79d721f3-62a2-3059-a60f-969fb55c440d', 'Production', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('5ee7d1f4-ac06-36d2-bf94-4b830be3717a', 'E12 Παραγωγή', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('cb8ec535-ce23-3e11-95a0-b0973cf2a629', 'Παραγωγή', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'el', 'altLabel');
INSERT INTO "values" VALUES ('47b58b8e-5228-3ca4-a8ff-620b5739b8c0', 'E12 Herstellung', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('7d2393ff-2203-38c0-a05e-4f7c2b9378d6', 'Herstellung', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'de', 'altLabel');
INSERT INTO "values" VALUES ('2dda02dc-07f7-36dc-bd4f-f1b1633180f8', 'E12 Событие Производства', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('b55b84b5-e2f0-34bf-a5b8-55eafce32120', 'Событие Производства', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('6d5a6a72-c77b-30f5-810a-9509c2f2335d', 'E12 Production', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('cc443a6b-c796-31fd-b6ca-f0b31e0e2e6f', 'Production', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'en', 'altLabel');
INSERT INTO "values" VALUES ('2cd4d0bd-c9a2-3938-813b-586f6a1eef24', 'E12 Produção', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('af34e76e-9deb-3ccb-aade-8308088e6437', 'Produção', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('936b3bb4-918c-3e0b-9074-f6e2027f75aa', 'E12 生产', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('97158e60-f963-3aa8-bc72-bdff05a975bc', '生产', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('3db68e40-12c9-39e2-84fc-c6bfdf48cf37', 'This class comprises activities that are designed to, and succeed in, creating one or more new items. 
It specializes the notion of modification into production. The decision as to whether or not an object is regarded as new is context sensitive. Normally, items are considered “new” if there is no obvious overall similarity between them and the consumed items and material used in their production. In other cases, an item is considered “new” because it becomes relevant to documentation by a modification. For example, the scribbling of a name on a potsherd may make it a voting token. The original potsherd may not be worth documenting, in contrast to the inscribed one. 
This entity can be collective: the printing of a thousand books, for example, would normally be considered a single event. 
An event should also be documented using E81 Transformation if it results in the destruction of one or more objects and the simultaneous production of others using parts or material from the originals. In this case, the new items have separate identities and matter is preserved, but identity is not.
', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('6f804d2d-058a-36d5-9fc9-33b77e833aac', 'E13 Присвоение Атрибута', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('b4a41337-60a8-3c21-a8a9-06c6f20ceeb5', 'Присвоение Атрибута', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('9265527f-947b-38ce-bf7f-36869d92d4ae', 'E13 Affectation d''attribut', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('2b6dece7-0605-366d-8936-0e0fc2d016d0', 'Affectation d''attribut', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('029b91dd-847f-350a-beb3-ddd6fcb8c1b8', 'E13 Merkmalszuweisung', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('e045263f-4ed2-33c9-a6a3-60bb5fad4fa9', 'Merkmalszuweisung', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'de', 'altLabel');
INSERT INTO "values" VALUES ('5cdeb35a-96ef-3926-abe3-ad9f9a47eb18', 'E13 Attribute Assignment', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('a28e4505-6d4a-3c64-a43a-482816a9ae23', 'Attribute Assignment', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'en', 'altLabel');
INSERT INTO "values" VALUES ('adef7631-bcfd-32f2-984d-94fe2bc82a90', 'E13 Απόδοση Ιδιοτήτων', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('d53f8ab7-2314-3897-bef3-e4af66b4cc9e', 'Απόδοση Ιδιοτήτων', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'el', 'altLabel');
INSERT INTO "values" VALUES ('bd4ed846-52ee-302c-a5fe-c50131f31629', 'E13 Atribuição de Característica', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('555a19f1-ae09-3f1f-bf98-7ff61ecd4c91', 'Atribuição de Característica', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b3aa76b5-1be3-320c-ba74-af8cebdcd9ad', 'E13 屬性指定', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('9000bc12-78a1-306d-ac80-e9a91466d8d1', '屬性指定', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('e88f7b19-a662-3881-93ef-0b1dfbab582e', 'This class comprises the actions of making assertions about properties of an object or any relation between two items or concepts. 
This class allows the documentation of how the respective assignment came about, and whose opinion it was. All the attributes or properties assigned in such an action can also be seen as directly attached to the respective item or concept, possibly as a collection of contradictory values. All cases of properties in this model that are also described indirectly through an action are characterised as "short cuts" of this action. This redundant modelling of two alternative views is preferred because many implementations may have good reasons to model either the action or the short cut, and the relation between both alternatives can be captured by simple rules. 
In particular, the class describes the actions of people making propositions and statements during certain museum procedures, e.g. the person and date when a condition statement was made, an identifier was assigned, the museum object was measured, etc. Which kinds of such assignments and statements need to be documented explicitly in structures of a schema rather than free text, depends on if this information should be accessible by structured queries. 
', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('d5322d5e-a724-3623-a7c5-4ea8265852d1', 'E14 Εκτίμηση Κατάστασης', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('55a24f71-9402-3387-8ced-a1bd0dc87de8', 'Εκτίμηση Κατάστασης', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'el', 'altLabel');
INSERT INTO "values" VALUES ('3824b55b-2599-3b4f-ac59-94955ac8559f', 'E14 Оценка Состояния', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('ae31e35d-91fc-3115-be4e-757b1ef0c831', 'Оценка Состояния', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('8e798040-240d-3abd-b05b-f02de0fc216d', 'E14 Expertise de l''état matériel', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('aac184f4-7977-324b-979a-c6dd529c5c5b', 'Expertise de l''état matériel', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('def2765d-8ef6-341f-bc63-6008a1910674', 'E14 Zustandsfeststellung', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('794e4f07-088d-34da-a839-e2ba7fe96b6e', 'Zustandsfeststellung', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'de', 'altLabel');
INSERT INTO "values" VALUES ('d75489c2-8dd6-3268-b78d-e8ce1f95fcd8', 'E14 Condition Assessment', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('07db9a61-a9d8-393c-af03-b8e8828d5972', 'Condition Assessment', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'en', 'altLabel');
INSERT INTO "values" VALUES ('66f8947b-0931-35a3-a591-9b36c3e563e6', 'E14 Avaliação do Estado Material', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('843ba807-3322-33ae-87fb-2ffff17631fe', 'Avaliação do Estado Material', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('40ab79f9-e110-301e-adb1-a2c466b4876a', 'E14 状态评估', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('e5e2e707-8ac6-3022-9748-2df72d1ba735', '状态评估', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('3525792a-b3e1-3d3c-9361-ad7f7d666edc', 'This class describes the act of assessing the state of preservation of an object during a particular period. 
The condition assessment may be carried out by inspection, measurement or through historical research. This class is used to document circumstances of the respective assessment that may be relevant to interpret its quality at a later stage, or to continue research on related documents. 
', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('ccbcaab8-2b99-3ad6-8b9e-4ff2d8020803', 'E15 Απόδοση Αναγνωριστικού', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('4c9ed279-7ccd-306c-b2e8-d5f1acee2c8d', 'Απόδοση Αναγνωριστικού', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'el', 'altLabel');
INSERT INTO "values" VALUES ('f944b49f-54ee-3f34-8a77-e1ce6682d579', 'E15 Назначение Идентификатора', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('b53f9552-a878-39b9-9875-4a77d7e648a9', 'Назначение Идентификатора', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('52c81b60-66ab-3093-aaa6-68e4ab5e7c7a', 'E15 Identifier Assignment', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('221b946b-d67b-38c0-9e0f-41b0b1ef5672', 'Identifier Assignment', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'en', 'altLabel');
INSERT INTO "values" VALUES ('d14b75dd-3268-37a0-88a3-ba962fc751fa', 'E15 Kennzeichenzuweisung', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('61dcf7a1-f053-3d74-ad95-8febf676e446', 'Kennzeichenzuweisung', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'de', 'altLabel');
INSERT INTO "values" VALUES ('b81f2c4c-d6fe-32dc-85d4-1aad2ed4cfd3', 'E15 Attribution d’identificateur', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('472700e0-9fd5-35da-a6d2-6a911bb9ffd4', 'Attribution d’identificateur', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('aef8ca7b-7980-3bbb-bd2a-07f301e98d6f', 'E15 Atribuição de Identificador', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('c1f9f252-6677-33a5-843c-5239c85ca296', 'Atribuição de Identificador', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('57d560aa-f800-3a79-bedd-86aef1f88505', 'E15 标识符指定', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('02687dc1-9e91-3279-a978-dc32f5b02162', '标识符指定', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('02be6711-7f3c-3746-a925-d91ea59ce9f3', 'Рукотворный Объект', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('9f3fba76-4eb7-3ff7-b39f-b5a2d7b808d8', 'E22 Man-Made Object', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('bccbb8aa-b403-373d-ab6f-0284c3b26324', 'Man-Made Object', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'en', 'altLabel');
INSERT INTO "values" VALUES ('ea386df5-291a-3b1e-a111-516e93bb159b', 'E22 Objeto Fabricado', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('1bb8ecdf-4381-322a-914c-4f41cbbf36fb', 'Objeto Fabricado', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('45dc0f39-d65a-3b5c-b33e-badcd0a0a1f6', 'E22 人造物件', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('e85f5f16-53c9-37c8-ac12-60055c1f68e5', '人造物件', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('be65b49a-d068-3ae0-b14b-5ac5174917ed', 'This class comprises activities that result in the allocation of an identifier to an instance of E1 CRM Entity. An E15 Identifier Assignment may include the creation of the identifier from multiple constituents, which themselves may be instances of E41 Appellation. The syntax and kinds of constituents to be used may be declared in a rule constituting an instance of E29 Design or Procedure.
Examples of such identifiers include Find Numbers, Inventory Numbers, uniform titles in the sense of librarianship and Digital Object Identifiers (DOI). Documenting the act of identifier assignment and deassignment is especially useful when objects change custody or the identification system of an organization is changed. In order to keep track of the identity of things in such cases, it is important to document by whom, when and for what purpose an identifier is assigned to an item.
The fact that an identifier is a preferred one for an organisation can be expressed by using the property E1 CRM Entity. P48 has preferred identifier (is preferred identifier of): E42 Identifier. It can better be expressed in a context independent form by assigning a suitable E55 Type, such as “preferred identifier assignment”, to the respective instance of E15 Identifier Assignment via the P2 has type property.
', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('dbbf1368-1fee-304e-891c-7fc7b37ea465', 'E16 Событие Измерения', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('b93176f6-0eb9-3ab8-8876-2e92ab7a92ea', 'Событие Измерения', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('08585298-2659-376a-be8b-057f1013570d', 'E16 Μέτρηση', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('477b7e3c-bbab-3e27-8ff4-f739fd22e964', 'Μέτρηση', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'el', 'altLabel');
INSERT INTO "values" VALUES ('55240d0a-821a-3657-8339-a1acdf074691', 'E16 Messung', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('9fe08f9f-4b0d-37af-a060-d227bb2ebd44', 'Messung', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'de', 'altLabel');
INSERT INTO "values" VALUES ('3c064bb1-808a-33dc-a850-f28422b4f85e', 'E16 Mesurage', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('4b43803c-b21e-3921-af11-dd9dc868a08d', 'Mesurage', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('3966463e-981c-351c-9464-f919786e058f', 'E16 Measurement', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('0a676df1-c958-3ba2-9b72-4082f650bdce', 'Measurement', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c48d7ff3-7630-3564-9e9f-fda2e45631f0', 'E16 Medição', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('b68d815d-79c0-3328-9c34-34a87bce3409', 'Medição', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('2263ebf1-d66c-3531-834a-ff94ca7e9f0f', 'E16 测量', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('03410d6b-9875-3d75-81b1-d327688b7fc8', '测量', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('7acf824f-60bd-3902-8db0-f513d3aa8d97', 'This class comprises actions measuring physical properties and other values that can be determined by a systematic procedure. 
Examples include measuring the monetary value of a collection of coins or the running time of a specific video cassette. 
The E16 Measurement may use simple counting or tools, such as yardsticks or radiation detection devices. The interest is in the method and care applied, so that the reliability of the result may be judged at a later stage, or research continued on the associated documents. The date of the event is important for dimensions, which may change value over time, such as the length of an object subject to shrinkage. Details of methods and devices are best handled as free text, whereas basic techniques such as "carbon 14 dating" should be encoded using P2 has type (is type of:) E55 Type.
', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('3a011508-7753-37c5-a357-143acee2fa8d', 'E17 Typuszuweisung', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('03804b82-d39d-35ff-aa8a-d708759c03c0', 'Typuszuweisung', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'de', 'altLabel');
INSERT INTO "values" VALUES ('0cccb800-37c2-3562-ac25-9c050c35255e', 'E17 Присвоение Типа', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('0b7dee1c-408a-33fb-b3f4-7554d5eb3eb5', 'Присвоение Типа', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('e1555e9d-b314-30e1-8aa5-d2d956ee6f52', 'E17 Attribution de type', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5d0761c4-bd1d-3804-9c49-cae0bffe50ee', 'Attribution de type', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('98c3943d-f982-31e3-898c-88e97d26988f', 'E17 Type Assignment', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('2e06516d-15be-3263-a0f6-4b1b22ef6331', 'Type Assignment', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'en', 'altLabel');
INSERT INTO "values" VALUES ('7d5c3b73-fe0f-3b43-8785-f7676ecea207', 'E17 Απόδοση Τύπου', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('2dc0e625-b01f-36c4-88cd-bda595edd483', 'Απόδοση Τύπου', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'el', 'altLabel');
INSERT INTO "values" VALUES ('33452c93-5a89-33cd-b622-a2a8a33d8f38', 'E17 Atribuição de Tipo', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('b7bd4cc3-0754-3742-ac4e-c347541eaf76', 'Atribuição de Tipo', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('bf98e6a0-cdde-3d3c-92b3-98cd1fc9b29e', 'E17 类型指定', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('4df7702d-1e90-3eb0-919b-7590758346ce', '类型指定', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('db56b3db-9cf9-38bd-9ce9-897482fc2ec4', 'This class comprises the actions of classifying items of whatever kind. Such items include objects, specimens, people, actions and concepts. 
This class allows for the documentation of the context of classification acts in cases where the value of the classification depends on the personal opinion of the classifier, and the date that the classification was made. This class also encompasses the notion of "determination," i.e. the systematic and molecular identification of a specimen in biology. 
', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('8f9615b6-d60f-313c-ac03-251bb2bbcb79', 'E18 Materielles', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('8947fda2-92ec-3ecc-bd48-e001e6fbee55', 'Materielles', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'de', 'altLabel');
INSERT INTO "values" VALUES ('75b2551d-b7ea-3d72-a3d3-1818a58aa96b', 'E18 Υλικό Πράγμα', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('da5b8dea-2e02-3e45-a10d-7b3a63c88994', 'Υλικό Πράγμα', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'el', 'altLabel');
INSERT INTO "values" VALUES ('bc07f60d-6044-362d-b62d-e01a50f9ffdc', 'E18 Physical Thing', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('d94bd30a-3ead-3fc4-9b7c-b891143aaa32', 'Physical Thing', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'en', 'altLabel');
INSERT INTO "values" VALUES ('f8f8d781-4eb4-3bdd-85af-617975f5fcc8', 'E18 Chose matérielle', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('931ed734-ae81-3f3e-b537-f7cae5128c63', 'Chose matérielle', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('0a14e89e-beaf-3c63-9400-20929e025568', 'E18 Физическая Вещь', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('3c995f09-3107-3443-9ff0-dcaaf24a2cd6', 'Физическая Вещь', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('eca60ae1-1d9b-3cf5-9558-c9bef52c8e65', 'E18 Coisa Material', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('900e35eb-a826-330d-805a-5be2952fe3e3', 'Coisa Material', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('ab573f4d-86c8-3d00-82c5-efbba2b96119', 'E18 实体物', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('7b529ef6-7c03-3ce8-a8c5-d65fd84275c3', '实体物', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('1a61ab5b-ed8c-3d3a-bcf2-e955361cca32', 'This class comprises physical objects purposely created by human activity.
No assumptions are made as to the extent of modification required to justify regarding an object as man-made. For example, an inscribed piece of rock or a preserved butterfly are both regarded as instances of E22 Man-Made Object.
', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('e493f6db-7b59-38f4-87c8-0d43d4f31c12', 'E24 Физическая Рукотворная Вещь', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('07b1524e-05d7-3363-83f8-fa65ac3d66a4', 'Физическая Рукотворная Вещь', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('fd394f3d-9496-30f0-b86b-2980741831b2', 'E24 Physical Man-Made Thing', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('5366af6f-7f26-3d3e-b0e9-75249564e091', 'Physical Man-Made Thing', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'en', 'altLabel');
INSERT INTO "values" VALUES ('45cdd95b-7ead-327f-92f0-5d61813e700d', 'E24 Ανθρωπογενές Υλικό Πράγμα', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('05844e02-c88f-3b02-9058-e32bf95e08ed', 'Ανθρωπογενές Υλικό Πράγμα', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'el', 'altLabel');
INSERT INTO "values" VALUES ('5f11d27b-e1eb-34f1-bccb-5a7f9eadb47f', 'E24 Hergestelltes', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('9e88c6ce-bcd3-38eb-963c-b69d67684f2a', 'This class comprises all persistent physical items with a relatively stable form, man-made or natural.

Depending on the existence of natural boundaries of such things, the CRM distinguishes the instances of E19 Physical Object from instances of E26 Physical Feature, such as holes, rivers, pieces of land etc. Most instances of E19 Physical Object can be moved (if not too heavy), whereas features are integral to the surrounding matter.

An instance of E18 Physical Thing occupies not only a particular geometric space, but in the course of its existence it also forms a trajectory through spacetime, which occupies a real, that is phenomenal, volume in spacetime. We include in the occupied space the space filled by the matter of the physical thing and all its inner spaces, such as the interior of a box. Physical things consisting of aggregations of physically unconnected objects, such as a set of chessmen, occupy a number of individually contiguous spacetime volumes equal to the number of unconnected objects that constitute the set.

We model E18 Physical Thing to be a subclass of E72 Legal Object and of E92 Spacetime volume. The latter is intended as a phenomenal spacetime volume as defined in CRMgeo (Doerr and Hiebel 2013). By virtue of this multiple inheritance we can discuss the physical extent of an E18 Physical Thing without representing each instance of it together with an instance of its associated spacetime volume. This model combines two quite different kinds of substance: an instance of E18 Physical Thing is matter while a spacetime volume is an aggregation of points in spacetime. However, the real spatiotemporal extent of an instance of E18 Physical Thing is regarded to be unique to it, due to all its details and fuzziness; its identity and existence depends uniquely on the identity of the instance of E18 Physical Thing. Therefore this multiple inheritance is unambiguous and effective and furthermore corresponds to the intuitions of natural language.

The CIDOC CRM is generally not concerned with amounts of matter in fluid or gaseous states. 
', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('46d2bdbd-5edf-3f8a-8406-fc2715193d26', 'E19 Физический Объект', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('dc9e1627-88d1-35e8-9f26-875d9745f1ed', 'Физический Объект', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('3fd45d3d-5f7c-35f1-9d00-ee95c5e408f2', 'E19 Objet matériel', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('a59b9f59-25f8-3265-bfd3-b2f0b3adc595', 'Objet matériel', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('58da2dc3-2906-3103-a507-ad908db485a0', 'E19 Physical Object', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('f3eb4b15-5a0f-3fc9-974e-8a24f9816380', 'Physical Object', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'en', 'altLabel');
INSERT INTO "values" VALUES ('2ccc50d1-9f21-379a-b7bd-86aa056f31ee', 'E19 Υλικό Αντικείμενο', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('15f4df5c-b6f4-33c7-ac84-0d9252f26085', 'Υλικό Αντικείμενο', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'el', 'altLabel');
INSERT INTO "values" VALUES ('44ef7c02-0b22-3b6d-b69f-1512307a2bad', 'E19 Materieller Gegenstand', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('4e4e7a2d-55c6-3d5a-b61a-1b735700e2b7', 'Materieller Gegenstand', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'de', 'altLabel');
INSERT INTO "values" VALUES ('cdc2d3ce-2156-330f-aaf2-0e969c7597b0', 'E19 Objeto Material', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('8bc7a2e8-4d08-3535-845b-27ce12660203', 'Objeto Material', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('5471c6b3-bffc-301a-a991-07c443323152', 'E19 实体物件', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('7a02e983-38ea-351c-9600-8128ab73f131', '实体物件', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('5772e0d3-dd55-3786-91fd-60fb5138f326', 'This class comprises items of a material nature that are units for documentation and have physical boundaries that separate them completely in an objective way from other objects. 
The class also includes all aggregates of objects made for functional purposes of whatever kind, independent of physical coherence, such as a set of chessmen. Typically, instances of E19 Physical Object can be moved (if not too heavy).
In some contexts, such objects, except for aggregates, are also called “bona fide objects” (Smith & Varzi, 2000, pp.401-420), i.e. naturally defined objects. 
The decision as to what is documented as a complete item, rather than by its parts or components, may be a purely administrative decision or may be a result of the order in which the item was acquired.
', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('1f996956-0816-3675-a599-4e056e782a7a', 'E20 Биологический Объект', '2c287084-c289-36b2-8328-853e381f0ed4', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('f8dd7b04-9db9-3aa0-a32a-cf9fb37d2f05', 'Биологический Объект', '2c287084-c289-36b2-8328-853e381f0ed4', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('ca3e8bbe-d9e6-3204-9a37-2ff64502f9df', 'E20 Biological Object', '2c287084-c289-36b2-8328-853e381f0ed4', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('ae801d56-8cb5-3ef6-8403-0558361c5743', 'Biological Object', '2c287084-c289-36b2-8328-853e381f0ed4', 'en', 'altLabel');
INSERT INTO "values" VALUES ('49bfdc02-065e-3987-8045-373eb0b7dbb8', 'E20 Βιολογικό Ακτικείμενο', '2c287084-c289-36b2-8328-853e381f0ed4', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('4530e7b2-63bb-36a4-b80c-251d4c275624', 'Βιολογικό Ακτικείμενο', '2c287084-c289-36b2-8328-853e381f0ed4', 'el', 'altLabel');
INSERT INTO "values" VALUES ('c90fe365-5c4c-3139-b6ce-5871347b9fdb', 'E20 Objet biologique', '2c287084-c289-36b2-8328-853e381f0ed4', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('556afdf0-112c-33b1-b08b-598aaa65a5c2', 'Objet biologique', '2c287084-c289-36b2-8328-853e381f0ed4', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('7be2127d-231e-3f2d-8a3f-bcc3c8d3fc52', 'E20 Biologischer Gegenstand', '2c287084-c289-36b2-8328-853e381f0ed4', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f6be638b-1d6d-3f33-9ddd-64f39da90008', 'Biologischer Gegenstand', '2c287084-c289-36b2-8328-853e381f0ed4', 'de', 'altLabel');
INSERT INTO "values" VALUES ('c63b4e72-19b0-3337-8bfb-8d139c238275', 'E20 Objeto Biológico', '2c287084-c289-36b2-8328-853e381f0ed4', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('247a8e8e-c1cc-39f2-8401-eff70af8a1a2', 'Objeto Biológico', '2c287084-c289-36b2-8328-853e381f0ed4', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('6b79b0f8-3f71-3386-9903-aad0fc3305a6', 'E20 生物体', '2c287084-c289-36b2-8328-853e381f0ed4', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('403dec14-ad89-38d5-8aed-de7d1dffa03b', '生物体', '2c287084-c289-36b2-8328-853e381f0ed4', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('997be5d2-1580-3bdd-b5a0-e3c6360a86c3', 'This class comprises individual items of a material nature, which live, have lived or are natural products of or from living organisms. 
Artificial objects that incorporate biological elements, such as Victorian butterfly frames, can be documented as both instances of E20 Biological Object and E22 Man-Made Object. 
', '2c287084-c289-36b2-8328-853e381f0ed4', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('d55e782c-c8dc-306c-a117-bcab215843e6', 'E21 Person', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('a4f86d30-c05b-31be-8feb-64500c971dc5', 'Person', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'de', 'altLabel');
INSERT INTO "values" VALUES ('4776398a-467d-3616-9528-a9d1515ab1c3', 'E21 Personne', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('e8f50caa-4fc7-3bd4-abaa-7b32c869f874', 'Personne', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('9a71322a-06fb-3a65-9bb8-74058cfa8c93', 'E21 Person', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('e008f17f-9881-3915-84b3-49338d4729ec', 'Person', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'en', 'altLabel');
INSERT INTO "values" VALUES ('9be3774e-248a-3506-b43a-bd132a156898', 'E21 Личность', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('5feaf115-ead2-3baf-b6f9-ec947d1b3e25', 'Личность', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('3e3186f6-b071-3cdf-b066-5d4bbac13741', 'E21 Πρόσωπο', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('c69981bd-23c2-38ec-9eff-dde9f23bed5b', 'Πρόσωπο', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'el', 'altLabel');
INSERT INTO "values" VALUES ('7edec471-b8f1-3e07-98f5-7f0d3e5e0a7e', 'E21 Pessoa', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('f4cc8a5e-c62b-39df-93ba-073e2f37c6a0', 'Pessoa', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('4c01bbac-f0eb-317e-8879-82f7a1a72770', 'E21 人物', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('10451673-5f45-3ebc-b921-39f3f885fc43', '人物', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('ab4ea925-c503-32d2-b45f-b425d998ff00', 'This class comprises real persons who live or are assumed to have lived. 
Legendary figures that may have existed, such as Ulysses and King Arthur, fall into this class if the documentation refers to them as historical figures. In cases where doubt exists as to whether several persons are in fact identical, multiple instances can be created and linked to indicate their relationship. The CRM does not propose a specific form to support reasoning about possible identity.
', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('a93f68cd-7308-3af6-be60-d92a06c4cc8d', 'E22 Objet fabriqué', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('c03612af-c118-3cbb-8a33-c0b08df16f36', 'Objet fabriqué', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('efad6a16-447b-39f1-b559-c7fbc5b2f534', 'E22 Ανθρωπογενές Αντικείμενο', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('f59720f7-6620-3e07-9875-e8e0e344f5c6', 'Ανθρωπογενές Αντικείμενο', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'el', 'altLabel');
INSERT INTO "values" VALUES ('f232f56d-a6b0-3a48-a271-eb9485bb9a0b', 'E22 Künstlicher Gegenstand', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('e0161e8b-0b72-34ea-9eae-39aa80768f84', 'Künstlicher Gegenstand', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'de', 'altLabel');
INSERT INTO "values" VALUES ('dbfc15a0-c30c-3963-abb0-7e1cbf5cca3e', 'E22 Рукотворный Объект', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('233281a1-46b6-39b5-b28f-531eff0c2abf', 'Hergestelltes', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'de', 'altLabel');
INSERT INTO "values" VALUES ('99b62449-957c-31f7-923a-c231b0bbe8ef', 'E24 Chose matérielle fabriquée', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('353e6f0e-afc1-3f85-8df3-0bce8fdf58df', 'Chose matérielle fabriquée', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('bdf157b7-240d-3d40-96db-74b13293c961', 'E24 Coisa Material Fabricada', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('c232d3cf-aa91-3403-9e44-ef8521c776c2', 'Coisa Material Fabricada', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('4a05b3fe-88cb-3881-96d6-b8bd9658abeb', 'E24 人造实体物', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('749c730f-514a-3676-8e50-703cdc2fe494', '人造实体物', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('e7d8be63-d2eb-3fed-a47c-bbfdea68cf4d', 'This class comprises all persistent physical items that are purposely created by human activity.
This class comprises man-made objects, such as a swords, and man-made features, such as rock art. No assumptions are made as to the extent of modification required to justify regarding an object as man-made. For example, a “cup and ring” carving on bedrock is regarded as instance of E24 Physical Man-Made Thing. 
', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('cdb519df-03ec-30e0-9c3f-bc694eff5016', 'E25 Caractéristique fabriquée', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('65f537e3-05fb-38fa-a79c-2c6068bf1440', 'Caractéristique fabriquée', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('e90a4953-b92a-3d65-8ab1-4130a2989de1', 'E25 Man-Made Feature', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('18becfb1-82e9-3489-a7c0-8b6c9b59edd1', 'Man-Made Feature', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'en', 'altLabel');
INSERT INTO "values" VALUES ('15f37443-61fa-3ad4-8bd2-efc035818c25', 'E25 Искусственный Признак', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('8645b4b0-413a-3a9c-8411-4cb1e992d7cc', 'Искусственный Признак', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('e856b5d5-2460-3548-9b31-f30c19ca6340', 'E25 Ανθρωπογενές Μόρφωμα', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('aa2a3dd5-aaf1-3c11-9c23-ff4fbf3c6ae7', 'Ανθρωπογενές Μόρφωμα', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'el', 'altLabel');
INSERT INTO "values" VALUES ('1ec1e1b9-e7c1-31fd-a347-2ee4d3894d15', 'E25 Hergestelltes Merkmal', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('99991683-4866-30de-b15a-e9d0cbd39fd2', 'Hergestelltes Merkmal', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'de', 'altLabel');
INSERT INTO "values" VALUES ('22105abf-3915-31ed-9c53-a04daabab48d', 'E25 Característica Fabricada', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('71e3a9a5-d966-3bfd-98e2-a330f1442491', 'Característica Fabricada', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b11975ad-abce-3b6e-9ae3-70d2d6575e85', 'E25 人造外貌表征', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('b25691eb-67c5-3dde-97f2-5ca4e76fb9f2', '人造外貌表征', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('5cba3bff-24d9-3b92-9e66-63a75f61e26f', 'This class comprises physical features that are purposely created by human activity, such as scratches, artificial caves, artificial water channels, etc. 
No assumptions are made as to the extent of modification required to justify regarding a feature as man-made. For example, rock art or even “cup and ring” carvings on bedrock a regarded as types of E25 Man-Made Feature.
', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('b944068f-e408-30ac-9b79-a2dcc03e3af6', 'E26 Υλικό Μόρφωμα', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('73538491-4732-3309-9869-a50e9de170aa', 'Υλικό Μόρφωμα', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'el', 'altLabel');
INSERT INTO "values" VALUES ('2d709cd2-6061-304d-85d5-e8f4800220f6', 'E26 Physical Feature', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('6055fc28-a5a2-3708-820b-4dcec2f62fcf', 'Physical Feature', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'en', 'altLabel');
INSERT INTO "values" VALUES ('dcf6b406-6f4d-36a0-b904-13609aba7a03', 'E26 Физический Признак', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('52e39e31-a6a4-3c44-a83c-a8bc340ab7d6', 'Физический Признак', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('4fedd4bc-444b-3352-965c-abf17d68a649', 'E26 Materielles Merkmal', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('d1aedac9-5cec-3e8f-92bf-7ad153c47800', 'Materielles Merkmal', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'de', 'altLabel');
INSERT INTO "values" VALUES ('6d048315-6016-3233-9a2e-4e265930c7c7', 'E26 Caractéristique matérielle', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5dffd3a4-6dcb-38c3-91c8-85df89acabba', 'Caractéristique matérielle', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('1fc76a00-e086-3f7f-8f23-152fc0edf2a1', 'E26 Característica Material', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('21a5aef3-8ba7-3e12-bfec-d3436f1d39f5', 'Característica Material', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('67109fb2-a17f-3665-b6cb-719c3cfaac33', 'E26 实体外貌表征', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('88780f26-d385-3538-8087-051c90db9526', '实体外貌表征', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('2ec86c89-4381-336a-a8d8-f51b91d7dd69', 'This class comprises identifiable features that are physically attached in an integral way to particular physical objects. 
Instances of E26 Physical Feature share many of the attributes of instances of E19 Physical Object. They may have a one-, two- or three-dimensional geometric extent, but there are no natural borders that separate them completely in an objective way from the carrier objects. For example, a doorway is a feature but the door itself, being attached by hinges, is not. 
Instances of E26 Physical Feature can be features in a narrower sense, such as scratches, holes, reliefs, surface colours, reflection zones in an opal crystal or a density change in a piece of wood. In the wider sense, they are portions of particular objects with partially imaginary borders, such as the core of the Earth, an area of property on the surface of the Earth, a landscape or the head of a contiguous marble statue. They can be measured and dated, and it is sometimes possible to state who or what is or was responsible for them. They cannot be separated from the carrier object, but a segment of the carrier object may be identified (or sometimes removed) carrying the complete feature. 
This definition coincides with the definition of "fiat objects" (Smith & Varzi, 2000, pp.401-420), with the exception of aggregates of “bona fide objects”. 
', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('c52105b9-2d89-379a-ad24-13b11d8f1894', 'E27 Φυσικός Χώρος', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('accb848a-e08c-367b-aa45-fdfa159a3b4e', 'Φυσικός Χώρος', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'el', 'altLabel');
INSERT INTO "values" VALUES ('69b84d17-3a14-3ec4-bc88-789a6e3ae408', 'E27 Site', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b1534692-bc8f-3419-a022-6b1c269c443e', 'Site', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'en', 'altLabel');
INSERT INTO "values" VALUES ('9ab0e19a-5f55-3751-9801-1f83f4eafa8c', 'E27 Site', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('f04e5a29-8587-3bff-ac07-020e3f45291f', 'Site', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('fd867e8e-a0b5-3d32-a240-6c2061e0c3b7', 'E27 Участок', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('21a43e19-6c47-3c07-9aca-0112c4ff3b3f', 'Участок', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('f61faa68-8329-34a0-81bd-3e24be68827b', 'E27 Gelände', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('844c5b6c-77ef-3c69-8164-e2e8ecda6d08', 'Gelände', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'de', 'altLabel');
INSERT INTO "values" VALUES ('aae681ff-68f6-3c30-a87e-53fc0c4aed70', 'E27 Lugar', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('6007f857-5d4b-39e2-a271-7ed8079a73ea', 'Lugar', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('3f58b281-0145-379f-b221-b1f20e7b2901', 'E27 场地', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('62c8b442-fd1e-3f59-9bf5-a360e74b598e', '场地', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('5a2c355e-ee71-38ed-b420-f1c72c133712', 'This class comprises pieces of land or sea floor. 
In contrast to the purely geometric notion of E53 Place, this class describes constellations of matter on the surface of the Earth or other celestial body, which can be represented by photographs, paintings and maps.
 Instances of E27 Site are composed of relatively immobile material items and features in a particular configuration at a particular location', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('3fe7aed3-7dfe-3161-bd47-4d593647abb8', 'E28 Objet conceptuel', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('1922f29f-bc51-3566-9ff7-57bd18d1a1b4', 'Objet conceptuel', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('516229cf-f820-3709-a7f2-39a24f3d5158', 'E28 Begrifflicher Gegenstand', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('e38e1b58-a1a7-3f34-870d-f70bc3314ba0', 'Begrifflicher Gegenstand', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'de', 'altLabel');
INSERT INTO "values" VALUES ('9501395a-89fb-3aea-92a9-cc2dbb875fcf', 'E28 Концептуальный Объект', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('6ba5fb24-7490-39eb-834f-9e7074014777', 'Концептуальный Объект', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('8459a4ba-aaa9-3066-90a8-4bb11853d4e9', 'E28 Conceptual Object', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('f4d7bb7d-2209-354e-a580-be5ef51903fd', 'Conceptual Object', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('8d895725-ae6f-35bd-826e-e70534e68060', 'E28 Νοητικό Αντικείμενο', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('7c8a8d02-4e63-3d62-a031-86d65be1e3a4', 'Νοητικό Αντικείμενο', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'el', 'altLabel');
INSERT INTO "values" VALUES ('f7c9d5b1-dec3-3218-8a40-2ef8bbc05cb0', 'E28 Objeto Conceitual', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('adc39126-e323-39a1-a818-5886cb2362fd', 'Objeto Conceitual', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('63f4947f-2ff7-387a-b79b-eaa650ac60b4', 'E28 概念物件', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('587b5cf4-2878-301e-b051-05b20c4151ab', '概念物件', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('2e373ae0-b7db-3915-9921-16f191c466e4', 'This class comprises non-material products of our minds and other human produced data that 		have become objects of a discourse about their identity, circumstances of creation or historical 		implication. The production of such information may have been supported by the use of    		technical devices such as cameras or computers.
Characteristically, instances of this class are created, invented or thought by someone, and then may be documented or communicated between persons. Instances of E28 Conceptual Object have the ability to exist on more than one particular carrier at the same time, such as paper, electronic signals, marks, audio media, paintings, photos, human memories, etc.
They cannot be destroyed. They exist as long as they can be found on at least one carrier or in at least one human memory. Their existence ends when the last carrier and the last memory are lost. 
', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('afc7012b-5488-364c-8552-0c6d54f12aa2', 'E29 Σχέδιο', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('56927aee-9fcd-3920-95e1-2814290efd2d', 'Σχέδιο', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'el', 'altLabel');
INSERT INTO "values" VALUES ('a39cafa8-cba0-3051-8b01-40949a61ef46', 'E29 Entwurf oder Verfahren', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('1b9231a0-9169-3d8c-9dc3-b2a2e0bb9182', 'Entwurf oder Verfahren', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'de', 'altLabel');
INSERT INTO "values" VALUES ('d43c2221-d338-335d-b1f9-318cdfb60603', 'E29 Conception ou procédure', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('2101554e-437b-362c-8437-28a4aeed55ea', 'Conception ou procédure', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('b70fb1df-e86c-3c6c-ab04-1f6ac4e22844', 'E29 Проект или Процедура', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('f850c058-c837-3b32-a3e9-1d3b32726ed4', 'Проект или Процедура', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('1ae5568c-8aaf-3ac0-a170-6450b3a73bca', 'E29 Design or Procedure', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('ba7d00ad-53b6-3d06-b656-bf3ed4db1b20', 'Design or Procedure', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'en', 'altLabel');
INSERT INTO "values" VALUES ('f5a9dcec-f703-3218-80cd-231adc14e0e8', 'E29 Projeto ou Procedimento', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('f27186ec-250b-36c8-9422-d5fc25b4d3ff', 'Projeto ou Procedimento', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b008bec6-35e7-3673-9862-bf43bb066fc6', 'E29 设计或程序', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('0c2f52b1-55ee-3625-9262-3d300b6751c7', '设计或程序', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('757bfb5e-3983-366a-99fe-94169ecc48fd', 'This class comprises documented plans for the execution of actions in order to achieve a result of a specific quality, form or contents. In particular it comprises plans for deliberate human activities that may result in the modification or production of instances of E24 Physical Thing. 
Instances of E29 Design or Procedure can be structured in parts and sequences or depend on others. This is modelled using P69 has association with (is associated with). 
Designs or procedures can be seen as one of the following:
1.	A schema for the activities it describes
2.	A schema of the products that result from their application. 
3.	An independent intellectual product that may have never been applied, such as Leonardo da Vinci’s famous plans for flying machines.
Because designs or procedures may never be applied or only partially executed, the CRM models a loose relationship between the plan and the respective product.
', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('f8cbcd8a-7af5-3bac-b5e5-62e7ed97699f', 'E30 Право', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('c020bd2e-8853-3095-bab1-953c69e463cc', 'Право', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('456fa928-5fd7-372c-b318-185c2a214435', 'E30 Δικαίωμα', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('1a7110f0-3d9e-3292-a7c3-5c06747265d7', 'Δικαίωμα', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'el', 'altLabel');
INSERT INTO "values" VALUES ('ffc41645-d034-3234-bf9b-d98009d5d905', 'E30 Droit', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('41bac7e3-7a59-380e-8a14-c6e287c1471d', 'Droit', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('d86a40fe-1e61-3ff1-bb79-fd719ec5a846', 'E30 Right', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('642c0d29-6d44-3181-bbac-9b80ab80d0ed', 'Right', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'en', 'altLabel');
INSERT INTO "values" VALUES ('5c5e5047-bdfb-3ba6-aa78-09e2ea8cc764', 'E30 Recht', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('237a9c9b-aa89-3f02-b66a-b1bf5401f548', 'Recht', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'de', 'altLabel');
INSERT INTO "values" VALUES ('db67fc91-d91b-365b-9f2e-ce2cb9c23fd3', 'E30 Direitos', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('34bcf45b-e02f-3a0f-805d-90148bee3b4d', 'Direitos', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('d3de093d-1fd9-3814-83f6-17f924a172b8', 'E30 权限', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('b5a8cec7-1c5a-37a8-b386-e4b5a74b2be6', '权限', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('7109d707-89b7-3d1d-9e95-a623d7408391', 'This class comprises legal privileges concerning material and immaterial things or their derivatives. 
These include reproduction and property rights', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('116e3300-0b9c-320d-8d16-3e00ecf7cc5e', 'E31 Document', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('fc860453-4562-3834-bf09-511a9f2ac9d3', 'Document', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('9b4e7668-1509-3dc2-aa1c-50ac6aa8bb8e', 'E31 Document', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('e5c9b604-1d07-39bc-bd6a-faf596d7f549', 'Document', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'en', 'altLabel');
INSERT INTO "values" VALUES ('1bcf6f5a-918e-32b1-b8cc-55637cc2551b', 'E31 Dokument', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('29c0fa25-e258-334a-b5a5-a71c958a302b', 'Dokument', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'de', 'altLabel');
INSERT INTO "values" VALUES ('479e4bee-af38-32d6-8167-cfa36ac02f3d', 'E31 Документ', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('057e4466-d121-303c-91db-4f85549503d1', 'Документ', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('42b7d9e0-144e-3c72-938d-6cb9c027e23e', 'E31 Τεκμήριο', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('cabb81d8-30c2-3b42-940b-b943cc9709e9', 'Τεκμήριο', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'el', 'altLabel');
INSERT INTO "values" VALUES ('1638bacb-b579-3ab4-81d1-5067adb551de', 'E31 Documento', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('62c761ab-1bd4-3420-a717-f4231560f5f1', 'Documento', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('99f10b5c-85b6-3541-b23b-7e3aa775d00f', 'E31 文献', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('3a4744e7-1f46-3f79-9535-b007c3719b40', '文献', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('b21f882b-a88d-34d5-9c1d-9b95ec07b262', 'This class comprises identifiable immaterial items that make propositions about reality.
These propositions may be expressed in text, graphics, images, audiograms, videograms or by other similar means. Documentation databases are regarded as a special case of E31 Document. This class should not be confused with the term “document” in Information Technology, which is compatible with E73 Information Object.
', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('b2b81125-13e8-3a14-900a-8f8426ee5f6b', 'E32 Referenzdokument', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('3c9df907-a8c6-3529-ba6e-df09ddce2e97', 'Referenzdokument', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'de', 'altLabel');
INSERT INTO "values" VALUES ('2b04baab-c070-3300-8459-441ae67781ec', 'E32 Официальный Документ', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('70108e66-04a3-39af-8ec4-bf8857ddf5c9', 'Официальный Документ', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('ccfe9f34-9290-3016-8012-f8eafa4013ee', 'E32 Document de référence', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('c6e7c6b6-973c-3971-8ed5-b66d39227d8a', 'Document de référence', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('9846cd49-7d05-3ec0-beb8-ec7ef677fcca', 'E32 Πηγή Καθιερωμένων Όρων', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('5a4bcefa-4c96-3ef5-8f34-323b7cb9e059', 'Πηγή Καθιερωμένων Όρων', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'el', 'altLabel');
INSERT INTO "values" VALUES ('722f11a2-581c-3500-a028-861ac2c34ae9', 'E32 Authority Document', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('599ae678-4bfd-3e72-82b5-3810aaab83f6', 'Authority Document', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'en', 'altLabel');
INSERT INTO "values" VALUES ('08d2e4b4-cee4-3bbc-8007-9f2b698dd30e', 'E32 Documento de Referência', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('8b649de0-412c-3a16-8837-b29af862a9b4', 'Documento de Referência', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('66eb656e-5be5-3719-b82d-e0fa960ca8bd', 'E32 权威文献', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('f22376d5-20c8-33e2-be1b-5303f8c9813b', '权威文献', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('1547c561-9413-3358-9324-cc510cd094d5', 'This class comprises encyclopaedia, thesauri, authority lists and other documents that define terminology or conceptual systems for consistent use.
', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('852215eb-34cf-3d01-82bf-b75d109fbe90', 'E33 Линвистический Объект', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('87b196d5-4439-388b-8a24-000470e02490', 'Линвистический Объект', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('e057f1bf-595f-33d4-8f79-3b466d2ad10d', 'E33 Linguistic Object', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('503c690d-3f95-3c12-b40f-901a50ed0f2f', 'Linguistic Object', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('03d46e0a-cd1b-3e21-af27-c35db9d3ec89', 'E33 Γλωσσικό Αντικείμενο', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('80796de6-cf7a-345c-aee6-7324a9481db7', 'Γλωσσικό Αντικείμενο', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'el', 'altLabel');
INSERT INTO "values" VALUES ('d583d1af-39a2-3b3a-aa3a-f70fe26872c0', 'E33 Objet linguistique', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('541b95a9-ebb2-39cc-9f57-763008d8be6b', 'Objet linguistique', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('2e7b7196-2367-3bdb-ab04-c5d2308b0642', 'E33 Sprachlicher Gegenstand', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('a5b12537-6ede-384b-9479-ffd9556d5e5b', 'Sprachlicher Gegenstand', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'de', 'altLabel');
INSERT INTO "values" VALUES ('dc5c4762-40e4-3dd3-908d-2498a9234026', 'E33 Objeto Lingüístico', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('7486c60a-8e68-3ed6-8cb1-388eb4c4514b', 'Objeto Lingüístico', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('3b5c21e3-596c-31ce-bb38-a1c1803ac91c', 'E33 语言物件', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('4c135170-82ee-32e2-89ec-7bf466dc764f', '语言物件', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('04bfc2b9-ab54-387c-b1de-5d956019f42a', 'This class comprises identifiable expressions in natural language or languages. 
Instances of E33 Linguistic Object can be expressed in many ways: e.g. as written texts, recorded speech or sign language. However, the CRM treats instances of E33 Linguistic Object independently from the medium or method by which they are expressed. Expressions in formal languages, such as computer code or mathematical formulae, are not treated as instances of E33 Linguistic Object by the CRM. These should be modelled as instances of E73 Information Object.
The text of an instance of E33 Linguistic Object can be documented in a note by P3 has note: E62 String
', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('9f3632d8-a9e0-320e-9ce1-b8fbce29c504', 'E34 Επιγραφή', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('22c545ac-d10a-3159-a94d-78975a16b66d', 'Επιγραφή', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'el', 'altLabel');
INSERT INTO "values" VALUES ('21b529cb-5bab-371b-890d-85cdb66576d4', 'E34 Inscription', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('ff1decad-83e3-341b-9f41-ad3ddc3b586d', 'Inscription', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'en', 'altLabel');
INSERT INTO "values" VALUES ('4569f7b5-c53c-3b35-bde3-074c5bb936a0', 'E34 Inscription', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('6a0ef596-4133-3fd4-b2f2-0b7b67d0e708', 'Inscription', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('c28f4ef8-75e7-3481-bd66-7a15b2d61374', 'E34 Надпись', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('6a419820-d4a2-31c7-8f2f-b593707e7c29', 'Надпись', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('8cd69f51-acb2-3f43-9614-7503fa9d16ec', 'E34 Inschrift', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('958211d9-557d-32a5-9826-116b8290e6fb', 'Inschrift', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'de', 'altLabel');
INSERT INTO "values" VALUES ('2af4fadf-341d-3802-a0e7-6e1abec6273a', 'E34 Inscrição', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('1e846fa6-a59d-3478-b71f-3b9922bc34b2', 'Inscrição', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('37bf45e1-4f7b-347e-b6a7-597fd25da16b', 'E34 题字', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('c7d4d2bc-3ecc-3fcc-aaa7-431b8b233a24', '题字', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('84b27b11-eecb-3964-aa69-bdf986eddd5f', 'This class comprises recognisable, short texts attached to instances of E24 Physical Man-Made Thing. 
The transcription of the text can be documented in a note by P3 has note: E62 String. The alphabet used can be documented by P2 has type: E55 Type. This class does not intend to describe the idiosyncratic characteristics of an individual physical embodiment of an inscription, but the underlying prototype. The physical embodiment is modelled in the CRM as E24 Physical Man-Made Thing.
The relationship of a physical copy of a book to the text it contains is modelled using E84 Information Carrier. P128 carries (is carried by): E33 Linguistic Object. 
', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('ee212976-7b40-3b6a-9995-aba9e00efee5', 'E35 Заголовок', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('581e7606-72ae-3677-b866-db34ed7cf801', 'Заголовок', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('c3308d35-5748-39d2-af08-02050f147635', 'E35 Titre', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('03a024c9-db9c-3eda-a898-59f66db2638b', 'Titre', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('6b0663b4-0eb7-3aef-a1cd-69a07a0ab9db', 'E35 Titel', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f3404796-2185-3254-a42f-1ed61dfc30c3', 'Titel', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'de', 'altLabel');
INSERT INTO "values" VALUES ('0f9a7185-c632-33b4-8011-f09f8de71035', 'E35 Title', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('2ab50d13-6065-34f2-a84f-a75d31a66b30', 'Title', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'en', 'altLabel');
INSERT INTO "values" VALUES ('7ea9861b-e88d-3728-8b04-059a7a4d9c42', 'E35 Τίτλος', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('3007533a-a007-3a08-8f35-5ca410d1a86f', 'Τίτλος', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'el', 'altLabel');
INSERT INTO "values" VALUES ('eaf84c63-aeef-3c1b-8d11-105e4d330218', 'E35 Título', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('6befac65-a17b-3041-95c8-c32a4bab1dd8', 'Título', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('d76664e2-0914-3d0e-a0e4-a171a80a9180', 'E35 题目', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('20745e7c-8591-3f25-8c66-c741c681ec09', '题目', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('891b500d-2001-3bf4-968b-abf38056bd54', 'This class comprises the names assigned to works, such as texts, artworks or pieces of music. 
Titles are proper noun phrases or verbal phrases, and should not be confused with generic object names such as “chair”, “painting” or “book” (the latter are common nouns that stand for instances of E55 Type). Titles may be assigned by the creator of the work itself, or by a social group. 
This class also comprises the translations of titles that are used as surrogates for the original titles in different social contexts.
', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('9095ecf7-e0c7-3d94-b4b5-f5bfc6161f05', 'E36 Визуальный Предмет', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('34f69023-dd85-3306-8a5d-4377b1211f86', 'Визуальный Предмет', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('8ba8a912-6138-30e7-96f3-e73f0f279aa1', 'E36 Item visuel', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('965fd7d6-ff71-3288-9cd5-c3b2283e05d6', 'Item visuel', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('4f142c69-fcd8-340b-9e83-fcf71d8cc404', 'E36 Οπτικό Στοιχείο', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('46831bb5-a953-3db1-ac67-9c1f6c688f14', 'Οπτικό Στοιχείο', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'el', 'altLabel');
INSERT INTO "values" VALUES ('73dfb4ba-aa9c-3b10-939d-a59612858336', 'E36 Visual Item', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('2ef2c00b-7696-31e2-a500-e7373dd4f769', 'Visual Item', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'en', 'altLabel');
INSERT INTO "values" VALUES ('2af43765-9ce5-359c-81f8-15ae14b33898', 'E36 Bildliches', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('af88e31b-526b-3cd9-a057-32d42b8e0c32', 'Bildliches', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'de', 'altLabel');
INSERT INTO "values" VALUES ('4da59da1-63d9-388c-a556-e62805d4f948', 'E36 Item Visual', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('9a22fbdb-0272-36b9-8127-77869c775049', 'Item Visual', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('f45ac10f-5c5c-3120-95ec-5d788dca7f96', 'E36 视觉项目', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('54fa8aed-d9ec-3db6-ac6f-3db2f977f7ea', '视觉项目', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('4501ad64-9c0b-33d1-9667-dccd9b9ca319', 'This class comprises the intellectual or conceptual aspects of recognisable marks and images.
This class does not intend to describe the idiosyncratic characteristics of an individual physical embodiment of a visual item, but the underlying prototype. For example, a mark such as the ICOM logo is generally considered to be the same logo when used on any number of publications. The size, orientation and colour may change, but the logo remains uniquely identifiable. The same is true of images that are reproduced many times. This means that visual items are independent of their physical support. 
The class E36 Visual Item provides a means of identifying and linking together instances of E24 Physical Man-Made Thing that carry the same visual symbols, marks or images etc. The property P62 depicts (is depicted by) between E24 Physical Man-Made Thing and depicted subjects (E1 CRM Entity) can be regarded as a short-cut of the more fully developed path from E24 Physical Man-Made Thing through P65 shows visual item (is shown by), E36 Visual Item, P138 represents (has representation) to E1CRM Entity, which in addition captures the optical features of the depiction.  
', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('e3c836fb-8eb9-3129-84e7-962e27182b5a', 'E37 Пометка', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('911b0c9a-8794-3b9f-bd79-30b089d4d6c6', 'Пометка', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('ed5a9eb6-4b08-3133-b3ad-08da027227f9', 'E37 Marque', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('7fbe04f9-727a-3e70-a444-0d80cbc3cabf', 'Marque', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('b7cbcc5a-51eb-3d63-929e-4f3749818c10', 'E37 Σήμανση', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('dbae65bc-7fc2-3288-b019-12972d6b0b81', 'Σήμανση', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'el', 'altLabel');
INSERT INTO "values" VALUES ('081eb0db-c824-336e-bb7b-21c5026101c1', 'E37 Mark', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('442a05d3-d804-30d5-9d47-b4f1a2382951', 'Mark', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'en', 'altLabel');
INSERT INTO "values" VALUES ('ba9ccab3-b716-3448-9caa-5fe7a0b4db3c', 'E37 Marke', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('27d347b4-784d-3f10-9fed-af3c703ce723', 'Marke', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'de', 'altLabel');
INSERT INTO "values" VALUES ('380d61a7-d842-310c-9dd7-a48b7f9c22df', 'E37 Marca', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('0d157099-52fe-3307-9124-fdd58a69dd06', 'Marca', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('26fad3ee-8f92-3ee3-8fd0-139b93f0a1dd', 'E37 标志', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('fd58814e-7c2f-323b-8c98-5afb5c8cad01', '标志', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('84c162bc-0d97-3971-8980-e44a796413a1', 'This class comprises symbols, signs, signatures or short texts applied to instances of E24 Physical Man-Made Thing by arbitrary techniques in order to indicate the creator, owner, dedications, purpose, etc. 
This class specifically excludes features that have no semantic significance, such as scratches or tool marks. These should be documented as instances of E25 Man-Made Feature. 
', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('bebbc7ad-8dde-386e-aa2b-6d673ae8f45e', 'E38 Изображение', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('1e2a78c6-af5f-3589-8e1e-821243fe6457', 'Изображение', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('ced2c4fb-479f-3de6-9bbd-6065ff0c20a4', 'E38 Εικόνα', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ded4a42f-8975-3433-8d79-a331402e49e2', 'Εικόνα', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'el', 'altLabel');
INSERT INTO "values" VALUES ('b52d271f-98f1-3644-a56b-444fdbb502b2', 'E38 Bild', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('23e40fcc-276d-32a8-b58d-9fbfabba653e', 'Bild', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'de', 'altLabel');
INSERT INTO "values" VALUES ('c498f415-fd63-3380-b712-5dfb44dec2a8', 'E38 Image', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('0fe923da-1693-3000-8aef-86521a7fa7f3', 'Image', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('6cb1aeb1-6171-393b-96df-afd7481da94a', 'E38 Image', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b37b8ff1-0c23-3ade-ade0-5788d565c205', 'Image', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'en', 'altLabel');
INSERT INTO "values" VALUES ('5f3ef2f4-ea5c-3f3f-9de2-9ccf4a121b7d', 'E38 Imagem', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('ab70b66d-c886-37d0-b733-f94acc7df7ce', 'Imagem', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('5b852943-e502-3ccf-9a73-3044f39cb19f', 'E38 图像', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('2e0bd036-23bc-3ffc-be0f-59850da483bf', '图像', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('35f90f35-bd66-3ef9-ba99-b45fb394a0c3', 'This class comprises distributions of form, tone and colour that may be found on surfaces such as photos, paintings, prints and sculptures or directly on electronic media. 
The degree to which variations in the distribution of form and colour affect the identity of an instance of E38 Image depends on a given purpose. The original painting of the Mona Lisa in the Louvre may be said to bear the same instance of E38 Image as reproductions in the form of transparencies, postcards, posters or T-shirts, even though they may differ in size and carrier and may vary in tone and colour. The images in a “spot the difference” competition are not the same with respect to their context, however similar they may at first appear.
', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('1f16868f-9f43-3d8b-b7b3-7d91a5472895', 'E39 Akteur', 'af051b0a-be2f-39da-8f46-429a714e242c', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('719b9dee-bcd7-3f49-aebe-a0beabfddb81', 'Akteur', 'af051b0a-be2f-39da-8f46-429a714e242c', 'de', 'altLabel');
INSERT INTO "values" VALUES ('09adf672-b989-3bd5-8590-4cfd277376e5', 'E39 Агент', 'af051b0a-be2f-39da-8f46-429a714e242c', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('d61496b7-cb06-3014-8834-84f5b47a6187', 'Агент', 'af051b0a-be2f-39da-8f46-429a714e242c', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('31a28641-7e93-3986-acc9-21b78170df3a', 'E39 Agent', 'af051b0a-be2f-39da-8f46-429a714e242c', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('55ce5062-f901-36e6-b905-a49295c1b55f', 'Agent', 'af051b0a-be2f-39da-8f46-429a714e242c', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('6a4269c6-95f5-3ad7-98cc-d81eba61413f', 'E39 Δράστης', 'af051b0a-be2f-39da-8f46-429a714e242c', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('d0c17f6c-dd25-393a-a37c-5c254ee61607', 'Δράστης', 'af051b0a-be2f-39da-8f46-429a714e242c', 'el', 'altLabel');
INSERT INTO "values" VALUES ('2495f768-1c3e-348c-8154-f8e93b1e079b', 'E39 Actor', 'af051b0a-be2f-39da-8f46-429a714e242c', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('3a3001e5-426e-3c0d-aa08-ea7c930bd9f8', 'Actor', 'af051b0a-be2f-39da-8f46-429a714e242c', 'en', 'altLabel');
INSERT INTO "values" VALUES ('8e95feac-141b-3489-8023-6c65d047e854', 'E39 Agente', 'af051b0a-be2f-39da-8f46-429a714e242c', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('3f535337-3807-3898-9027-610e3b7b9468', 'Agente', 'af051b0a-be2f-39da-8f46-429a714e242c', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('bb6933ff-2594-3be4-abd3-790a3d901fc5', 'E39 角色', 'af051b0a-be2f-39da-8f46-429a714e242c', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('8284d554-a50b-3268-b015-72dcbf357ad6', '角色', 'af051b0a-be2f-39da-8f46-429a714e242c', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('32018d5e-a4a2-3b47-b640-b3eb1b198fbf', 'This class comprises people, either individually or in groups, who have the potential to perform intentional actions of kinds for which someone may be held responsible.
The CRM does not attempt to model the inadvertent actions of such actors. Individual people should be documented as instances of E21 Person, whereas groups should be documented as instances of either E74 Group or its subclass E40 Legal Body.
', 'af051b0a-be2f-39da-8f46-429a714e242c', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('09c65bf0-da58-34ff-9aab-101c59b24b8c', 'E40 Collectivité', '40a8beed-541b-35cd-b287-b7c345f998fe', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('dd68d550-20ee-3776-bf27-6f258566e4e8', 'Collectivité', '40a8beed-541b-35cd-b287-b7c345f998fe', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('5fe49dce-17c7-3dcc-968a-89adc150f39d', 'E40 Juristische Person', '40a8beed-541b-35cd-b287-b7c345f998fe', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f5334374-e047-3261-aa26-416a5a372a59', 'Juristische Person', '40a8beed-541b-35cd-b287-b7c345f998fe', 'de', 'altLabel');
INSERT INTO "values" VALUES ('3fdbe46e-5759-3d71-9886-85147f6f4453', 'E40 Νομικό Πρόσωπο', '40a8beed-541b-35cd-b287-b7c345f998fe', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('e937ec6d-5a55-3297-9a8e-8e973b691af6', 'Νομικό Πρόσωπο', '40a8beed-541b-35cd-b287-b7c345f998fe', 'el', 'altLabel');
INSERT INTO "values" VALUES ('8dfecb25-c4b3-36f9-93fd-840df9f17957', 'E40 Юридическое Лицо', '40a8beed-541b-35cd-b287-b7c345f998fe', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('088695d6-c2f7-388e-88dd-14bdf1a0bcf8', 'Юридическое Лицо', '40a8beed-541b-35cd-b287-b7c345f998fe', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('b45ca682-d3cc-363d-a9fa-24eec72fa481', 'E40 Legal Body', '40a8beed-541b-35cd-b287-b7c345f998fe', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('13ed511d-e578-3070-ac1f-c507e29f55ab', 'Legal Body', '40a8beed-541b-35cd-b287-b7c345f998fe', 'en', 'altLabel');
INSERT INTO "values" VALUES ('02cea76f-9840-3c9e-9a83-e28657aa684b', 'E40 Pessoa Jurídica', '40a8beed-541b-35cd-b287-b7c345f998fe', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('c9aeddaf-8e87-3a52-82ec-859acd91e254', 'Pessoa Jurídica', '40a8beed-541b-35cd-b287-b7c345f998fe', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('098724c1-2f53-35b2-b5e9-41f1176712ed', 'E40 法律组织', '40a8beed-541b-35cd-b287-b7c345f998fe', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('31554201-2bd2-33ce-89d9-aec45d170344', '法律组织', '40a8beed-541b-35cd-b287-b7c345f998fe', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('fa5ac6a6-0db7-34c4-b3db-c8623252eaf4', 'This class comprises institutions or groups of people that have obtained a legal recognition as a group and can act collectively as agents.  
This means that they can perform actions, own property, create or destroy things and can be held collectively responsible for their actions like individual people. The term ''personne morale'' is often used for this in French. 
', '40a8beed-541b-35cd-b287-b7c345f998fe', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('7c258d91-4be6-33b8-bf25-d374754b0108', 'E41 Benennung', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('093eb81e-55b5-3f53-9e56-8aabf61ef1cf', 'Benennung', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'de', 'altLabel');
INSERT INTO "values" VALUES ('b9e65cac-94fb-317a-9d80-f7785fa56439', 'E41 Обозначение', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('48912e1a-083c-3b41-90dd-41bb40b15a33', 'Обозначение', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('13249d3a-6057-3d52-bfc8-3bb498ae5bd3', 'E41 Appellation', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('c9cd383c-ebc5-32e0-895c-fca5aa5d0116', 'Appellation', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'en', 'altLabel');
INSERT INTO "values" VALUES ('ebdcb5ba-3dca-38aa-9e02-9661e4c45d46', 'E41 Appellation', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('a8cc0373-2331-3b59-9c4c-3e323514b369', 'Appellation', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('5cfa1a75-1497-390b-99c4-2fae73916ae1', 'E41 Ονομασία', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('513b1210-a421-30be-8903-440a7cfda008', 'Ονομασία', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'el', 'altLabel');
INSERT INTO "values" VALUES ('a0f5e3fc-04de-3868-82a0-761bf0c5e9e0', 'E41 Designação', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('b7409c82-175d-3550-a1ea-4b481ec09a70', 'Designação', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('27aa11c6-9a35-3c02-87b6-011edc06a0c1', 'E41 称号', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('728675f5-9745-3f73-a7db-0b6f4d6aab92', '称号', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('48dd205c-43d1-3df9-9867-3bd009054021', 'This class comprises signs, either meaningful or not, or arrangements of signs following a specific syntax, that are used or can be used to refer to and identify a specific instance of some class or category within a certain context.
Instances of E41 Appellation do not identify things by their meaning, even if they happen to have one, but instead by convention, tradition, or agreement. Instances of E41 Appellation are cultural constructs; as such, they have a context, a history, and a use in time and space by some group of users. A given instance of E41 Appellation can have alternative forms, i.e., other instances of E41 Appellation that are always regarded as equivalent independent from the thing it denotes. 
Specific subclasses of E41 Appellation should be used when instances of E41 Appellation of a characteristic form are used for particular objects. Instances of E49 Time Appellation, for example, which take the form of instances of E50 Date, can be easily recognised.
E41 Appellation should not be confused with the act of naming something. Cf. E15 Identifier Assignment
', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('97c19fff-480d-3ace-9ece-3698815a118a', 'E42 Identificateur d''objet', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('05a860ec-8f54-3308-b8c2-c047043aefe3', 'Identificateur d''objet', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('d66bcbdd-4453-38ea-9ded-9881f17f7f7f', 'E42 Κωδικός Αναγνώρισης', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('39035186-5c01-3d62-80fb-51cedfa85432', 'Κωδικός Αναγνώρισης', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'el', 'altLabel');
INSERT INTO "values" VALUES ('0c1b92ae-ddcd-3bbc-91d6-2cc4a1ddaa80', 'E42 Идентификатор Объекта', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('406696c6-69fd-386d-8e22-b73d0e049f4c', 'Идентификатор Объекта', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('4572b39a-6b15-349a-9d96-97fe96e39f47', 'E42 Kennung', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f5299819-7600-3972-9210-d615c9db1f90', 'Kennung', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'de', 'altLabel');
INSERT INTO "values" VALUES ('ee25f970-4978-32f6-9867-28cfa6314f10', 'E42 Identifier', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('52e83abc-ec0a-301f-a95b-65be27864ee8', 'Identifier', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'en', 'altLabel');
INSERT INTO "values" VALUES ('bd828f07-9a52-3ebd-a50c-77bda34efc46', 'E42 Identificador de Objeto', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('d658c087-07ac-3de6-affe-b9f3286d2d41', 'Identificador de Objeto', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('a07abc0d-d2b9-3d98-b6b3-056af1d9ff2a', 'E42 标识符', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('12e39991-eb66-390f-8c04-b7c6fe1d97b1', '标识符', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('e992ce11-0339-37b4-a623-e69a4f685cd9', 'This class comprises strings or codes assigned to instances of E1 CRM Entity in order to identify them uniquely and permanently within the context of one or more organisations. Such codes are often known as inventory numbers, registration codes, etc. and are typically composed of alphanumeric sequences. The class E42 Identifier is not normally used for machine-generated identifiers used for automated processing unless these are also used by human agents.', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('7a1038ff-a573-3832-a4b3-aa798610261c', 'E44 Обозначение Места', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('858b5936-c706-3bfb-a77d-3b56fefaf11a', 'Обозначение Места', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('2f0e3d98-d1ad-3c76-86ac-1caefb95e783', 'E44 Place Appellation', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('02dfc810-ef3c-3393-b124-d4edaae87510', 'Place Appellation', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'en', 'altLabel');
INSERT INTO "values" VALUES ('9a88f70c-e31e-3c5f-b9be-1990e1299598', 'E44 Appellation de lieu', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('cc7ee7ad-4c24-3866-a967-a0e419f42c53', 'Appellation de lieu', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('395e02df-04c7-324d-9ec1-9fe24ef3a915', 'E44 Ortsbenennung', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('8984ed50-79e0-3de7-9330-14c41886fe00', 'Ortsbenennung', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'de', 'altLabel');
INSERT INTO "values" VALUES ('a4b8b5ee-3b30-3815-8016-ef02e6cb30b8', 'E44 Ονομασία Τόπου', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('e559ed40-3654-3de8-ac34-a9c497e0db06', 'Ονομασία Τόπου', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'el', 'altLabel');
INSERT INTO "values" VALUES ('0ba64d47-5316-3486-8139-161276c632af', 'E44 Designação de Local', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('156593c9-dc44-3550-9f5f-db61d16e8036', 'Designação de Local', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('27fe694b-8213-3cb7-bc85-7bada10272cc', 'E44 地点称号', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('edf04c93-5ea3-3dc0-b2c5-1fe6af0b112b', '地点称号', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('8d95e40d-5221-370b-bcd0-cd2f187e7ba0', 'This class comprises any sort of identifier characteristically used to refer to an E53 Place. 
Instances of E44 Place Appellation may vary in their degree of precision and their meaning may vary over time - the same instance of E44 Place Appellation may be used to refer to several places, either because of cultural shifts, or because objects used as reference points have moved around. Instances of E44 Place Appellation can be extremely varied in form: postal addresses, instances of E47 Spatial Coordinate, and parts of buildings can all be considered as instances of E44 Place Appellation.
', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('d250608b-307e-3edf-aced-fb64c730f70f', 'E45 Adresse', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('9060848d-21f7-37f3-966a-991c90fbe9a5', 'Adresse', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('124f7bde-4f61-3824-9971-c28138e293b2', 'E45 Adresse', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('69b6c19b-6d44-3a49-a68e-b110d3c3b7aa', 'Adresse', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'de', 'altLabel');
INSERT INTO "values" VALUES ('b5d4b9ac-31c5-34ee-b447-8e691db6325e', 'E45 Διεύθυνση', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('e59c83f9-57a1-3679-ba45-849b03d0984d', 'Διεύθυνση', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'el', 'altLabel');
INSERT INTO "values" VALUES ('e6496228-7831-3c19-bb9f-814cf03b0a3c', 'E45 Адрес', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('0780f6b1-cef9-31c9-bfa5-6a72b304b723', 'Адрес', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('5368fc93-c65b-31a9-855f-53083a1746d2', 'E45 Address', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('2d46efec-ab75-3284-9e11-cf008bba17f8', 'Address', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'en', 'altLabel');
INSERT INTO "values" VALUES ('03473069-cff1-323e-aac5-06189e2e9937', 'E45 Endereço', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('b6a031c2-d836-3829-9001-d5e7f27d6f52', 'Endereço', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('7d63145b-ba5f-3c34-8af3-2bacb29c19e7', 'E45 地址', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('6c3153a7-bbcc-3370-bfbe-4a5011fceb3a', '地址', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('caec128b-a9c6-39f2-83a7-3edb90372751', 'This class comprises identifiers expressed in coding systems for places, such as postal addresses used for mailing.
An E45 Address can be considered both as the name of an E53 Place and as an E51 Contact Point for an E39 Actor. This dual aspect is reflected in the multiple inheritance. However, some forms of mailing addresses, such as a postal box, are only instances of E51 Contact Point, since they do not identify any particular Place. These should not be documented as instances of E45 Address.
', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('b7b6d95c-3e09-3b62-b737-a41ffa021f22', 'E46 Désignation de section', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('6f76a7b4-bddc-399e-9e49-426ba9ba7a68', 'Désignation de section', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('cb654cfb-63a1-3948-bc31-26438b2f46e2', 'E46 Определение Района', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('5da98d9f-ef6d-3469-9236-806556af9744', 'Определение Района', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('1a7c6a60-ed16-3fd5-9cba-1f2aab67c9cd', 'E46 Section Definition', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('3e7894e4-0790-3730-81a6-a41b19f6eeb7', 'Section Definition', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'en', 'altLabel');
INSERT INTO "values" VALUES ('a5b4a068-2228-3dc7-a5a7-ff7f7f2268d4', 'E46 Abschnittsdefinition', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('59aa4f5c-2ab7-325a-9430-3cf7232d1dbc', 'Abschnittsdefinition', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'de', 'altLabel');
INSERT INTO "values" VALUES ('682fddb4-3d6a-3559-821e-f92988558920', 'E46 Ονομασία Τμήματος', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('a6c639d8-8440-3cbe-9fca-d829a73a3c40', 'Ονομασία Τμήματος', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'el', 'altLabel');
INSERT INTO "values" VALUES ('281b10cb-e7f2-3f2d-9dfd-c70f72a38d96', 'E46 Designação de Seção', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('118064af-426e-387b-bf21-db770af0bd81', 'Designação de Seção', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('c89a314a-6b56-374f-802b-b2c36152fbe1', 'E46 区域定义', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('e2aa914a-9e90-3ec7-ad36-5640bd48d504', '区域定义', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('54bcc8ce-292b-3c42-8f13-0f0435a0b01f', 'This class comprises areas of objects referred to in terms specific to the general geometry or structure of its kind. 
The ''prow'' of the boat, the ''frame'' of the picture, the ''front'' of the building are all instances of E46 Section Definition. The class highlights the fact that parts of objects can be treated as locations. This holds in particular for features without natural boundaries, such as the “head” of a marble statue made out of one block (cf. E53 Place). In answer to the question ''where is the signature?'' one might reply ''on the lower left corner''. (Section Definition is closely related to the term “segment” in Gerstl, P.& Pribbenow, S, 1996 “ A conceptual theory of part – whole relations and its applications”, Data & Knowledge 	Engineering 20 305-322, North Holland- Elsevier ).
', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('7435e0f2-da32-3885-8a95-6cad11c09317', 'E47 Coordonnées spatiales', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('a0cd224b-5c24-3b20-877b-3030185d9ad1', 'Coordonnées spatiales', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('70a9a934-01c9-31cd-9701-6e4f0a69f59d', 'E47 Пространственные Координаты', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('eb380b7c-23eb-37bb-864f-260df02fcaae', 'Пространственные Координаты', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('d0745b59-65f5-3a62-a509-278f13059b37', 'E47 Χωρικές Συντεταγμένες', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ac262f95-5c86-3c12-b8f5-544f8b7a2044', 'Χωρικές Συντεταγμένες', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'el', 'altLabel');
INSERT INTO "values" VALUES ('fd52e03a-9d3b-3a19-926c-9cb2f9511217', 'E47 Raumkoordinaten', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('9e32ac99-e36f-3b9a-be2d-72e7c6e19bf3', 'Raumkoordinaten', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'de', 'altLabel');
INSERT INTO "values" VALUES ('513b6d1e-8559-334a-85ec-99c90a8f05ed', 'E47 Spatial Coordinates', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('bad5d160-e77b-3ede-83fd-344e67e7cdc0', 'Spatial Coordinates', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'en', 'altLabel');
INSERT INTO "values" VALUES ('98be708f-b227-3b5a-8a27-e12a942ff97b', 'E47 Coordenadas Espaciais', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('cfda3f23-1e12-32d0-a283-8df8a4102e38', 'Coordenadas Espaciais', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('54fb45ec-1b46-3f82-8ced-5b824f39073f', 'E47 空间坐标', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('a6c0b7f8-6dca-38ec-9d07-ecf9e157081e', '空间坐标', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('114f5c4c-09af-3ec8-9443-b4ddf45d5bdf', 'This class comprises the textual or numeric information required to locate specific instances of E53 Place within schemes of spatial identification. 

Coordinates are a specific form of E44 Place Appellation, that is, a means of referring to a particular E53 Place. Coordinates are not restricted to longitude, latitude and altitude. Any regular system of reference that maps onto an E19 Physical Object can be used to generate coordinates.
', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('fa252599-fa91-39a9-834b-54e6e0b7866a', 'E48 Название Места', 'e276711d-008c-3380-934b-e048a6a0d665', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('0ab8201a-b72c-3102-b2ac-58fe31fad1bf', 'Название Места', 'e276711d-008c-3380-934b-e048a6a0d665', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('02593d8f-51f3-3b33-982d-018bc64aa7c3', 'E48 Toponyme', 'e276711d-008c-3380-934b-e048a6a0d665', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('896ea210-2b6a-39ea-917d-a57b33d8c533', 'Toponyme', 'e276711d-008c-3380-934b-e048a6a0d665', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('c19e3e33-84f3-3e74-bd0d-8276cc69ef50', 'E48 Τοπωνύμιο', 'e276711d-008c-3380-934b-e048a6a0d665', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('b9ed3733-ab22-353f-b385-a825f592e255', 'Τοπωνύμιο', 'e276711d-008c-3380-934b-e048a6a0d665', 'el', 'altLabel');
INSERT INTO "values" VALUES ('baba35f6-7853-3b3c-89f6-248dfcf35f29', 'E48 Place Name', 'e276711d-008c-3380-934b-e048a6a0d665', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('d4345be0-873f-3752-935a-4d2eac21c0ef', 'Place Name', 'e276711d-008c-3380-934b-e048a6a0d665', 'en', 'altLabel');
INSERT INTO "values" VALUES ('1815412e-e0d8-3a55-92a0-d4f28cfeecb4', 'E48 Orts- oder Flurname', 'e276711d-008c-3380-934b-e048a6a0d665', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('0884d6b6-aa1f-3423-be4b-3b63006e93a9', 'Orts- oder Flurname', 'e276711d-008c-3380-934b-e048a6a0d665', 'de', 'altLabel');
INSERT INTO "values" VALUES ('f1e243d6-c878-333f-bb59-a5d236febf58', 'E48 Nome de Local', 'e276711d-008c-3380-934b-e048a6a0d665', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('b29261cb-844c-3b6c-b842-e3c0318abe45', 'Nome de Local', 'e276711d-008c-3380-934b-e048a6a0d665', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('013aa60a-796f-3df6-9819-4ee78a72ff6d', 'E48 地名', 'e276711d-008c-3380-934b-e048a6a0d665', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('1678ad6e-80f8-3368-a2bf-3f662fbab10c', '地名', 'e276711d-008c-3380-934b-e048a6a0d665', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('afa0bd5f-69b0-39af-a4b3-638ddbf77aa2', 'This class comprises particular and common forms of E44 Place Appellation. 
Place Names may change their application over time: the name of an E53 Place may change, and a name may be reused for a different E53 Place. Instances of E48 Place Name are typically subject to place name gazetteers.', 'e276711d-008c-3380-934b-e048a6a0d665', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('1afb013a-6ac8-38b9-99f2-aa278453947b', 'E49 Обозначение Времени', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('c2a06fd4-9c26-3565-91c1-913af9e92f77', 'Обозначение Времени', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('5e99394d-4d2d-3c19-ac09-259f92a5d013', 'E49 Ονομασία Χρόνου', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('c6fb0315-dc0e-3c35-911c-0b1ed1ccc8df', 'Ονομασία Χρόνου', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'el', 'altLabel');
INSERT INTO "values" VALUES ('6182fce5-e39d-339a-a5a1-f52adfdb5b93', 'E49 Zeitbenennung', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('2c0faab6-2e2f-3f1d-b08b-8cc266d02c21', 'Zeitbenennung', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'de', 'altLabel');
INSERT INTO "values" VALUES ('e15086ef-9bee-3c07-9fb1-b0648cf0b332', 'E49 Time Appellation', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('662d7fad-6e76-341e-a780-5e9edcce6b22', 'Time Appellation', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'en', 'altLabel');
INSERT INTO "values" VALUES ('0f750c49-2731-3bc0-bfcb-afe7d6ed0717', 'E49 Appellation temporelle', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('6a3b6a84-da1a-3200-8016-e1d2e1d5f749', 'Appellation temporelle', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('43029259-ef06-3043-9d40-c7f6207fe186', 'E49 Designação de Tempo', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('904092d9-2d0d-38e4-928c-07a1b55d6dca', 'Designação de Tempo', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('0efba2c2-3d9a-3394-8606-53502abf26b2', 'E49 时间称号', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('70862777-d7dc-3fd6-aa92-be7ca15ec599', '时间称号', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('cea57234-3f08-3fe9-ae21-6ec2b62385b0', 'This class comprises all forms of names or codes, such as historical periods, and dates, which are characteristically used to refer to a specific E52 Time-Span. 
The instances of E49 Time Appellation may vary in their degree of precision, and they may be relative to other time frames, “Before Christ” for example. Instances of E52 Time-Span are often defined by reference to a cultural period or an event e.g. ‘the duration of the Ming Dynasty’.', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('72683954-679a-3919-b5db-e425ea7c764d', 'E50 Datum', 'c8b36269-f507-32fc-8624-2a9404390719', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('80899210-48ea-33c3-b1d1-0effeac5234a', 'Datum', 'c8b36269-f507-32fc-8624-2a9404390719', 'de', 'altLabel');
INSERT INTO "values" VALUES ('16c6a223-0768-34c2-8524-4cd6089e6680', 'E50 Ημερομηνία', 'c8b36269-f507-32fc-8624-2a9404390719', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('211d77df-b495-3542-ba8e-eac2581446a6', 'Ημερομηνία', 'c8b36269-f507-32fc-8624-2a9404390719', 'el', 'altLabel');
INSERT INTO "values" VALUES ('1cebc5dd-d8b6-3e05-8962-31ea2a3f82a0', 'E50 Дата', 'c8b36269-f507-32fc-8624-2a9404390719', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('2b085e59-7ec3-32d7-9919-c111c7901be4', 'Дата', 'c8b36269-f507-32fc-8624-2a9404390719', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('139a7c84-f1f8-3664-bd5e-e6a67b869c13', 'E50 Date', 'c8b36269-f507-32fc-8624-2a9404390719', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('180c32e8-78ed-389c-bb5d-bfcd8eebc2d6', 'Date', 'c8b36269-f507-32fc-8624-2a9404390719', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('f68829a7-49e2-3d5e-9718-333478b4a95f', 'E50 Date', 'c8b36269-f507-32fc-8624-2a9404390719', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b228a53a-cb6a-372b-91a2-8da52d887551', 'Date', 'c8b36269-f507-32fc-8624-2a9404390719', 'en', 'altLabel');
INSERT INTO "values" VALUES ('f9746df8-ba38-3293-9902-82fa86594255', 'E50 Data', 'c8b36269-f507-32fc-8624-2a9404390719', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('af977e05-41fb-3c29-b0e3-963bfce0f982', 'Data', 'c8b36269-f507-32fc-8624-2a9404390719', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('68503581-b36d-3297-8abb-60614d87f271', 'E50 日期', 'c8b36269-f507-32fc-8624-2a9404390719', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('87c77375-0cfb-31e9-a997-f62b9de03b57', '日期', 'c8b36269-f507-32fc-8624-2a9404390719', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('365cffb1-f03b-3a6d-bd49-3eb69ec5edd7', 'This class comprises specific forms of E49 Time Appellation.', 'c8b36269-f507-32fc-8624-2a9404390719', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('0c001e1d-50ef-39a7-97a9-c095f6c1d8ba', 'E51 Kontaktpunkt', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('26971487-2c43-3664-b874-ba8da1c29c62', 'Kontaktpunkt', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'de', 'altLabel');
INSERT INTO "values" VALUES ('c44751dc-b0c2-3a38-a44a-939ab605cfb7', 'E51 Στοιχείο Επικοινωνίας', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('c587e31e-58c6-3953-8edd-a25f3870ce40', 'Στοιχείο Επικοινωνίας', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'el', 'altLabel');
INSERT INTO "values" VALUES ('540e8164-95ef-3fc5-92b0-cb5a28e24b1a', 'E51 Coordonnées individuelles', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('229bffe6-1c51-3617-8595-ee7a60a2b3e5', 'Coordonnées individuelles', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('54afb505-df98-31c0-a8eb-74726c825ded', 'E51 Contact Point', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('5bb784f8-a93b-316c-b21b-abea5f841178', 'Contact Point', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'en', 'altLabel');
INSERT INTO "values" VALUES ('6893350f-cbdf-3b77-b242-a8d0c46160eb', 'E51 Контакт', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('05a1d50f-d920-346c-b465-86075d618bab', 'Контакт', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('a9db5615-4224-36b2-969e-68d6fb71d5bf', 'E51 Ponto de Contato', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('94eb9ea1-9084-3324-898d-2143055a4a1d', 'Ponto de Contato', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('a2c9768f-cb0a-38bc-8151-9c8ce4531e76', 'E51 联系方式', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('f02d1f3c-407b-31e1-aa4b-0d012a0aa63a', '联系方式', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('1ffb0870-74f5-3bf0-8582-aec908c01297', 'This class comprises identifiers employed, or understood, by communication services to direct communications to an instance of E39 Actor. These include E-mail addresses, telephone numbers, post office boxes, Fax numbers, URLs etc. Most postal addresses can be considered both as instances of E44 Place Appellation and E51 Contact Point. In such cases the subclass E45 Address should be used. 
URLs are addresses used by machines to access another machine through an http request. Since the accessed machine acts on behalf of the E39 Actor providing the machine, URLs are considered as instances of E51 Contact Point to that E39 Actor.
', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('00a38562-1d84-3cbe-aafb-bd305c02797b', 'E52 Durée', '9d55628a-0085-3b88-a939-b7a327263f53', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('c24357c1-442e-31c7-8529-923ade6e0da0', 'Durée', '9d55628a-0085-3b88-a939-b7a327263f53', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('ab923eda-84cc-3f27-82e2-c0b3999bc52a', 'E52 Zeitspanne', '9d55628a-0085-3b88-a939-b7a327263f53', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('7d15f304-5b17-35de-909b-f01074dffa42', 'Zeitspanne', '9d55628a-0085-3b88-a939-b7a327263f53', 'de', 'altLabel');
INSERT INTO "values" VALUES ('9958e26a-e889-31d4-8dd1-6c3cca836abb', 'E52 Интервал Времени', '9d55628a-0085-3b88-a939-b7a327263f53', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('d192a90f-da70-3566-9777-489ab1d1d37e', 'Интервал Времени', '9d55628a-0085-3b88-a939-b7a327263f53', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('6114e3f6-d5db-3a34-bbae-625601a7b40b', 'E52 Χρονικό Διάστημα', '9d55628a-0085-3b88-a939-b7a327263f53', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('7c27b0ee-3c46-3b65-9ad3-fde0a083b246', 'Χρονικό Διάστημα', '9d55628a-0085-3b88-a939-b7a327263f53', 'el', 'altLabel');
INSERT INTO "values" VALUES ('5b156b14-caa3-3747-a90d-f1e8bbf58015', 'E52 Time-Span', '9d55628a-0085-3b88-a939-b7a327263f53', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b82aaf6b-1afd-3305-b296-7f64ae1e1928', 'Time-Span', '9d55628a-0085-3b88-a939-b7a327263f53', 'en', 'altLabel');
INSERT INTO "values" VALUES ('2c1c2e3f-d737-35d0-afb6-a36f041e9dba', 'E52 Período de Tempo', '9d55628a-0085-3b88-a939-b7a327263f53', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('56321d6c-3161-3cd6-b036-cdec73af5128', 'Período de Tempo', '9d55628a-0085-3b88-a939-b7a327263f53', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('6003caa7-6499-375e-8520-aa8b505006f1', 'E52 时段', '9d55628a-0085-3b88-a939-b7a327263f53', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('7a679758-6ae3-305e-8a9a-5a1c645a9eab', '时段', '9d55628a-0085-3b88-a939-b7a327263f53', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('ccccad81-dfb8-39e1-b975-76ef5dffdbd0', 'This class comprises abstract temporal extents, in the sense of Galilean physics, having a beginning, an end and a duration. 
Time Span has no other semantic connotations. Time-Spans are used to define the temporal extent of instances of E4 Period, E5 Event and any other phenomena valid for a certain time. An E52 Time-Span may be identified by one or more instances of E49 Time Appellation. 
Since our knowledge of history is imperfect, instances of E52 Time-Span can best be considered as approximations of the actual Time-Spans of temporal entities. The properties of E52 Time-Span are intended to allow these approximations to be expressed precisely.  An extreme case of approximation, might, for example, define an E52 Time-Span having unknown beginning, end and duration. Used as a common E52 Time-Span for two events, it would nevertheless define them as being simultaneous, even if nothing else was known. 
	Automatic processing and querying of instances of E52 Time-Span is facilitated if data can be parsed into an E61 Time Primitive.
', '9d55628a-0085-3b88-a939-b7a327263f53', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('284bdf0a-4b54-3edc-a598-024f9799a57b', 'E53 Lieu', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('4107c20e-1edf-3623-997a-5253ce657fd0', 'Lieu', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('68fcfdc8-0e00-3bc0-9287-ee5004c4a7e2', 'E53 Place', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('ab6296af-69c1-333c-9ed3-c2fa2013d17f', 'Place', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'en', 'altLabel');
INSERT INTO "values" VALUES ('b7bd2286-4aad-3055-b4db-adf60af2a21f', 'E53 Τόπος', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('4faa2253-c484-32e6-8212-fd8129ade995', 'Τόπος', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'el', 'altLabel');
INSERT INTO "values" VALUES ('7fa20eab-ef83-3272-b360-7d8cb3a7f0b0', 'E53 Место', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('3eac1c69-1624-3a48-a66f-5423c4a54d0c', 'Место', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('8664cc97-4df6-375b-8fec-780289b00e2e', 'E53 Ort', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('c2acca1b-76a9-3d56-a990-a2bc07d2a411', 'Ort', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'de', 'altLabel');
INSERT INTO "values" VALUES ('656ca5ea-0046-3cf5-a56f-f6241ee7700a', 'E53 Local', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('855db895-1d79-3581-96be-21a2c9bd101e', 'Local', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('1a68df8e-2a42-31e4-b516-60cc4f96d2b1', 'E53 地点', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('cb96fa63-d797-3800-8c9f-0884f7efbb25', '地点', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('830017a6-657c-3600-a914-431b848d15e7', 'Материал', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('b101ee80-2b7f-3b02-bf1f-9f24f1b39197', 'E57 Material', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('5d805fa8-b861-30dc-bc52-8d19f2b75052', 'This class comprises extents in space, in particular on the surface of the earth, in the pure sense of physics: independent from temporal phenomena and matter. 
The instances of E53 Place are usually determined by reference to the position of “immobile” objects such as buildings, cities, mountains, rivers, or dedicated geodetic marks. A Place can be determined by combining a frame of reference and a location with respect to this frame. It may be identified by one or more instances of E44 Place Appellation.
 It is sometimes argued that instances of E53 Place are best identified by global coordinates or absolute reference systems. However, relative references are often more relevant in the context of cultural documentation and tend to be more precise. In particular, we are often interested in position in relation to large, mobile objects, such as ships. For example, the Place at which Nelson died is known with reference to a large mobile object – H.M.S Victory. A resolution of this Place in terms of absolute coordinates would require knowledge of the movements of the vessel and the precise time of death, either of which may be revised, and the result would lack historical and cultural relevance.
Any object can serve as a frame of reference for E53 Place determination. The model foresees the notion of a "section" of an E19 Physical Object as a valid E53 Place determination.', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('cf2b5ed8-f9eb-36b4-91a7-ceb14c8162d6', 'E54 Dimension', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('ae41955f-d08e-373a-9048-dc3adcd68b66', 'Dimension', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'en', 'altLabel');
INSERT INTO "values" VALUES ('92ae2abd-d6cf-3df4-bc00-8950a7f3b889', 'E54 Dimensions', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('437b7a3a-a27a-3d9c-b1c7-44771bfce12b', 'Dimensions', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('6f6f1414-d56e-3079-bac8-59ce4f233fa2', 'E54 Μέγεθος', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('84b3c731-ac59-38bf-94d9-390214ca4947', 'Μέγεθος', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'el', 'altLabel');
INSERT INTO "values" VALUES ('32b9e3df-6def-3987-82b7-bb843b0d23f8', 'E54 Величина', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('942251b3-c2b7-334e-82f8-43df26181059', 'Величина', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('7328b1c0-a0e8-3dbc-88d3-22615a96cc91', 'E54 Maß', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f7d79b66-9752-3cd3-8e39-6c1315adf625', 'Maß', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'de', 'altLabel');
INSERT INTO "values" VALUES ('df08a6d5-80f6-3bb9-b9b4-aacd7a82dd9a', 'E54 Dimensão', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('4c9e138d-7925-39d4-ac0a-55c3652a6fea', 'Dimensão', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('3464e1dc-1ace-3284-8468-5f8d88ff19b4', 'E54 规模数量', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('30c7547a-27cb-3d0c-bad4-b03ad9dd760c', '规模数量', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('3b146b4a-17d4-3059-8aa4-42a1e480fa3d', 'This class comprises quantifiable properties that can be measured by some calibrated means and can be approximated by values, i.e. points or regions in a mathematical or conceptual space, such as natural or real numbers, RGB values etc.
An instance of E54 Dimension represents the true quantity, independent from its numerical approximation, e.g. in inches or in cm. The properties of the class E54 Dimension allow for expressing the numerical approximation of the values of an instance of E54 Dimension. If the true values belong to a non-discrete space, such as spatial distances, it is recommended to record them as approximations by intervals or regions of indeterminacy enclosing the assumed true values. For instance, a length of 5 cm may be recorded as 4.5-5.5 cm, according to the precision of the respective observation. Note, that interoperability of values described in different units depends critically on the representation as value regions.
Numerical approximations in archaic instances of E58 Measurement Unit used in historical records should be preserved. Equivalents corresponding to current knowledge should be recorded as additional instances of E54 Dimension as appropriate.
', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('2ea60c85-edeb-38f9-a9c8-d5ea8f350b18', 'E55 Τύπος', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('cc97e7d0-2ddf-3135-ae73-7adf2b895268', 'Τύπος', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'el', 'altLabel');
INSERT INTO "values" VALUES ('21840359-53b1-3985-b42c-0f8056330478', 'E55 Type', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('938969ad-55e6-3ab9-9093-7d27676df443', 'Type', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'en', 'altLabel');
INSERT INTO "values" VALUES ('265c97ec-0ff2-3480-a53c-1cf6bcae7899', 'E55 Type', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('aa79387c-1ab7-3a01-9cb7-bf30f96493a1', 'Type', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('42756498-12ae-3184-982f-250fe1f25cb1', 'E55 Тип', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('e6798f24-fd13-3c88-a37a-943ddb1933b4', 'Тип', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('43b752cb-4603-3af7-b40f-82b9d9c18869', 'E55 Typus', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('0b03d672-95d6-3b19-9983-fe61eaff9ccf', 'Typus', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'de', 'altLabel');
INSERT INTO "values" VALUES ('97a09c20-ecf2-3117-bf44-bc02d55acde3', 'E55 Tipo', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('9e156372-0c5d-3714-ac0a-54b554f2b6fd', 'Tipo', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('94bab250-4ce4-3c69-adb1-afaeaf86b836', 'E55 类型', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('2b16182b-bfcb-3294-a07a-9a5f0a9e8bee', '类型', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('d8ee5aaa-88fb-3a3b-9e21-394ef62d1468', 'This class comprises concepts denoted by terms from thesauri and controlled vocabularies used to characterize and classify instances of CRM classes. Instances of E55 Type represent concepts  in contrast to instances of E41 Appellation which are used to name instances of CRM classes. 
E55 Type is the CRM’s interface to domain specific ontologies and thesauri. These can be represented in the CRM as subclasses of E55 Type, forming hierarchies of terms, i.e. instances of E55 Type linked via P127 has broader  term (has narrower term). Such hierarchies may be extended with additional properties. 
', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('8252e21a-7ee8-32ff-85e5-51540b4bc764', 'E56 Langue', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('f84ae4f0-7ef5-37b6-8471-bd50eb0174cd', 'Langue', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('9962f73d-5bed-3a41-a383-98a09bd75c1e', 'E56 Язык', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('a037f955-b7eb-3a99-b0b2-e1e3b0b0e6f5', 'Язык', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('14cb0557-d390-3863-b1b4-c9df9da6a154', 'E56 Language', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('3cab60f1-e379-34af-8964-6dcab6f8746f', 'Language', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'en', 'altLabel');
INSERT INTO "values" VALUES ('dd8eacc1-c797-3045-978e-0c3e86aa6c84', 'E56 Γλώσσα', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ee31d0fa-9e9e-3ad5-82e4-8d667781064e', 'Γλώσσα', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'el', 'altLabel');
INSERT INTO "values" VALUES ('33180851-6678-3669-a72a-44581a442cc8', 'E56 Sprache', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('93286ff3-e75e-3d76-a455-07c2d1242995', 'Sprache', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'de', 'altLabel');
INSERT INTO "values" VALUES ('f7608e3d-64b5-3553-9bd7-7f2137d7d77e', 'E56 Língua', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('54855516-4529-37ca-9b71-2c8ddd595a31', 'Língua', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('40bf390d-e71b-3b45-b66a-62741b79e1cd', 'E56 语言', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('e5ebb234-7a3e-37ef-a247-30cf946eb1ec', '语言', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('6fa6db87-5873-31b4-90a8-ea20c4065668', 'This class is a specialization of E55 Type and comprises the natural languages in the sense of concepts. 
This type is used categorically in the model without reference to instances of it, i.e. the Model does not foresee the description of instances of instances of E56 Language, e.g.: “instances of  Mandarin Chinese”.
It is recommended that internationally or nationally agreed codes and terminology are used to denote instances of E56 Language, such as those defined in ISO 639:1988. 
', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('1d588ac4-028d-3c0a-89a0-e1ba619d39e1', 'E57 Matériau', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('bb955e9b-bc3b-37ca-8388-07c00577b2f0', 'Matériau', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('92b1e84d-26ab-32e1-84ba-82b7d1615a4b', 'E57 Υλικό', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('95b42c6d-4a83-3959-9097-43e218ca4f2f', 'Υλικό', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'el', 'altLabel');
INSERT INTO "values" VALUES ('e3c5cc0a-d6cb-3971-9689-4fde9e78fbe5', 'E57 Материал', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('a37b1064-036e-34e9-b6e4-a02e3172f3d1', 'Material', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'en', 'altLabel');
INSERT INTO "values" VALUES ('e3bb0f9e-7337-3d59-b073-7c49cf2c5313', 'E57 Material', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('4d4edba7-4503-3547-b28d-bf3bb5aac726', 'Material', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'de', 'altLabel');
INSERT INTO "values" VALUES ('319e2264-f038-34e5-a0a3-34eb8e337c79', 'E57 Material', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('acc1a3bd-28fb-306e-9f04-66bb3857e401', 'Material', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('5d4006de-ce04-30a5-a943-e5d0a11fac7c', 'E57 材料', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('8158956d-54a4-3722-a905-2dabe5b69d98', '材料', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('04a98948-f653-3814-8e33-3bd954fa255b', 'This class is a specialization of E55 Type and comprises the concepts of materials. 
Instances of E57 Material may denote properties of matter before its use, during its use, and as incorporated in an object, such as ultramarine powder, tempera paste, reinforced concrete. Discrete pieces of raw-materials kept in museums, such as bricks, sheets of fabric, pieces of metal, should be modelled individually in the same way as other objects. Discrete used or processed pieces, such as the stones from Nefer Titi''s temple, should be modelled as parts (cf. P46 is composed of).
This type is used categorically in the model without reference to instances of it, i.e. the Model does not foresee the description of instances of instances of E57 Material, e.g.: “instances of  gold”.
It is recommended that internationally or nationally agreed codes and terminology are used.', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('4cc196c2-476c-3916-8647-b152da672b5c', 'E58 Unité de mesure', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('38051afb-804c-360d-acc8-f1fdf6bb83b5', 'Unité de mesure', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('2de2bd88-103c-39d4-8beb-03e6c15c3ce1', 'E58 Measurement Unit', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b1000561-2439-3f47-bb65-bbe5081c0c20', 'Measurement Unit', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'en', 'altLabel');
INSERT INTO "values" VALUES ('234cad4a-9872-3487-b9f5-19efbaa74a84', 'E58 Μονάδα Μέτρησης', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ec3dc6ca-121f-3c6e-9ccb-4d370403028f', 'Μονάδα Μέτρησης', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'el', 'altLabel');
INSERT INTO "values" VALUES ('3d702ab7-baf9-339c-9ac5-367f8764607b', 'E58 Maßeinheit', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('4905ccda-b13b-35ee-9efe-621ba68e8625', 'Maßeinheit', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'de', 'altLabel');
INSERT INTO "values" VALUES ('3c400a91-971e-3226-b240-47c82e385e6b', 'E58 Единица Измерения', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('6d615c6a-2b98-346d-9033-78a3ed8bd10d', 'Единица Измерения', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('a3e99a8d-8750-309b-91eb-d142450b1dd6', 'E58 Unidade de Medida', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('f81281a6-6867-32ec-9f71-b82cf8ef1be6', 'Unidade de Medida', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('272a1017-c8ee-3277-884c-9d8155ed9e2c', 'E58 测量单位', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('850ad545-9a36-31fa-b520-4a039f285d02', '测量单位', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('547c3a23-02c3-35ea-b9e2-4c0618e45a2a', 'This class is a specialization of E55 Type and comprises the types of measurement units: feet, inches, centimetres, litres, lumens, etc. 
This type is used categorically in the model without reference to instances of it, i.e. the Model does not foresee the description of instances of instances of E58 Measurement Unit, e.g.: “instances of cm”.
Syst?me International (SI) units or internationally recognized non-SI terms should be used whenever possible. (ISO 1000:1992). Archaic Measurement Units used in historical records should be preserved.
', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('1ed529d3-327a-36be-b4c3-6d0d236cfd3e', 'E59 Primitive Value', '8471e471-3045-3269-a9b8-86d0e6065176', 'en-US', 'prefLabel');
INSERT INTO "values" VALUES ('87b6c0e6-4187-39f7-921b-a5d51448120d', 'Primitive Value', '8471e471-3045-3269-a9b8-86d0e6065176', 'en-US', 'altLabel');
INSERT INTO "values" VALUES ('0f3e6fe7-e285-32a7-9c98-0e069b5d3986', 'This class comprises values of primitive data types of programming languages or database management systems and data types composed of such values used as documentation elements, as well as their mathematical abstractions. 
', '8471e471-3045-3269-a9b8-86d0e6065176', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('488ade58-c35f-3c04-88ce-7c7c09ab76e4', 'E60 Number', '30c58f1c-03f4-36f8-9f50-4fefc84bb0a6', 'en-US', 'prefLabel');
INSERT INTO "values" VALUES ('f305fb17-07e8-3bbb-97cd-9838fd1d5c8d', 'Number', '30c58f1c-03f4-36f8-9f50-4fefc84bb0a6', 'en-US', 'altLabel');
INSERT INTO "values" VALUES ('2177483b-e4b0-36cb-a816-43bc5ec93696', 'This class comprises any encoding of computable (algebraic) values such as integers, real numbers, complex numbers, vectors, tensors etc., including intervals of these values to express limited precision
', '30c58f1c-03f4-36f8-9f50-4fefc84bb0a6', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('5600be76-f055-35e9-ae03-66af744b8bb5', 'E61 Time Primitive', 'fd8302b4-921b-300c-a9bf-c50d92418797', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('eaef72f7-e2ac-3899-9e93-1fcb2d6ecc95', 'Time Primitive', 'fd8302b4-921b-300c-a9bf-c50d92418797', 'en', 'altLabel');
INSERT INTO "values" VALUES ('f5506c04-1e55-392d-a971-8046635fd940', 'This class comprises instances of E59 Primitive Value for time that should be implemented with appropriate validation, precision and interval logic to express date ranges relevant to cultural documentation. 
', 'fd8302b4-921b-300c-a9bf-c50d92418797', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('6a9b8f46-6dad-3a4a-aa11-7e972f796ca8', 'E62 String', '6e30fbe8-5a0d-3de8-be79-4ec6ebf4db39', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('d31634e8-6679-3f34-8735-1ac7c663b111', 'String', '6e30fbe8-5a0d-3de8-be79-4ec6ebf4db39', 'en', 'altLabel');
INSERT INTO "values" VALUES ('2f6d28a6-1e7c-3751-9559-3673fa5d7fd8', 'This class comprises the instances of E59 Primitive Values used for documentation such as free text strings, bitmaps, vector graphics, etc.
', '6e30fbe8-5a0d-3de8-be79-4ec6ebf4db39', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('f09b20af-0990-3bfb-b7b6-7255b0dab0a4', 'E63 Début d''existence', '255bba42-8ffb-3796-9caa-807179a20d9a', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('fb5d9115-2cb3-3c49-9df1-f3c299f4dfef', 'Début d''existence', '255bba42-8ffb-3796-9caa-807179a20d9a', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('3661e118-ac88-376a-9086-cda9081d968b', 'E63 Beginning of Existence', '255bba42-8ffb-3796-9caa-807179a20d9a', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('a612cf0a-4993-3868-b08f-6d998f04a1fd', 'Beginning of Existence', '255bba42-8ffb-3796-9caa-807179a20d9a', 'en', 'altLabel');
INSERT INTO "values" VALUES ('009e6e45-1a4e-3af8-b339-5a84f8c5cc14', 'E63 Daseinsbeginn', '255bba42-8ffb-3796-9caa-807179a20d9a', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('5637b393-501b-34ff-95ae-c8de569bd3fc', 'Daseinsbeginn', '255bba42-8ffb-3796-9caa-807179a20d9a', 'de', 'altLabel');
INSERT INTO "values" VALUES ('6f4f4885-1a00-3d48-b41b-466feb111b44', 'E63 Αρχή Ύπαρξης', '255bba42-8ffb-3796-9caa-807179a20d9a', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('266512bd-4503-3308-aa14-f87d7fd5ca2d', 'Αρχή Ύπαρξης', '255bba42-8ffb-3796-9caa-807179a20d9a', 'el', 'altLabel');
INSERT INTO "values" VALUES ('6f5572d9-1582-35bb-8859-c5e4cdac9b71', 'E63 Начало Существования', '255bba42-8ffb-3796-9caa-807179a20d9a', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('1c63a009-f1f9-3de7-81b5-02c2b61e89a8', 'Начало Существования', '255bba42-8ffb-3796-9caa-807179a20d9a', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('f2935aff-6a28-3cc6-bb10-c1f737129abf', 'E63 Início da Existência', '255bba42-8ffb-3796-9caa-807179a20d9a', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('dc202890-9ade-329d-9b7c-b5ef93a31006', 'Início da Existência', '255bba42-8ffb-3796-9caa-807179a20d9a', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('8a31ea9d-3f8a-3b6a-ab62-7401d56ac0cb', 'E63 存在开始', '255bba42-8ffb-3796-9caa-807179a20d9a', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('2eafaf1d-9060-3813-8679-afa2d6e12386', '存在开始', '255bba42-8ffb-3796-9caa-807179a20d9a', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('ae3e7b30-f659-31e0-8da1-fbfe954b02dc', 'This class comprises events that bring into existence any E77 Persistent Item. 
It may be used for temporal reasoning about things (intellectual products, physical items, groups of people, living beings) beginning to exist; it serves as a hook for determination of a terminus post quem and ante quem. ', '255bba42-8ffb-3796-9caa-807179a20d9a', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('89626a19-dbe1-34a1-b58f-edd68d9a34be', 'E64 Daseinsende', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('af2f906c-f18d-3170-8c00-369a53cdf054', 'Daseinsende', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'de', 'altLabel');
INSERT INTO "values" VALUES ('a6dc5627-c9c8-3f2a-b432-5de481ad7a8e', 'E64 Конец Существования', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('53eedd3a-8868-39ee-bb0e-d874d6e8d04b', 'Конец Существования', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('cd310770-7c00-37ad-a979-776318a1baee', 'E64 Τέλος Ύπαρξης', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('b52251a5-2208-3349-b1d3-c4cbac0f5fec', 'Τέλος Ύπαρξης', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'el', 'altLabel');
INSERT INTO "values" VALUES ('ee0ce48b-4c18-3479-a0fb-a0c9ee93f2dc', 'E64 Fin d''existence', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('0acb5c74-3832-32bb-a4ad-e8f710768948', 'Fin d''existence', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('4b4bdff9-2985-3dec-9fb4-dc7a5deaedd9', 'E64 End of Existence', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('90584c50-ea68-3d52-93ea-7be25de7da8c', 'End of Existence', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'en', 'altLabel');
INSERT INTO "values" VALUES ('9a46e83d-3727-35cb-bd0a-a3a48c8697d4', 'E64 Fim da Existência', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('607c6f4b-b1e2-39cf-a710-214dc0c5e3d2', 'Fim da Existência', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('86275a69-e81d-312a-8c52-997b2e87aae4', 'E64 存在结束', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('9636c122-e921-32b5-9d45-b6141d817204', '存在结束', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('c24620c2-0711-3e97-9a32-6440b2fb22ab', 'This class comprises events that end the existence of any E77 Persistent Item. 
It may be used for temporal reasoning about things (physical items, groups of people, living beings) ceasing to exist; it serves as a hook for determination of a terminus postquem and antequem. In cases where substance from a Persistent Item continues to exist in a new form, the process would be documented by E81 Transformation.
', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('e5c0f16e-9cca-37e8-bfa7-e09b92b9fec2', 'E65 Δημιουργία', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('be5a273e-62ad-3a81-ad71-c234208dbcf9', 'Δημιουργία', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'el', 'altLabel');
INSERT INTO "values" VALUES ('eb29cdf0-c507-36ed-a647-b1f52453f719', 'E65 Событие Творения', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('fb0e0a22-7e73-34b4-b86e-0997d69d8407', 'Событие Творения', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('1bbee8c0-48b5-339e-adbd-130bac17c22a', 'E65 Création', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('01d137c5-5f04-391a-a61e-0e9fa000ba30', 'Création', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('b36356b1-cb9e-3dd9-9894-70e5b86fd7f9', 'E65 Begriffliche Schöpfung', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('717dd288-df9f-3fea-92a0-c63ab3d1ff33', 'Begriffliche Schöpfung', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'de', 'altLabel');
INSERT INTO "values" VALUES ('07c17c53-a49f-3c64-877b-2b49e289d719', 'E65 Creation', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('a6fa1799-b43e-3fa7-9b14-d520bc3ac1c9', 'Creation', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'en', 'altLabel');
INSERT INTO "values" VALUES ('1c3d08e0-d9fd-3a4a-a006-440f730d1606', 'E65 Criação', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('c8227270-5752-3fa5-93c2-1e258b017bd5', 'Criação', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('a56976f4-9dc7-3d92-90e2-ab05f3a9e301', 'E65 创造', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('1988d5d8-db61-35a5-a2bf-672ccb2d3683', '创造', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('801b14c6-8c97-3d88-8cb9-04dc61ec2336', 'This class comprises events that result in the creation of conceptual items or immaterial products, such as legends, poems, texts, music, images, movies, laws, types etc.
', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('6e1e14ed-f667-3685-89f9-439421a2abf2', 'E66 Formation', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('570d3630-e790-390b-a3bf-b269e952a974', 'Formation', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'en', 'altLabel');
INSERT INTO "values" VALUES ('39289aaf-9370-39ce-8fa8-6319153928fb', 'E66 Событие Формирования', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('2eb85822-6811-3e7f-bd4e-eac25b42b034', 'Событие Формирования', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('a8d67849-7675-38ea-8cdf-af8ed1d600c7', 'E66 Formation', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('edcb24d0-48ec-3666-9794-f530fc0bb789', 'Formation', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('6f11169f-f557-32ca-8f11-2f8d9a88f068', 'E66 Gruppenbildung', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('aa30c431-3f68-3237-9226-a4df0c1117ef', 'Gruppenbildung', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'de', 'altLabel');
INSERT INTO "values" VALUES ('1913c3fa-0874-375b-af1d-8b6aa06eefde', 'E66 Συγκρότηση Ομάδας', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('d1720796-28f0-3376-857b-9cf67b886537', 'Συγκρότηση Ομάδας', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'el', 'altLabel');
INSERT INTO "values" VALUES ('0535dd06-4817-382a-975a-37aff844d7f5', 'E66 Formação', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('e2af82da-96ac-37ae-bdac-f4ed767557b0', 'Formação', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('a7979df5-252b-3e01-b23a-52f154704ec1', 'E66 组成', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('6009a48b-8d01-383d-883c-c461d544f592', '组成', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('15316d33-bdaf-35f7-9490-d0d93de91435', 'This class comprises events that result in the formation of a formal or informal E74 Group of people, such as a club, society, association, corporation or nation. 

E66 Formation does not include the arbitrary aggregation of people who do not act as a collective.
The formation of an instance of E74 Group does not require that the group is populated with members at the time of formation. In order to express the joining of members at the time of formation, the respective activity should be simultaneously an instance of both E66 Formation and E85 Joining.
', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('0462ec22-eafe-326c-b9cd-be09d980462f', 'E67 Birth', '07fcf604-d28f-3993-90fa-d301c4004913', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('9795e4b1-71fb-3754-a990-e93dc3fc1da1', 'Birth', '07fcf604-d28f-3993-90fa-d301c4004913', 'en', 'altLabel');
INSERT INTO "values" VALUES ('53c84bf6-d2df-32e1-8149-6c26c24a16b6', 'E67 Рождение', '07fcf604-d28f-3993-90fa-d301c4004913', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('beb701f1-1f8f-3dce-b5ac-301eaf9e5b1d', 'Рождение', '07fcf604-d28f-3993-90fa-d301c4004913', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('6df6b2b4-3f19-35f0-86b0-d028d2e5a842', 'E67 Naissance', '07fcf604-d28f-3993-90fa-d301c4004913', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('98671f04-c331-375f-9a0e-eabeec0c3076', 'Naissance', '07fcf604-d28f-3993-90fa-d301c4004913', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('696d55f8-80ea-3015-ab5c-d4097fb1622c', 'E67 Geburt', '07fcf604-d28f-3993-90fa-d301c4004913', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('1c97fdab-5586-37b7-bbdf-a4f9fc1eb1ff', 'Geburt', '07fcf604-d28f-3993-90fa-d301c4004913', 'de', 'altLabel');
INSERT INTO "values" VALUES ('6050a330-7f3d-3415-bd46-8cffed89b016', 'E67 Γέννηση', '07fcf604-d28f-3993-90fa-d301c4004913', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('69bc1dbe-3163-3562-a7ac-ffa37162c9bc', 'Γέννηση', '07fcf604-d28f-3993-90fa-d301c4004913', 'el', 'altLabel');
INSERT INTO "values" VALUES ('ac92f1c6-779a-32f6-952d-b338413bc5f4', 'E67 Nascimento', '07fcf604-d28f-3993-90fa-d301c4004913', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('e0bde70e-d665-3773-8d17-28a208f27254', 'Nascimento', '07fcf604-d28f-3993-90fa-d301c4004913', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('bd359d4f-9b3c-3d11-bebc-a7dc414949fb', 'E67 诞生', '07fcf604-d28f-3993-90fa-d301c4004913', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('b5c73589-bd23-3aa4-8061-33e4ff7bffb1', '诞生', '07fcf604-d28f-3993-90fa-d301c4004913', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('ce169a9b-ff76-3d77-9b9d-64312dd3c701', 'This class comprises the births of human beings. E67 Birth is a biological event focussing on the context of people coming into life. (E63 Beginning of Existence comprises the coming into life of any living beings). 
Twins, triplets etc. are brought into life by the same E67 Birth event. The introduction of the E67 Birth event as a documentation element allows the description of a range of family relationships in a simple model. Suitable extensions may describe more details and the complexity of motherhood with the intervention of modern medicine. In this model, the biological father is not seen as a necessary participant in the E67 Birth event.
', '07fcf604-d28f-3993-90fa-d301c4004913', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('d9ce88d5-6a06-3892-af5a-d8ae1e0ba124', 'E68 Роспуск', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('a0b642e4-0471-3485-91bc-c8b567b1b0da', 'Роспуск', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('dce1a7a9-52b1-37bb-9e9d-4f5e0730705c', 'E68 Gruppenauflösung', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f4f10af2-68d6-3ce8-a681-6c2a54ab3a18', 'Gruppenauflösung', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'de', 'altLabel');
INSERT INTO "values" VALUES ('b8a065bf-c2be-3147-bdb5-ec2bfe62c6b3', 'E68 Διάλυση Ομάδας', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('78d67471-58ee-3473-a3e9-8eddb0c42080', 'Διάλυση Ομάδας', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'el', 'altLabel');
INSERT INTO "values" VALUES ('2a9230aa-18f8-375a-9e09-2533264ce918', 'E68 Dissolution', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('925820d7-1d8a-3681-9f88-5aae4f6091e2', 'Dissolution', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'en', 'altLabel');
INSERT INTO "values" VALUES ('079f645a-3d7e-3a20-9d24-c7b9c78a067e', 'E68 Dissolution', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('c20e6c4d-d0cd-3337-9343-cfdae8b429f5', 'Dissolution', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('9973f24d-7ce6-3538-8f56-4b3f8b55406e', 'E68 Dissolução', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('e547f5df-1899-3594-9dc4-931ff51505b2', 'Dissolução', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('8f158337-af65-3ec8-bdcd-8d9e91a9e7ec', 'E68 解散', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('3706dc59-dc02-370b-a388-8d274be1d43d', '解散', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('14baf293-8d0e-31b0-a48d-d23da5ca77dd', 'This class comprises the events that result in the formal or informal termination of an E74 Group of people. 
If the dissolution was deliberate, the Dissolution event should also be instantiated as an E7 Activity.
', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('23457a43-12c2-3d9c-83d7-4ae10944a3bb', 'E69 Смерть', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('9067da9c-2c3b-3cf4-9dcd-467ebb65484a', 'Смерть', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('1b3d27d9-0a1a-3f4e-8da4-6122745c061a', 'E69 Death', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('eabaac70-693b-3cf4-93dc-3d5dc255d8ff', 'Death', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'en', 'altLabel');
INSERT INTO "values" VALUES ('5651bfaf-0093-37e1-a152-234efce7d86d', 'E69 Tod', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('576563ef-83ef-336b-a1a2-9c8c539c9272', 'Tod', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'de', 'altLabel');
INSERT INTO "values" VALUES ('e402e111-2c9f-32de-b89e-5e3598ee491a', 'E69 Mort', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('d171f4f2-b2fe-3716-9811-ea2047a5b0d8', 'Mort', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('1e7c460f-abde-33e4-984d-c4427d3674f4', 'E69 Θάνατος', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('22c08c66-23f9-3087-a3b7-7d227a76b7db', 'Θάνατος', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'el', 'altLabel');
INSERT INTO "values" VALUES ('c0c04649-48c3-340b-88df-caf987cdc281', 'E69 Morte', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('2fdf33de-7482-3f89-b9eb-5d19f7631d2a', 'Morte', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('01a10876-2958-3999-a658-46b3eddc4df4', 'E69 死亡', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('86141c07-2a91-34c0-a45c-4fecc09fde29', '死亡', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('7921a186-41ec-3d19-9b15-e19bf29b7c76', 'This class comprises the deaths of human beings. 
If a person is killed, their death should be instantiated as E69 Death and as E7 Activity. The death or perishing of other living beings should be documented using E64 End of Existence.
', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('62e2d942-7d75-3fae-b676-eb4a9f120088', 'E70 Chose', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('685e0e9b-c6c5-3f36-8000-b7bb29de8d42', 'Chose', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('c5ddaaa1-2b06-3407-9513-cdf92ae42395', 'E70 Thing', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('48a83fc3-6c5b-3bea-8f67-e034ee5dc3cf', 'Thing', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'en', 'altLabel');
INSERT INTO "values" VALUES ('ae6139b2-fd1f-31e1-879a-546e196f23da', 'E70 Πράγμα', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('7a258b80-721c-3612-a2d1-dff4398a4da4', 'Πράγμα', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'el', 'altLabel');
INSERT INTO "values" VALUES ('b3e3e125-4873-3213-a025-141b7718ef18', 'E70 Sache', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('2399966e-55db-30ab-9c67-3d43e5b21d4e', 'Sache', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'de', 'altLabel');
INSERT INTO "values" VALUES ('91a599cc-99dd-351b-94b5-791e761c016e', 'E70 Coisa', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('44573277-b81b-3e04-bc93-4ffcdee57724', 'Coisa', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('481d4ea1-231e-372d-ac3f-56a00a2974c4', 'E70 万物', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('63520cdf-dda2-3b5c-a409-c5feabf5dfc3', '万物', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('97dc7ede-b7fa-371b-8586-46a09344e043', 'This general class comprises discrete, identifiable, instances of E77 Persistent Item that are documented as single units, that either consist of matter or depend on being carried by matter and are characterized by relative stability.
They may be intellectual products or physical things. They may for instance have a solid physical form, an electronic encoding, or they may be a logical concept or structure.
', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('f00601b2-fe33-36f1-914c-4cd5f004b21b', 'E71 Künstliches', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('ff9c6c41-ae05-3d60-9e27-d06ac877dab0', 'Künstliches', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'de', 'altLabel');
INSERT INTO "values" VALUES ('fd6ccc8c-49c5-3034-bf50-5c4b5ef9a969', 'E71 Chose fabriquée', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('23239bf1-d785-3342-8bdc-0eb1138f8f90', 'Chose fabriquée', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('4d430ac1-6a47-39d8-9dad-2d92a426a453', 'E71 Рукотворная Вещь', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('da08fe0f-b7a3-3d41-9534-2a9f11337967', 'Рукотворная Вещь', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('5c513062-67b0-3a0d-a433-4b242587ba8a', 'E71 Man-Made Thing', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b0da3f36-5911-3966-b6c4-98315b07198c', 'Man-Made Thing', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'en', 'altLabel');
INSERT INTO "values" VALUES ('95d4b5fc-a237-3579-8f8f-f869f9be7ede', 'E71 Ανθρώπινο Δημιούργημα', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('3e1e1595-a633-30fb-967b-2c203dbaf723', 'Ανθρώπινο Δημιούργημα', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'el', 'altLabel');
INSERT INTO "values" VALUES ('2ec63870-ce85-387a-b16f-e548fd96694e', 'E71 Coisa Fabricada', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('e8cb6b23-1738-3bb4-a4e1-53503330ffb2', 'Coisa Fabricada', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('8551156a-b50b-3dcb-84a1-834e4868ed1b', 'E71 人造物', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('7f20e1b5-dac1-3506-a75c-8be61e8949d4', '人造物', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('043a14ae-aa1e-36b3-a697-34ab5925e3d6', 'This class comprises discrete, identifiable man-made items that are documented as single units. 
These items are either intellectual products or man-made physical things, and are characterized by relative stability. They may for instance have a solid physical form, an electronic encoding, or they may be logical concepts or structures.
', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('5a7cfc7b-8700-35c6-8394-576d98b3cd91', 'E72 Objet juridique', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('f55f3fa6-e9ce-3c6d-a565-a74776ba980f', 'Objet juridique', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('7a3b98ee-2e1b-3bef-bc6d-abc07a32ad82', 'E72 Объект Права', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('c9f5005f-c610-3872-9cfa-d8d5bbcbd4d2', 'Объект Права', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('34509151-736d-3b53-acf7-26b8aec45086', 'E72 Νομικό Αντικείμενο', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('d3ccf07d-99c6-33f7-851e-a2e6082e7660', 'Νομικό Αντικείμενο', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'el', 'altLabel');
INSERT INTO "values" VALUES ('3ec86055-1b0a-3348-af35-64e7ee2fe056', 'E72 Legal Object', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('64830a90-0eef-377d-90ec-88c1035be6d2', 'Legal Object', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'en', 'altLabel');
INSERT INTO "values" VALUES ('d1f194cc-f1cd-3440-962c-9621b31c2378', 'E72 Rechtsobjekt', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('304e87a5-c3d6-3e8d-9530-c7a81064a919', 'Rechtsobjekt', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'de', 'altLabel');
INSERT INTO "values" VALUES ('19cf20d9-c413-36ca-82ae-3649dd18c64f', 'E72 Objeto Jurídico', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('919c3abe-f92d-3a81-97a7-4888b63ac384', 'Objeto Jurídico', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('d34742ee-fc44-3a34-86db-aa80f701854a', 'E72 法律物件', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('9e13356f-5d7e-3258-9d04-36365c3d46f8', '法律物件', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('9e813b65-fe97-34c8-976f-5f938f6af582', 'This class comprises those material or immaterial items to which instances of E30 Right, such as the right of ownership or use, can be applied. 
This is true for all E18 Physical Thing. In the case of instances of E28 Conceptual Object, however, the identity of the E28 Conceptual Object or the method of its use may be too ambiguous to reliably establish instances of E30 Right, as in the case of taxa and inspirations. Ownership of corporations is currently regarded as out of scope of the CRM. 
', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('435df18a-6f33-348c-aedf-639b7273717b', 'E73 Informationsgegenstand', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('8158a095-3ec3-3841-812c-35ecfd6f525b', 'Informationsgegenstand', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'de', 'altLabel');
INSERT INTO "values" VALUES ('b731bd0e-045f-34e2-942d-654263661077', 'E73 Information Object', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('776e81cc-7562-3afa-9ef6-c26b1cdd4ea5', 'Information Object', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c956146c-db57-3ff0-9ee1-b79a182da79d', 'E73 Πληροφοριακό Αντικείμενο', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('a3747579-e35d-30f2-a6e7-1feb40c9b326', 'Πληροφοριακό Αντικείμενο', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'el', 'altLabel');
INSERT INTO "values" VALUES ('9cd113e1-7732-38e1-b1fc-c8d015b4acd6', 'E73 Objet d''information', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('1c5be60c-8c33-3d94-8022-608c033b890b', 'Objet d''information', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('423ba1c2-d8bc-3302-ad22-4ae2d58d8bbb', 'E73 Информационный Объект', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('4eeb5680-a34c-35bc-a54e-6a9a47a76103', 'Информационный Объект', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('8b80ba89-2a59-3074-889a-83c597c2002c', 'E73 Objeto de Informação', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('39301e0f-bcd8-3563-ae7b-8cf0b3babfa2', 'Objeto de Informação', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b39fdb1d-9e32-3870-9011-2a7007e6a43e', 'E73 信息物件', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('35373669-ca4d-3011-99b7-7f9ed778289c', '信息物件', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('bf7fdcc2-62bd-36e9-9ba5-bbca67e8d696', 'This class comprises identifiable immaterial items, such as a poems, jokes, data sets, images, texts, multimedia objects, procedural prescriptions, computer program code, algorithm or mathematical formulae, that have an objectively recognizable structure and are documented as single units. The encoding structure known as a "named graph" also falls under this class, so that each "named graph" is an instance of an E73 Information Object. 
An E73 Information Object does not depend on a specific physical carrier, which can include human memory, and it can exist on one or more carriers simultaneously. 
Instances of E73 Information Object of a linguistic nature should be declared as instances of the E33 Linguistic Object subclass. Instances of E73 Information Object of a documentary nature should be declared as instances of the E31 Document subclass. Conceptual items such as types and classes are not instances of E73 Information Object, nor are ideas without a reproducible expression. 
 ', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('1698dd15-01c5-3000-a4ca-0b111d8a305f', 'E74 Группа', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('24163acc-da16-3571-8526-9a5828301fa5', 'Группа', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('92edf875-1bd6-34d3-bacd-429bf8c7f276', 'E74 Group', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('380fb63b-1c41-37d1-8480-0a292a7d97c4', 'Group', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'en', 'altLabel');
INSERT INTO "values" VALUES ('91675477-12ea-3203-978c-e34f147b8fa7', 'E74 Ομάδα', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('fb02b8a2-d9d9-32a2-a14c-223d3cc29c0b', 'Ομάδα', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'el', 'altLabel');
INSERT INTO "values" VALUES ('685e1117-cfe3-3cb9-99be-701fb682ceaf', 'E74 Menschliche Gruppe', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('cb51364b-4a17-3601-9dbf-d4944675d4ec', 'Menschliche Gruppe', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'de', 'altLabel');
INSERT INTO "values" VALUES ('500d0d6b-2144-3e5c-b0e9-e758818cbc9f', 'E74 Groupe', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('3dd95a9f-be07-369a-a31c-a878d6dbe93e', 'Groupe', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('93352837-2180-3f03-9994-ebe4618fa076', 'E74 Grupo', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('5ad75f33-d3b3-36fa-8a25-d72dad71cd43', 'Grupo', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('78c732a6-b719-313c-a7c9-998c1c01b4d7', 'E74 群组', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('226204c7-d197-3a4c-a330-859353839a79', '群组', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('6ffccb61-1903-3ced-af9f-816998f36b62', 'This class comprises any gatherings or organizations of E39 Actors that act collectively or in a similar way due to any form of unifying relationship. In the wider sense this class also comprises official positions which used to be regarded in certain contexts as one actor, independent of the current holder of the office, such as the president of a country. In such cases, it may happen that the Group never had more than one member. A joint pseudonym (i.e., a name that seems indicative of an individual but that is actually used as a persona by two or more people) is a particular case of E74 Group.
A gathering of people becomes an E74 Group when it exhibits organizational characteristics usually typified by a set of ideas or beliefs held in common, or actions performed together. These might be communication, creating some common artifact, a common purpose such as study, worship, business, sports, etc. Nationality can be modeled as membership in an E74 Group (cf. HumanML markup). Married couples and other concepts of family are regarded as particular examples of E74 Group.
', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('1542b6de-bfdf-35a8-adb2-77161ca16f86', 'E75 Appellation d''objet conceptuel', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('aa1d83d4-1fc4-3554-b593-65f632d318e4', 'Appellation d''objet conceptuel', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('a5317b04-b32f-3a14-959d-0a60b83b8acb', 'E75 Обозначение Концептуального Объекта', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('6c96c4a1-e503-3fed-8aff-9e5603fb4676', 'Обозначение Концептуального Объекта', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('220b255e-dfa7-36df-8a2f-36a0fb097dea', 'E75 Begriff- oder Konzeptbenennung ', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('46d7e7be-0882-3d6b-8b58-722e23c83fd4', 'Begriff- oder Konzeptbenennung ', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'de', 'altLabel');
INSERT INTO "values" VALUES ('f7431ac2-16a0-3520-86f8-d965f1204e67', 'E75 Conceptual Object Appellation', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('9fb6b65f-aa42-3b5d-b92a-e5d5543c2af7', 'Conceptual Object Appellation', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'en', 'altLabel');
INSERT INTO "values" VALUES ('a8302387-36c7-341e-a915-8e1f33bff2bd', 'E75 Ονομασία Νοητικού Αντικειμένου', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('eb7c6ea6-b58c-3774-bbdf-c4b00aaa396b', 'Ονομασία Νοητικού Αντικειμένου', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'el', 'altLabel');
INSERT INTO "values" VALUES ('375d7e82-b0cd-3d9c-9d2a-d1d60cb19e4a', 'E75 Designação de Objeto Conceitual', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('d7fcd900-6671-3b05-81d5-47bd1e77e21c', 'Designação de Objeto Conceitual', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('f69bc0ea-9a2d-3ef5-a013-1dd870a48001', 'E75 概念物件称号', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('66828d4c-87ee-3d6b-a8e0-7fd3187a47bb', '概念物件称号', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('4eea650a-3018-36ba-abe1-7e4d376cc8be', 'This class comprises appellations that are by their form or syntax specific to identifying instances of E28 Conceptual Object, such as intellectual products, standardized patterns etc.', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('2a32df8e-e1a5-33bc-85dd-1bcef049df1f', 'E77 Persistent Item', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('343fb652-ccca-3554-9c00-b95c4eeb7932', 'Persistent Item', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'en', 'altLabel');
INSERT INTO "values" VALUES ('f4abb3b0-ff51-30fa-a7ac-390f1b834605', 'E77 Постоянная Сущность', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('8f51a99e-30a0-3e58-9ad2-edbb7e3fb6a1', 'Постоянная Сущность', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('f96640d7-07f6-3de8-a6ee-54211aab7e24', 'E77 Seiendes', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('260960dd-560d-3c15-9029-6bca649232ee', 'Seiendes', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'de', 'altLabel');
INSERT INTO "values" VALUES ('319f9d97-6596-3fcf-8394-591fd60bf865', 'E77 Ον', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('f6869bcb-a1cf-3c88-a24d-e73892198dee', 'Ον', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'el', 'altLabel');
INSERT INTO "values" VALUES ('77c57fa5-58da-3a95-be61-edfda0d81a11', 'E77 Entité persistante', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('cec207a1-5700-3472-ad65-10435ef2a5a8', 'Entité persistante', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('c6a28af7-481f-3de7-8ca1-d6ca4abb09c5', 'E77 Entidade Persistente', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('023040f2-c125-3cc8-b1da-3c304ad653d1', 'Entidade Persistente', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b4678564-4c39-33d9-b2be-4d93001d549a', 'E77 持续性项目', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('0da7fc98-b6c5-3f69-91ed-5172686bfcef', '持续性项目', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('326d5281-4665-3b66-b5c3-2d1580bb5871', 'This class comprises the activities that result in an instance of E18 Physical Thing being decreased by the removal of a part.
Typical scenarios include the detachment of an accessory, the removal of a component or part of a composite object, or the deaccessioning of an object from a curated E78 Collection. If the E80 Part Removal results in the total decomposition of the original object into pieces, such that the whole ceases to exist, the activity should instead be modelled as an E81 Transformation, i.e. a simultaneous destruction and production. In cases where the part removed has no discernible identity prior to its removal but does have an identity subsequent to its removal, the activity should be regarded as both E80 Part Removal and E12 Production. This class of activities forms a basis for reasoning about the history, and continuity of identity over time, of objects that are removed from other objects, such as precious gemstones being extracted from different items of jewelry, or cultural artifacts being deaccessioned from different museum collections over their lifespan.
', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('179447c2-2c88-3a17-ad0a-9c1030ee061b', 'E81 Трансформация', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('9e0c2125-b492-321c-a5b0-75d00a0d9115', 'This class comprises items that have a persistent identity, sometimes known as “endurants” in philosophy. 
They can be repeatedly recognized within the duration of their existence by identity criteria rather than by continuity or observation. Persistent Items can be either physical entities, such as people, animals or things, or conceptual entities such as ideas, concepts, products of the imagination or common names.
The criteria that determine the identity of an item are often difficult to establish -; the decision depends largely on the judgement of the observer. For example, a building is regarded as no longer existing if it is dismantled and the materials reused in a different configuration. On the other hand, human beings go through radical and profound changes during their life-span, affecting both material composition and form, yet preserve their identity by other criteria. Similarly, inanimate objects may be subject to exchange of parts and matter. The class E77 Persistent Item does not take any position about the nature of the applicable identity criteria and if actual knowledge about identity of an instance of this class exists. There may be cases, where the identity of an E77 Persistent Item is not decidable by a certain state of knowledge.
The main classes of objects that fall outside the scope the E77 Persistent Item class are temporal objects such as periods, events and acts, and descriptive properties. ', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('23e2bb01-7519-393f-bd47-ba2e41be8fde', 'E78 Коллекция', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('77a53c3b-7736-371e-92a1-60a2934fa830', 'Коллекция', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('50d7459e-a96d-3ea9-a6f2-2923b7084fa6', 'E78 Συλλογή', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('4d741409-1404-37bd-950e-34df5aea9244', 'Συλλογή', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'el', 'altLabel');
INSERT INTO "values" VALUES ('b4a2bbc7-8d26-39b3-9fd0-3d72e1bf8b68', 'E78 Collection', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5501adab-3a2a-3f59-8d23-5155b885915c', 'Collection', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('f6a4418c-042c-3223-8091-2fa47d3d0e81', 'E78 Collection', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('36451821-77c5-3dc7-9140-58b57ca7b1e0', 'Collection', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'en', 'altLabel');
INSERT INTO "values" VALUES ('645f3edb-9b26-3ae2-9484-41bdd40f00c5', 'E78 Sammlung', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('50c95aa9-d7d2-3582-87a6-85d08d01d9e7', 'Sammlung', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'de', 'altLabel');
INSERT INTO "values" VALUES ('fdfabde5-945c-3c8a-bb13-d6026c88453f', 'E78 Coleção', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('1e962989-145b-39f5-a200-a22c3d74398f', 'Coleção', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('8b9cf731-c90f-3def-b371-6c7defc189a5', 'E78 收藏', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('e98602ce-7a27-3e62-88e4-a6e954eb8252', '收藏', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('71ba337a-db4a-3fc1-b87b-d70075ca17ca', 'This class comprises aggregations of instances of E18 Physical Thing that are assembled and maintained ("curated" and "preserved", in museological terminology) by one or more instances of E39 Actor over time for a specific purpose and audience, and according to a particular collection development plan.  
Items may be added or removed from an E78 Collection in pursuit of this plan. This class should not be confused with the E39 Actor maintaining the E78 Collection often referred to with the name of the E78 Collection (e.g. “The Wallace Collection decided…”).
Collective objects in the general sense, like a tomb full of gifts, a folder with stamps or a set of chessmen, should be documented as instances of E19 Physical Object, and not as instances of E78 Collection. This is because they form wholes either because they are physically bound together or because they are kept together for their functionality.
', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('da165358-6c07-30cb-92e4-9e8a5b3e42ce', 'E79 Addition d''élément', '048fe43e-349a-3dda-9524-7046dcbf7287', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('134df047-be80-3991-a702-79162c663753', 'Addition d''élément', '048fe43e-349a-3dda-9524-7046dcbf7287', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('642bdfea-a240-3911-85be-ed426855de2c', 'E79 Part Addition', '048fe43e-349a-3dda-9524-7046dcbf7287', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('696fa468-f3d3-3118-abef-73359dba029a', 'Part Addition', '048fe43e-349a-3dda-9524-7046dcbf7287', 'en', 'altLabel');
INSERT INTO "values" VALUES ('f22cf77e-d68c-3393-be0f-611127243f9b', 'E79 Teilhinzufügung', '048fe43e-349a-3dda-9524-7046dcbf7287', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('29f3b561-8107-3189-b97c-dcb4d21d375f', 'Teilhinzufügung', '048fe43e-349a-3dda-9524-7046dcbf7287', 'de', 'altLabel');
INSERT INTO "values" VALUES ('44741fda-fa8c-321a-b396-01626dff034d', 'E79 Добавление Части', '048fe43e-349a-3dda-9524-7046dcbf7287', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('e9270dec-15c7-3f91-9afa-d8567b7674a1', 'Добавление Части', '048fe43e-349a-3dda-9524-7046dcbf7287', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('96cde89d-ba23-3800-b693-4e4718ae36d4', 'E79 Προσθήκη Μερών', '048fe43e-349a-3dda-9524-7046dcbf7287', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('3430a306-0cf0-3b6d-b6bb-1d5ef5341d04', 'Προσθήκη Μερών', '048fe43e-349a-3dda-9524-7046dcbf7287', 'el', 'altLabel');
INSERT INTO "values" VALUES ('e24fc3a7-e5b2-3e90-a5fb-01d9994b2856', 'E79 Adição de Parte', '048fe43e-349a-3dda-9524-7046dcbf7287', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('8a6d0694-dcb5-3dbb-bb0d-e68e2b0ad3c9', 'Adição de Parte', '048fe43e-349a-3dda-9524-7046dcbf7287', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('20415757-eefc-31f7-bdb3-9cedbd1e115c', 'E79 部件增加', '048fe43e-349a-3dda-9524-7046dcbf7287', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('9e3807f9-a843-3474-bbc1-52f8923bcd3b', '部件增加', '048fe43e-349a-3dda-9524-7046dcbf7287', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('a1ba6cec-de94-3a3a-92fe-c4e67620d638', 'This class comprises activities that result in an instance of E24 Physical Man-Made Thing being increased, enlarged or augmented by the addition of a part. 
Typical scenarios include the attachment of an accessory, the integration of a component, the addition of an element to an aggregate object, or the accessioning of an object into a curated E78 Collection. Objects to which parts are added are, by definition, man-made, since the addition of a part implies a human activity. Following the addition of parts, the resulting man-made assemblages are treated objectively as single identifiable wholes, made up of constituent or component parts bound together either physically (for example the engine becoming a part of the car), or by sharing a common purpose (such as the 32 chess pieces that make up a chess set). This class of activities forms a basis for reasoning about the history and continuity of identity of objects that are integrated into other objects over time, such as precious gemstones being repeatedly incorporated into different items of jewellery, or cultural artifacts being added to different museum instances of E78 Collection over their lifespan.
', '048fe43e-349a-3dda-9524-7046dcbf7287', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('176c8149-7973-3b1c-8f0c-5a8fa8cb1e91', 'E80 Teilentfernung', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('31c6c09b-d093-351a-b6f7-003c50422875', 'Teilentfernung', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'de', 'altLabel');
INSERT INTO "values" VALUES ('099afc72-eb24-3448-ae68-f91cfa5b4447', 'E80 Soustraction d''élément', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('7c7b2a71-a70f-3922-abfc-0f4d3093747b', 'Soustraction d''élément', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('3c562c05-7b98-3da7-b15a-61d999851378', 'E80 Part Removal', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('814ab91f-33ee-37b6-b491-4dfeadb688a7', 'Part Removal', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'en', 'altLabel');
INSERT INTO "values" VALUES ('e5dc45a5-8bb6-33ff-8740-6eba921ecd9d', 'E80 Удаление Части', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('52ae6a96-7849-3d7d-bf1e-9be42968a744', 'Удаление Части', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('e8c16209-bae1-3e97-b675-dcf118a0f7df', 'E80 Αφαίρεση Μερών', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('106a1d7d-ac53-3a1d-b5ca-b3c53077f888', 'Αφαίρεση Μερών', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'el', 'altLabel');
INSERT INTO "values" VALUES ('bd7fab1b-594e-3cd5-8275-3e9ef047c8ef', 'E80 Remoção de Parte', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('3501570c-226d-3215-b9eb-b12fc85a0228', 'Remoção de Parte', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('82bc1227-208c-3402-a314-9b00b55f8818', 'E80 部件删除', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('863a5623-ead1-3b2f-99ac-6f242b532354', '部件删除', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('be94d5e2-0dd9-3e6e-b8cf-da1e2eef9f1a', 'Трансформация', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('fcb6e3ae-88c4-3870-bdc5-c94d2a1d4988', 'E81 Transformation', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('246a2a73-fdc3-3eba-b562-67612dcafcd5', 'Transformation', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'en', 'altLabel');
INSERT INTO "values" VALUES ('2668e545-1d78-3633-a5c4-04f18a3af5b5', 'E81 Transformation', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('cdfeb88e-2c26-36c4-b913-db935fea455d', 'Transformation', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('c0df579f-168d-35fe-bf82-1b2fba61a19f', 'E81 Umwandlung', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('97ca8376-8e63-3468-84e4-ed48d077ab99', 'Umwandlung', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'de', 'altLabel');
INSERT INTO "values" VALUES ('12e0e611-7bda-3c79-8807-ea54211da9b6', 'E81 Μετατροπή', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('3d280ecf-6fbc-3c15-b930-444bea6ab8ab', 'Μετατροπή', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'el', 'altLabel');
INSERT INTO "values" VALUES ('f1e01238-c129-3099-b7d3-e0409c384b2b', 'E81 Transformação', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('2eb800cc-f19d-3497-9d8a-729494fe96f0', 'Transformação', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('82a76922-5574-3eaa-977e-78f0afea89bd', 'E81 转变', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('1efe0d50-e53f-3542-b228-a1bb0fcde82b', '转变', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('d31d945e-9c55-31d3-affd-964cec574d33', 'This class comprises the events that result in the simultaneous destruction of one or more than one E77 Persistent Item and the creation of one or more than one E77 Persistent Item that preserves recognizable substance from the first one(s) but has fundamentally different nature and identity. 
Although the old and the new instances of E77 Persistent Item are treated as discrete entities having separate, unique identities, they are causally connected through the E81 Transformation; the destruction of the old E77 Persistent Item(s) directly causes the creation of the new one(s) using or preserving some relevant substance. Instances of E81 Transformation are therefore distinct from re-classifications (documented using E17 Type Assignment) or modifications (documented using E11 Modification) of objects that do not fundamentally change their nature or identity. Characteristic cases are reconstructions and repurposing of historical buildings or ruins, fires leaving buildings in ruins, taxidermy of specimen in natural history and the reorganization of a corporate body into a new one.
', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('a5722898-1174-37fd-a20a-a875628cdb28', 'E82 Actor Appellation', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('07325f8e-b04c-3ff1-9b9b-3160f3c5124f', 'Actor Appellation', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('0bfade69-ddaf-3eb5-ae7c-515b2cc69d84', 'E82 Обозначение Агента', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('678f2814-444a-3b21-9de2-8475bbc6da36', 'Обозначение Агента', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('9a644330-d792-3498-8fda-fd892c889e56', 'E82 Ονομασία Δράστη', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('27f01b23-2220-35cf-9273-391daa76bb23', 'Ονομασία Δράστη', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'el', 'altLabel');
INSERT INTO "values" VALUES ('be7c73d2-d9d5-3099-87b1-a07672e9c901', 'E82 Appellation d''agent', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('ff8ac3cd-390f-3d52-8123-ec915cf5bd6c', 'Appellation d''agent', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('aae988f0-d189-3074-b6f6-e9b81db444e9', 'E82 Akteurbenennung', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('6ea8c40c-fac4-3ee3-8a21-5fe00b263448', 'Akteurbenennung', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'de', 'altLabel');
INSERT INTO "values" VALUES ('429596ba-88e6-3fd0-a1cf-b507d6e7bd1b', 'E82 Designação de Agente', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('1c5af085-a7c1-3231-9936-4125900f58ae', 'Designação de Agente', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('d59d0c48-e771-39d8-9ecb-54820cc52bb9', 'E82 角色称号', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('560651aa-de72-3000-87d9-a63a59c18009', '角色称号', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('e19075a4-1095-3e6e-bedc-8bd8baa5ae3a', 'This class comprises any sort of name, number, code or symbol characteristically used to identify an E39 Actor. 
An E39 Actor will typically have more than one E82 Actor Appellation, and instances of E82 Actor Appellation in turn may have alternative representations. The distinction between corporate and personal names, which is particularly important in library applications, should be made by explicitly linking the E82 Actor Appellation to an instance of either E21 Person or E74 Group/E40 Legal Body. If this is not possible, the distinction can be made through the use of the P2 has type mechanism. 
', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('1a5d7786-99f7-3569-8b60-acc9f01aa572', 'E83 Typuserfindung', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('36d89b3f-e615-39fa-aaab-f521faab8693', 'Typuserfindung', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'de', 'altLabel');
INSERT INTO "values" VALUES ('53663d48-16e8-312b-a5ae-71f70fe360e1', 'E83 Создание Типа', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('1154240f-50cd-3a02-93bd-914e35ee1443', 'Создание Типа', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('e495aae8-4cb7-3e81-bc62-31d2f90441d5', 'E83 Type Creation', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('934860c3-1012-3711-be47-7dee05a98ae0', 'Type Creation', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'en', 'altLabel');
INSERT INTO "values" VALUES ('ae03f6be-bfec-35fb-a6d2-ca39d8e4dad9', 'E83 Création de type', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('7e7ecce2-0bd3-38bd-9091-6663901db6e3', 'Création de type', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('631f4d4c-6c99-34d8-bf39-ff893cee794e', 'E83 Δημιουργία Τύπου', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('8bf9a8c6-fd9d-3fc0-a628-307268ed4b2e', 'Δημιουργία Τύπου', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'el', 'altLabel');
INSERT INTO "values" VALUES ('41d413d7-63f3-323f-a713-adac7a7b8945', 'E83 Criação de Tipo', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('c118772e-1076-310a-89c2-e05d970e0cff', 'Criação de Tipo', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b2dd1993-1a35-30bc-9082-ad77cd3b0e8e', 'E83 类型创造', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('989f4966-1361-31cc-b808-73274278bae8', '类型创造', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('534340a6-c9a6-363e-8483-540161a89593', 'This class comprises activities formally defining new types of items. 
It is typically a rigorous scholarly or scientific process that ensures a type is exhaustively described and appropriately named. In some cases, particularly in archaeology and the life sciences, E83 Type Creation requires the identification of an exemplary specimen and the publication of the type definition in an appropriate scholarly forum. The activity of E83 Type Creation is central to research in the life sciences, where a type would be referred to as a “taxon,” the type description as a “protologue,” and the exemplary specimens as “orgininal element” or “holotype”.
', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('98e7465b-4774-3976-bbd9-7eaddef0de3f', 'E84 Φορέας Πληροφορίας', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('4c8bf390-0033-37ee-866a-a52bb42a5de1', 'Φορέας Πληροφορίας', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'el', 'altLabel');
INSERT INTO "values" VALUES ('bae9d7d2-268e-34a5-9722-50d3acff6755', 'E84 Information Carrier', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('558e85df-4a5a-326c-8354-f7927e317546', 'Information Carrier', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'en', 'altLabel');
INSERT INTO "values" VALUES ('756d1285-9420-3376-90e1-5efb5a7e9d2c', 'E84 Носитель Информации', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('cff5699f-7d8a-3b62-97e5-b082f4c58486', 'Носитель Информации', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('285a7bcc-5982-3e0c-ad78-82e5e2a249b9', 'E84 Support d''information', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('0bf2f4c2-85c0-3970-aa61-3c1eaa79b0d2', 'Support d''information', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('576856ee-db50-35ca-ab23-e9a102db76c0', 'E84 Informationsträger', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('cbed5e4c-b105-3359-bcf2-3de7f27251eb', 'Informationsträger', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'de', 'altLabel');
INSERT INTO "values" VALUES ('1a09dd82-3d36-32d2-8b13-4394df614476', 'E84 Suporte de Informação', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('24af5c04-f7a2-35b0-bda3-735457a3863d', 'Suporte de Informação', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('f2ae4e90-e12b-3f26-9df3-7d63f0169040', 'E84 信息载体', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('35436247-010d-3dc7-b71f-cb961e2ba118', '信息载体', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('3c7366a6-d81e-3504-ac23-7d9309b28b31', '有说明', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('f80e0ceb-e895-3921-baf5-7407b86b4f4a', 'P13 a détruit', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('cb96133f-c382-30dc-9ca3-99a820ae9706', 'a détruit', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('6ebfff6f-545d-3014-b14f-890212b71094', 'P13 уничтожил', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('4dc784fc-a818-35d3-a290-46426ef335ce', 'уничтожил', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('574899af-45fa-3a06-be8e-2ded1ac7e1c1', 'This class comprises all instances of E22 Man-Made Object that are explicitly designed to act as persistent physical carriers for instances of E73 Information Object.
An E84 Information Carrier may or may not contain information, e.g., a diskette. Note that any E18 Physical Thing may carry information, such as an E34 Inscription. However, unless it was specifically designed for this purpose, it is not an Information Carrier. Therefore the property P128 carries (is carried by) applies to E18 Physical Thing in general.
	', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('77f5c24d-7909-3c81-a59b-61bec792e057', 'E85 Beitritt', 'b4f509a5-bf1f-3b1b-875f-e4dade14f862', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('b65edb95-21f8-3ce7-a59e-dfac8c07b29e', 'Beitritt', 'b4f509a5-bf1f-3b1b-875f-e4dade14f862', 'de', 'altLabel');
INSERT INTO "values" VALUES ('8b9daa94-838f-3b07-9221-3eb63aa3e604', 'E85 Joining', 'b4f509a5-bf1f-3b1b-875f-e4dade14f862', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b53f0499-8627-32e1-ada9-90ab56c3d0e0', 'Joining', 'b4f509a5-bf1f-3b1b-875f-e4dade14f862', 'en', 'altLabel');
INSERT INTO "values" VALUES ('34a47ea1-1dd5-3228-a9f4-b15902de5701', 'E85 加入', 'b4f509a5-bf1f-3b1b-875f-e4dade14f862', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('7e8ee542-2e6c-395c-a6ff-f9cb3a661d7a', '加入', 'b4f509a5-bf1f-3b1b-875f-e4dade14f862', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('8d77f2fa-aa71-3edd-9563-ec096f86cbbc', 'This class comprises the activities that result in an instance of E39 Actor becoming a member of an instance of E74 Group. This class does not imply initiative by either party. It may be the initiative of a third party.
Typical scenarios include becoming a member of a social organisation, becoming employee of a company, marriage, the adoption of a child by a family and the inauguration of somebody into an official position. 
', 'b4f509a5-bf1f-3b1b-875f-e4dade14f862', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('0215dd54-facb-34f3-9ddc-c4eab7a232af', 'E86 Austritt', '2c5fbf8d-b6ca-39f4-8ee7-5522732fe77e', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('941210e3-401e-364f-a683-ae94f3179efd', 'Austritt', '2c5fbf8d-b6ca-39f4-8ee7-5522732fe77e', 'de', 'altLabel');
INSERT INTO "values" VALUES ('0f108bac-3176-35f2-a94f-a256d7a5d802', 'E86 Leaving', '2c5fbf8d-b6ca-39f4-8ee7-5522732fe77e', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('22c2dfe1-43c1-3c79-b892-b67c18976224', 'Leaving', '2c5fbf8d-b6ca-39f4-8ee7-5522732fe77e', 'en', 'altLabel');
INSERT INTO "values" VALUES ('f58e3622-994e-3fe2-853f-cf4e183ecb20', 'E86 脱离', '2c5fbf8d-b6ca-39f4-8ee7-5522732fe77e', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('b004412e-28a7-3549-8462-f407bb3e8d9e', '脱离', '2c5fbf8d-b6ca-39f4-8ee7-5522732fe77e', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('e1b6ba28-0822-3c87-bc84-0b3b31b6953d', 'This class comprises the activities that result in an instance of E39 Actor to be disassociated from an instance of E74 Group. This class does not imply initiative by either party. It may be the initiative of a third party. 
Typical scenarios include the termination of membership in a social organisation, ending the employment at a company, divorce, and the end of tenure of somebody in an official position.', '2c5fbf8d-b6ca-39f4-8ee7-5522732fe77e', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('ff6f6360-c028-308c-a9c6-0d93dab7cdbe', 'E87 Kuratorische Tätigkeit', 'de74c0db-a5fa-3f45-8684-344c379e6b0d', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('616321f0-980e-37d6-8213-b66d430e813b', 'Kuratorische Tätigkeit', 'de74c0db-a5fa-3f45-8684-344c379e6b0d', 'de', 'altLabel');
INSERT INTO "values" VALUES ('c559d5c4-9854-3ec3-b978-ba5e74588bb0', 'E87 Curation Activity', 'de74c0db-a5fa-3f45-8684-344c379e6b0d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('04e88122-3c85-3fb9-9880-b6d1036c1553', 'Curation Activity', 'de74c0db-a5fa-3f45-8684-344c379e6b0d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('2ea3ec12-6811-3240-b79e-d4a9708c5f31', 'E87 典藏管理', 'de74c0db-a5fa-3f45-8684-344c379e6b0d', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('10dfe983-b84a-30e5-8e9a-657c49b59770', '典藏管理', 'de74c0db-a5fa-3f45-8684-344c379e6b0d', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('8c404195-0b81-3ae8-b919-0606ef897d74', 'This class comprises the activities that result in the continuity of management and the preservation and evolution of instances of E78 Collection, following an implicit or explicit curation plan. 
It specializes the notion of activity into the curation of a collection and allows the history of curation to be recorded.
Items are accumulated and organized following criteria like subject, chronological period, material type, style of art etc. and can be added or removed from an E78 Collection for a specific purpose and/or audience. The initial aggregation of items of a collection is regarded as an instance of E12 Production Event while the activity of evolving, preserving and promoting a collection is regarded as an instance of E87 Curation Activity.
', 'de74c0db-a5fa-3f45-8684-344c379e6b0d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('a3ab68bc-40b6-3628-819a-636d2dd6f28b', 'E89 Aussagenobjekt', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('b0b8a4a9-da54-3b7d-8cb0-9390dafc3ee0', 'Aussagenobjekt', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', 'de', 'altLabel');
INSERT INTO "values" VALUES ('80cdb33c-1526-340f-95e3-fc9037dcb440', 'E89 Propositional Object', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('f3441c15-eec0-32fc-881f-0d5740582981', 'Propositional Object', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('72f31ecf-bd66-3405-9489-b52376354575', 'E89 陈述性物件', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('4ec1d9a7-02e7-3cc3-97e5-a26cf08a0b27', '陈述性物件', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('53aa026d-ac94-39bc-b963-90174c935033', 'This class comprises immaterial items, including but not limited to stories, plots, procedural prescriptions, algorithms, laws of physics or images that are, or represent in some sense, sets of propositions about real or imaginary things and that are documented as single units or serve as topics of discourse. 
	
This class also comprises items that are “about” something in the sense of a subject. In the wider sense, this class includes expressions of psychological value such as non-figural art and musical themes. However, conceptual items such as types and classes are not instances of E89 Propositional Object. This should not be confused with the definition of a type, which is indeed an instance of E89 Propositional Object.
', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('be22cfdf-44d5-3cfd-b65d-e8ca3895d13e', 'E90 Symbolisches Objekt', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('205df178-7428-388b-8147-bf27f1e1af13', 'Symbolisches Objekt', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'de', 'altLabel');
INSERT INTO "values" VALUES ('0032b19b-49f2-3d81-a6d8-383ac5187493', 'E90 Symbolic Object', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('f527eeb5-0bfa-3dc4-84dd-ae52d0cbfd22', 'Symbolic Object', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'en', 'altLabel');
INSERT INTO "values" VALUES ('a02ee977-e734-356c-9110-a8b2d9c2fc6e', 'E90 符号物件', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('4d05bd62-0ddf-3ad3-96c0-a1fe560bd1eb', '符号物件', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('e0aa2cb9-c84d-3b77-b416-8ea0f67d4321', 'This class comprises identifiable symbols and any aggregation of symbols, such as characters, identifiers, traffic signs, emblems, texts, data sets, images, musical scores, multimedia objects, computer program code or mathematical formulae that have an objectively recognizable structure and that are documented as single units.
	It includes sets of signs of any nature, which may serve to designate something, or to communicate some propositional content.
	An instance of E90 Symbolic Object does not depend on a specific physical carrier, which can include human memory, and it can exist on one or more carriers simultaneously. An instance of E90 Symbolic Object may or may not have a specific meaning, for example an arbitrary character string.
	In some cases, the content of an instance of E90 Symbolic Object may completely be represented by a serialized content model, such.. as the property P3 has note allows for describing this content model…P3.1 has type: E55 Type to specify the encoding..
', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('c775aa3d-c091-3d7a-889f-487c4df32955', 'E92 Spacetime Volume', '94ffd715-18f7-310a-bee2-010d800be058', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('66384838-41f7-3ae7-8275-68e0409c03c0', 'Spacetime Volume', '94ffd715-18f7-310a-bee2-010d800be058', 'en', 'altLabel');
INSERT INTO "values" VALUES ('96353b48-4028-32da-a164-3b3657833b44', 'a eu lieu sur ou dans', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('fc153c42-c309-32bd-a187-d92851ec3f03', 'P8 ocorreu em ou dentro', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('54e8be29-5d43-350b-b76f-f39b5db4c5ca', 'ocorreu em ou dentro', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('7e597788-0dd8-39be-b3f2-ff8b6bff559c', 'P8 发生所在物件是', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('93d3693e-c08b-380d-bbea-f7b305c36542', '发生所在物件是', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('f4a0e013-dc0b-3795-b05b-859349d4f936', 'P13 κατέστρεψε', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('e306b46f-ae55-3c19-b54e-cd5e8c0dd0d6', 'κατέστρεψε', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'el', 'altLabel');
INSERT INTO "values" VALUES ('43f91225-d025-366e-bedd-517cbef46019', 'P13 destroyed', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('6bf62c1b-37c2-3354-9ee6-f9ae96954818', 'This class comprises 4 dimensional point sets (volumes) in physical spacetime regardless its true geometric form. They may derive their identity from being the extent of a material phenomenon or from being the interpretation of an expression defining an extent in spacetime. 
	Intersections of instances of E92 Spacetime Volume, Place and Timespan are also regarded as instances of E92 Spacetime Volume.  An instance of E92 Spacetime Volume is either contiguous or composed of a finite number of contiguous subsets. 
	Its boundaries may be fuzzy due to the properties of the phenomena it derives from or due to the limited precision up to which defining expression can be identified with a real extent in spacetime. The duration of existence of an instance of a spacetime volume is trivially its projection on time.
', '94ffd715-18f7-310a-bee2-010d800be058', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('cd2a5ad0-9918-35ad-b9a7-20b5dbed35a5', 'E93 Presence', 'b9af2b98-3c9d-34f1-9a87-f5eb071fb53d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('df181717-3805-3923-9e7f-0cabc827389c', 'Presence', 'b9af2b98-3c9d-34f1-9a87-f5eb071fb53d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('d8d82a43-97f7-3b92-a14f-815773b19921', 'This class comprises instances of E92 Spacetime Volume that result from intersection of instances of E92 Spacetime Volume with an instance of E52 Time-Span.  The identity of an instance of this class is determined by the identities of the  constituing spacetime volume and the time-span. 
	
This class can be used to define temporal snapshots at a particular time-span, such as the extent of the Roman Empire at 33 B.C., or the extent occupied by a museum object at rest in an exhibit. In particular, it can be used to define the spatial projection of a spacetime volume during a particular time-span,  such as the maximal spatial extent of a flood at some particular hour, or all areas covered by the Poland within the 20th century AD.
', 'b9af2b98-3c9d-34f1-9a87-f5eb071fb53d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('f863d3f8-467e-3d15-885c-87ae0047d503', 'E94 Space', '1036c7f1-ea95-3ad8-886f-849ca10f9584', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('03a3fd37-cfc4-3478-bf85-05b855159392', 'Space', '1036c7f1-ea95-3ad8-886f-849ca10f9584', 'en', 'altLabel');
INSERT INTO "values" VALUES ('82064453-dc1d-3f73-a583-5b4ec1d735d0', 'This class comprises instances of E92 Spacetime Volume that result from intersection of instances of
E92 Spacetime Volume with an instance of E52 Time-Span. The identity of an instance of this class is
determined by the identities of the constituing spacetime volume and the time-span.
', '1036c7f1-ea95-3ad8-886f-849ca10f9584', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('de22539f-e5fe-3dd8-b0fd-e227d14cbc40', 'P1 αναγνωρίζεται ως', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('8bdc0e5c-172a-324a-b681-f7ba82d17517', 'αναγνωρίζεται ως', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'el', 'altLabel');
INSERT INTO "values" VALUES ('9a1aab49-5238-3595-86f6-a5703ad0694f', 'P1 wird bezeichnet als', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('258db39b-8c31-3c61-84bf-1c33b21f9e37', 'wird bezeichnet als', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'de', 'altLabel');
INSERT INTO "values" VALUES ('492f3991-5986-3f08-b1c8-e6d0dab58852', 'P1 is identified by', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('8dfcdea1-d968-3170-a32e-168101c0468a', 'is identified by', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'en', 'altLabel');
INSERT INTO "values" VALUES ('f2c0c931-b1ad-3d2a-b8c5-6df02049e561', 'P1 идентифицируется посредством', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('ee0c2d92-c36a-3446-bed7-346d5a7c4bec', 'идентифицируется посредством', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('bf2a49e7-ec6f-3883-a45e-0f1653c749e9', 'P1 est identifiée par', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('12a1c96b-8dc7-3d01-afab-6d3d363e7521', 'est identifiée par', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('029ceb51-9045-3a22-8590-0e2066db4e27', 'P1 é identificado por', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('4e330e67-a2ca-3d7e-8b54-638c20c0c38c', 'é identificado por', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('424c0d13-d44a-3527-ac27-f4fadbf6ac79', 'P1 有识别称号', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('309ba400-613e-31a1-a30b-6822cb896d80', '有识别称号', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('70a10c48-a2d3-3d02-9488-161772d5a507', 'This property describes the naming or identification of any real world item by a name or any other identifier. 
This property is intended for identifiers in general use, which form part of the world the model intends to describe, and not merely for internal database identifiers which are specific to a technical system, unless these latter also have a more general use outside the technical context. This property includes in particular identification by mathematical expressions such as coordinate systems used for the identification of instances of E53 Place. The property does not reveal anything about when, where and by whom this identifier was used. A more detailed representation can be made using the fully developed (i.e. indirect) path through E15 Identifier Assignment.
', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('af2d9b8c-a6fc-3437-a893-1f3198bfd0d7', 'P2 hat den Typus', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('b2685470-5086-3cda-b0e0-f926f2681d02', 'hat den Typus', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'de', 'altLabel');
INSERT INTO "values" VALUES ('00bd0506-7340-37b9-a74c-b0014876acb8', 'P2 has type', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('8c56cde2-2ce1-3322-9004-e1924debbec5', 'has type', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'en', 'altLabel');
INSERT INTO "values" VALUES ('eb287a83-af3d-37ac-939e-a638fdb28ef7', 'P2 έχει τύπο', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('1dbd97f7-0303-3743-b8fb-edd3884b646c', 'έχει τύπο', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'el', 'altLabel');
INSERT INTO "values" VALUES ('9ec2d07b-77bf-3bcb-97e4-667cabca9458', 'P2 est de type', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('d33dc2fa-3403-365a-bc32-1e0492ba9857', 'est de type', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('bd0b5133-5ec0-3e0b-9880-cdf04e6502ef', 'P2 имеет тип', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('68af98e1-1d1c-3ec4-b7e1-4d4b229c6914', 'имеет тип', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('3ae38f86-2435-3f36-9ab8-a69e91b15897', 'P2 é do tipo', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('f04615aa-4359-3983-868a-ca3b9647c597', 'é do tipo', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('cd9a8b70-2503-31aa-9046-787643bf14f0', 'P2 有类型', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('0966ca12-2762-31a4-a73f-7589272bd366', '有类型', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('5999aaa4-65d6-3523-b7be-d0a040e611f7', 'This property allows sub typing of CRM entities - a form of specialisation – through the use of a terminological hierarchy, or thesaurus. 
The CRM is intended to focus on the high-level entities and relationships needed to describe data structures. Consequently, it does not specialise entities any further than is required for this immediate purpose. However, entities in the isA hierarchy of the CRM may by specialised into any number of sub entities, which can be defined in the E55 Type hierarchy. E51 Contact Point, for example, may be specialised into “e-mail address”, “telephone number”, “post office box”, “URL” etc. none of which figures explicitly in the CRM hierarchy. Sub typing obviously requires consistency between the meaning of the terms assigned and the more general intent of the CRM entity in question.
', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('e970850b-c008-3205-81a2-16ac9013d5dc', 'P3 hat Anmerkung', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f7702b89-17f0-3da4-a724-3bce3fc4020c', 'hat Anmerkung', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'de', 'altLabel');
INSERT INTO "values" VALUES ('e057dc7b-258b-3c07-8c02-c0dddae4f74b', 'P3 имеет примечание', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('4f48bac2-e6b8-39b9-9239-0ef5f0dfc5ea', 'имеет примечание', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('dbd04310-2e81-3302-85e2-21543fe7a788', 'P3 has note', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('22d3e1cf-8af0-3ccf-9174-46d39f994a18', 'has note', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'en', 'altLabel');
INSERT INTO "values" VALUES ('6aa466f4-17c1-33d5-83ea-efe51bc3ad9a', 'P3 a pour note', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('7c7206e9-bb7f-33c7-b83d-0a2f691a7107', 'a pour note', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('2e45f90e-91c6-3fcf-97dc-ac508c0ab26a', 'P3 έχει επεξήγηση', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('160bfa82-ffba-33bd-962c-60502a44d473', 'έχει επεξήγηση', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'el', 'altLabel');
INSERT INTO "values" VALUES ('e8f37772-eb1f-311b-a62c-5941f30cf6e0', 'P3 tem nota', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('dc67440f-e701-346d-ba19-46194c4eb0be', 'tem nota', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('a85ff5de-f70c-34df-8b8a-689eb6db1ccc', 'P3 有说明', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('8a61cc51-2999-3e67-8eb1-c53d8442d34d', 'This property is a container for all informal descriptions about an object that have not been expressed in terms of CRM constructs. 
In particular it captures the characterisation of the item itself, its internal structures, appearance etc.
Like property P2 has type (is type of), this property is a consequence of the restricted focus of the CRM. The aim is not to capture, in a structured form, everything that can be said about an item; indeed, the CRM formalism is not regarded as sufficient to express everything that can be said. Good practice requires use of distinct note fields for different aspects of a characterisation. The P3.1 has type property of P3 has note allows differentiation of specific notes, e.g. “construction”, “decoration” etc. 
An item may have many notes, but a note is attached to a specific item.
', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('d8006cf6-e10f-359a-b774-0ab6e6620fc4', 'P4 a pour durée', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('e5accd04-a55c-3e60-b47f-0b6733b95a30', 'a pour durée', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('1404b706-a8c3-3163-9362-b07340864782', 'P4 has time-span', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('8da4f0ba-850b-3c14-b1ba-7a656bb79c74', 'has time-span', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'en', 'altLabel');
INSERT INTO "values" VALUES ('a67a60c5-92cb-32c4-9642-512f808b45a2', 'P4 hat Zeitspanne', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('36fb75c7-b31d-3bab-bd95-f49ec56a5fad', 'hat Zeitspanne', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'de', 'altLabel');
INSERT INTO "values" VALUES ('e90ca173-8cdf-3841-834e-b278821a54a7', 'P4 βρισκόταν σε εξέλιξη', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('882a178e-d78d-3a36-9990-95aec8009e47', 'βρισκόταν σε εξέλιξη', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'el', 'altLabel');
INSERT INTO "values" VALUES ('bfbc4d1b-cb72-33cf-9b87-4da027a039fd', 'P4 имеет временной отрезок', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('00e4b51d-f6fd-327d-91f7-727a1505d363', 'имеет временной отрезок', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('b477d8b8-e06a-33ac-b66e-69e2a237b0c0', 'P4 tem período de tempo', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('14791515-4342-33c1-9a42-202167815480', 'tem período de tempo', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('d2481f4b-b3e9-310f-8443-004ffc368163', 'P4 发生时段是', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('56addd7f-f57e-3b27-ad11-ae6d3ec91786', '发生时段是', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('08d9132f-b2c4-30e8-9f12-848888bc17a8', 'This property describes the temporal confinement of an instance of an E2 Temporal Entity.
The related E52 Time-Span is understood as the real Time-Span during which the phenomena were active, which make up the temporal entity instance. It does not convey any other meaning than a positioning on the “time-line” of chronology. The Time-Span in turn is approximated by a set of dates (E61 Time Primitive). A temporal entity can have in reality only one Time-Span, but there may exist alternative opinions about it, which we would express by assigning multiple Time-Spans. Related temporal entities may share a Time-Span. Time-Spans may have completely unknown dates but other descriptions by which we can infer knowledge.
', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('5d970207-5a9a-3253-8206-49c0d7e9df15', 'P5 consists of', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('1f8ea007-6977-328f-8ffd-ed5136f30557', 'consists of', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'en', 'altLabel');
INSERT INTO "values" VALUES ('ebf105ef-4b03-3d10-93fa-b74d8ec7431e', 'P5 consiste en', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('6b307d11-a60a-345f-93ed-582f7fb3c4f7', 'consiste en', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('9b95b60c-84c5-346d-8f31-58ac99596ae8', 'P5 αποτελείται από', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('72f2290b-8794-360b-a59d-7e235cbbb12c', 'αποτελείται από', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'el', 'altLabel');
INSERT INTO "values" VALUES ('df75465f-f0c8-3cea-a7ea-02fe53e44263', 'P5 besteht aus', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('e871a7a9-745a-3fb9-8f7d-ef47219548f4', 'besteht aus', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'de', 'altLabel');
INSERT INTO "values" VALUES ('7d6f89dc-656b-35b5-b7a3-d931f74104a4', 'P5 состоит из', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('73d0e60e-6a47-352c-aefc-6203a651cdcd', 'состоит из', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('70b953ff-a5cf-34aa-9748-d81275db922b', 'P5 consiste de', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('fbfab37c-dd80-3dd6-8b5b-9c0c4138d0f4', 'consiste de', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('3f78b270-c64b-3c09-bd38-80e0944f2c63', 'P5 包含', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('d2d23a1b-8f14-34ad-8a80-9fd36794af04', '包含', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('1ff0aab7-ba51-330a-b240-b16651b1a364', 'This property describes the decomposition of an E3 Condition State into discrete, subsidiary states. 
It is assumed that the sub-states into which the condition state is analysed form a logical whole - although the entire story may not be completely known – and that the sub-states are in fact constitutive of the general condition state. For example, a general condition state of “in ruins” may be decomposed into the individual stages of decay', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('350f2374-d67f-3a14-a852-d65fc8e2cae2', 'P7 a eu lieu dans', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('53bbfb28-da10-3bc4-b772-ead4dec220d1', 'a eu lieu dans', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('1be85580-91b7-35e7-87a3-fdbe67c1f026', 'P7 совершался на', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('9387f145-0b12-34a1-8f98-080fcfda3576', 'совершался на', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('53e2b376-ad92-39d7-ba59-dd1bd24e6de1', 'P7 έλαβε χώρα σε', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('7750e3d2-1404-3258-8e31-5977115fb63a', 'έλαβε χώρα σε', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'el', 'altLabel');
INSERT INTO "values" VALUES ('87e98158-2045-3056-9f9b-e7f8e287f6f4', 'P7 fand statt in', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('e802cdd1-4058-316c-8794-6bb2085edae5', 'fand statt in', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'de', 'altLabel');
INSERT INTO "values" VALUES ('14f8ec52-dd4a-324c-acbe-3bcc38d9c0ae', 'P7 took place at', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('edbf3c9c-c0aa-3b9e-a16e-92dafb3e0d7b', 'took place at', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'en', 'altLabel');
INSERT INTO "values" VALUES ('519e8a79-d6ea-3884-8b3a-71db61f72b9b', 'P7 ocorreu em', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('e863b041-9fb7-3620-8b85-ce06fc80477c', 'ocorreu em', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('fc131d07-c1b8-35de-8175-de2082130879', 'P7 发生地在', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('69f2f091-98ff-373c-9319-61e094d69aac', '发生地在', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('75726983-341c-32d4-b12d-c568f89aab6e', 'This property describes the spatial location of an instance of E4 Period. 

The related E53 Place should be seen as an approximation of the geographical area within which the phenomena that characterise the period in question occurred. P7took place at (witnessed) does not convey any meaning other than spatial positioning (generally on the surface of the earth).  For example, the period "Révolution française" can be said to have taken place in “France”, the “Victorian” period, may be said to have taken place in “Britain” and its colonies, as well as other parts of Europe and north America.
A period can take place at multiple locations.
It is a shortcut of the more fully developed path from E4 Period through P161 has spatial projection, E53 Place, P89 falls within (contains) to E53 Place. 
', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('f74544ad-f143-3f4c-adcd-79a02cc3f0ec', 'P8 имел место на или в', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('6eba00e9-39da-33ba-9d51-caf9dc749472', 'имел место на или в', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('15eda132-10a3-315f-9ef2-98ac2959219a', 'P8 έλαβε χώρα σε ή εντός', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('f105264d-1e47-33de-b461-8f98de4d6455', 'έλαβε χώρα σε ή εντός', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'el', 'altLabel');
INSERT INTO "values" VALUES ('5e30f894-000a-3dd0-ba91-57b1ef868aa9', 'P8 fand statt auf oder innerhalb von ', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('ee6ca9c0-6239-3242-8252-53d5280b70fa', 'fand statt auf oder innerhalb von ', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'de', 'altLabel');
INSERT INTO "values" VALUES ('645a3607-07e0-363a-bca9-7db1963eb749', 'P8 took place on or within', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('7630b64c-df74-3a44-9a22-a83700a892de', 'took place on or within', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'en', 'altLabel');
INSERT INTO "values" VALUES ('98f94b06-7cf5-33dd-b557-3f82dd664497', 'P8 a eu lieu sur ou dans', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('9b0d3a38-9a45-3486-9912-d2898fb05342', 'This property describes the location of an instance of E4 Period with respect to an E19 Physical Object. 
P8 took place on or within (witnessed) is a shortcut of the more fully developed path from E4 Period through P7 took place at, E53 Place, P156 occupies (is occupied by) to E18 Physical Thing.

It describes a period that can be located with respect to the space defined by an E19 Physical Object such as a ship or a building. The precise geographical location of the object during the period in question may be unknown or unimportant. 
For example, the French and German armistice of 22 June 1940 was signed in the same railway carriage as the armistice of 11 November 1918.
', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('9ae74c88-ad73-3854-bf9e-b8097f23541a', 'P9 αποτελείται από', '6909b643-03f7-3606-b276-2be0e8773207', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('a21dad2d-b0a4-3735-8690-a45fbb54eeb7', 'αποτελείται από', '6909b643-03f7-3606-b276-2be0e8773207', 'el', 'altLabel');
INSERT INTO "values" VALUES ('5741ffea-7ed1-3b17-b895-ea37e6452e1d', 'P9 consists of', '6909b643-03f7-3606-b276-2be0e8773207', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('7f41b1bc-499d-325f-95b9-6b94dfbabdf9', 'consists of', '6909b643-03f7-3606-b276-2be0e8773207', 'en', 'altLabel');
INSERT INTO "values" VALUES ('2735d96b-d2fe-3be3-a0fc-a9ab0155b1a8', 'P9 setzt sich zusammen aus', '6909b643-03f7-3606-b276-2be0e8773207', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('1b289407-8d92-33be-af23-ad78ac300a2b', 'setzt sich zusammen aus', '6909b643-03f7-3606-b276-2be0e8773207', 'de', 'altLabel');
INSERT INTO "values" VALUES ('3326b1be-b4b5-36da-ba7d-c311e5ad5e54', 'P9 состоит из', '6909b643-03f7-3606-b276-2be0e8773207', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('cd0cfd28-011c-38c3-b155-4153d1e8ffdf', 'состоит из', '6909b643-03f7-3606-b276-2be0e8773207', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('d38bcb9c-4330-3886-8312-802c178d7791', 'P9 consiste en', '6909b643-03f7-3606-b276-2be0e8773207', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('48a5d30b-94e9-308f-aa65-f063faed44a8', 'consiste en', '6909b643-03f7-3606-b276-2be0e8773207', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('6ecfd70b-70b1-3ee8-89a8-f2e7085fef3b', 'P9 consiste de', '6909b643-03f7-3606-b276-2be0e8773207', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('c64c12ed-ee85-3177-bb0f-0cfbf35b62b2', 'consiste de', '6909b643-03f7-3606-b276-2be0e8773207', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('36ded9f6-bb29-3df9-bcf2-e343a3059460', 'P9 包含子时期', '6909b643-03f7-3606-b276-2be0e8773207', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('10cb6e50-a22b-325b-a165-d2b9dba51d33', '包含子时期', '6909b643-03f7-3606-b276-2be0e8773207', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('0b973e61-60f1-323a-ba1b-d8cce661b76f', 'This property associates an instance of E4 Period with another instance of E4 Period that is defined by a subset of the phenomena that define the former. Therefore the spacetime volume of the latter must fall within the spacetime volume of the former.
', '6909b643-03f7-3606-b276-2be0e8773207', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('3b203c3c-510d-3d1b-8a2b-3250e37dc55d', 'P10 находится в пределах', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('97523901-ecf2-33c0-9643-e74e3ed1d528', 'находится в пределах', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('03ec78b5-0255-3443-a21c-cd8de815d95f', 'P10 εμπίπτει', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('f39fe1bc-c144-343e-a44b-64c606837790', 'εμπίπτει', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'el', 'altLabel');
INSERT INTO "values" VALUES ('ecd422bb-1e40-3b58-a41b-7bde47d5b125', 'P10 s’insère dans le cours de', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('19eefb30-1ff7-3dc1-9536-614dbae519b5', 's’insère dans le cours de', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('68e7589c-621b-3b7a-8b40-039fb215ed63', 'P10 falls within', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('9f6fcb4d-f449-391a-aed5-be841048ec2d', 'falls within', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'en', 'altLabel');
INSERT INTO "values" VALUES ('6f0a33ba-e8c3-3b9d-b615-de7baab646dc', 'P10 fällt in', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('7103b36a-3791-3133-8ac9-9dac53d64f90', 'fällt in', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'de', 'altLabel');
INSERT INTO "values" VALUES ('01dffbbf-da82-3e74-9d70-acfc37f385bb', 'P10 está contido em', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('29d2c37a-2918-3267-a537-9818ba301665', 'está contido em', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('554687fc-05b5-30bb-afc8-76709089332e', 'P10 发生时间涵盖於', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('29572f5d-2226-3779-b0cf-0fae531c51a0', '发生时间涵盖於', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('79c4f04c-42e8-3c1f-81b5-37a30a251eee', 'This property associates an instance of E92 Spacetime Volume with another instance of E92 Spacetime Volume that falls within the latter. In other words, all points in the former are also points in the latter.
', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('ee126e85-6620-3f0d-9e64-7eaa14f8a81c', 'P11 a eu pour participant', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('ced6177c-d298-33c4-8ab1-e8fcda7fd33b', 'a eu pour participant', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('f394c5c3-f560-3e04-911e-7e5a92f72aca', 'P11 имел участника', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('9b2c18c0-0713-3c52-8a12-072fbb6d4c9f', 'имел участника', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('c79c4260-2027-3eb8-946c-a787fb43fbcc', 'P11 hatte Teilnehmer', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('fabfb8fb-6e48-3c19-87aa-b0f269c69371', 'hatte Teilnehmer', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'de', 'altLabel');
INSERT INTO "values" VALUES ('d9e6a115-dffe-3d0d-8236-11f90cf1feb8', 'P11 had participant', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('f80dea18-2ab9-35f8-846f-16a0a0148390', 'had participant', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c37f59e3-cf52-3181-96df-3d82ab06baee', 'P11 είχε συμμέτοχο', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('452be7df-1240-3451-93e0-2b2a9523d59a', 'είχε συμμέτοχο', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'el', 'altLabel');
INSERT INTO "values" VALUES ('3da8ab28-01d6-31b8-b61e-c66c360239c5', 'P11 tem participante', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('b54e3661-defa-38e6-919c-73ce146ac02d', 'tem participante', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b1d6f7d2-7e8c-3ddd-8672-576f6b7a5314', 'P11 有参与者', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('64558ba9-e9d9-3da6-81cd-3b4c83cc24cc', '有参与者', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('9a5d662f-7217-388d-b842-a799b4906d74', 'This property describes the active or passive participation of instances of E39 Actors in an E5 Event. 
It connects the life-line of the related E39 Actor with the E53 Place and E50 Date of the event. The property implies that the Actor was involved in the event but does not imply any causal relationship. The subject of a portrait can be said to have participated in the creation of the portrait.
', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('21e94ffb-0c69-33f0-8a1f-1c971186b3cc', 'P12 occurred in the presence of', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('2611ea9e-15ce-38c9-840f-c3ed8fdc6b35', 'occurred in the presence of', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'en', 'altLabel');
INSERT INTO "values" VALUES ('ef3438a3-8fb3-3d71-acbf-e21f0c70c225', 'P12 появился в присутствии', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('30da444a-88fb-3752-9b14-0e077bfb82d4', 'появился в присутствии', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('1803dfd7-9f6e-3ee4-94d1-d308e16c3d37', 'P12 fand statt im Beisein von', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('892ad13d-a196-3b30-aa43-3809784286b5', 'fand statt im Beisein von', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'de', 'altLabel');
INSERT INTO "values" VALUES ('40418703-b21a-3736-b3f8-0c73928c6fd1', 'P12 συνέβη παρουσία του/της', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('a92bf536-6314-3afc-b8ee-e33a9e018337', 'συνέβη παρουσία του/της', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'el', 'altLabel');
INSERT INTO "values" VALUES ('8bc7ba47-6dd3-323e-9998-6e776afa5856', 'P12 est arrivé en présence de', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('7a9b3d52-9a13-38a2-93a3-96d997164494', 'est arrivé en présence de', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('5d71b87c-2aa1-39aa-805d-a2161ea94dfd', 'P12 ocorreu na presença de', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('de77dd98-05df-3a55-922b-86c2c22b782a', 'ocorreu na presença de', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('7fd92679-77e7-3402-86d9-a6e440a8885d', 'P12 发生现场存在', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('e5e1acc4-e09e-3e0b-9174-2e1dcc176c02', '发生现场存在', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('ddfc46bf-9891-3e1d-9112-8ad8b12efbec', 'This property describes the active or passive presence of an E77 Persistent Item in an E5 Event without implying any specific role. 
It connects the history of a thing with the E53 Place and E50 Date of an event. For example, an object may be the desk, now in a museum on which a treaty was signed. The presence of an immaterial thing implies the presence of at least one of its carriers.
', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('95505d7d-c308-3979-aad1-2dfb022c4a36', 'P13 zerstörte', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('e85d422b-4879-3127-aecb-3907be4102d8', 'zerstörte', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'de', 'altLabel');
INSERT INTO "values" VALUES ('ffc2dae6-491c-3e71-91fe-bba124228d40', 'destroyed', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'en', 'altLabel');
INSERT INTO "values" VALUES ('ffbf2b26-84cf-3037-a167-4615036361de', 'P13 destruiu', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('3700f3a4-7699-389e-927b-63fe67e7d7f2', 'destruiu', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('22f0e662-78ba-382c-b87c-0a3c1eabd3ba', 'P13 毁灭了', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('1dbed35d-ee9c-3062-87f8-5e9c697144dd', '毁灭了', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('8c4ecad0-98ed-319b-bef7-d97ee4d9bba1', 'This property allows specific instances of E18 Physical Thing that have been destroyed to be related to a destruction event. 
Destruction implies the end of an item’s life as a subject of cultural documentation – the physical matter of which the item was composed may in fact continue to exist. A destruction event may be contiguous with a Production that brings into existence a derived object composed partly of matter from the destroyed object.
', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('53ceb476-8025-30a3-8783-f90a0f96637d', 'P14 wurde ausgeführt von', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('a3d3571a-9e7b-3af6-8fed-4f304a2db768', 'wurde ausgeführt von', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'de', 'altLabel');
INSERT INTO "values" VALUES ('700f1298-e20f-3b8e-a92b-b05130b58732', 'P14 réalisée par', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('a99f065c-727e-378a-8d18-8ddeb6ad61e1', 'réalisée par', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('62630e07-6fd8-3d09-8c41-540ce518e879', 'P14 carried out by', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('af8008f2-92bd-38bc-ac07-516c5b3c989d', 'carried out by', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'en', 'altLabel');
INSERT INTO "values" VALUES ('e3835045-2785-389f-a29d-244890234de9', 'P14 πραγματοποιήθηκε από', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('d5461857-0e1d-3500-a3e1-9e5a15a8b1a6', 'πραγματοποιήθηκε από', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'el', 'altLabel');
INSERT INTO "values" VALUES ('5ea5cf6f-f522-33f2-a8c4-c7958734616d', 'P14 выполнялся', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('2949d342-8c72-3a3c-8606-354413246e97', 'выполнялся', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('a5c558cd-e447-32c8-acba-ba13e356db4e', 'P14 realizada por', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('080c52dc-c143-314a-9cc5-a9127761ec21', 'realizada por', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('942cf89d-7388-30c3-91e9-ba24531f9c1f', 'P14 有执行者', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('06dc92cc-6564-3ee5-9ba3-3fe1e0ab0374', '有执行者', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('60fef912-ca6a-32b2-907b-a223c3ad605e', 'This property describes the active participation of an E39 Actor in an E7 Activity. 
It implies causal or legal responsibility. The P14.1 in the role of property of the property allows the nature of an Actor’s participation to be specified.
', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('b47c57eb-cb7f-3f37-9b24-9ae0f2617302', 'P15 wurde beeinflußt durch', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('e0c58f5a-8323-3888-af78-90e5f3e817d7', 'wurde beeinflußt durch', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'de', 'altLabel');
INSERT INTO "values" VALUES ('bf209447-ba65-399d-841a-a98c3601293b', 'P15 a été influencée par', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('65f6a28d-ec5b-3716-bb81-08ebc041e445', 'a été influencée par', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('cdccc5ab-3d59-3730-a40f-e6e1cd6969cc', 'P15 επηρεάστηκε από', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('1ac98dc2-93f4-3830-a37b-aca3bc40ebf8', 'επηρεάστηκε από', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'el', 'altLabel');
INSERT INTO "values" VALUES ('fdae8805-ce8e-3c7c-83e0-690483847b0c', 'P15 находился под влиянием', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('95fb7dc6-d6bd-32d3-9184-4bd6ea847c41', 'находился под влиянием', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('5231f2f4-25d8-3ba9-8466-57b1132ba3ed', 'P15 was influenced by', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('00241451-8132-33b6-9c62-b5dec0ee3c93', 'was influenced by', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('d1b475ac-a9ed-37e1-a295-a17bdd08cb97', 'P15 foi influenciado por ', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('bc4cf904-0ff7-3303-aece-d34745288ee4', 'foi influenciado por ', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('1131165b-fc86-3fe5-891d-d15f6f2678af', 'P15 有影响事物', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('be9d4b58-ec05-31ea-b13e-9e59a42226be', '有影响事物', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('922a40e4-6226-3e2f-843d-d5e276d4451c', 'This is a high level property, which captures the relationship between an E7 Activity and anything that may have had some bearing upon it.
The property has more specific sub properties.
', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('d74b4ffe-6450-37ff-8632-adb4261e5149', 'P16 a utilisé l''objet spécifique', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('e4d2f805-bb9d-3786-9496-98ecd9ff54ea', 'a utilisé l''objet spécifique', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('cb337acf-18a2-3f20-90c0-d390f165da24', 'P16 χρησιμοποίησε αντικείμενο', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('b1fe9aa4-2c0c-3dd3-8cbf-48d963bc06af', 'χρησιμοποίησε αντικείμενο', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'el', 'altLabel');
INSERT INTO "values" VALUES ('911578f6-90a2-3f47-accb-62df0d571a2c', 'P16 used specific object', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('c9f99590-f090-36a6-87a9-8949dc85128f', 'used specific object', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'en', 'altLabel');
INSERT INTO "values" VALUES ('07c1d76b-27ec-3b88-bc3a-91619c3a4aa4', 'P16 benutzte das bestimmte Objekt', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('decc38a2-5acd-3174-a641-74e2a825f6ff', 'benutzte das bestimmte Objekt', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'de', 'altLabel');
INSERT INTO "values" VALUES ('f2502319-ec68-3b4a-ba7b-37cfc3e3f567', 'P16 использовал особый объект', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('b9be25d7-19b6-3057-bbad-5cef177aef00', 'использовал особый объект', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('4cbdbef0-e737-3fa2-8a7b-e1067dd41f2d', 'P16 usou objeto específico', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('bfc436d0-59a9-3052-b312-857353397ba5', 'usou objeto específico', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('0080200d-f95d-3b76-ac81-c9fd8c824090', 'P16 使用特定物', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('1b9e0a5d-f5ae-3c26-a7e8-f27e06e3b40c', '使用特定物', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('81a44bd6-2874-3fe4-b9f2-4d7986113d7c', 'This property describes the use of material or immaterial things in a way essential to the performance or the outcome of an E7 Activity. 
This property typically applies to tools, instruments, moulds, raw materials and items embedded in a product. It implies that the presence of the object in question was a necessary condition for the action. For example, the activity of writing this text required the use of a computer. An immaterial thing can be used if at least one of its carriers is present. For example, the software tools on a computer.
Another example is the use of a particular name by a particular group of people over some span to identify a thing, such as a settlement. In this case, the physical carriers of this name are at least the people understanding its use.
', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('6f9df05d-c021-39da-88d2-e73ad0dd0d3d', 'P17 был обусловлен посредством', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('42ce269d-2f18-3eec-ac69-1270d74674c0', 'был обусловлен посредством', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('0f2d70f4-504d-31b9-9c15-8bd9e50a8a73', 'P17 wurde angeregt durch', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('7bd38767-40ed-35fb-af1d-0071437acdda', 'wurde angeregt durch', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'de', 'altLabel');
INSERT INTO "values" VALUES ('0f144b4a-0a6e-377d-bf9a-a586017297e9', 'P17 είχε ως αφορμή', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('02ab3b18-7ac9-35a4-8138-7852260fcf7b', 'είχε ως αφορμή', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'el', 'altLabel');
INSERT INTO "values" VALUES ('54db5f87-c5ab-36f7-860f-e00bf6067b87', 'P17 was motivated by', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('df3ceb6e-cf19-3b3d-a5ae-10f303c6c5c2', 'was motivated by', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c283baa7-19b5-32ef-a3f6-d06c3cb1af26', 'P17 a été motivée par', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('073d6dc9-6d06-3497-a5a8-d14600211f44', 'a été motivée par', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('6a941550-99db-3e3b-b92a-4c5b46d87204', 'P17 foi motivado por', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('8a69dd16-4edd-393e-886f-5db4f80e2414', 'foi motivado por', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('726f06d4-b01d-3443-a152-07e18cc784c1', 'P17 有促动事物', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('a9bd9c86-5c62-362c-bd1f-e2ed7db9a14f', '有促动事物', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('2edd5b1e-2893-3c76-a9b2-25ba73bdbe63', 'This property describes an item or items that are regarded as a reason for carrying out the E7 Activity. 
For example, the discovery of a large hoard of treasure may call for a celebration, an order from head quarters can start a military manoeuvre. 
', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('a1bb6c81-c57d-39b7-a7aa-bbae189c586b', 'P19 был предполагаемым использованием для', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('0c532ab8-cdd3-391d-92ba-2af3b8ca01dd', 'был предполагаемым использованием для', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('f8cbda12-99d5-3be4-ad09-4545c2b763b4', 'P19 était l''utilisation prévue de', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('393b34f8-7efd-375f-9df5-57ada2556869', 'était l''utilisation prévue de', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('23300941-ea8d-3efd-b25d-9664a06318f3', 'P19 war beabsichtigteter Gebrauch von ', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('7ed38473-0156-3fb8-a0db-a26b8be1247f', 'war beabsichtigteter Gebrauch von ', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'de', 'altLabel');
INSERT INTO "values" VALUES ('a72c509e-09b7-308f-819a-eaac00bbffaa', 'P19 ήταν προορισμένη χρήση του', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('df285aa5-89ae-35db-82b9-5ff0ceedd7b9', 'ήταν προορισμένη χρήση του', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'el', 'altLabel');
INSERT INTO "values" VALUES ('3af5a244-2240-358f-a6c7-81033dc305e6', 'P19 was intended use of', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('9df2349b-4cc3-3ea2-900b-19f9d788977e', 'was intended use of', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c00dd96f-4127-3526-b46a-d8683424d7b4', 'P19 era prevista a utilização de', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('ce4a2be1-fe42-3af8-bab6-2a9d548ffcd0', 'era prevista a utilização de', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('9b6a613e-d5ef-3e6a-9b79-81cf4d8d57ca', 'P19 特别使用了', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('3dec2b78-abda-3f57-8afa-4ac3c24deba3', '特别使用了', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('cf026136-ec23-30af-ad1e-303fdaf03bc2', 'This property relates an E7 Activity with objects created specifically for use in the activity. 
This is distinct from the intended use of an item in some general type of activity such as the book of common prayer which was intended for use in Church of England services (see P101 had as general use (was use of)).', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('e25457b2-6c66-38ea-8a10-b751964ffcd7', 'P20 hatte den bestimmten Zweck', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('ea1c2ccd-be72-3dd7-be60-91322b6e68d0', 'hatte den bestimmten Zweck', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'de', 'altLabel');
INSERT INTO "values" VALUES ('acb1fbb1-7f47-30db-b66c-305d0c4a4f0d', 'P20 avait pour but spécifique', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('cdb3c933-2b9a-3159-9fa9-8082ace93b74', 'avait pour but spécifique', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('95caa1c7-a362-3568-98b4-81ca95a12d31', 'P20 είχε συγκεκριμένο σκοπό', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('e28a8a0c-146e-375a-b84a-eac8f5b86857', 'είχε συγκεκριμένο σκοπό', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'el', 'altLabel');
INSERT INTO "values" VALUES ('fb8a71b4-3c4a-3eb8-88ca-792177dd8a0f', 'P20 had specific purpose', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('100b826e-bb8b-3507-bc5f-5ca6e0020f80', 'had specific purpose', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'en', 'altLabel');
INSERT INTO "values" VALUES ('a4fe172b-fcdf-3817-ae05-0056bd64c105', 'P20 имел конкретную цель', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('c7131c5f-c381-3ab9-b2b1-118fe2f31aaf', 'имел конкретную цель', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('516d51af-c1b7-3f1e-b137-f0447997e60e', 'P20 tinha propósito específico', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('42c389f9-8b06-33ac-bdac-0474f9d4645d', 'tinha propósito específico', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('e7a93394-f1f5-3fb4-952e-4a381bb28f90', 'P20 有特定目地', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('b0a8c8de-55f4-384e-b5b3-acab6dc1f849', '有特定目地', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('767543b0-a809-32c6-935d-7e54aae1b9e8', 'This property identifies the relationship between a preparatory activity and the event it is intended to be preparation for.
This includes activities, orders and other organisational actions, taken in preparation for other activities or events. 
P20 had specific purpose (was purpose of) implies that an activity succeeded in achieving its aim. If it does not succeed, such as the setting of a trap that did not catch anything, one may document the unrealized intention using P21 had general purpose (was purpose of):E55 Type and/or  P33 used specific technique (was used by): E29 Design or Procedure.', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('5ed69fdb-8fe8-3f9f-8776-21165f278324', 'P21 είχε γενικό σκοπό', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ab63044f-5c41-3e8f-b33b-02d8d6689f93', 'είχε γενικό σκοπό', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'el', 'altLabel');
INSERT INTO "values" VALUES ('abd8c33c-0a6c-3ea4-84d4-da29c645b22a', 'P21 hatte den allgemeinen Zweck', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('cded3c3b-0938-3d44-b282-0e2c4e33dedf', 'hatte den allgemeinen Zweck', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'de', 'altLabel');
INSERT INTO "values" VALUES ('bc97e170-9b30-3027-80d5-56ad8513f9e2', 'P21 avait pour but général', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('b599ad41-6f88-31f3-8aa9-96cf99b3d4e0', 'avait pour but général', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('1618f492-f0e4-3bf6-bab6-827aba7d419a', 'P21 имел общую цель', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('d7de1a5c-cd75-34e3-822f-bab900c60a2f', 'имел общую цель', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('9b4ec533-78aa-365f-954d-89989422737b', 'P21 had general purpose', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('aee0504f-e353-3313-9e3d-9be13be8f762', 'had general purpose', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'en', 'altLabel');
INSERT INTO "values" VALUES ('68a2f53d-e62f-37ca-afb0-e7e48daee5b5', 'P21 tinha propósito geral', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('79558728-b904-3b3f-9416-1a1eba73bf22', 'tinha propósito geral', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('4ea1a8bf-a08b-3959-ae98-b2c247f846af', 'P21 有通用目地', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('2cf0896e-caab-30b3-9037-1f25c58b4fe8', '有通用目地', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('f04d73b3-f469-307c-b5a0-b32871c94e18', 'This property describes an intentional relationship between an E7 Activity and some general goal or purpose. 
This may involve activities intended as preparation for some type of activity or event. P21had general purpose (was purpose of) differs from P20 had specific purpose (was purpose of) in that no occurrence of an event is implied as the purpose. 
', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('1ff75133-3c35-32c7-9a8e-b2257eb047c4', 'P22 μετεβίβασε τον τίτλο σε', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('cd75d8d7-64d3-3ff0-a27c-cde9fe9124e6', 'μετεβίβασε τον τίτλο σε', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'el', 'altLabel');
INSERT INTO "values" VALUES ('db6d5ac2-a653-32cf-ada8-09cc9cb7b261', 'P22 a fait passer le droit de propriété à', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('1233c7a7-93c6-3cf0-8e07-0d823bf8053a', 'a fait passer le droit de propriété à', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('a4d184ef-aa5a-3dfa-a6bf-b73d58cca3d5', 'P22 übertrug Besitztitel auf', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('2d26b821-3437-3df8-99f3-63cc53e1b554', 'übertrug Besitztitel auf', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'de', 'altLabel');
INSERT INTO "values" VALUES ('d1c6d24f-d545-302b-8a01-9ad67de5c608', 'P22 transferred title to', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('0fca0162-0383-3e04-a676-f4c90c72ddcc', 'transferred title to', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'en', 'altLabel');
INSERT INTO "values" VALUES ('4a149290-5fda-3ba3-9c75-c106c17946f8', 'P22 передал право собственности', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('42d9278b-c9e2-368d-8863-4a03379849e4', 'передал право собственности', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('374bf4b4-fe6f-3816-8c01-5d9bece2d0c0', 'P22 transferiu os direitos de propriedade para', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('4dc5d5d5-ab9b-3a47-b3d0-1961c5742e67', 'transferiu os direitos de propriedade para', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b749c75b-e95d-36c9-b847-6168841c4f65', 'P22 转交所有权给', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('a57907fd-8490-3085-93d5-779d3700f6c9', '转交所有权给', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('9f112c50-60e3-37bc-a821-34b5bc80e48a', 'This property identifies the E39 Actor that acquires the legal ownership of an object as a result of an E8 Acquisition. 
The property will typically describe an Actor purchasing or otherwise acquiring an object from another Actor. However, title may also be acquired, without any corresponding loss of title by another Actor, through legal fieldwork such as hunting, shooting or fishing.
In reality the title is either transferred to or from someone, or both.
', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('13aad2bf-2727-35e7-9747-b1c17f5738d1', 'P23 μετεβίβασε τον τίτλο από', '345681a7-8324-331c-94d4-1777c36538b5', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('1ac41846-f2e6-3986-9c29-16493991c2ab', 'μετεβίβασε τον τίτλο από', '345681a7-8324-331c-94d4-1777c36538b5', 'el', 'altLabel');
INSERT INTO "values" VALUES ('3f164142-7085-336a-b6a0-b8df13dee82e', 'P23 a fait passer le droit de propriété de', '345681a7-8324-331c-94d4-1777c36538b5', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('717abea3-9715-37b1-b361-e2a990aeddad', 'a fait passer le droit de propriété de', '345681a7-8324-331c-94d4-1777c36538b5', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('d865179b-b6dc-3245-8f27-22eb15bbb5d8', 'P23 передал право собственности от', '345681a7-8324-331c-94d4-1777c36538b5', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('6dba3830-3d33-3f9d-9c6a-ecd8da4b3382', 'передал право собственности от', '345681a7-8324-331c-94d4-1777c36538b5', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('ca140141-dde5-3d77-91b6-0e58c351749e', 'P23 übertrug Besitztitel von', '345681a7-8324-331c-94d4-1777c36538b5', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('e08c3a51-607d-378f-a10c-9c004db1046e', 'übertrug Besitztitel von', '345681a7-8324-331c-94d4-1777c36538b5', 'de', 'altLabel');
INSERT INTO "values" VALUES ('acb3e66c-d967-3bd2-a678-ac9f5380cdd5', 'P23 transferred title from', '345681a7-8324-331c-94d4-1777c36538b5', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('f9aa63f3-6e5f-37dc-ae5f-861361b09a1a', 'transferred title from', '345681a7-8324-331c-94d4-1777c36538b5', 'en', 'altLabel');
INSERT INTO "values" VALUES ('40bfe935-4cde-3d1d-8d70-7981b5319f89', 'P23 transferiu os direitos de propriedade de', '345681a7-8324-331c-94d4-1777c36538b5', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('46b11a96-a0f9-3b61-b397-6d8098f81c1e', 'transferiu os direitos de propriedade de', '345681a7-8324-331c-94d4-1777c36538b5', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('e6ccdd7e-81b1-34c0-b5c5-82467221b3f3', 'P23 原所有权者是', '345681a7-8324-331c-94d4-1777c36538b5', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('0daf0aac-ad87-329c-800a-110f9098feab', '原所有权者是', '345681a7-8324-331c-94d4-1777c36538b5', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('bbb0e987-de06-34ac-bc08-22dd7c8ec561', 'This property identifies the E39 Actor or Actors who relinquish legal ownership as the result of an E8 Acquisition.
The property will typically be used to describe a person donating or selling an object to a museum. In reality title is either transferred to or from someone, or both.
', '345681a7-8324-331c-94d4-1777c36538b5', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('0ff1887c-ff24-38fa-9a18-ff0c8cefa9f4', 'P24 übertrug Besitz über', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('65f5dc50-9d9e-3263-9326-99ebc5c6815d', 'übertrug Besitz über', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'de', 'altLabel');
INSERT INTO "values" VALUES ('bbdea559-28bf-3f35-8093-1de6e144eb8b', 'P24 передал право собственности на', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('cef80c13-fd3a-3622-b964-4adc52593eaf', 'передал право собственности на', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('8b7b985d-4449-3aeb-80a2-57c118a8db20', 'P24 μετεβίβασε τον τίτλο του/της', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('af7bfec4-3d1a-3ddf-9224-5f13c4346c8d', 'μετεβίβασε τον τίτλο του/της', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'el', 'altLabel');
INSERT INTO "values" VALUES ('9a77e32f-3c9d-3554-9024-c1d4fd5db4d6', 'P24 a fait passer le droit de propriété sur', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('037371cf-8459-30a1-8042-f4ceef1eca83', 'a fait passer le droit de propriété sur', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('f040cd50-9af4-3b70-914c-1b21cae84917', 'P24 transferred title of', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('4478b379-3629-32d9-a676-16ddf0f59236', 'transferred title of', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'en', 'altLabel');
INSERT INTO "values" VALUES ('8f385487-d83a-3f44-97ba-5fee6968b476', 'P24 transferiu os direitos de propriedade sobre o', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('a8a07f73-d13e-3af6-93cc-565676e29e64', 'transferiu os direitos de propriedade sobre o', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('6e139b88-1a00-39fd-95ae-b4031afb90ba', 'P24 转移所有权的标的物是', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('14a9f636-7dd9-3377-b473-da4d634bf604', '转移所有权的标的物是', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('6cc8d08f-22a8-3988-8701-539329ddbdf9', 'This property identifies the E18 Physical Thing or things involved in an E8 Acquisition. 
In reality, an acquisition must refer to at least one transferred item.
', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('8a94ded4-737a-34e5-8d13-50d1af3abf22', 'P25 moved', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('59a81cd3-de78-3681-a6b0-c8acdd9f9059', 'moved', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'en', 'altLabel');
INSERT INTO "values" VALUES ('474f0f22-c0fa-3808-b75a-9e361d0dca9f', 'P25 μετεκίνησε', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('81a7e889-4634-36b6-a5ce-4276b4a42b31', 'μετεκίνησε', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'el', 'altLabel');
INSERT INTO "values" VALUES ('781378db-f15f-3940-b686-dcb1c19f3de0', 'P25 переместил', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('143af1cb-a0d2-30f2-8b5a-65166171621f', 'переместил', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('a1b7ee80-7da0-3178-8240-05622f249721', 'P25 a déplacé', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('7467f051-b512-3526-8fad-532f89a0c74c', 'a déplacé', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('de428212-adc1-39c9-8610-9a74d58827f0', 'P25 bewegte', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('9260825d-4ac1-30c8-9f9c-cd85d858b09f', 'bewegte', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'de', 'altLabel');
INSERT INTO "values" VALUES ('865edda8-735c-31f4-98e7-f22c7d455e30', 'P25 locomoveu', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('b2cb4ef9-cd8e-3dfe-b248-372f310d88ac', 'locomoveu', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b6c3eef9-a1a5-339f-8f46-8df5e2eeab99', 'P25 移动了', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('a734f910-e00e-35fc-a699-5ad7e4ef5c94', '移动了', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('9925c1b2-2781-3888-85b7-2330f0b1c31f', 'This property identifies an instance of E19 Physical Object that was moved by a move event. A move must concern at least one object.

The property implies the object''s passive participation. For example, Monet''s painting "Impression sunrise" was moved for the first Impressionist exhibition in 1874. 
', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('f729313f-93a1-331e-a650-ab2bace3b792', 'P26 μετακινήθηκε προς', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('5a2eb785-27cc-3f76-a92b-2890622dc2f5', 'μετακινήθηκε προς', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'el', 'altLabel');
INSERT INTO "values" VALUES ('c88787bd-c50a-3a26-bb50-1c2dbcb3eb08', 'P26 moved to', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('9e293945-4c5c-32ae-bf3d-54ee13c92514', 'moved to', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'en', 'altLabel');
INSERT INTO "values" VALUES ('7bd58407-7f16-3363-9840-039f27186595', 'P26 a déplacé vers', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('94c06767-a595-351b-8b6a-f2f415e60677', 'a déplacé vers', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('3a6b6959-cfc6-31a1-ad0c-90de32e309fb', 'P26 перемещен в', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('f8d47009-b980-35c5-bda5-9626f8522fee', 'перемещен в', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('667cbbea-c04b-3148-8f6e-9ee508439e22', 'P26 bewegte bis zu', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('e319ef5e-aea3-348e-8a62-1fbcc007a9be', 'bewegte bis zu', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'de', 'altLabel');
INSERT INTO "values" VALUES ('19bb4000-9d1e-3844-981f-1d20732f5b11', 'P26 locomoveu para', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('ebc9524d-1526-3468-b19a-2d9cc0a46ffb', 'locomoveu para', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('f53fe6d5-cfdf-336e-8a5e-b19a688636b9', 'P26 移入物件至', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('9c24687b-23e1-3ab4-92d6-3d44fe3b914a', '移入物件至', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('52f77aed-a640-36ed-961a-f86a4f73d118', 'This property identifies a destination of a E9 Move. 
A move will be linked to a destination, such as the move of an artefact from storage to display. A move may be linked to many terminal instances of E53 Place by multiple instances of this property. In this case the move describes a distribution of a set of objects. The area of the move includes the origin(s), route and destination(s).
Therefore the described destination is an instance of E53 Place which P89 falls within (contains) the instance of E53 Place the move P7 took place at.
', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('a7380710-82e8-3e5f-ad38-5f6e3577e990', 'P27 μετακινήθηκε από', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('73dec8c5-51ee-37b1-9382-db404a8dd00e', 'μετακινήθηκε από', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'el', 'altLabel');
INSERT INTO "values" VALUES ('8f5b0e11-2133-3ac2-a66a-b76c9895bad4', 'P27 moved from', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('ecdf82c5-430e-3e0c-a1b7-fb41e25e0a3a', 'moved from', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'en', 'altLabel');
INSERT INTO "values" VALUES ('afa1f031-3a03-3c45-8c9f-f2d450207dad', 'P27 a retiré de', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('2166133f-7d70-39d4-90c3-5377f3f7ab37', 'a retiré de', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('6d9995d9-9fe8-31f4-a193-d7778c5e165d', 'P27 bewegte weg von', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('8fa0e25c-1eb5-3faa-9cc5-5597d520e924', 'bewegte weg von', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'de', 'altLabel');
INSERT INTO "values" VALUES ('3beefcd5-3f99-3b0c-a0ab-750fffc02066', 'P27 перемещен из', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('dea72ea7-15fb-334b-a540-fe3f5df53c7d', 'перемещен из', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('124d5a43-e389-31f0-93a0-85c4ae9995f1', 'P27 locomoveu de', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('11b0c71c-da2a-339e-9100-3e0473b9444c', 'locomoveu de', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('64aa03b8-3a77-3379-8c0f-16542ac6ed22', 'P27 有移出地', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('a1fa3e48-5669-3345-a70d-9f3b0c0e9280', '有移出地', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('c639759e-fd80-3439-b50d-81530aae36ba', 'This property identifies a starting E53 Place of an E9 Move.

A move will be linked to an origin, such as the move of an artefact from storage to display. A move may be linked to many starting instances of E53 Place by multiple instances of this property. In this case the move describes the picking up of a set of objects. The area of the move includes the origin(s), route and destination(s).
Therefore the described origin is an instance of E53 Place which P89 falls within (contains) the instance of E53 Place the move P7 took place at.
', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('6a3bc4dc-a402-3369-894e-fff062b5c256', 'P28 changement de détenteur au détriment de', 'aad29816-af79-36cf-919e-80980f7c41a3', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('fe28de61-8ffe-3ba5-a9ca-e2ff02ace460', 'changement de détenteur au détriment de', 'aad29816-af79-36cf-919e-80980f7c41a3', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('1c552b1e-342b-3d9c-9681-74f47aa5ef36', 'P28 übergab Gewahrsam an', 'aad29816-af79-36cf-919e-80980f7c41a3', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('3e65f58a-12df-3d33-a687-1d8a4cdc554f', 'übergab Gewahrsam an', 'aad29816-af79-36cf-919e-80980f7c41a3', 'de', 'altLabel');
INSERT INTO "values" VALUES ('1fd9e04e-f761-337d-86e7-9e1e13b0dabe', 'P28 custody surrendered by', 'aad29816-af79-36cf-919e-80980f7c41a3', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('9bb24ab5-798b-3cfa-a2c2-5da36ab7543a', 'custody surrendered by', 'aad29816-af79-36cf-919e-80980f7c41a3', 'en', 'altLabel');
INSERT INTO "values" VALUES ('60e1992a-8a2c-3589-9a4d-94f6b212f428', 'P28 μετεβίβασε κατοχή από', 'aad29816-af79-36cf-919e-80980f7c41a3', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('7bdba325-02ae-3a1e-96d6-308444794247', 'μετεβίβασε κατοχή από', 'aad29816-af79-36cf-919e-80980f7c41a3', 'el', 'altLabel');
INSERT INTO "values" VALUES ('93d55b0d-0776-3843-81e1-059c060e92dd', 'P28 опека отдана', 'aad29816-af79-36cf-919e-80980f7c41a3', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('fbb6659c-b57d-3898-8089-02c0944edffc', 'опека отдана', 'aad29816-af79-36cf-919e-80980f7c41a3', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('0edba6c8-4a84-30e0-9deb-9e1641f1264f', 'P28 custódia concedida por', 'aad29816-af79-36cf-919e-80980f7c41a3', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('0ea095aa-77b7-39f0-b076-e46c6def768f', 'custódia concedida por', 'aad29816-af79-36cf-919e-80980f7c41a3', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('c03d7e7c-ce78-34ab-bde5-459b1ef1663f', 'P28 有原保管人', 'aad29816-af79-36cf-919e-80980f7c41a3', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('dfe0ce72-3535-3340-9e3a-fdaad644746e', '有原保管人', 'aad29816-af79-36cf-919e-80980f7c41a3', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('f80b488d-8a02-3f46-b2ec-3090f26ea457', 'This property identifies the E39 Actor or Actors who surrender custody of an instance of E18 Physical Thing in an E10 Transfer of Custody activity. 
The property will typically describe an Actor surrendering custody of an object when it is handed over to someone else’s care. On occasion, physical custody may be surrendered involuntarily – through accident, loss or theft.
In reality, custody is either transferred to someone or from someone, or both.
', 'aad29816-af79-36cf-919e-80980f7c41a3', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('01e19168-2161-3dc6-9a84-b30c7227b14a', 'P29 μετεβίβασε κατοχή σε', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('bb2cc100-33c4-32db-bde6-954055fac27c', 'μετεβίβασε κατοχή σε', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'el', 'altLabel');
INSERT INTO "values" VALUES ('e9811341-5894-32de-aea2-b17bf1c653f4', 'P29 опека получена', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('5e676267-b8bc-3d0e-8a07-cbbfa472a624', 'опека получена', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('ae112268-184e-3d0b-9591-9b4ca54f25a0', 'P29 custody received by', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('d92d1f91-a938-31c4-a694-87206655589b', 'custody received by', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'en', 'altLabel');
INSERT INTO "values" VALUES ('ad312452-6034-32c1-908d-2318cf38ff32', 'P29 changement de détenteur au profit de', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('ad23b2a7-cdce-36c1-98ac-b6674b304596', 'changement de détenteur au profit de', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('c968b0b0-4777-33fa-ab19-dd4803cc02c6', 'P29 übertrug Gewahrsam auf', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('35e1c2fa-53f7-36cd-a8a7-61232bad4055', 'übertrug Gewahrsam auf', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'de', 'altLabel');
INSERT INTO "values" VALUES ('14e3ca9d-6045-37b5-bf44-fbb2bab0992d', 'P29 custódia recebida por', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('95339617-c8b7-3450-918e-082bc40b1cbb', 'custódia recebida por', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('7178a252-ea02-30c6-8751-d3f36026d4cd', 'P29 移转保管作业给', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('987feb5f-8a4b-312a-8669-530e6272a14c', '移转保管作业给', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('445182a4-0164-38d9-a23e-7e4733e7bf4d', 'This property identifies the E39 Actor or Actors who receive custody of an instance of E18 Physical Thing in an E10 Transfer of Custody activity. 
The property will typically describe Actors receiving custody of an object when it is handed over from another Actor’s care. On occasion, physical custody may be received involuntarily or illegally – through accident, unsolicited donation, or theft.
In reality, custody is either transferred to someone or from someone, or both.
', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('36ee6c7f-46a5-3b91-8e6a-b7df177c6518', 'P30 передало опеку на', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('4a58646d-6896-3456-a553-8fe13ef0a8d0', 'передало опеку на', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('861ea03f-e39d-37d0-80ca-cc946ab0ebd0', 'P30 transferred custody of', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('f5af2a61-aa8d-3690-b2eb-ab65abe5963c', 'transferred custody of', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'en', 'altLabel');
INSERT INTO "values" VALUES ('7f6de9dc-e456-3971-bdc9-f9e03191aec0', 'P30 changement de détenteur concernant', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('bb326d4e-fe0f-30fd-a66b-ac83d13af79c', 'changement de détenteur concernant', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('3ab1c104-34bb-3c44-93c5-8c4e343c69c6', 'P30 übertrug Gewahrsam über', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('de526968-4045-3abc-9b6b-8747eb43334d', 'übertrug Gewahrsam über', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'de', 'altLabel');
INSERT INTO "values" VALUES ('27b821bd-133e-3919-b71a-7ba04ec20f8a', 'P30 μετεβίβασε κατοχή του/της/των', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('7188afb0-a3bd-3d12-b35a-23f2e74ce871', 'μετεβίβασε κατοχή του/της/των', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'el', 'altLabel');
INSERT INTO "values" VALUES ('9453e200-202f-3581-bb73-d691e22990eb', 'P30 transferida custódia de', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('c4ad3547-d70f-3d83-b74f-3b0bca66725c', 'transferida custódia de', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('dfddc263-df3a-3a57-a949-af64f7964cca', 'P30 有保管标的物', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('6a6ee66e-1032-3e98-86cc-a3780c18feaa', '有保管标的物', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('5ff7be30-9e0a-3088-b6a4-29a2c975d96f', 'This property identifies an item or items of E18 Physical Thing concerned in an E10 Transfer of Custody activity. 
The property will typically describe the object that is handed over by an E39 Actor to another Actor’s custody. On occasion, physical custody may be transferred involuntarily or illegally – through accident, unsolicited donation, or theft.
', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('d9757901-b082-360d-b51a-119a5c380367', 'P31 veränderte', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('791ec07c-be84-3d38-9385-acc4a3b0dca2', 'veränderte', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'de', 'altLabel');
INSERT INTO "values" VALUES ('3284eb6f-3364-324d-924f-5fd247692d70', 'P31 a modifié', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5ee20f93-6c5c-3270-a7a2-773c3b5d3a1a', 'a modifié', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('3b407ff1-43a6-379a-b66b-d0ab6c5237de', 'P31 has modified', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('ebd56d97-fc61-3956-bc68-8f486baf0936', 'has modified', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'en', 'altLabel');
INSERT INTO "values" VALUES ('0e4bcf72-5ea2-3708-8fe7-c5b3d1333e63', 'P31 изменил', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('7359bdf0-8bea-33dc-ab2f-bc3ae2ddfc4b', 'изменил', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('9fa9ab59-358f-3af9-986f-59cd095830ad', 'P31 τροποποίησε', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('1b9706be-15b7-31e2-b2f3-27425fab1d81', 'τροποποίησε', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'el', 'altLabel');
INSERT INTO "values" VALUES ('bee684aa-8dfb-3c82-abd9-26520810296a', 'P31 modificou', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('68f8a8c9-3955-3e80-a320-869fcc86d573', 'modificou', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('852ebaaa-8488-3e2d-b9f3-3949cc8dada5', 'P31 修改了', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('e6fb1f68-198b-3f93-81c3-5c13f265a82b', '修改了', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('72fedba5-7615-3299-a4e3-58cc950f7650', 'This property identifies the E24 Physical Man-Made Thing modified in an E11 Modification.
If a modification is applied to a non-man-made object, it is regarded as an E22 Man-Made Object from that time onwards. 
', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('6c23b25d-2d70-3ae1-a17e-8e75bde27cb3', 'P32 χρησιμοποίησε γενική τεχνική', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('e93cde79-9e80-3a39-b7fb-a692c6d0b140', 'χρησιμοποίησε γενική τεχνική', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'el', 'altLabel');
INSERT INTO "values" VALUES ('b6d106ee-b71b-3686-8da3-9d7fc3e4de4a', 'P32 benutzte das allgemeine Verfahren', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('41310010-d00c-324e-ba59-b8507481d24a', 'benutzte das allgemeine Verfahren', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'de', 'altLabel');
INSERT INTO "values" VALUES ('c7a4dc3f-2df1-3b82-bf9e-e5dbd6a05481', 'P32 a employé comme technique générique', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('e5de06e2-9401-3dd9-b138-0b1902856e37', 'a employé comme technique générique', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('db29bb8a-b95a-391e-b73c-2017a0455627', 'P32 использовал общую технику', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('96b061cf-5683-39b4-92ce-1e12830bcf1f', 'использовал общую технику', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('cabc8bb4-0a5a-3642-adb7-23c93f6defa9', 'P32 used general technique', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('655c5e25-6524-3328-95ea-f28735d78576', 'used general technique', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'en', 'altLabel');
INSERT INTO "values" VALUES ('73762826-b70d-3757-89cf-eb1d0a96c001', 'P32 usou técnica geral', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('5e75bccc-041b-3e5e-a324-d2746b51cd98', 'usou técnica geral', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('3f393710-8a76-342d-8742-2eac4904d9d0', 'P32 使用通用技术', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('0ebdfe2b-84d0-3ff8-a0fd-612ddb3ce8a0', '使用通用技术', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('f80df094-bfbb-33e6-b290-76688f174f4c', 'This property identifies the technique or method that was employed in an activity.
These techniques should be drawn from an external E55 Type hierarchy of consistent terminology of general techniques or methods such as embroidery, oil-painting, carbon dating, etc. Specific documented techniques should be described as instances of E29 Design or Procedure. This property identifies the technique that was employed in an act of modification.
', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('3c03d82f-137d-3128-8717-4f20c19553e6', 'P33 χρησιμοποίησε συγκεκριμένη τεχνική', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('c28822fb-d874-326b-86e1-50a4db8a3b72', 'χρησιμοποίησε συγκεκριμένη τεχνική', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'el', 'altLabel');
INSERT INTO "values" VALUES ('c71ab98f-b093-32fa-b130-cbaa8aec7d71', 'P33 used specific technique', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('f8e9cd6f-2558-3f6a-89cf-34a9faf5ee6b', 'used specific technique', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'en', 'altLabel');
INSERT INTO "values" VALUES ('5fd19b4f-87b6-3639-96dd-4a68b5e900a9', 'P33 a employé comme technique spécifique', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('01c3c97e-437b-3369-b337-abe9145809cb', 'a employé comme technique spécifique', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('44b4b913-1552-39eb-942b-b6ba87312ccd', 'P33 использовал особую технику', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('dac16033-defe-3858-863a-efd5248858c9', 'использовал особую технику', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('b877fb25-bd3b-3dce-9cd9-ed7a38712cd7', 'P33 benutzte das bestimmte Verfahren', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('47eaa8b8-ed2e-38f5-a655-58d962a63e84', 'benutzte das bestimmte Verfahren', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'de', 'altLabel');
INSERT INTO "values" VALUES ('34e31741-c133-365c-a09d-57cb5d042838', 'P33 usou técnica específica', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('25e8f8eb-b8e9-3fe0-9ed7-cad9f2855d2b', 'usou técnica específica', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('41402e1b-673d-3f8b-a4c6-8e8a10445e47', 'P33 使用特定技术', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('2c2901ab-a650-37ac-a35c-3cef25ffe8ea', '使用特定技术', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('3f96cacd-0c2a-3fd9-b0c4-2aef53bb54ac', 'This property identifies a specific instance of E29 Design or Procedure in order to carry out an instance of E7 Activity or parts of it. 
The property differs from P32 used general technique (was technique of) in that P33 refers to an instance of E29 Design or Procedure, which is a concrete information object in its own right rather than simply being a term or a method known by tradition. 
Typical examples would include intervention plans for conservation or the construction plans of a building.
', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('68534fa8-ccea-337a-b631-3d6f5224d255', 'P34 αφορούσε σε', 'd9f02df8-6676-371e-8114-1f37700639b5', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('f364e709-2cb0-3c00-beea-314537c7f319', 'αφορούσε σε', 'd9f02df8-6676-371e-8114-1f37700639b5', 'el', 'altLabel');
INSERT INTO "values" VALUES ('f3c7c05d-9c84-318d-8dcb-12855ac5bf6c', 'P34 имел дело с', 'd9f02df8-6676-371e-8114-1f37700639b5', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('dfe03134-8e41-3c68-840a-2624808b76de', 'имел дело с', 'd9f02df8-6676-371e-8114-1f37700639b5', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('f5970500-92ee-325d-93d3-603f2a14cc35', 'P34 betraf', 'd9f02df8-6676-371e-8114-1f37700639b5', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('4da73ffd-0c2a-3e16-93ba-82bbd5e2f52c', 'betraf', 'd9f02df8-6676-371e-8114-1f37700639b5', 'de', 'altLabel');
INSERT INTO "values" VALUES ('55301b30-eea5-3461-9ff0-2eeb9c72d311', 'P34 concerned', 'd9f02df8-6676-371e-8114-1f37700639b5', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('acfc4dc1-0a04-3117-a518-b8421a555a58', 'concerned', 'd9f02df8-6676-371e-8114-1f37700639b5', 'en', 'altLabel');
INSERT INTO "values" VALUES ('7881fe43-f1f5-37bd-a405-e831906cf8c8', 'P34 a concerné', 'd9f02df8-6676-371e-8114-1f37700639b5', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('befa5128-6835-39a3-9663-5fdb9910131d', 'a concerné', 'd9f02df8-6676-371e-8114-1f37700639b5', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('fe5307d7-abc9-3975-8352-d15084735e2b', 'P34 interessada', 'd9f02df8-6676-371e-8114-1f37700639b5', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('798a1ff4-2a4e-3293-845c-1b32565dcd42', 'interessada', 'd9f02df8-6676-371e-8114-1f37700639b5', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('6e766111-4f8e-38be-a03b-9a58a0426613', 'P34 评估了', 'd9f02df8-6676-371e-8114-1f37700639b5', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('a1d8bfb6-3d72-3da7-87e2-0e56b093e082', '评估了', 'd9f02df8-6676-371e-8114-1f37700639b5', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('a31a80a8-fe24-3637-85f0-f21fbe181bef', 'This property identifies the E18 Physical Thing that was assessed during an E14 Condition Assessment activity. 
Conditions may be assessed either by direct observation or using recorded evidence. In the latter case the E18 Physical Thing does not need to be present or extant.
', 'd9f02df8-6676-371e-8114-1f37700639b5', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('b867861e-4641-35d9-8f95-998df9b552c1', 'P35 идентифицировал', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('5832b33d-97dd-3296-93da-d933224df352', 'идентифицировал', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('ef04b15b-0fa3-3552-99e2-1c9557e5e3d3', 'P35 hat identifiziert', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('fd2cf027-bcb7-3309-bd67-706d4d80e876', 'hat identifiziert', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'de', 'altLabel');
INSERT INTO "values" VALUES ('28193e4e-ac43-3a71-8211-ad31e2269714', 'P35 a identifié', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('726cfab5-54fe-3f4d-9f4b-bb836f34ea8a', 'a identifié', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('3ef3eb64-42c7-31bc-abba-ab427c22d83f', 'P35 έχει διαπιστώσει', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('89661878-113c-3c40-8833-02a2d4e1a7c6', 'έχει διαπιστώσει', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'el', 'altLabel');
INSERT INTO "values" VALUES ('b648b017-59b5-3c1a-8788-8f1a1be1f7cc', 'P35 has identified', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('671698c0-f2ab-3def-8cd4-57f27b8074af', 'has identified', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'en', 'altLabel');
INSERT INTO "values" VALUES ('5ba23951-e96b-3372-aaab-3973b85e80af', 'P35 identificou', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('3d962a3b-c6cf-3e3a-acbb-76890906b0c3', 'identificou', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('afcf5dd3-b049-3142-a185-8e54d3808ab0', 'P35 评估认定了', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('7b92ee57-e714-3f88-a087-eca1ce0251de', '评估认定了', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('eb732032-6c4c-3198-b779-2e83eac1ac38', 'This property identifies the E3 Condition State that was observed in an E14 Condition Assessment activity.', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('e4ffc8d2-2064-30c0-a391-61072201a4be', 'P37 a attribué', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('6e93303a-2624-3143-bf01-ec8ccab9c2e1', 'a attribué', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('4ff801e3-d0ec-33b7-aa4d-5590dd36f4ff', 'P37 απέδωσε', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('b4607a54-dfb8-3af6-a1cd-1e438361479c', 'απέδωσε', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'el', 'altLabel');
INSERT INTO "values" VALUES ('17306ca6-2c9e-39c3-8fb0-4a40c9b4c80a', 'P37 assigned', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('4905d4ee-ff2b-342a-9942-a7054e775d8b', 'assigned', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'en', 'altLabel');
INSERT INTO "values" VALUES ('86159b92-9b27-394c-a2d1-cfdf6f849d6b', 'P37 wies zu', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('01dfcf9d-8554-3890-bdd1-db0d3bd34b50', 'wies zu', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'de', 'altLabel');
INSERT INTO "values" VALUES ('9c2d8fbf-e8bf-3081-b62d-b38728e9b383', 'P37 назначил', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('4f73a1b9-1dc2-32eb-96f8-09f213225018', 'назначил', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('9954ace9-4ec3-38b1-8964-7d42d2ee8e80', 'P37 atribuiu', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('26b8b52d-0b0b-3a9b-81f2-77aab8512acc', 'atribuiu', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('99ce241d-6deb-31be-a4f3-cc62d119e2ce', 'P37 指定标识符为', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('5beeeed6-1e04-385c-af46-2783a776c557', '指定标识符为', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('4ff6d606-52aa-321a-a225-e982432f68e8', 'This property records the identifier that was assigned to an item in an Identifier Assignment activity.
The same identifier may be assigned on more than one occasion.
An Identifier might be created prior to an assignment.
', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('4db11b9c-106e-360e-8cd8-a9868160f5b8', 'P38 ακύρωσε', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('1f609195-8052-3900-ac13-8d39c13d6b1e', 'ακύρωσε', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'el', 'altLabel');
INSERT INTO "values" VALUES ('7855733a-99a0-31c4-8da5-75c3f55bb6d7', 'P38 отменил назначение', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('98725005-4d7b-344d-a16f-d33dc057a0b3', 'отменил назначение', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('aa42b685-651c-3a6d-b077-38938c4f7628', 'P38 deassigned', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('ba34d43f-a752-3ed9-ab77-5155542a3b2e', 'deassigned', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c9241eda-6b73-37f7-8b30-a74697c32770', 'P38  hob Zuweisung auf von', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('12e1fedb-b977-3491-8738-7338674d8202', ' hob Zuweisung auf von', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'de', 'altLabel');
INSERT INTO "values" VALUES ('fc1b7948-c87b-377f-b130-7cbe88ea330b', 'P38 a désattribué', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5e33d06f-9119-330f-b7d5-360e9ea59b5d', 'a désattribué', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('475c6dde-d9f2-3857-beaa-ca1ea1230cb9', 'P38 retirou a atribuição do', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('4f17645d-27fe-3ae9-b688-f4b15bae48ac', 'retirou a atribuição do', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('3d6abb9d-cb3f-3e76-bf74-9fd51302c0e4', 'P38 取消标识符', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('14ff8693-6035-3fb3-82a7-eb7ee0dcce6e', '取消标识符', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('6a1ca6f9-17e5-3423-b7b4-0427134ac1bc', 'This property records the identifier that was deassigned from an instance of E1 CRM Entity.
Deassignment of an identifier may be necessary when an item is taken out of an inventory, a new numbering system is introduced or items are merged or split up. 
The same identifier may be deassigned on more than one occasion.
', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('cb51fb8c-c09c-30c2-83eb-2fafa3b1ff45', 'P39 a mesuré', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5e314b70-c272-3056-b39f-8d6fafc42ac2', 'a mesuré', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('27d46877-cbd6-333e-b9bb-50469282f031', 'P39 vermaß', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('6648766d-9e82-3a59-ad3f-b6fb18a856d5', 'vermaß', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'de', 'altLabel');
INSERT INTO "values" VALUES ('99f62292-a94c-34ae-87c2-bc519a2a7531', 'P39 μέτρησε', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('e15f70dc-fe2a-34d8-86bb-0aaf6fd060fe', 'μέτρησε', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'el', 'altLabel');
INSERT INTO "values" VALUES ('00c2278b-f435-3d4d-ab9e-290592be77f7', 'P39 measured', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('bfc2cffe-13d4-3d75-ab10-85e6994498c9', 'measured', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'en', 'altLabel');
INSERT INTO "values" VALUES ('e55c2875-06c0-3e51-a3a0-a20eaf544097', 'P39 измерил', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('07f46a56-fc16-3c4e-9baf-8c6e98c36a5c', 'измерил', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('eb21c152-b724-37b4-b945-e15d3e6070ed', 'P39 mediu', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('4fb09dda-77d7-385f-8558-042119cb0bb4', 'mediu', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('7e5cdd49-d1a1-3440-ad39-78429c6833f6', 'P39 测量了', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('937acbb6-74d9-3157-8af8-c83078aaa1b6', '测量了', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('4ffb02c2-8236-3715-bfdf-f4d393c31125', 'This property associates an instance of E16 Measurement with the instance of E1 CRM Entity to which it applied. An instance of E1 CRM Entity may be measured more than once. Material and immaterial things and processes may be measured, e.g. the number of words in a text, or the duration of an event.
', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('6b857d7f-7139-3ed8-9da1-f28f2195fbed', 'P40 observed dimension', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('eb47b170-1158-3378-97fb-b40c51201b10', 'observed dimension', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'en', 'altLabel');
INSERT INTO "values" VALUES ('69dd4b64-5748-38f1-9c39-5ad845d7645d', 'P40 παρατήρησε', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ea25d286-432f-37fa-a67f-8158d2523d12', 'παρατήρησε', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'el', 'altLabel');
INSERT INTO "values" VALUES ('8f3438f1-ee4b-3b77-8410-dadbdb3422ac', 'P40 определил величину', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('5e01e0d1-7659-3759-81a0-827bd87b22bb', 'определил величину', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('ce7d1765-23ea-3d2a-8001-15a13d0c2064', 'P40 beobachtete Dimension', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('c8a1cb6a-362d-3089-9580-cf4bffb62fea', 'beobachtete Dimension', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'de', 'altLabel');
INSERT INTO "values" VALUES ('e61e8683-2442-3066-b1a2-2f4e8c5963d6', 'P40 a relevé comme dimension', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('bb916fa8-4810-3e58-8a0a-c5c45686bb08', 'a relevé comme dimension', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('624e4375-34e3-3912-85b2-69d9c773add6', 'P40 verificou a dimensão', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('07b2c5c0-b42d-3f64-9bbd-769e6a9fcff1', 'verificou a dimensão', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('ab44db18-bd75-3c59-be4e-6e04280b08cd', 'P40 观察认定的规模是', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('6923587f-efd1-3c20-ba55-3e1a796cc925', '观察认定的规模是', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('b9e760af-f2cf-3d1b-ba74-948316e1b21c', 'This property records the dimension that was observed in an E16 Measurement Event.
E54 Dimension can be any quantifiable aspect of E70 Thing. Weight, image colour depth and monetary value are dimensions in this sense. One measurement activity may determine more than one dimension of one object.
Dimensions may be determined either by direct observation or using recorded evidence. In the latter case the measured Thing does not need to be present or extant.
Even though knowledge of the value of a dimension requires measurement, the dimension may be an object of discourse prior to, or even without, any measurement being made.
', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('781b9da3-7edb-3057-a756-3fc23b4b9753', 'P41 классифицировал', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('e86dc8da-0b1c-3612-a11c-df89403900c0', 'классифицировал', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('3c8e42ce-f8da-38a6-a77e-2375a0e95ad9', 'P41 classified', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b6ff34a6-c93d-3a7a-89ce-9ddac7369ee7', 'classified', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'en', 'altLabel');
INSERT INTO "values" VALUES ('a9c63cf0-1103-31dc-8865-1b2971e634d0', 'P41 a classifié', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('faf7f6c1-5e98-3b4d-b5f7-6a8771299b6e', 'a classifié', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('e4eae1a8-6a5b-3065-8bf4-eda1e1d0bb88', 'P41 χαρακτήρισε', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('8bee89f9-493e-3ebe-8a1c-e9e1452b6be8', 'χαρακτήρισε', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'el', 'altLabel');
INSERT INTO "values" VALUES ('4cab87e3-2ffb-3db0-acf9-2b70b8ffa6ef', 'P41 klassifizierte', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f6d56b17-b743-32c6-9814-dbd67759685d', 'klassifizierte', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'de', 'altLabel');
INSERT INTO "values" VALUES ('910a1485-ea9e-3bfc-a2ec-1300aaa95cb2', 'P41 classificou', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('171e0efc-e88a-3224-9a6c-149169497f7a', 'classificou', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('a6a516bd-00e7-35fa-8002-6d605d4d1ab8', 'P41 分类了', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('6035204a-9331-3ffd-a041-425bd0c1e1c8', '分类了', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('57422f52-b52e-306c-a3a6-4fb8f0e80912', 'This property records the item to which a type was assigned in an E17 Type Assignment activity.
Any instance of a CRM entity may be assigned a type through type assignment. Type assignment events allow a more detailed path from E1 CRM Entity through P41 classified (was classified), E17 Type Assignment, P42 assigned (was assigned by) to E55 Type for assigning types to objects compared to the shortcut offered by P2 has type (is type of).
', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('8623350f-88a3-3f45-a177-907c3585f6fd', 'P42 απέδωσε ως ιδιότητα', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('be3f5e64-55fe-3e27-b14e-ecf3218b736f', 'απέδωσε ως ιδιότητα', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'el', 'altLabel');
INSERT INTO "values" VALUES ('25fc695d-c2bb-3590-9671-af24de4ecfd9', 'P42 assigned', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('f4dc6a4c-2d2e-31a5-8699-71e8885686da', 'assigned', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'en', 'altLabel');
INSERT INTO "values" VALUES ('a201a776-a010-3278-b1b2-22aa9ad5a9ff', 'P42 a attribué', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('eb43f457-0d9d-348e-b5fd-573e4b111d77', 'a attribué', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('8b9dd04e-a7d8-35fe-a428-3b5b217982b5', 'P42 назначил', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('f1613e1e-1e8e-3f03-918f-81fc853d1bf5', 'назначил', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('24ec5979-191e-3c28-97b9-6abd41fdedd6', 'P42 wies zu', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('68cf7cfe-0ef2-3b4f-aaaa-e17301b3529d', 'wies zu', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'de', 'altLabel');
INSERT INTO "values" VALUES ('9711c361-99e8-3146-827e-8431ffb76fac', 'P42 atribuiu', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('c8161c5e-6474-379d-b7e5-b3faec5473e3', 'atribuiu', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('e9377dda-a81b-3b47-b569-19afd9cc17e8', 'P42 指定类型为', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('c5f906bd-a444-3ee7-a742-b638ec3f61b8', '指定类型为', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('5a8c34a2-42f8-3b1a-8a40-e58f53eb357a', 'This property records the type that was assigned to an entity by an E17 Type Assignment activity. 
Type assignment events allow a more detailed path from E1 CRM Entity through P41 classified (was classified by), E17 Type Assignment, P42 assigned (was assigned by) to E55 Type for assigning types to objects compared to the shortcut offered by P2 has type (is type of).
For example, a fragment of an antique vessel could be assigned the type “attic red figured belly handled amphora” by expert A. The same fragment could be assigned the type “shoulder handled amphora” by expert B.
A Type may be intellectually constructed independent from assigning an instance of it.
', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('1c21d7ef-9cc8-3319-bb0f-751d22618b86', 'P43 hat Dimension', '167c0167-35fd-3c57-b90e-20715fd2c200', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('59e2b383-bb10-3ac1-b67b-60705f0f1c12', 'hat Dimension', '167c0167-35fd-3c57-b90e-20715fd2c200', 'de', 'altLabel');
INSERT INTO "values" VALUES ('aebda5b7-ed5b-323a-9258-58c44b01804c', 'P43 a pour dimension', '167c0167-35fd-3c57-b90e-20715fd2c200', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('b18df48d-dabb-3747-94eb-a8fda9ad2c2f', 'a pour dimension', '167c0167-35fd-3c57-b90e-20715fd2c200', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('d2babfbe-5233-3d65-b4f2-6c5543319d16', 'P43 имеет величину', '167c0167-35fd-3c57-b90e-20715fd2c200', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('cf61dc36-9278-3a35-b05c-81dc74c209ee', 'имеет величину', '167c0167-35fd-3c57-b90e-20715fd2c200', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('5a25d734-6e6c-331c-a599-38207cfa3a08', 'P43 has dimension', '167c0167-35fd-3c57-b90e-20715fd2c200', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('41903c9a-5a69-3c19-8126-bfe9553f4252', 'has dimension', '167c0167-35fd-3c57-b90e-20715fd2c200', 'en', 'altLabel');
INSERT INTO "values" VALUES ('7df83041-e568-3323-bc66-3294b114d5b3', 'P43 έχει μέγεθος', '167c0167-35fd-3c57-b90e-20715fd2c200', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('b50e45c2-c46c-33af-a486-c437b6cd4b08', 'έχει μέγεθος', '167c0167-35fd-3c57-b90e-20715fd2c200', 'el', 'altLabel');
INSERT INTO "values" VALUES ('d4383199-fce0-3347-9ae3-692d00fe39b2', 'P43 tem dimensão', '167c0167-35fd-3c57-b90e-20715fd2c200', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('3a2459d7-829c-3d40-b8b2-e9b3aaf82708', 'tem dimensão', '167c0167-35fd-3c57-b90e-20715fd2c200', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('be3f84e3-b2f6-33a8-82e7-4ac6a0c7b73b', 'P43 有规模数量', '167c0167-35fd-3c57-b90e-20715fd2c200', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('e5c0216c-9b6c-3d81-8dc3-633044e0dbdf', '有规模数量', '167c0167-35fd-3c57-b90e-20715fd2c200', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('d7ad19b7-8067-3c5e-8fba-e85239f70eee', 'This property records a E54 Dimension of some E70 Thing.
It is a shortcut of the more fully developed path from E70 Thing through P39 measured (was measured by), E16 Measurement P40 observed dimension (was observed in) to E54 Dimension. It offers no information about how and when an E54 Dimension was established, nor by whom.
An instance of E54 Dimension is specific to an instance of E70 Thing.
', '167c0167-35fd-3c57-b90e-20715fd2c200', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('ab72d7d8-63fe-312a-a886-857f6e03fd4c', 'P44 имеет условие', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('2d954163-7f6d-3083-a7eb-ebc725068347', 'имеет условие', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('92a47a8b-ce77-311e-9522-6212ce6c0ca1', 'P44 hat Zustand', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('fe68c4e8-ccd5-3235-b175-98e4221580e1', 'hat Zustand', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'de', 'altLabel');
INSERT INTO "values" VALUES ('8a52acf8-5bca-3901-ae0a-c8d70b9c015e', 'P44 a pour état matériel', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('ffcbc268-6a46-392f-8c0f-c544e22c6547', 'a pour état matériel', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('c201ab12-a742-3176-b640-8092a820f65a', 'P44 has condition', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('f8f4a7b3-0af4-39fb-8e5c-d4a618e9ef15', 'has condition', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c4930734-d18a-35d9-bc81-5b6eff7ab227', 'P44 έχει κατάσταση', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('4bae1575-f0e9-3dc4-9320-bded9be36899', 'έχει κατάσταση', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'el', 'altLabel');
INSERT INTO "values" VALUES ('bdde11a6-1f89-3438-8702-37b637913fdc', 'P44 tem estado material ', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('9bc169a9-67cc-3921-8a33-3d8c51fd1420', 'tem estado material ', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('c469ca8d-90d5-3e69-95c7-a216dc95abe6', 'P44 有状态', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('c437c4cf-a60b-3dce-9aeb-41d20b811adf', '有状态', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('ee5061b8-0f6d-3890-b3c1-f46fd2e3d4a1', 'This property records an E3 Condition State for some E18 Physical Thing.
It is a shortcut of the more fully developed path from E18 Physical Thing through P34 concerned (was assessed by), E14 Condition Assessment P35 has identified (was identified by) to E3 Condition State. It offers no information about how and when the E3 Condition State was established, nor by whom. 
An instance of Condition State is specific to an instance of Physical Thing.
', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('d3d03c78-b794-3a5b-800e-2e158c72252d', 'P45 consiste en', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('084e33c5-c8fc-3717-ae5e-1effd1d09904', 'consiste en', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('a75ac323-6ee6-31fc-ba7e-612a6b1d4e9c', 'P45 αποτελείται από', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('d3527509-c347-3535-882f-d9422aea7f34', 'αποτελείται από', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'el', 'altLabel');
INSERT INTO "values" VALUES ('acd4db46-79e4-37f6-9ca5-36c4724e12ef', 'P45 besteht aus', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('5902f0b1-acb0-3c94-8c7a-e703376d0938', 'besteht aus', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'de', 'altLabel');
INSERT INTO "values" VALUES ('8fc9c6c8-45e5-3184-8a67-01678455658b', 'P45 consists of', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('4aa0bee5-8b1a-39db-9e27-c1ba588478e1', 'consists of', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'en', 'altLabel');
INSERT INTO "values" VALUES ('a5806f59-d88c-378a-9e53-dac747ca8bf2', 'P45 составлен из', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('bfe02cb9-a166-3e66-aa27-93caf7469da2', 'составлен из', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('6519b3fe-a82d-394f-8959-edc7730908d6', 'P45 consiste de', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('750cf60f-aba1-38d5-826a-614d78e5c978', 'consiste de', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b77d2520-5876-3531-b826-090c41c98ce9', 'P45 有构成材料', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('21af7564-e774-3489-ae4e-92a34ceb94d9', '有构成材料', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('d7e1fe14-6962-36e0-9ac2-302e3041025c', 'This property identifies the instances of E57 Materials of which an instance of E18 Physical Thing is composed.
All physical things consist of physical materials. P45 consists of (is incorporated in) allows the different Materials to be recorded. P45 consists of (is incorporated in) refers here to observed Material as opposed to the consumed raw material.
A Material, such as a theoretical alloy, may not have any physical instances', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('6c648f70-fed9-3e12-b1aa-fd6ce7474786', 'P46 is composed of', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('162340fc-248a-3bec-a107-c30c5c57cbe1', 'is composed of', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'en', 'altLabel');
INSERT INTO "values" VALUES ('9e8da40b-88b2-3678-8686-baab1a0afe6d', 'P46 est composée de', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('013f6a3e-fc9b-3628-9fc4-7ced01facd3f', 'est composée de', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('0ed07492-9c71-374c-904b-47660bf6f25e', 'P46 αποτελείται από', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('2c87db5a-f578-3383-9c26-69b23a746e0f', 'αποτελείται από', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'el', 'altLabel');
INSERT INTO "values" VALUES ('dcfa4a3f-17ad-30c3-a3a7-372ecb90061f', 'P46 ist zusammengesetzt aus', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('3c116860-ed7d-3f64-89b3-7a6dbf929eea', 'ist zusammengesetzt aus', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'de', 'altLabel');
INSERT INTO "values" VALUES ('f17cd1be-89e0-3cd5-b225-32dd72679355', 'P46 составлен из', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('ce0146ec-7d51-35c7-9f56-eabde21323e3', 'составлен из', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('af4df560-a9f9-3e1f-b3bd-a6cc1c585cc3', 'P46 é composto de', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('a6380505-08db-3e2a-9f39-03b248ec7b92', 'é composto de', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('38a6c6fd-cc51-388f-913e-6f5435f71885', 'P46 有组件', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('0da6bf65-cca5-3dd0-bffd-018a5e877bb3', '有组件', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('1df42c39-7257-3298-ad71-ddaea48cf6c5', 'This property allows instances of E18 Physical Thing to be analysed into component elements.

Component elements, since they are themselves instances of E18 Physical Thing, may be further analysed into sub-components, thereby creating a hierarchy of part decomposition. An instance of E18 Physical Thing may be shared between multiple wholes, for example two buildings may share a common wall. This property does not specify when and for how long a component element resided in the respective whole. If  a component is not part of a whole from the beginning of existence or until the end of existence of the whole, the classes E79 Part Addition and E90 Part Removal can be used to document when a component became part of a particular whole and/or when it stopped being a part of it. For the time-span of being part of the respective whole, the component is completely contained in the place the whole occupies.

This property is intended to describe specific components that are individually documented, rather than general aspects. Overall descriptions of the structure of an instance of E18 Physical Thing are captured by the P3 has note property.

The instances of E57 Material of which an item of E18 Physical Thing is composed should be documented using P45 consists of (is incorporated in).
', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('6207a0e5-7746-3a60-b8ee-1feb2da5596f', 'P48 has preferred identifier', '356c8ba7-0114-32c3-861f-8432bc46e963', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('6704778c-6fd9-3032-baa2-b32ce82a7623', 'has preferred identifier', '356c8ba7-0114-32c3-861f-8432bc46e963', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c1e2b3f7-5396-3f32-ab59-7fd3b6ad3fe4', 'P48 a pour identificateur retenu', '356c8ba7-0114-32c3-861f-8432bc46e963', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('169f5c9e-2453-3a15-aa2b-86ff5bd1ed86', 'a pour identificateur retenu', '356c8ba7-0114-32c3-861f-8432bc46e963', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('f04d247a-03ff-3e0c-aa44-78fefe8fe49e', 'P48 hat bevorzugtes Kennzeichen', '356c8ba7-0114-32c3-861f-8432bc46e963', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('9fba7052-e081-361c-be78-6aa05d0572b0', 'hat bevorzugtes Kennzeichen', '356c8ba7-0114-32c3-861f-8432bc46e963', 'de', 'altLabel');
INSERT INTO "values" VALUES ('9c18c4c5-002c-33b4-bd34-490133e4bdc5', 'P48 имеет предпочтительный идентификатор', '356c8ba7-0114-32c3-861f-8432bc46e963', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('e7d4bc9b-a1f9-32ba-87f1-0ea91a0a8538', 'имеет предпочтительный идентификатор', '356c8ba7-0114-32c3-861f-8432bc46e963', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('e3c262bf-2017-3a6d-836a-e242f3ac98ed', 'P48 έχει προτιμώμενο αναγνωριστικό', '356c8ba7-0114-32c3-861f-8432bc46e963', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('8869e7cb-00d2-38fd-880f-baa2568f0376', 'έχει προτιμώμενο αναγνωριστικό', '356c8ba7-0114-32c3-861f-8432bc46e963', 'el', 'altLabel');
INSERT INTO "values" VALUES ('524624a6-601f-3eda-b4f7-b88488f93d0f', 'P48 tem identificador preferido', '356c8ba7-0114-32c3-861f-8432bc46e963', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('6d1dd7da-7901-314f-a985-dab664f3fa65', 'tem identificador preferido', '356c8ba7-0114-32c3-861f-8432bc46e963', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('da9121d5-0394-3b2d-a652-82c470f68d17', 'P48 有首选标识符', '356c8ba7-0114-32c3-861f-8432bc46e963', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('1e554567-f3ce-3269-8a53-60b2ea5269d2', '有首选标识符', '356c8ba7-0114-32c3-861f-8432bc46e963', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('26b7e901-40d6-31ee-abc2-753dad5a5302', 'This property records the preferred E42 Identifier that was used to identify an instance of E1 CRM Entity at the time this property was recorded.
More than one preferred identifier may have been assigned to an item over time.
Use of this property requires an external mechanism for assigning temporal validity to the respective CRM instance.
P48 has preferred identifier (is preferred identifier of), is a shortcut for the path from E1 CRM Entity through P140 assigned attribute to (was attributed by), E15 Identifier Assignment, P37 assigned (was assigned by) to E42 Identifier. The fact that an identifier is a preferred one for an organisation can be better expressed in a context independent form by assigning a suitable E55 Type to the respective instance of E15 Identifier Assignment using the P2 has type property.
', '356c8ba7-0114-32c3-861f-8432bc46e963', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('cbf0691e-c2ec-302c-a23b-0cb9b59c07fb', 'P49 имеет бывшего или текущего смотрителя', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('fb494756-d953-34f0-ab5d-82769e3def0e', 'имеет бывшего или текущего смотрителя', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('a758f7cb-3c47-3ee4-91ba-d5a7e8fe5d83', 'P49 είναι ή ήταν στην κατοχή του', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('961cb376-819e-38c0-823a-5e7d50c85ba1', 'είναι ή ήταν στην κατοχή του', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'el', 'altLabel');
INSERT INTO "values" VALUES ('9e6f2a24-ca72-3457-b948-6bd65c2988f7', 'P49 est ou a été détenu par', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('75b46fa4-4b88-3fe6-be47-2fbe51b003b7', 'est ou a été détenu par', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('52d120c3-e7fb-3164-908f-4314863bc39f', 'P49 hat früheren oder derzeitigen Betreuer', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('05aaf69d-08ff-3dba-956e-bf6ce1a0ac3f', 'hat früheren oder derzeitigen Betreuer', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'de', 'altLabel');
INSERT INTO "values" VALUES ('28357148-8aa8-39ac-8a46-0244bb7729dc', 'P49 has former or current keeper', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('1625a7e7-b834-3615-b84a-1aae5fafdfd3', 'has former or current keeper', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'en', 'altLabel');
INSERT INTO "values" VALUES ('e9bd9014-f45b-3bb0-9a65-8f6743f0b6e6', 'P49 é ou foi guardada por', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('f5b2ece8-7c1e-300c-8839-5c4dde2d917d', 'é ou foi guardada por', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('35c941c1-3a2f-31a8-be43-0552ebfdaed1', 'P49 有前任或现任保管者', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('c8d16606-b19d-3719-9da7-2145f117cb50', '有前任或现任保管者', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('94212c69-e737-3cad-8ebb-292f5e61f263', 'has former or current location', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'en', 'altLabel');
INSERT INTO "values" VALUES ('2f224d3b-3cd1-3721-92c6-a29f71a14621', 'P53 hat früheren oder derzeitigen Standort', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('652e7a3c-0c5f-3c55-b48c-fbc54e0b0365', 'This property identifies the E39 Actor or Actors who have or have had custody of an instance of E18 Physical Thing at some time. 
The distinction with P50 has current keeper (is current keeper of) is that P49 has former or current keeper (is former or current keeper of) leaves open the question as to whether the specified keepers are current. 
P49 has former or current keeper (is former or current keeper of) is a shortcut for the more detailed path from E18 Physical Thing through P30 transferred custody of (custody transferred through), E10 Transfer of Custody, P28 custody surrendered by (surrendered custody through) or P29 custody received by (received custody through) to E39 Actor.
', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('5717dd75-107b-3a24-885e-cf2eaa7f5e64', 'P50 hat derzeitigen Betreuer', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('925f10d6-ad35-3c6c-aa59-d8b06406195a', 'hat derzeitigen Betreuer', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'de', 'altLabel');
INSERT INTO "values" VALUES ('d9435f4b-4e56-3e2b-b393-18765f077151', 'P50 has current keeper', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('d8f422b0-6e6e-306a-80cc-0aa5d7f10320', 'has current keeper', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'en', 'altLabel');
INSERT INTO "values" VALUES ('05f3adba-294a-3f4f-8740-e04ce25bd4fc', 'P50 είναι στην κατοχή του', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('f18148ff-c83f-3114-8e18-a6952cb7e478', 'είναι στην κατοχή του', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'el', 'altLabel');
INSERT INTO "values" VALUES ('e366b6e9-b974-3b91-9c36-af196b527f9c', 'P50 est actuellement détenu par', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('35631eac-010d-3dd5-b648-65b29f5fbf2b', 'est actuellement détenu par', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('162421fd-9c03-3b16-b4e8-4e5b18629851', 'P50 имеет текущего смотрителя', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('331e602b-f634-3a8f-8c75-80df05a11ffa', 'имеет текущего смотрителя', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('712baf0e-1a19-32cc-bd01-c14eb875b976', 'P50 é guardada por', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('f19d5534-1d80-3742-aec6-de2cc0ea1093', 'é guardada por', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('124b9e77-55ee-32cc-971e-c1724d6d8ef8', 'P50 有现任保管者', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('26154d3d-0161-35bb-ae9a-36b7cb17eb17', '有现任保管者', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('98211d35-5e29-343f-8859-e44b8ecc090c', 'This property identifies the E39 Actor or Actors who had custody of an instance of E18 Physical Thing at the time of validity of the record or database containing the statement that uses this property.
	P50 has current keeper (is current keeper of) is a shortcut for the more detailed path from E18 Physical Thing through P30 transferred custody of (custody transferred through), E10 Transfer of Custody, P29 custody received by (received custody through) to E39 Actor.
', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('f01f0c56-5683-3342-9db9-601c32c199c0', 'P51 hat früheren oder derzeitigen Besitzer ', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('a319c8a0-0d45-3fa7-9d5a-223c61527efc', 'hat früheren oder derzeitigen Besitzer ', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'de', 'altLabel');
INSERT INTO "values" VALUES ('caf8ec28-bc97-3edc-b91c-7808eb4aa956', 'P51 имеет бывшего или текущего владельца', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('81eb16a9-10fe-3b56-b2b7-7ea589c47b7a', 'имеет бывшего или текущего владельца', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('6bd1e302-9986-3d7b-9e84-21c1cae75e3e', 'P51 έχει ή είχε ιδιοκτήτη', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('78a07370-8003-30bc-99e9-44a41f024a3f', 'έχει ή είχε ιδιοκτήτη', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'el', 'altLabel');
INSERT INTO "values" VALUES ('19653b97-471c-377f-a1a5-73fce36215a9', 'P51 est ou a été possédée par', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('60c2d196-843a-32d7-9b7d-9908a40fd2df', 'est ou a été possédée par', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('e1920196-d15d-30f9-a559-a00c77881e1b', 'P51 has former or current owner', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('079898a1-83f4-36a2-966c-6d2edaa9ef7c', 'has former or current owner', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'en', 'altLabel');
INSERT INTO "values" VALUES ('29d19fda-56df-384b-b359-0b5d1612427b', 'P51 é ou foi propriedade de', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('bb715a68-a640-30d2-b045-ece3b47a956e', 'é ou foi propriedade de', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('ba31f884-d37b-322d-a8bb-96c29c40bde9', 'P51 有前任或现任物主', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('952c27eb-2cd8-3345-bea7-3ac59625dbb5', '有前任或现任物主', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('7fbce49b-a9ad-30dd-a8f2-1bf3b942bce3', 'This property identifies the E39 Actor that is or has been the legal owner (i.e. title holder) of an instance of E18 Physical Thing at some time.
The distinction with P52 has current owner (is current owner of) is that P51 has former or current owner (is former or current owner of) does not indicate whether the specified owners are current. P51 has former or current owner (is former or current owner of) is a shortcut for the more detailed path from E18 Physical Thing through P24 transferred title of (changed ownership through), E8 Acquisition, P23 transferred title from (surrendered title through), or P22 transferred title to (acquired title through) to E39 Actor.
', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('4fff1897-d739-36e5-8f53-20ca6c32c3ba', 'P52 has current owner', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('443a7650-5524-3c23-9d94-67cbfeabc6f3', 'has current owner', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'en', 'altLabel');
INSERT INTO "values" VALUES ('49b828e0-ae36-38e3-86e9-0c6512245f01', 'P52 hat derzeitigen Besitzer', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('c3cf3d22-ee8a-34b0-a00c-0bf9cf84291e', 'hat derzeitigen Besitzer', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'de', 'altLabel');
INSERT INTO "values" VALUES ('fba2a728-a1c3-3b2e-84a6-4225edb8390c', 'P52 имеет текущего владельца', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('b724b51b-c334-3a47-ae59-56517496d1f8', 'имеет текущего владельца', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('4c3a5e51-2257-34f7-916b-fc6a88b04d47', 'P52 est actuellement possédée par', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('71d8b376-9e31-3ae1-ba2a-2bba89a41ba0', 'est actuellement possédée par', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('7da6b47d-5c13-374b-99ec-bd15973ce2f6', 'P52 έχει ιδιοκτήτη', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('54f9774e-db10-320f-aa86-438fa8b5411f', 'έχει ιδιοκτήτη', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'el', 'altLabel');
INSERT INTO "values" VALUES ('52ae5aa5-fc3a-3cff-8b31-4e98b7cdb90e', 'P52 é propriedade de', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('8785be95-8c92-350b-a8ab-76b56903de3d', 'é propriedade de', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('0bd5d35e-0e1a-3952-b584-489c56cdc6dd', 'P52 有现任物主', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('5cf8b202-c587-3f32-b5b7-84883b01a8f1', '有现任物主', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('47044ec2-a32c-34b1-9a02-fa9712c9edc2', 'This property identifies the E21 Person, E74 Group or E40 Legal Body that was the owner of an instance of E18 Physical Thing at the time of validity of the record or database containing the statement that uses this property.
P52 has current owner (is current owner of) is a shortcut for the more detailed path from E18 Physical Thing through P24 transferred title of (changed ownership through), E8 Acquisition, P22 transferred title to (acquired title through) to E39 Actor, if and only if this acquisition event is the most recent.
', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('7cd4a78f-b039-39f7-b687-03bc4382b1ca', 'P53 a ou a eu pour localisation', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('f7632af7-6952-344b-81e0-063c4bc8cfa4', 'a ou a eu pour localisation', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('0d6a5fdb-ad64-322b-b97d-5edd6105b12a', 'P53 βρίσκεται ή βρισκόταν σε', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('5aa976b5-1c9c-3e89-8376-5e66c067d185', 'βρίσκεται ή βρισκόταν σε', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'el', 'altLabel');
INSERT INTO "values" VALUES ('fbdfee35-65e7-3f5d-8180-75d3b8692d0c', 'P53 имеет текущее или бывшее местоположение', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('39573e29-cd0b-369b-a271-4782c88247f0', 'имеет текущее или бывшее местоположение', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('6246ca19-822f-386c-b0c8-75b71c037c20', 'P53 has former or current location', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('ccb33cbb-3a0a-3b2f-a9ee-a5b05f6a8422', 'hat früheren oder derzeitigen Standort', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'de', 'altLabel');
INSERT INTO "values" VALUES ('48c11176-9d76-39d3-bc8c-4a886038fc36', 'P53 é ou foi localizada em', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('197eddd2-d109-394c-8907-e619cd6b2448', 'é ou foi localizada em', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('5cfdf70c-fdb7-3e41-a2f6-1ae571d84f09', 'P53 目前或曾经被置放於', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('846a8dfe-af15-3497-a8f3-4eb44e559a54', '目前或曾经被置放於', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('424997b4-cd8b-37d4-9537-aa30d730ae85', 'This property allows an instance of E53 Place to be associated as the former or current location of an instance of E18 Physical Thing.
In the case of E19 Physical Objects, the property does not allow any indication of the Time-Span during which the Physical Object was located at this Place, nor if this is the current location.
In the case of immobile objects, the Place would normally correspond to the Place of creation.
P53 has former or current location (is former or current location of) is a shortcut. A more detailed representation can make use of the fully developed (i.e. indirect) path from E19 Physical Object through P25 moved (moved by), E9 Move, P26 moved to (was destination of) or P27 moved from (was origin of) to E53 Place.
', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('77ba0526-5037-38bc-bfa6-a2c590cb5068', 'P54 a actuellement pour localisation à demeure', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('cfaa8991-e676-3a56-832a-8864a1344511', 'a actuellement pour localisation à demeure', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('9d1f20f7-3d78-3d97-842b-94e8f1e31b8a', 'P54 hat derzeitigen permanenten Standort', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('bc5be859-e631-3701-ae79-386c26b37a11', 'hat derzeitigen permanenten Standort', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'de', 'altLabel');
INSERT INTO "values" VALUES ('7de30e6e-f4f1-340a-bf3a-fa4a7fd3f694', 'P54 has current permanent location', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('7d94ac30-3fc4-3b7a-b055-b92fecfbbb41', 'has current permanent location', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'en', 'altLabel');
INSERT INTO "values" VALUES ('3b9d5593-b8d7-3081-868b-32ce65d72c30', 'P54 έχει μόνιμη θέση', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('a642592c-200d-3011-8532-8c401af45cbc', 'έχει μόνιμη θέση', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'el', 'altLabel');
INSERT INTO "values" VALUES ('78f4e05a-15f8-3581-b495-3ba370a29c4b', 'P54 имеет текущее постоянное местоположение', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('e0e5d69a-e29a-32bb-a202-3eaffa8e3e92', 'имеет текущее постоянное местоположение', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('21930aad-86fe-3931-9ed5-afc8432c903a', 'P54 é localizado permanentemente em', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('c9ccff2e-f4a1-3208-afc4-f8c9381ee295', 'é localizado permanentemente em', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('d571614f-dd65-34c5-8fbc-9a35d6847847', 'P54 目前的永久位置位於', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('d8749326-19e3-318e-a2c2-b71a29303de9', '目前的永久位置位於', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('05d7410a-78d3-3d94-9a7b-2a9d2ed0d77a', 'This property records the foreseen permanent location of an instance of E19 Physical Object at the time of validity of the record or database containing the statement that uses this property.
P54 has current permanent location (is current permanent location of) is similar to P55 has current location (currently holds). However, it indicates the E53 Place currently reserved for an object, such as the permanent storage location or a permanent exhibit location. The object may be temporarily removed from the permanent location, for example when used in temporary exhibitions or loaned to another institution. The object may never actually be located at its permanent location.
', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('41cfa239-8395-3749-99e5-cbdd0b2a88b6', 'P55 βρίσκεται σε', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('900c3d08-4bdb-3303-ae20-d6e12946b6df', 'βρίσκεται σε', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'el', 'altLabel');
INSERT INTO "values" VALUES ('4f7ba484-d3ca-3b3a-9924-c407c51b62cf', 'P55 has current location', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('37f6e1f6-1b88-3d46-a130-59e751f926ae', 'has current location', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c68f89af-9f2a-3c35-bf88-1a604e9f4b9f', 'P55 a pour localisation actuelle', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('d236c65d-35d5-3a22-bee9-7c6a32632c22', 'a pour localisation actuelle', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('3f951b04-ed51-3153-9c85-1383a1110599', 'P55 в данный момент находится в', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('f35eef77-d43e-36c5-a560-55934947cda3', 'в данный момент находится в', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('882b7605-93dc-380c-abcc-53e1962f8409', 'P55 hat derzeitigen Standort', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('702ceaca-8e3c-33b9-81f3-89a2644137ed', 'hat derzeitigen Standort', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'de', 'altLabel');
INSERT INTO "values" VALUES ('7393b58a-13e0-3e22-89b5-57111c5691ca', 'P55 é localizado em', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('18c38f7b-d2b9-37fa-9312-165488e114cb', 'é localizado em', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('f85f17a3-e02a-378f-ae6a-8fd9e649df0d', 'P55 目前被置放於', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('51ec14fa-c783-3ace-9f58-3c9bb6ba5574', '目前被置放於', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('822a124a-f5c9-355c-b1e0-e677e4189f93', 'This property records the location of an E19 Physical Object at the time of validity of the record or database containing the statement that uses this property. 
	This property is a specialisation of P53 has former or current location (is former or current location of). It indicates that the E53 Place associated with the E19 Physical Object is the current location of the object. The property does not allow any indication of how long the Object has been at the current location. 
P55 has current location (currently holds) is a shortcut. A more detailed representation can make use of the fully developed (i.e. indirect) path from E19 Physical Object through P25 moved (moved by), E9 Move P26 moved to (was destination of) to E53 Place if and only if this Move is the most recent.
', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('b7a0c09a-4202-33aa-a496-7270edc892d9', 'P56 несет признак', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('7e595149-e874-3814-964c-27a132f1c348', 'несет признак', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('18d4d7b0-a737-373c-8687-a8ee52ae61c2', 'P56 trägt Merkmal', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('cb4290a5-3fe8-39c5-8f75-151de3513bf7', 'trägt Merkmal', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'de', 'altLabel');
INSERT INTO "values" VALUES ('814f4099-c094-38ba-8a63-d06002261963', 'P56 présente pour caractéristique', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5c8cd82a-fca1-38b0-b476-d80e141f09f4', 'présente pour caractéristique', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('57f0563a-ebe3-3469-9e83-879733e1ceb8', 'P56 φέρει μόρφωμα', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('1eef7d1c-f38c-3974-b978-016bbd911138', 'φέρει μόρφωμα', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'el', 'altLabel');
INSERT INTO "values" VALUES ('263c6753-be89-3d39-ac7b-d209294ad912', 'P56 bears feature', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('29b6d0f6-d777-38ae-a962-2d8f9d89f231', 'bears feature', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('8d12c632-e0e5-36fa-91fa-0c7fdb317c1d', 'P56 possui característica', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('5512d342-ec2c-387b-81d5-ef81a45e49a4', 'possui característica', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('8b8c8997-c071-3fa0-8206-0886c5e76bef', 'P56 有外貌表征', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('93a0634c-7fc3-3cbf-a39d-89022e4a3c9d', '有外貌表征', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('e5cf0b87-c6b1-320c-80fb-99dc8356bcdc', 'απεικονίζει', '05804845-b0d6-3634-a977-a5c7785d2dde', 'el', 'altLabel');
INSERT INTO "values" VALUES ('fa728981-5fdc-3cda-98ce-59a2d286d552', 'P62 figure', '05804845-b0d6-3634-a977-a5c7785d2dde', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('6fca1cf3-f89b-3ef7-9473-56965fab2f84', 'figure', '05804845-b0d6-3634-a977-a5c7785d2dde', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('b73335b0-c619-3ec0-b094-7e0883b8ad6b', 'P62 retrata', '05804845-b0d6-3634-a977-a5c7785d2dde', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('560f6ea5-9a6a-393b-9855-d019d8e98eb1', 'retrata', '05804845-b0d6-3634-a977-a5c7785d2dde', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b9d6832b-17f3-3541-9b93-ec0451a8d1fa', 'P62 描绘', '05804845-b0d6-3634-a977-a5c7785d2dde', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('59cd26d3-76da-3fd9-96e1-d7701665f358', '描绘', '05804845-b0d6-3634-a977-a5c7785d2dde', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('b18a0074-5bd5-3403-9051-38521d6e08a8', 'This property links an instance of E19 Physical Object to an instance of E26 Physical Feature that it bears.
An E26 Physical Feature can only exist on one object. One object may bear more than one E26 Physical Feature. An E27 Site should be considered as an E26 Physical Feature on the surface of the Earth.
An instance B of E26 Physical Feature being a detail of the structure of another instance A of E26 Physical Feature can be linked to B by use of the property P46 is composed of (forms part of). This implies that the subfeature B is P56i found on the same E19 Physical Object as A.
P56 bears feature (is found on) is a shortcut. A more detailed representation can make use of the fully developed (i.e. indirect) path from E19 Physical Object through P59 has section (is located on or
Definition of the CIDOC Conceptual Reference Model 149 within), E53 Place, P53 has former or current location (is former or current location of) to E26 Physical Feature.
', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('2598263f-a6d2-397e-8e13-7a843505cbbb', 'P57 has number of parts', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('8527fcaa-e5ad-3756-bdc1-12b33ee028a3', 'has number of parts', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'en', 'altLabel');
INSERT INTO "values" VALUES ('51758214-eb44-3f5b-973f-49f60022d429', 'P57 имеет число частей', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('4431e3a1-f107-3b1a-a5d7-63eb892edec0', 'имеет число частей', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('559a3ea1-8931-3050-bedf-a5c22737dccd', 'P57 έχει αριθμό μερών', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('65de7255-d56a-36a4-b91e-540a4e34a45a', 'έχει αριθμό μερών', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'el', 'altLabel');
INSERT INTO "values" VALUES ('bb8d3be5-3e84-30cc-a4b8-736042601e49', 'P57 a pour nombre de parties', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5358a80b-672e-3b64-8aaa-4efa13c2a02a', 'a pour nombre de parties', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('fc109130-4cb9-386a-a719-de76762a77da', 'P57 hat Anzahl Teile', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f98931a3-c992-3d43-8405-468270cc7a1d', 'hat Anzahl Teile', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'de', 'altLabel');
INSERT INTO "values" VALUES ('26390a76-a54c-3bbb-b695-badd4884aecd', 'P57 tem número de partes', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('7edc165f-353a-3351-9d7f-6f5cc448d33f', 'tem número de partes', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('49c30512-5648-3a88-98fa-4e7f65576d4f', 'P57 有组件数目', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('0284a0ab-a9db-329b-a921-8168b869e533', '有组件数目', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('f90801fc-4a83-3f33-b619-b6f54826d074', 'This property documents the E60 Number of parts of which an instance of E19 Physical Object is composed.
This may be used as a method of checking inventory counts with regard to aggregate or collective objects. What constitutes a part or component depends on the context and requirements of the documentation. Normally, the parts documented in this way would not be considered as worthy of individual attention.
For a more complete description, objects may be decomposed into their components and constituents using P46 is composed of (forms parts of) and P45 consists of (is incorporated in). This allows each element to be described individually.
', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('ec534fe5-f2fa-3fc3-afe6-b3b84b09f772', 'P58 has section definition', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('e81fc179-449e-33a6-939a-16a3edfb531b', 'has section definition', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'en', 'altLabel');
INSERT INTO "values" VALUES ('89ddbab9-ec6a-3230-848c-bac56871269f', 'P58 hat Abschittsdefinition', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('3d74e969-3566-381e-b3ee-9ad158006fc5', 'hat Abschittsdefinition', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'de', 'altLabel');
INSERT INTO "values" VALUES ('d6b97be3-aa73-3132-a80b-f816adeed60f', 'P58 имеет определение района', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('99d3860c-3a05-357b-a4f6-cd144df3e1aa', 'имеет определение района', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('7ce7babb-ae80-3fa8-a293-657cdba669f9', 'P58 έχει ορισμό τμήματος', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ade60d06-50ea-364c-bf94-c1cf0ececf4d', 'έχει ορισμό τμήματος', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'el', 'altLabel');
INSERT INTO "values" VALUES ('548da796-98f5-32ad-999e-34b824854af6', 'P58 a pour désignation de section', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('9b653126-0f7e-369f-877d-9a7215cd7a67', 'a pour désignation de section', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('448b4ca0-8714-32e3-8f55-347a257351d4', 'P58 tem designação de seção', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('75843237-5e0c-32e3-a84a-4d874ae005a8', 'tem designação de seção', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('2f940c81-a5d9-385b-baef-a5217e2512e4', 'P58 有区域定义', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('7bd06586-21f6-37a5-a28d-31265f874086', '有区域定义', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('0f2ec8ce-7730-3e77-a18e-a4652d2db8b6', 'This property links an area (section) named by a E46 Section Definition to the instance of E18 Physical Thing upon which it is found.
The CRM handles sections as locations (instances of E53 Place) within or on E18 Physical Thing that are identified by E46 Section Definitions. Sections need not be discrete and separable components or parts of an object.
This is part of a more developed path from E18 Physical Thing through P58, E46 Section Definition, P87 is identified by (identifies) that allows a more precise definition of a location found on an object than the shortcut P59 has section (is located on or within).
A particular instance of a Section Definition only applies to one instance of Physical Thing.', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('9c194820-0b92-31dc-9c89-a531f9caf3d0', 'P59 has section', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('a39e731d-ebf3-316d-8623-b696c927c5ba', 'has section', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c91bf862-fc3d-34a8-ac5f-848667c77089', 'P59 έχει τομέα', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('78d76d07-fd07-3aaf-9591-5fb5f6f53508', 'έχει τομέα', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'el', 'altLabel');
INSERT INTO "values" VALUES ('67209c73-89d8-3efe-bfec-af19d363cef5', 'P59 hat Bereich', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('411dc18e-17d3-3e31-869a-e493a095752e', 'hat Bereich', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'de', 'altLabel');
INSERT INTO "values" VALUES ('5439a380-304c-385f-938e-781b4818b736', 'P59 имеет район', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('10e4875c-55a2-365b-aac3-1ed6bb92eb98', 'имеет район', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('325a71df-a8d5-31b8-bee3-e7b6f6fe6e6d', 'P59 a pour section', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('6a4229f1-bceb-3fe0-b7ab-4ee09f82ad47', 'a pour section', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('754af36e-57d4-346e-8898-c40e3acfbc01', 'P59 tem seção', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('64561718-a1f5-331e-b892-9a2965a49258', 'tem seção', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('5eda0a2b-dd1f-30f7-ab0e-a2d9776bc9da', 'P59 有区域', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('e57e94da-7d41-355e-b4cb-1e3ea8596982', '有区域', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('02a8b032-2781-3c90-bd14-c4b0a71afd1d', 'This property links an area to the instance of E18 Physical Thing upon which it is found.
It is typically used when a named E46 Section Definition is not appropriate.
E18 Physical Thing may be subdivided into arbitrary regions. 
P59 has section (is located on or within) is a shortcut. If the E53 Place is identified by a Section Definition, a more detailed representation can make use of the fully developed (i.e. indirect) path from E18 Physical Thing through P58 has section definition (defines section), E46 Section Definition, P87 is identified by (identifies) to E53 Place. A Place can only be located on or within one Physical Object.
', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('cb1b6335-4d08-3a21-8abe-77acce75b52c', 'P62 bildet ab', '05804845-b0d6-3634-a977-a5c7785d2dde', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('a7e77f7c-d150-3395-8adf-da4cb5bd0429', 'bildet ab', '05804845-b0d6-3634-a977-a5c7785d2dde', 'de', 'altLabel');
INSERT INTO "values" VALUES ('67eb0358-8420-39e8-88f1-40534839defe', 'P62 описывает', '05804845-b0d6-3634-a977-a5c7785d2dde', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('85902387-9e75-3e8e-a099-e7689069cf78', 'описывает', '05804845-b0d6-3634-a977-a5c7785d2dde', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('de1b4c90-70cd-3b2c-94cf-4263dcc2f053', 'P62 depicts', '05804845-b0d6-3634-a977-a5c7785d2dde', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('29129a44-dddd-350d-a6bb-2dac720e8a53', 'depicts', '05804845-b0d6-3634-a977-a5c7785d2dde', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c9095164-c465-3fc2-83ce-d96851387e41', 'P62 απεικονίζει', '05804845-b0d6-3634-a977-a5c7785d2dde', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('55aa360d-e2f7-30d6-93be-eaa7aa063211', 'This property identifies something that is depicted by an instance of E24 Physical Man-Made Thing. Depicting is meant in the sense that the surface of the E24 Physical Man-Made Thing shows, through its passive optical qualities or form, a representation of the entity depicted. It does not pertain to inscriptions or any other information encoding.

This property is a shortcut of the more fully developed path from E24 Physical Man-Made Thing through P65 shows visual item (is shown by), E36 Visual Item, P138 represents (has representation) to E1 CRM Entity. P62.1 mode of depiction allows the nature of the depiction to be refined.
', '05804845-b0d6-3634-a977-a5c7785d2dde', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('683b157f-3af5-3e50-b689-0d333ce9446d', 'P65 présente l''item visuel', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('97faf578-a76c-3f76-8205-113b7e8d2c10', 'présente l''item visuel', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('46e69af0-811e-3952-be43-6785c7067370', 'P65 shows visual item', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('a31a0c0b-e389-3f56-8f16-9fd034d08a3d', 'shows visual item', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'en', 'altLabel');
INSERT INTO "values" VALUES ('0624035b-b477-3af4-bc4d-5aeb4cb97671', 'P65 zeigt Bildliches', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('09ef858a-a09d-319e-98bd-dbdd3e7d8da5', 'zeigt Bildliches', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'de', 'altLabel');
INSERT INTO "values" VALUES ('9e696da0-0ece-3295-9a93-ed3175ece818', 'P65 показывает визуальный предмет', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('b08038d6-410b-3631-920c-e58f8788955d', 'показывает визуальный предмет', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('ee2b6cfc-6bb7-306f-8ed8-52a906367b5e', 'P65 εμφανίζει οπτικό στοιχείο', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('a2dcc219-6624-3439-982b-46838b1de506', 'εμφανίζει οπτικό στοιχείο', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'el', 'altLabel');
INSERT INTO "values" VALUES ('6fe22b1c-f1b0-3add-81ae-9c2ef0318c00', 'P65 apresenta item visual', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('4dcfaf4e-5a8d-38f1-92e3-6c42e9572ea7', 'apresenta item visual', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('017296e9-4e4c-366d-a03d-5c48266afb11', 'P65 显示视觉项目', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('dcadf4de-94e3-3d27-90e6-294799f0a232', '显示视觉项目', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('779ae6a9-61e6-3379-a60c-1d7d26209aef', 'This property documents an E36 Visual Item shown by an instance of E24 Physical Man-Made Thing.
This property is similar to P62 depicts (is depicted by) in that it associates an item of E24 Physical Man-Made Thing with a visual representation. However, P65 shows visual item (is shown by) differs from the P62 depicts (is depicted by) property in that it makes no claims about what the E36 Visual Item is deemed to represent. E36 Visual Item identifies a recognisable image or visual symbol, regardless of what this image may or may not represent.
For example, all recent British coins bear a portrait of Queen Elizabeth II, a fact that is correctly documented using P62 depicts (is depicted by). Different portraits have been used at different periods, however. P65 shows visual item (is shown by) can be used to refer to a particular portrait.
P65 shows visual item (is shown by) may also be used for Visual Items such as signs, marks and symbols, for example the ''Maltese Cross'' or the ''copyright symbol’ that have no particular representational content. 
This property is part of the fully developed path from E24 Physical Man-Made Thing through P65 shows visual item (is shown by), E36 Visual Item, P138 represents (has representation) to E1 CRM Entity which is shortcut by, P62 depicts (is depicted by).
', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('0abaff88-4053-3c1b-88a7-25766e98e2f5', 'P67 αναφέρεται σε', '629ed771-13e7-397e-8345-69f6cfb3db30', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('675a3d8e-ebcf-31ab-8b04-5d884f91469e', 'αναφέρεται σε', '629ed771-13e7-397e-8345-69f6cfb3db30', 'el', 'altLabel');
INSERT INTO "values" VALUES ('e24b73fc-2efa-30fe-8127-de0aa6ff4bf8', 'P67 refers to', '629ed771-13e7-397e-8345-69f6cfb3db30', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('edabf059-b467-3ef2-83c5-5b77303349ed', 'refers to', '629ed771-13e7-397e-8345-69f6cfb3db30', 'en', 'altLabel');
INSERT INTO "values" VALUES ('aab1eaad-8e04-3b80-bbd8-1758e0d1b13b', 'P67 ссылается на', '629ed771-13e7-397e-8345-69f6cfb3db30', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('8a7bb295-4b1f-3c39-ac92-4b000b436455', 'ссылается на', '629ed771-13e7-397e-8345-69f6cfb3db30', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('99fcee24-821b-374f-aaf0-bf9bf2f1e251', 'P67 fait référence à', '629ed771-13e7-397e-8345-69f6cfb3db30', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('21b103ea-2cd6-3f23-9213-45825aa08c37', 'fait référence à', '629ed771-13e7-397e-8345-69f6cfb3db30', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('1c55052f-f81f-390a-9709-fe938ad2b9a6', 'P67 verweist auf', '629ed771-13e7-397e-8345-69f6cfb3db30', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('5d958f89-2d16-338c-b0d1-fa557635b276', 'verweist auf', '629ed771-13e7-397e-8345-69f6cfb3db30', 'de', 'altLabel');
INSERT INTO "values" VALUES ('e4fd1e13-76a1-38b7-b90b-eb90b06ad956', 'P67 referencia', '629ed771-13e7-397e-8345-69f6cfb3db30', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('21b6a7c7-5f3a-358d-b1c2-cd826e991984', 'referencia', '629ed771-13e7-397e-8345-69f6cfb3db30', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('5c69cfac-75d2-3789-9ecf-6407c0db1c5c', 'P67 论及', '629ed771-13e7-397e-8345-69f6cfb3db30', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('66c48c2d-9054-329c-97ac-18f85d8a792f', '论及', '629ed771-13e7-397e-8345-69f6cfb3db30', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('a474334b-64bc-3524-b75c-c27ead2d6d22', 'This property documents that an E89 Propositional Object makes a statement about an instance of E1 CRM Entity. P67 refers to (is referred to by) has the P67.1 has type link to an instance of E55 Type. This is intended to allow a more detailed description of the type of reference. This differs from P129 is about (is subject of), which describes the primary subject or subjects of the E89 Propositional Object.
', '629ed771-13e7-397e-8345-69f6cfb3db30', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('02a73222-535c-328c-9416-83ce468b4459', 'P68 foresees use of', '037c3de7-65ae-3002-8328-18cc33572501', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('5e6c427c-fa43-334a-92e7-20da9547bb80', 'foresees use of', '037c3de7-65ae-3002-8328-18cc33572501', 'en', 'altLabel');
INSERT INTO "values" VALUES ('299bd659-b34d-31d2-99cf-961804f0fd6c', 'P68  sieht den Gebrauch vor von', '037c3de7-65ae-3002-8328-18cc33572501', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('df5322c9-6f23-34f3-8cb8-2ecd36691197', ' sieht den Gebrauch vor von', '037c3de7-65ae-3002-8328-18cc33572501', 'de', 'altLabel');
INSERT INTO "values" VALUES ('11a169fc-a927-35a7-8c1e-56fdfc989d3e', 'P68 обычно применяет', '037c3de7-65ae-3002-8328-18cc33572501', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('6dc5d1ee-2934-3f04-a06a-a9eeae39ba3f', 'обычно применяет', '037c3de7-65ae-3002-8328-18cc33572501', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('f50f3a59-915c-3d02-8027-3819d5af35ac', 'P68 utilise habituellement', '037c3de7-65ae-3002-8328-18cc33572501', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('a88131e2-7a08-3f07-822e-614a4c402937', 'utilise habituellement', '037c3de7-65ae-3002-8328-18cc33572501', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('300c6f5d-6cab-3c82-9cfb-a8a08d02590f', 'P68 συνήθως χρησιμοποιεί', '037c3de7-65ae-3002-8328-18cc33572501', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('5a9d9041-4433-3a61-bafa-645f8bde2dd3', 'συνήθως χρησιμοποιεί', '037c3de7-65ae-3002-8328-18cc33572501', 'el', 'altLabel');
INSERT INTO "values" VALUES ('d372b49d-f15c-36ad-9a0f-f697b9fe698f', 'P68 normalmente emprega', '037c3de7-65ae-3002-8328-18cc33572501', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('87cc012f-2c68-3be8-9b7c-803e01a0c5f1', 'normalmente emprega', '037c3de7-65ae-3002-8328-18cc33572501', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('4e329fad-5a13-3dee-94fb-f39c7fb469cc', 'P68 指定使用材料', '037c3de7-65ae-3002-8328-18cc33572501', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('fc4ca851-7bf9-37f9-9eef-e7c61d2777ab', '指定使用材料', '037c3de7-65ae-3002-8328-18cc33572501', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('dce18a1b-3a79-3914-8f79-c7def47454f7', 'This property identifies an E57 Material foreseeen to be used by an E29 Design or Procedure. 
E29 Designs and procedures commonly foresee the use of particular E57 Materials. The fabrication of adobe bricks, for example, requires straw, clay and water. This property enables this to be documented.
This property is not intended for the documentation of E57 Materials that were used on a particular occasion when an instance of E29 Design or Procedure was executed.
', '037c3de7-65ae-3002-8328-18cc33572501', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('26c54af5-2a77-31a0-9e0c-24a24e64f8ca', 'P69 est associée à', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('e80d929a-8013-381d-a016-5f5fb79b6e06', 'est associée à', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('ab9abd2f-87ab-3312-9a8e-0f61010e8bbb', 'P69 σχετίζεται με', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('0fb5c069-0438-38c2-8948-5209f6bc1473', 'σχετίζεται με', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'el', 'altLabel');
INSERT INTO "values" VALUES ('a8b1aee7-94a3-3a84-a0f3-1aef9d2a4a6a', 'P69 ассоциирован с', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('d903afc2-ef07-3c03-a3f5-c4e1cca7a66d', 'ассоциирован с', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('c324330f-7759-3afe-85eb-a81afdb8d23a', 'P69 ist verbunden mit', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('4663f241-80a0-3b5f-bd4e-1742a77c60d8', 'ist verbunden mit', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'de', 'altLabel');
INSERT INTO "values" VALUES ('e372c437-5d89-3688-b52c-ad07bc55cc48', 'P69 is associated with', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('cc4ca837-c8a8-396d-a910-1a11e100b3a0', 'is associated with', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'en', 'altLabel');
INSERT INTO "values" VALUES ('60f32d33-c6cb-30cc-bf07-266fb8b4eec0', 'P69 é associado com', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('b5d13831-51ee-3a15-be38-ca814ec31e96', 'é associado com', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('5c42a0f5-b2a6-3b47-af9d-c4ec2611a019', 'P69 相关於', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('8d140869-ed8d-3249-a373-fe5f7a75914b', '相关於', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('238ed8f1-3a5b-3458-9023-b2e996433a44', 'This property generalises relationships like whole-part, sequence, prerequisite or inspired by between instances of E29 Design or Procedure. Any instance of E29 Design or Procedure may be associated with other designs or procedures. The property is considered to be symmetrical unless otherwise indicated by P69.1 has type.
The P69.1 has type property of P69 has association with allows the nature of the association to be specified reading from domain to range; examples of types of association between instances of E29 Design or Procedure include: has part, follows, requires, etc.
The property can typically be used to model the decomposition of the description of a complete workflow into a series of separate procedures.
', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('85d375e7-42a6-3132-afce-6314ebc082cf', 'P70 mentionne', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('8ffe76c0-ebfb-3f3b-89ba-11dfd9650d78', 'mentionne', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('2a87bd68-f326-3e87-98a4-d3b340c92a53', 'P70 документирует', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('890f76d3-516d-3dd5-b6ce-2b7486eb5b07', 'документирует', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('e22536b1-cb23-3425-ad17-aa7894df761b', 'P70 τεκμηριώνει', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('3247307f-683f-39b4-9b3f-8d24c22e4d5d', 'τεκμηριώνει', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'el', 'altLabel');
INSERT INTO "values" VALUES ('ad42abaf-d3bc-3cb3-bb69-8e6b45cb60d3', 'P70 documents', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('761dd980-d4d0-3345-87a7-93028777fadf', 'documents', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'en', 'altLabel');
INSERT INTO "values" VALUES ('a89be3f5-bec1-363f-974e-b9378ca2da52', 'P70 belegt', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('a4aa7b83-fd7e-33f1-a13a-b1af19fa1ddf', 'belegt', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'de', 'altLabel');
INSERT INTO "values" VALUES ('4be79b6a-6cb1-3c26-b9ce-889b157ddd2b', 'P70 documenta', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('983cb0c8-f0c2-3e3c-baeb-6b14e0bec982', 'documenta', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('f2cf4ec3-d374-37d2-8fb3-61ced9fc73e5', 'P70 记录了', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('8bbfa840-047a-3c2e-a0d4-d889f3644149', '记录了', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('586ddc14-0cae-3c67-a6d1-a1f1c91a0698', 'This property describes the CRM Entities documented by instances of E31 Document.
Documents may describe any conceivable entity, hence the link to the highest-level entity in the CRM hierarchy. This property is intended for cases where a reference is regarded as being of a documentary character, in the scholarly or scientific sense.
', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('ee78ce00-ce32-37eb-9bd3-90dcf5c24b58', 'P71 listet', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('70b60826-8156-3ab9-9917-626c456ed2d6', 'listet', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'de', 'altLabel');
INSERT INTO "values" VALUES ('89af3e11-5882-389f-be67-194452cf3965', 'P71 перечисляет', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('118a4826-ab80-3162-a2f1-8b7aaea926a9', 'перечисляет', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('a9036835-857d-316d-a8cb-6264ba1ec317', 'P71 lists', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('9dd2f93c-9920-31c4-b6f3-9fd33389a500', 'lists', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'en', 'altLabel');
INSERT INTO "values" VALUES ('5de98ed9-c98a-32fc-b9a5-af50b91e424c', 'P71 περιλαμβάνει', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('0a26805f-3bc6-3746-bce3-6c9459e602a3', 'περιλαμβάνει', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'el', 'altLabel');
INSERT INTO "values" VALUES ('640e5394-ac58-32d9-8e26-4f361b7cea74', 'P71 définit', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('56fdb443-083e-3bbe-9e83-9f3cd01ffa71', 'définit', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('bfb9cb2a-8432-39e9-8eb9-de92ec4a644c', 'P71 define', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('6a7f941e-7321-3f98-b072-0b048d86af2c', 'define', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b74f40d5-b32a-3557-8426-407c8647022b', 'P71 条列出', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('d5a1ecc2-ce6d-3493-b23d-c9ed8d4ec9ed', '条列出', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('9f46de08-1240-3356-8fa4-d907b53a3df5', 'This property documents a source E32 Authority Document for an instance of an E1 CRM Entity.
', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('c8dfc10b-dd8e-381f-9e4f-81bb95733dd8', 'P72 est en langue', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('2a13c2ec-28f4-363f-a3b4-e9a57b03195f', 'est en langue', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('9874fceb-4606-3052-8d89-f5bf02244bf7', 'P72 имеет язык', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('8403ea18-2c2d-3795-9dc6-956c009d942a', 'имеет язык', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('04f02e68-fa90-3d01-a4a8-87910ec53019', 'P72 has language', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('7db29c72-4a2b-36c4-b0bf-2ca0ccb23e08', 'has language', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'en', 'altLabel');
INSERT INTO "values" VALUES ('03675a98-93d0-3b72-a30f-bb7dada5456a', 'P72 hat Sprache', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('d48fce50-6063-3c8d-8108-ce0cc1307317', 'hat Sprache', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'de', 'altLabel');
INSERT INTO "values" VALUES ('f489e9b5-afbd-34bf-b288-db1f2c5a419a', 'P72 έχει γλώσσα', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('2fabeb60-d0a3-34e4-97d9-ddc40a99ebf9', 'έχει γλώσσα', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'el', 'altLabel');
INSERT INTO "values" VALUES ('5f31a761-9305-3adf-a95e-6c578fbc5161', 'P72 é da língua ', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('425b2cf1-07b0-35bc-8b56-915e81476996', 'é da língua ', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('69e626c6-1a14-3a27-9466-3e6e339217cb', 'P72 使用语言', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('970f2f82-34bb-3796-9e97-5b9805d35730', '使用语言', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('3aa2be29-9af1-37c5-b2d9-6b532f192898', 'This property describes the E56 Language of an E33 Linguistic Object. 
Linguistic Objects are composed in one or more human Languages. This property allows these languages to be documented.
', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('95d5442a-d532-3fb6-ad47-fbdf3e4c295d', 'P73 έχει μετάφραση', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('c5aec3fc-dc59-30b3-ba29-f7c96bf85aaf', 'έχει μετάφραση', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'el', 'altLabel');
INSERT INTO "values" VALUES ('68c5f91b-fde0-31b3-99ba-9f005cf648cf', 'P73 hat Übersetzung', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('ef35764a-370c-3fc4-b008-b7f0cd54ddf8', 'hat Übersetzung', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'de', 'altLabel');
INSERT INTO "values" VALUES ('0c12abc5-992e-377c-9174-aedfc51a6912', 'P73 имеет перевод', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('35ab7112-bd56-38d2-91f0-7a204a2a4119', 'имеет перевод', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('f7c3dd6c-5630-35ec-893c-7b9b8c04fba1', 'P73 has translation', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('ddd01880-4321-39cd-ac67-f5885cf6ccc9', 'has translation', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'en', 'altLabel');
INSERT INTO "values" VALUES ('2429a0a4-2275-3a17-ae33-1ad12ad46967', 'P73 a pour traduction', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('19a31f4a-c8b4-3d75-a34d-f63507ec2cce', 'a pour traduction', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('783211ff-404b-3d79-8ead-2ed9b21d30ee', 'P73 tem tradução', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('63799f15-fb4b-3701-a569-1bbe2ef2ee09', 'tem tradução', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('38523087-59f0-3691-8c5d-63b03eac5071', 'P73 有译文', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('c3c9cc4e-7bcf-3ae5-ae3c-c38be7e46fae', '有译文', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('7c6c5bd1-ffb6-334b-8a47-a6db9d9c1490', 'This property describes the source and target of instances of E33Linguistic Object involved in a translation.
When a Linguistic Object is translated into a new language it becomes a new Linguistic Object, despite being conceptually similar to the source object.
', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('396796d5-84f7-39cf-b170-54665aa666db', 'P74 имеет текущее или бывшее местожительства', '5869a9ed-ebe5-3613-acc2-29c184737885', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('7d9aca35-3826-3793-bf6e-9725d85cde6a', 'P84 had at most duration', '86caed02-d112-3cd7-8f21-4836e4997850', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('52571f60-45cd-328c-be52-ea50cc44f84b', 'имеет текущее или бывшее местожительства', '5869a9ed-ebe5-3613-acc2-29c184737885', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('dbb90e76-64e3-382a-8a63-1db573859aec', 'P74 has current or former residence', '5869a9ed-ebe5-3613-acc2-29c184737885', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b88b31cc-88b1-38f0-bc68-42501d162a3c', 'has current or former residence', '5869a9ed-ebe5-3613-acc2-29c184737885', 'en', 'altLabel');
INSERT INTO "values" VALUES ('fb89bcae-3fcb-3336-97c3-cf6abd14e91f', 'P74 hat derzeitigen oder früheren Sitz', '5869a9ed-ebe5-3613-acc2-29c184737885', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('13e7defa-aba4-3cd2-ba92-8420be4bb53c', 'hat derzeitigen oder früheren Sitz', '5869a9ed-ebe5-3613-acc2-29c184737885', 'de', 'altLabel');
INSERT INTO "values" VALUES ('9753f691-62e2-3c8a-bc27-03f6674bc4d2', 'P74 έχει ή είχε κατοικία', '5869a9ed-ebe5-3613-acc2-29c184737885', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('fff4f4b4-2b61-3c89-af25-ce8dc3df33e1', 'έχει ή είχε κατοικία', '5869a9ed-ebe5-3613-acc2-29c184737885', 'el', 'altLabel');
INSERT INTO "values" VALUES ('5ffdcd02-1af6-39d0-b144-5e51f782e4aa', 'P74 réside ou a résidé à', '5869a9ed-ebe5-3613-acc2-29c184737885', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('6f8963c6-a558-3183-8486-e0dbbcccd731', 'réside ou a résidé à', '5869a9ed-ebe5-3613-acc2-29c184737885', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('cac6aa48-9b14-3ea3-8a5d-b603791bc93b', 'P74 reside ou residiu em', '5869a9ed-ebe5-3613-acc2-29c184737885', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('cdcc0dd0-185c-3caa-b6c7-2a49b3b5d3eb', 'reside ou residiu em', '5869a9ed-ebe5-3613-acc2-29c184737885', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('e56be3a8-d844-3ee6-8280-322317194401', 'P74 目前或曾经居住於', '5869a9ed-ebe5-3613-acc2-29c184737885', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('ab5a6b1d-6262-3e7f-9ad4-db221e9e3c77', '目前或曾经居住於', '5869a9ed-ebe5-3613-acc2-29c184737885', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('78c948f6-a21c-3ed2-8c96-f4a48403bf5c', 'This property describes the current or former E53 Place of residence of an E39 Actor. 
The residence may be either the Place where the Actor resides, or a legally registered address of any kind.
', '5869a9ed-ebe5-3613-acc2-29c184737885', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('3197e903-f5af-35ac-a88a-434602d52803', 'P75 владеет', '44813770-321a-370d-bb8f-ba619bcb4334', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('d794f42f-f990-3d56-8c28-c686de1eba94', 'владеет', '44813770-321a-370d-bb8f-ba619bcb4334', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('bc092be0-d52a-3049-858d-92bc732b6ac0', 'P75 κατέχει', '44813770-321a-370d-bb8f-ba619bcb4334', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('3d78ce0f-f848-3d34-8906-5c4ae71f358c', 'κατέχει', '44813770-321a-370d-bb8f-ba619bcb4334', 'el', 'altLabel');
INSERT INTO "values" VALUES ('14f43bc8-10e2-34a2-92dc-be8d44a5cf52', 'P75 besitzt', '44813770-321a-370d-bb8f-ba619bcb4334', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('463c52e6-d556-3ab4-9bae-07df8900b2b3', 'besitzt', '44813770-321a-370d-bb8f-ba619bcb4334', 'de', 'altLabel');
INSERT INTO "values" VALUES ('820301f0-5314-3b26-9f63-1a0dc1c15755', 'P75 est détenteur de', '44813770-321a-370d-bb8f-ba619bcb4334', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('dd9ac034-9f74-35aa-90e7-72e93f7f4059', 'est détenteur de', '44813770-321a-370d-bb8f-ba619bcb4334', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('22c85c2b-4c71-3f5a-b0b4-30919f3c8e85', 'P75 possesses', '44813770-321a-370d-bb8f-ba619bcb4334', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('624d0afd-c24a-3389-ae73-72597c4caf06', 'possesses', '44813770-321a-370d-bb8f-ba619bcb4334', 'en', 'altLabel');
INSERT INTO "values" VALUES ('16d6f4d3-b636-3b27-b039-72f49e747a1a', 'P75 é detentor de', '44813770-321a-370d-bb8f-ba619bcb4334', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('336cedc5-5ddb-3bf0-84b9-bf11ee36b3a7', 'é detentor de', '44813770-321a-370d-bb8f-ba619bcb4334', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('cab39f02-3b3d-3dc6-b8fc-b2f2b3e66369', 'P75 拥有', '44813770-321a-370d-bb8f-ba619bcb4334', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('42705d27-396a-3d9e-ba14-41993f609176', '拥有', '44813770-321a-370d-bb8f-ba619bcb4334', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('3bf4af73-3103-3915-85ac-75144ff09b84', 'This property identifies former or current instances of E30 Rights held by an E39 Actor.', '44813770-321a-370d-bb8f-ba619bcb4334', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('ccbbb3b8-9e79-3489-9d64-083d3202fe90', 'P76 has contact point', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('eb2a73c5-ea59-3939-9ffa-e354aa732e57', 'has contact point', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c6bd4438-a706-3f2e-9d33-265f66208e8b', 'P76 имеет контакт', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('eac28e58-b356-3653-925d-b9c57b1c2862', 'имеет контакт', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('6ab440de-d65c-384e-90b5-3c27f5a53568', 'P76 a pour coordonnées individuelles', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('7df38391-77c7-3d15-8f62-7e4c7b9d6aae', 'a pour coordonnées individuelles', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('26ea4f4d-d62f-33f2-a315-d1223fd3b5a6', 'P76 έχει σημείο επικοινωνίας', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('bbfc2598-c6fd-3cb0-ba22-66f2ee048c8b', 'έχει σημείο επικοινωνίας', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'el', 'altLabel');
INSERT INTO "values" VALUES ('bffc4fc7-d01a-3876-9ed8-b6a545865e45', 'P76 hat Kontaktpunkt', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('0a409404-bf2e-3139-8794-7642e4590322', 'hat Kontaktpunkt', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'de', 'altLabel');
INSERT INTO "values" VALUES ('cbd7eaa0-1f11-3f02-9ccd-4f6e21f773c1', 'P76 possui ponto de contato', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('00e380d7-fce6-3068-b5c6-71b79a8dd3d8', 'possui ponto de contato', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('2377a7fe-719f-3bc0-86fb-27c903c4d1dc', 'P76 有联系方式', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('1a7116ca-a9fb-30bd-8bdd-fb66219b05d6', '有联系方式', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('c5cc433c-0166-3e8e-be46-ae5fa183430f', 'This property identifies an E51 Contact Point of any type that provides access to an E39 Actor by any communication method, such as e-mail or fax.
', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('32232d2b-ddcc-3557-908d-f8b57bc79f8c', 'P78 αναγνωρίζεται ως', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('50faeab4-6de3-30ff-baa7-b2d6684cad2a', 'αναγνωρίζεται ως', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'el', 'altLabel');
INSERT INTO "values" VALUES ('bc31e96b-5988-3b84-abce-d99ea75cc807', 'P78 est identifiée par', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('9e5bf4d0-4006-3e09-bb14-c6df2d4c1309', 'est identifiée par', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('9856c568-7d4c-37a7-aca8-184294c39cf6', 'P78 is identified by', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('3c1de387-37ae-3d32-862e-54caea5cf0c2', 'is identified by', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'en', 'altLabel');
INSERT INTO "values" VALUES ('0c70b49d-f77c-36a5-9a1f-ea05f249d164', 'P78 идентифицируется посредством', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('a986414b-0eb9-3c53-a738-3dfe36bd4f27', 'идентифицируется посредством', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('1b9a1679-a9b8-330f-ab68-03bda8cf6719', 'P78 wird bezeichnet als', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('4f62d464-e96a-3fe1-a3cd-2335f5723f77', 'wird bezeichnet als', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'de', 'altLabel');
INSERT INTO "values" VALUES ('53f89927-158d-378e-a1a5-70de71a9529b', 'P78 é identificado por ', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('2a5fd7a4-4e82-3107-9aa3-934ddd6b39bb', 'é identificado por ', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('4adf84ea-b1b8-315e-8d7e-d252ec8da0ab', 'P78 有识别称号', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('7275404b-9adf-3b7b-9e5d-32e876cc91bd', '有识别称号', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('c2e6321d-a98f-3fe6-99a2-5859854fd1ba', 'This property identifies an E52 Time-Span using an E49Time Appellation.', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('9b44248e-d39f-3099-99eb-d8486b191566', 'P79 αρχή προσδιορίζεται από', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ef7126ce-8517-321b-a48d-650687ff492a', 'αρχή προσδιορίζεται από', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'el', 'altLabel');
INSERT INTO "values" VALUES ('a927345d-75c5-3e87-bd2d-946b60611230', 'P79 начало ограничено', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('ee074030-3a6b-32cc-8340-dc1da0aee9fc', 'начало ограничено', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('0715a99e-f89d-3475-89d1-a6180d040d58', 'P79 hat Anfangsbegründung', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('e43fc11a-05cc-39d7-891c-d477d91de27e', 'hat Anfangsbegründung', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'de', 'altLabel');
INSERT INTO "values" VALUES ('e6435462-956c-393b-b332-81f2f929a5ea', 'P79 beginning is qualified by', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('3e936c5d-8b9a-37f0-a6af-ea17422fe586', 'beginning is qualified by', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'en', 'altLabel');
INSERT INTO "values" VALUES ('02ebb2ce-6bf7-3a82-bf83-15444bab997f', 'P79 début est qualifié par', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5e40ef4d-ede0-3967-a0b4-a977accd86ca', 'début est qualifié par', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('d595f30f-1d8c-347d-a0bf-b05bb72682e0', 'P79 início é qualificado por', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('d48ec4e1-26bb-3190-827e-644225fec054', 'início é qualificado por', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('fa9f4573-42a2-35ad-9598-550019f05347', 'P79 起点认定的性质是', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('a0c99409-c497-3f51-8e59-5d8608fb2aa9', '起点认定的性质是', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('ae275574-460c-361f-9083-85a5441fcd83', 'had at most duration', '86caed02-d112-3cd7-8f21-4836e4997850', 'en', 'altLabel');
INSERT INTO "values" VALUES ('154068aa-6e28-3de2-b97b-c3717253a837', 'This property qualifies the beginning of an E52 Time-Span in some way. 
The nature of the qualification may be certainty, precision, source etc.
', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('3de347c4-ca1a-3b88-9564-b36f71c08d0f', 'P80 τέλος προσδιορίζεται από', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ba3d42ea-3eef-347b-842e-627aa85eff03', 'τέλος προσδιορίζεται από', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'el', 'altLabel');
INSERT INTO "values" VALUES ('1895b0b0-b3db-37e4-9eaa-aeceef4ee21f', 'P80 fin est qualifiée par', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('94209292-abd5-34b4-a01c-d86b0cc22fb7', 'fin est qualifiée par', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('f1a21abf-82bd-33de-a0e0-3666a0bb3328', 'P80 hat Begründung des Endes', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('c4b3be39-51e0-3110-8643-9b25b826b162', 'hat Begründung des Endes', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'de', 'altLabel');
INSERT INTO "values" VALUES ('aeaa24b9-6d5d-39ce-9ee3-9784952496e3', 'P80 конец ограничен', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('e2975aeb-e114-3039-9af9-de7c9616c21e', 'конец ограничен', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('76ca4314-a915-39a9-8e51-2ff2e1ccbf66', 'P80 end is qualified by', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('90f79bc0-4594-3c9a-a902-95804326fb02', 'end is qualified by', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'en', 'altLabel');
INSERT INTO "values" VALUES ('31e2369f-07a4-32a5-8e6e-7e2cf603e7e6', 'P80 final é qualificado por', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('31818538-0f53-3ce9-a5fa-0b1486cbcbf7', 'final é qualificado por', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('032d9381-40dd-3ae8-88a5-8e168af6628c', 'P80 终点认定的性质是', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('f33ea236-17ab-3bcd-a5eb-3d8e8bd69dea', '终点认定的性质是', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('973d8e50-3930-37b9-a62e-1fcbcd760f75', 'This property qualifies the end of an E52 Time-Span in some way. 
The nature of the qualification may be certainty, precision, source etc.
', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('a57ccfbc-b3e5-3a33-99bb-be273b6ef371', 'P81 ongoing throughout', '6a998971-7a85-3615-9929-d613fe90391c', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('008481c4-b032-35fb-8488-cd1926d8a9b9', 'ongoing throughout', '6a998971-7a85-3615-9929-d613fe90391c', 'en', 'altLabel');
INSERT INTO "values" VALUES ('f6950053-34b2-3a35-8021-35f02d6cf33d', 'P81 καθόλη τη διάρκεια του/της', '6a998971-7a85-3615-9929-d613fe90391c', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('012cbd09-ebc4-3de0-b52b-72c72b11cbaf', 'καθόλη τη διάρκεια του/της', '6a998971-7a85-3615-9929-d613fe90391c', 'el', 'altLabel');
INSERT INTO "values" VALUES ('e5441505-2528-30d8-982e-444aaa17e630', 'P81 andauernd während', '6a998971-7a85-3615-9929-d613fe90391c', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('df915c24-9635-3905-93ae-56adbc9085b9', 'andauernd während', '6a998971-7a85-3615-9929-d613fe90391c', 'de', 'altLabel');
INSERT INTO "values" VALUES ('3a49e878-eb29-3f7b-8694-f0bf82ff887d', 'P81 couvre au moins', '6a998971-7a85-3615-9929-d613fe90391c', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('e51979e9-afd8-31a2-b10f-d013bcc58dfe', 'couvre au moins', '6a998971-7a85-3615-9929-d613fe90391c', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('7922b242-ba7f-3f47-bd03-607c911e1f19', 'P81 длится в течение', '6a998971-7a85-3615-9929-d613fe90391c', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('9050aeba-b0b2-365c-8b08-2e3fa8445ddf', 'длится в течение', '6a998971-7a85-3615-9929-d613fe90391c', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('d2a385bb-b84b-30a1-aadc-ec437ab9196f', 'P81 abrange no mínimo', '6a998971-7a85-3615-9929-d613fe90391c', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('3caaa80d-0847-3a52-929c-90b08baa8b82', 'abrange no mínimo', '6a998971-7a85-3615-9929-d613fe90391c', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('6bf7aed2-aa75-3ca0-8dd5-517f0972529f', 'P81 时段的数值至少涵盖', '6a998971-7a85-3615-9929-d613fe90391c', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('6928f9a9-86f4-339e-8aa9-67e0398e5940', '时段的数值至少涵盖', '6a998971-7a85-3615-9929-d613fe90391c', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('deda015f-94b7-38dc-a524-465ade0ad772', 'This property describes the minimum period of time covered by an E52 Time-Span.
Since Time-Spans may not have precisely known temporal extents, the CRM supports statements about the minimum and maximum temporal extents of Time-Spans. This property allows a Time-Span’s minimum temporal extent (i.e. its inner boundary) to be assigned an E61 Time Primitive value. Time Primitives are treated by the CRM as application or system specific date intervals, and are not further analysed.
', '6a998971-7a85-3615-9929-d613fe90391c', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('89e47fb0-4e9d-3ed4-964d-34a72c2cab18', 'P82 κάποτε εντός', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('580f9ecc-d9af-3024-8f3b-97e27444e2c1', 'κάποτε εντός', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'el', 'altLabel');
INSERT INTO "values" VALUES ('282fedd8-3c23-3cc8-85b0-33de308a56b9', 'P82 некоторое время в течение', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('cf329c7a-0bd3-3766-a5ca-aaa53594fa12', 'некоторое время в течение', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('3c9826ce-375c-3171-8879-0a81fd146d6c', 'P82 irgendwann innerhalb von', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('bbb50ea6-9503-394a-9ae9-316369faea23', 'irgendwann innerhalb von', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'de', 'altLabel');
INSERT INTO "values" VALUES ('608f1466-a7bc-3c16-8090-ec83cd349306', 'P82 couvre au plus', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5098a957-0633-36c4-9157-34d8a6bece6f', 'couvre au plus', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('a7937815-f865-3980-8588-70075edfad90', 'P82 at some time within', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('0d2ebbcd-9091-368f-b2f2-cac5a6df3610', 'at some time within', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'en', 'altLabel');
INSERT INTO "values" VALUES ('50b5dcce-3f50-33b2-9726-56c94e35e538', 'P82 abrange no máximo', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('1dcfb2d7-451b-3826-94b3-43210d897d24', 'abrange no máximo', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('5ee9f7bc-d719-3920-9c35-f2fea38d76a0', 'P82 时段的数值不会超越', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('3fbad4d2-8c82-39de-881d-ef670531fa5f', '时段的数值不会超越', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('aa691ac1-9862-39d5-85d1-5e736785e5d1', 'This property describes the maximum period of time within which an E52 Time-Span falls.
Since Time-Spans may not have precisely known temporal extents, the CRM supports statements about the minimum and maximum temporal extents of Time-Spans. This property allows a Time-Span’s maximum temporal extent (i.e. its outer boundary) to be assigned an E61 Time Primitive value. Time Primitives are treated by the CRM as application or system specific date intervals, and are not further analysed.
', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('ec42ebab-b589-3900-976e-1702a67dd2be', 'P83 a duré au moins', 'b38666a2-59fd-3154-85c3-90edaa812979', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('f42c7340-456e-3829-b5a2-a055cdf6a97e', 'a duré au moins', 'b38666a2-59fd-3154-85c3-90edaa812979', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('58479224-f8b5-38b4-8b49-39e8739ab06f', 'P83 είχε ελάχιστη διάρκεια', 'b38666a2-59fd-3154-85c3-90edaa812979', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('57f93d07-01fe-3091-93cb-94bf8a0b2312', 'είχε ελάχιστη διάρκεια', 'b38666a2-59fd-3154-85c3-90edaa812979', 'el', 'altLabel');
INSERT INTO "values" VALUES ('4cf9f310-9818-3916-8bb8-94bf915136ec', 'P83 hatte Mindestdauer', 'b38666a2-59fd-3154-85c3-90edaa812979', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('8a0fddc1-bba6-3239-8d3b-1cc957414fda', 'hatte Mindestdauer', 'b38666a2-59fd-3154-85c3-90edaa812979', 'de', 'altLabel');
INSERT INTO "values" VALUES ('42d335a0-6600-386c-a7a4-ddef41fbd212', 'P83 had at least duration', 'b38666a2-59fd-3154-85c3-90edaa812979', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('03220f6f-cbbf-3a22-9679-f6e03f63ee94', 'had at least duration', 'b38666a2-59fd-3154-85c3-90edaa812979', 'en', 'altLabel');
INSERT INTO "values" VALUES ('7f08a23e-a15b-34a3-bb49-6b1d1f4c377e', 'P83 имеет длительность по крайней мере больше чем', 'b38666a2-59fd-3154-85c3-90edaa812979', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('bbf2752a-8e27-3c20-938c-44908b398f73', 'имеет длительность по крайней мере больше чем', 'b38666a2-59fd-3154-85c3-90edaa812979', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('2985286a-6972-3dc6-834f-96cdfeaaa84d', 'P83 durou no mínimo', 'b38666a2-59fd-3154-85c3-90edaa812979', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('a958f488-ed97-3131-af6d-9bed881775c2', 'durou no mínimo', 'b38666a2-59fd-3154-85c3-90edaa812979', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('c13662c6-ab02-3909-b5b6-ce20cd64310d', 'P83 时间最少持续了', 'b38666a2-59fd-3154-85c3-90edaa812979', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('403a3042-8bdc-3ebc-8dce-6a754a936b72', '时间最少持续了', 'b38666a2-59fd-3154-85c3-90edaa812979', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('44048ecc-83ac-3f85-acb9-33d3d352886d', 'This property describes the minimum length of time covered by an E52 Time-Span. 
It allows an E52 Time-Span to be associated with an E54 Dimension representing it’s minimum duration (i.e. it’s inner boundary) independent from the actual beginning and end.
', 'b38666a2-59fd-3154-85c3-90edaa812979', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('2f52e9dd-70a3-3e90-8857-88ca187a391c', 'P84 είχε μέγιστη διάρκεια', '86caed02-d112-3cd7-8f21-4836e4997850', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('279eba9c-a08a-3cbc-ac35-b44601b5383d', 'είχε μέγιστη διάρκεια', '86caed02-d112-3cd7-8f21-4836e4997850', 'el', 'altLabel');
INSERT INTO "values" VALUES ('0f264dd4-4d05-3c63-84ca-35a9a5ea413c', 'P84 hatte Höchstdauer', '86caed02-d112-3cd7-8f21-4836e4997850', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('e75121c0-ce52-34f1-8e68-d1dbb73f527f', 'hatte Höchstdauer', '86caed02-d112-3cd7-8f21-4836e4997850', 'de', 'altLabel');
INSERT INTO "values" VALUES ('a63e04df-9364-31b5-812e-977143112703', 'P84 имеет длительность меньше чем', '86caed02-d112-3cd7-8f21-4836e4997850', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('ce830dc0-b5f8-38f5-91ff-741110f6bccf', 'имеет длительность меньше чем', '86caed02-d112-3cd7-8f21-4836e4997850', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('fed7da3e-1727-3b39-b726-a5181838b803', 'P84 a duré au plus', '86caed02-d112-3cd7-8f21-4836e4997850', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('2cbb0dcf-d8f5-36c8-88d4-bdea15935f3d', 'a duré au plus', '86caed02-d112-3cd7-8f21-4836e4997850', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('5cc489fa-f4c4-3256-a985-45ede5687d26', 'P84 durou no máximo', '86caed02-d112-3cd7-8f21-4836e4997850', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('0c82b986-ce4e-3ad3-ad66-e42e60819304', 'durou no máximo', '86caed02-d112-3cd7-8f21-4836e4997850', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('04a73b2b-e24c-3670-bc0c-8ba72d4bcbc2', 'P84 时间最多持续了', '86caed02-d112-3cd7-8f21-4836e4997850', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('6296a87e-5b65-3f3b-b45c-67da016fccab', '时间最多持续了', '86caed02-d112-3cd7-8f21-4836e4997850', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('cda3e89c-1f1a-39a8-aecd-d4103b78418f', 'This property describes the maximum length of time covered by an E52 Time-Span. 
It allows an E52 Time-Span to be associated with an E54 Dimension representing it’s maximum duration (i.e. it’s outer boundary) independent from the actual beginning and end.
', '86caed02-d112-3cd7-8f21-4836e4997850', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('96db18a9-05b0-3124-9de8-0e0e61fefc6d', 'P86 falls within', '014fefdb-ddad-368b-b69c-951a0763824d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('62088079-bb5a-3ff4-b23b-1c532a6edb06', 'falls within', '014fefdb-ddad-368b-b69c-951a0763824d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('e5a7602f-93b6-3a89-b305-0d26947aab41', 'P86 содержится в', '014fefdb-ddad-368b-b69c-951a0763824d', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('7c94573f-30e0-388f-a025-03f4edac74ec', 'содержится в', '014fefdb-ddad-368b-b69c-951a0763824d', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('b454f58d-cda2-3d2c-92cd-c3de1f127c90', 'P86 περιέχεται σε', '014fefdb-ddad-368b-b69c-951a0763824d', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ffef5a84-616d-327b-8a66-0eb084b54f4c', 'περιέχεται σε', '014fefdb-ddad-368b-b69c-951a0763824d', 'el', 'altLabel');
INSERT INTO "values" VALUES ('ba568b74-e55d-369b-9f5f-d9b573326ac9', 'P86 s’insère dans', '014fefdb-ddad-368b-b69c-951a0763824d', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('8cd244b6-c785-390a-a9a7-8726d6a95136', 's’insère dans', '014fefdb-ddad-368b-b69c-951a0763824d', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('7aa20a47-2cf2-31fa-9c60-168049244443', 'P86 fällt in', '014fefdb-ddad-368b-b69c-951a0763824d', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('93c4eb20-f845-37cb-af02-6c2f3d98c6f2', 'fällt in', '014fefdb-ddad-368b-b69c-951a0763824d', 'de', 'altLabel');
INSERT INTO "values" VALUES ('676b85b7-8a66-3a1d-a535-eca3cb06ad79', 'P86 está contido em', '014fefdb-ddad-368b-b69c-951a0763824d', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('353fbffe-6ca3-3663-9ddd-189a47b2ac1e', 'está contido em', '014fefdb-ddad-368b-b69c-951a0763824d', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('2b3f9cb9-3dde-3bfb-a7d4-b93088fc7888', 'P86 时间上被涵盖於', '014fefdb-ddad-368b-b69c-951a0763824d', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('9c7f5bbb-5582-39e3-9e55-c2b4f91d1ba9', '时间上被涵盖於', '014fefdb-ddad-368b-b69c-951a0763824d', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('114289f9-5aef-394b-be10-f6c66bf73369', 'This property describes the inclusion relationship between two instances of E52 Time-Span.
This property supports the notion that a Time-Span’s temporal extent falls within the temporal extent of another Time-Span. It addresses temporal containment only, and no contextual link between the two instances of Time-Span is implied.
', '014fefdb-ddad-368b-b69c-951a0763824d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('bc4133b2-c598-3b3d-94c6-63fd21d896f7', 'P87 αναγνωρίζεται ως', '697dc6cc-0da6-301c-9703-78edbf812fac', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('b73cf29b-4434-3595-b16c-91f28403ef62', 'αναγνωρίζεται ως', '697dc6cc-0da6-301c-9703-78edbf812fac', 'el', 'altLabel');
INSERT INTO "values" VALUES ('3b5b9ddc-2f75-35f1-85fe-80175d0cf2a2', 'P87 is identified by', '697dc6cc-0da6-301c-9703-78edbf812fac', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('480c272a-84f7-372e-8e94-1c49762d6353', 'is identified by', '697dc6cc-0da6-301c-9703-78edbf812fac', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c1792d76-630a-38d0-8030-9ac35404ca7c', 'P87 идентифицируется посредством', '697dc6cc-0da6-301c-9703-78edbf812fac', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('a9a1cbea-25b8-3655-adfb-3cc130b8b209', 'идентифицируется посредством', '697dc6cc-0da6-301c-9703-78edbf812fac', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('c0d90d7c-23ae-32f5-bda4-c3a00ec8114c', 'P87 est identifié par', '697dc6cc-0da6-301c-9703-78edbf812fac', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('965741f1-5fd7-33d4-9e99-7c4010b616a5', 'est identifié par', '697dc6cc-0da6-301c-9703-78edbf812fac', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('bd7263e6-aa29-35a5-8fba-5be880f0c4a8', 'P87 wird bezeichnet als', '697dc6cc-0da6-301c-9703-78edbf812fac', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('34e9497c-9ae8-3fc2-ac82-3afe2d68adff', 'wird bezeichnet als', '697dc6cc-0da6-301c-9703-78edbf812fac', 'de', 'altLabel');
INSERT INTO "values" VALUES ('ba147576-2d44-347d-acbf-feadbcc655b1', 'P87 é identificado por', '697dc6cc-0da6-301c-9703-78edbf812fac', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('c53ad82f-e876-3558-a9bf-64711c339faf', 'é identificado por', '697dc6cc-0da6-301c-9703-78edbf812fac', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('113c172a-1201-33d9-a3d1-c5d1a47ad172', 'P87 有辨认码', '697dc6cc-0da6-301c-9703-78edbf812fac', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('8f0aea04-2f85-3397-b18f-bbc58b9403de', '有辨认码', '697dc6cc-0da6-301c-9703-78edbf812fac', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('35574042-f04a-3c08-8a63-7145df896176', 'This property identifies an E53 Place using an E44 Place Appellation. 
Examples of Place Appellations used to identify Places include instances of E48 Place Name, addresses, E47 Spatial Coordinates etc.
', '697dc6cc-0da6-301c-9703-78edbf812fac', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('eed691b0-6e75-3b95-a9c6-f0a9670f976e', 'P89 s’insère dans', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('6bea8594-c0e5-382e-a433-31caee285cda', 's’insère dans', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('1edd8956-0e60-34af-92ca-6c406921e2f5', 'P89 falls within', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('d74d1892-e17b-3199-acac-7f5bf307483e', 'falls within', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'en', 'altLabel');
INSERT INTO "values" VALUES ('3f4013cd-1d99-3f6f-a96c-14d6272c0a5d', 'P89 содержится в', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('ddff2183-c999-3917-bc00-fb9fd272bdf9', 'содержится в', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('3c784be7-e41c-320f-9bf5-a2baa25c1044', 'P89 fällt in', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('d293e422-e93a-3b14-84f9-818e7315b9f3', 'fällt in', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'de', 'altLabel');
INSERT INTO "values" VALUES ('59f82f0c-4cef-3a06-b338-22cc4107b4b1', 'P89 περιέχεται σε', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('6cd5285f-46a9-37b3-9944-fab7e87c9129', 'περιέχεται σε', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'el', 'altLabel');
INSERT INTO "values" VALUES ('09b763fd-b2c6-3323-bcb8-24c44ff9febe', 'P89 está contido em', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('12632439-cebc-3f7b-bb2a-392c80cddab9', 'está contido em', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('1693dbc3-515c-3f2a-a791-0bb0fff65c49', 'P89 空间上被包围於', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('c442b1d2-ec15-3ee1-a81b-d0b1dd45c173', '空间上被包围於', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('53d573c6-c553-3cb4-8999-a34c0918fff6', 'This property identifies an instance of E53 Place that falls wholly within the extent of another E53 Place.
It addresses spatial containment only, and does not imply any relationship between things or phenomena occupying these places.
', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('e548873f-11c2-3472-a4c5-adf2d242d360', 'P90 hat Wert', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('307d333c-417a-3473-abae-99219bf35e41', 'hat Wert', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'de', 'altLabel');
INSERT INTO "values" VALUES ('04fd225a-3112-3e98-b78a-d7a053f23c78', 'P90 έχει τιμή', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('21af9372-8625-3978-8bfb-1476f6a78009', 'έχει τιμή', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'el', 'altLabel');
INSERT INTO "values" VALUES ('63aef5d9-f595-3b94-9930-a41a42393311', 'P90 a la valeur', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('720e7541-01ca-343e-9ef8-c9be5ae554fb', 'a la valeur', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('7031d83f-7117-3c85-95a9-1734b158af1d', 'P90 имеет значение', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('468f464a-c740-3aef-a8a6-84871f04890d', 'имеет значение', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('104f328f-c1a9-38ca-aa2e-2f7e12303b16', 'P90 has value', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('35b01a72-4fc6-356d-88fc-590cd9c6e199', 'has value', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'en', 'altLabel');
INSERT INTO "values" VALUES ('4c62faf7-e82e-3294-81bc-4dc664911275', 'P90 tem valor', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('ed45ec18-72f7-3927-83ea-4e524afab789', 'tem valor', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('c01f31b9-a0b4-3d08-91c6-caeeb2dda85b', 'P90 有数值', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('811b1efb-f637-3742-bead-55d33b8d70cb', '有数值', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('799514b4-0298-3fb6-b9a8-cb3407a637b4', 'This property allows an E54 Dimension to be approximated by an E60 Number primitive.', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('ffe9aab0-770e-3794-9462-23883a3395f8', 'P91 имеет единицу', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('02a1adea-6c61-3ae0-8298-853ff7ecc963', 'имеет единицу', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('45bb42e7-4d86-3b14-a3d9-3052222b272b', 'P91 έχει μονάδα μέτρησης', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('2c57a924-19f4-3b6e-9f48-7a904a91aebe', 'έχει μονάδα μέτρησης', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'el', 'altLabel');
INSERT INTO "values" VALUES ('8dc4320f-7cf8-3a68-b3fe-893ee230453c', 'P91 a pour unité', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('9a932051-815b-37f9-ba44-f04ce7482bf7', 'a pour unité', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('1d406111-e647-3fb1-9ca6-ef3e12b29880', 'P91 hat Einheit', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('4fbdb83e-43a7-3c4d-b0c8-a86af5c133ac', 'hat Einheit', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'de', 'altLabel');
INSERT INTO "values" VALUES ('64bd370d-fde0-3983-8ab8-ce0ca4d398bc', 'P91 has unit', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('fa47a931-fc45-3a11-8f6e-8a748c16ab6f', 'has unit', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'en', 'altLabel');
INSERT INTO "values" VALUES ('fa31062a-5391-3f87-a5e2-4a9f4a301d5d', 'P91 tem unidade', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('0d52695a-9cf2-3728-8153-73b4d54d940e', 'tem unidade', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('7b45ed58-fd81-30e7-be15-dd98914ea6af', 'P91 有单位', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('74e021e3-63b4-303f-9861-5b1e9e8b57f1', '有单位', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('539998fd-3594-38d3-a07f-1f95406f9009', 'This property shows the type of unit an E54 Dimension was expressed in.', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('ccfe2797-112d-32f5-bc16-d0c5432e81bf', 'P92 a fait exister', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('82170e31-f50a-373e-82e9-b3b77d0290de', 'a fait exister', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('03f333c1-c846-329a-838c-4a14c989f421', 'P92 brought into existence', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('49500260-fc9f-38be-8ec7-2180774f6ad7', 'brought into existence', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'en', 'altLabel');
INSERT INTO "values" VALUES ('dd16375d-b7ef-3e1a-b0c3-de56d9076cfc', 'P92 создал', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('c430b4c9-1f65-3a15-a8c7-26948b5c8fe1', 'создал', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('fb64e194-4446-3060-9f4a-38fb8594112f', 'P92 brachte in Existenz', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('c1097743-f296-380e-a47e-4ae9e676693d', 'brachte in Existenz', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'de', 'altLabel');
INSERT INTO "values" VALUES ('3b51a0d5-832d-31fb-8f55-cbb135a59260', 'P92 γέννησε', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('b871ef3a-dea7-31f2-856d-c2d1d502c7c2', 'γέννησε', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'el', 'altLabel');
INSERT INTO "values" VALUES ('d08944cb-503d-3ba1-8a39-b2b341c8c9c0', 'P92 trouxe à existência', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('615e1455-00e2-350c-83ba-57876f287471', 'trouxe à existência', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('6e98ca00-7fe1-3c07-af76-24c47034f0b9', 'P92 开始了', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('8c45b18f-ec07-37a0-be18-79c8f05d81b1', '开始了', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('aa85b241-aa33-31cf-b376-f136f5f85f14', 'This property allows an E63 Beginning of Existence event to be linked to the E77 Persistent Item brought into existence by it.
It allows a “start” to be attached to any Persistent Item being documented i.e. E70 Thing, E72 Legal Object, E39 Actor, E41 Appellation, E51 Contact Point and E55 Type', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('335bf55c-c8e9-3161-b3ff-7f9d6d9b7f6d', 'P93 a fait cesser d’exister', 'f865c72a-09dd-386f-a9eb-385176727d94', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5106b289-dbb0-3d60-8b48-d6da4cc78b10', 'a fait cesser d’exister', 'f865c72a-09dd-386f-a9eb-385176727d94', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('d44963b4-8def-3d5d-bfa9-be818380e26b', 'P93 положил конец существованию', 'f865c72a-09dd-386f-a9eb-385176727d94', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('f33aacd6-0376-3899-9e44-203618297c7a', 'положил конец существованию', 'f865c72a-09dd-386f-a9eb-385176727d94', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('456ba154-1c2b-345b-93f3-2457f26e549c', 'P93 beendete die Existenz von', 'f865c72a-09dd-386f-a9eb-385176727d94', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('68628425-99a8-3ac8-8f74-cd23c829f971', 'beendete die Existenz von', 'f865c72a-09dd-386f-a9eb-385176727d94', 'de', 'altLabel');
INSERT INTO "values" VALUES ('019760c5-6a8f-3a21-8f03-68c0b50e298e', 'P93 took out of existence', 'f865c72a-09dd-386f-a9eb-385176727d94', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('9dc3d5f7-a89e-3852-a7ed-169e1e3721bc', 'took out of existence', 'f865c72a-09dd-386f-a9eb-385176727d94', 'en', 'altLabel');
INSERT INTO "values" VALUES ('2f2e7962-b5e8-36a1-84bb-67331cdea36e', 'P93 αναίρεσε', 'f865c72a-09dd-386f-a9eb-385176727d94', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('58b80754-0838-3e17-aecb-9cf10896080e', 'αναίρεσε', 'f865c72a-09dd-386f-a9eb-385176727d94', 'el', 'altLabel');
INSERT INTO "values" VALUES ('76754bf4-7929-3511-8427-743a6e8f1b7f', 'P93 cessou a existência de', 'f865c72a-09dd-386f-a9eb-385176727d94', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('67fd3383-57fa-3c93-b4a2-ec9bb60bc7ce', 'cessou a existência de', 'f865c72a-09dd-386f-a9eb-385176727d94', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('9f6f79d8-db72-3d53-8640-418e7c3e58c1', 'P93 结束了', 'f865c72a-09dd-386f-a9eb-385176727d94', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('be387466-3398-3ee5-8479-516a16c150ed', '结束了', 'f865c72a-09dd-386f-a9eb-385176727d94', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('4d8b767f-cbaa-328d-bfa1-3e33fc9d12ff', 'This property allows an E64 End of Existence event to be linked to the E77 Persistent Item taken out of existence by it.
In the case of immaterial things, the E64 End of Existence is considered to take place with the destruction of the last physical carrier.
This allows an “end” to be attached to any Persistent Item being documented i.e. E70 Thing, E72 Legal Object, E39 Actor, E41 Appellation, E51 Contact Point and E55 Type. For many Persistent Items we know the maximum life-span and can infer, that they must have ended to exist. We assume in that case an End of Existence, which may be as unnoticeable as forgetting the secret knowledge by the last representative of some indigenous nation.
', 'f865c72a-09dd-386f-a9eb-385176727d94', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('46f44dd4-0fff-31c0-bed3-f7dc4b3047e4', 'P94 δημιούργησε', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('20da3da4-fbdc-3702-9335-5ef9261df7a1', 'δημιούργησε', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'el', 'altLabel');
INSERT INTO "values" VALUES ('4d23b6e0-37f0-33c8-9b4e-48ee3648551e', 'P94 создал', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('24018de7-c369-3134-bce3-f3e9dd6f21be', 'создал', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('a332b469-ba2b-38f0-81e3-1dd452ca4bda', 'P94 has created', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('aa5a7b47-7c7c-3a90-9df0-ba7012e0a54d', 'has created', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'en', 'altLabel');
INSERT INTO "values" VALUES ('d18565ce-6e68-338e-80bd-8a5217c038b9', 'P94 hat erschaffen', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('22036263-aaa2-384d-a42b-2d118d4cdaf2', 'hat erschaffen', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'de', 'altLabel');
INSERT INTO "values" VALUES ('7fc2d24f-4ca8-3f77-943b-107800684f23', 'P94 a créé', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('4673bca6-7934-3f97-86bf-1fa722da9d72', 'a créé', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('1d4af2b5-3fc3-3127-9ad1-1054c0ad139a', 'P94 criou', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('1e41d056-7350-3d32-92be-ee18bd9a3f40', 'criou', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('50b4a202-650b-35f5-b867-eca99d8fb495', 'P94 创造了', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('dbdc46c0-c794-30f4-84ec-c9454fe5588a', '创造了', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('267be108-8527-3051-bcaf-f2683683851e', 'This property allows a conceptual E65 Creation to be linked to the E28 Conceptual Object created by it. 
It represents the act of conceiving the intellectual content of the E28 Conceptual Object. It does not represent the act of creating the first physical carrier of the E28 Conceptual Object. As an example, this is the composition of a poem, not its commitment to paper.
', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('699bcb75-8f6d-3e96-ad16-d94b1d5e4dbe', 'P95 a fondé', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('a73ca5a4-0da1-3712-ac24-be4670a2b18f', 'a fondé', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('44b97cef-b60f-3e76-9119-28b7310ada88', 'P95 сформировал', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('fbb6a724-6d04-3c4c-b441-e82f2a76d6d0', 'сформировал', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('7258deee-3234-3b13-a49f-456c213b45b4', 'P95 hat gebildet', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('621d3c2e-54cf-398b-9ece-bdba347cbc74', 'hat gebildet', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'de', 'altLabel');
INSERT INTO "values" VALUES ('3d3bf99c-a585-3f47-beac-a339049a7adb', 'P95 has formed', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('a7cc0f01-f8b5-3f1d-8015-99793666d84c', 'has formed', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'en', 'altLabel');
INSERT INTO "values" VALUES ('efd58c82-aeb9-3e7e-af05-c2bd428efdfc', 'P95 σχημάτισε', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('adefee2a-21e5-3780-a68a-7cf1e359a63b', 'σχημάτισε', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'el', 'altLabel');
INSERT INTO "values" VALUES ('9103a868-40a6-31bd-b57c-7e1696e51e37', 'P95 formou', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('95aca1c9-3fd3-37a2-b6ff-72238c718d51', 'formou', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('ee9207b9-3568-3ee1-a9c8-0168c96b4493', 'P95 组成了', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('4d25a736-a5b0-3add-ba01-ef1602714fda', '组成了', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('6f87a62a-3312-36d0-b404-30d437126fc9', 'This property links the founding or E66 Formation for an E74 Group with the Group itself.', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('9cbb2fd3-f9cf-3503-bed3-03e8e9104081', 'P96 посредством матери', '9e806e49-e728-32cf-821e-504ca9916afc', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('8f167019-0927-3943-b521-062ac6e4e9d8', 'посредством матери', '9e806e49-e728-32cf-821e-504ca9916afc', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('392cf877-015e-362d-a1e0-256f414e13ae', 'P96 durch Mutter', '9e806e49-e728-32cf-821e-504ca9916afc', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('1c74f7b9-0ea9-3eb0-86e4-e17c22b12802', 'durch Mutter', '9e806e49-e728-32cf-821e-504ca9916afc', 'de', 'altLabel');
INSERT INTO "values" VALUES ('f32b813b-16d1-30e8-aa05-edb6dc8e0729', 'P96 de mère', '9e806e49-e728-32cf-821e-504ca9916afc', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('36d5af41-b0f4-33d3-a84d-94fc6a06a4d1', 'de mère', '9e806e49-e728-32cf-821e-504ca9916afc', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('046b9a25-9ed1-3c8b-91e7-97cab0e0951d', 'P96 by mother', '9e806e49-e728-32cf-821e-504ca9916afc', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('7d468e90-ffea-3809-92a7-f4d2dddc1afd', 'by mother', '9e806e49-e728-32cf-821e-504ca9916afc', 'en', 'altLabel');
INSERT INTO "values" VALUES ('d519badd-d4a8-312b-a276-299a8f003510', 'P96 είχε μητέρα', '9e806e49-e728-32cf-821e-504ca9916afc', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('063cd0d4-af57-3d9c-b30f-b945bc83f1c8', 'είχε μητέρα', '9e806e49-e728-32cf-821e-504ca9916afc', 'el', 'altLabel');
INSERT INTO "values" VALUES ('2ddc195b-1a1d-3f62-8d86-cd1f9b4c6200', 'P96 pela mãe', '9e806e49-e728-32cf-821e-504ca9916afc', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('d6f52e9f-f839-3084-87cd-855dcf40841d', 'pela mãe', '9e806e49-e728-32cf-821e-504ca9916afc', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('56d07805-eb0f-3ea7-a05b-b75c3b6aa630', 'P96 来自生母', '9e806e49-e728-32cf-821e-504ca9916afc', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('1c5c3b26-57a4-3297-9165-99daf7285629', '来自生母', '9e806e49-e728-32cf-821e-504ca9916afc', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('5502a5c7-d43d-32f2-b0bb-e7ab80691eb5', 'This property links an E67 Birth event to an E21 Person as a participant in the role of birth-giving mother.

Note that biological fathers are not necessarily participants in the Birth (see P97 from father (was father for)). The Person being born is linked to the Birth with the property P98 brought into life (was born). This is not intended for use with general natural history material, only people. There is no explicit method for modelling conception and gestation except by using extensions. This is a sub-property of P11 had participant (participated in).
', '9e806e49-e728-32cf-821e-504ca9916afc', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('79ed041d-d48b-3210-843d-55470756077a', 'P97 gab Vaterschaft', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('22206a12-3035-3fa0-ac26-14656718faab', 'gab Vaterschaft', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'de', 'altLabel');
INSERT INTO "values" VALUES ('8e854b64-84e2-3533-8848-f99280fe0d61', 'P97 от отца', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('d5b588a1-a0b9-3aaa-9a01-b70c2c5f6869', 'от отца', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('484cf402-51ca-3ba3-aee3-63a3037f79a5', 'P97 from father', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('1b836750-db76-31d7-be99-7233a2de9211', 'from father', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'en', 'altLabel');
INSERT INTO "values" VALUES ('62569694-c931-309e-ba82-3e0b5feae0b2', 'P97 είχε πατέρα', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('e5b0e2c3-72f1-37a7-a4b7-3d21988cc05e', 'είχε πατέρα', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'el', 'altLabel');
INSERT INTO "values" VALUES ('f12518c2-85b1-379f-80bb-a54ef7d2e109', 'P97 de père', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('558e4bf6-b86c-3ea4-82f0-f9ba72335363', 'de père', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('5eb8083e-4e82-3b7d-b74d-e0ea17a4fd8d', 'P97 pelo pai', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('b6fc9ef5-1155-3ce2-afe9-88af34c4b6c2', 'pelo pai', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('7aab5549-7cc9-3c08-a812-44ff483d3d2d', 'P97 来自父亲', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('4f441be0-f057-3cb4-b95f-8c1020d55205', '来自父亲', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('5ca58d11-386f-3e52-8519-7ca4c773f4cf', 'This property links an E67 Birth event to an E21 Person in the role of biological father.
Note that biological fathers are not seen as necessary participants in the Birth, whereas birth-giving mothers are (see P96 by mother (gave birth)). The Person being born is linked to the Birth with the property P98 brought into life (was born).
This is not intended for use with general natural history material, only people. There is no explicit method for modelling conception and gestation except by using extensions. 
A Birth event is normally (but not always) associated with one biological father.
', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('f323bdac-0612-3ca6-8d0f-b649c7021b2c', 'P98 a donné vie à', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('e2e947f4-61ba-3659-a6ba-97387093c851', 'a donné vie à', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('c6f820c4-82f8-3c13-82b2-50a6d24830c7', 'P98 brachte zur Welt', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('3ad90bf5-929d-32e3-8094-7bbda8585380', 'brachte zur Welt', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'de', 'altLabel');
INSERT INTO "values" VALUES ('258240df-8466-364f-a1bd-606ffb84ee70', 'P98 brought into life', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('deec387a-7c7f-3b09-abcd-a4a043488a14', 'brought into life', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'en', 'altLabel');
INSERT INTO "values" VALUES ('a5e35d65-c718-3508-8710-8f23dbdd74b4', 'P98 породил', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('57d573f7-d2b6-38cf-81c2-cee5a99b8097', 'породил', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('560344c3-e082-394e-a7c1-eaa22876503d', 'P98 έφερε στη ζωή', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('c9302d07-83ee-30b9-82be-14d11fecac7b', 'έφερε στη ζωή', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'el', 'altLabel');
INSERT INTO "values" VALUES ('194e5833-2b90-35ab-8a55-512e867bbfeb', 'P98 trouxe à vida', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('b714d860-74f2-3ac8-9bd5-837af9c37e7b', 'trouxe à vida', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('80ce0f37-eb64-3a8c-a9d7-b26cdba939fa', 'P98 诞生了', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('53d13abe-d52c-38c2-82e8-d464b56f1d63', '诞生了', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('ee18575d-e8e6-3168-ba7f-2787e1a94f29', 'This property links an E67Birth event to an E21 Person in the role of offspring.
Twins, triplets etc. are brought into life by the same Birth event. This is not intended for use with general Natural History material, only people. There is no explicit method for modelling conception and gestation except by using extensions.
', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('5e0c2135-acc7-3d23-b8e2-860f965a64e2', 'P99 διέλυσε', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('894b1463-b302-3533-bcb1-e816ab26672f', 'διέλυσε', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'el', 'altLabel');
INSERT INTO "values" VALUES ('d062381d-990f-3fab-99f7-20ccbff818aa', 'P99 распустил', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('b72ff50c-8a79-35ef-b91a-13df1e618579', 'распустил', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('2315f5ef-eab3-3075-9538-d91a374b6ea1', 'P99 a dissous', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('94e36fe4-974d-34f0-a702-c1dc0e07cf49', 'a dissous', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('183950a6-4371-392e-ae8d-68c1e7828879', 'P99 dissolved', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('e9c7787e-ffbc-3ae3-897a-3028af4eacc4', 'dissolved', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'en', 'altLabel');
INSERT INTO "values" VALUES ('0540998f-ffa1-3440-b11b-51a3425532af', 'P99 löste auf', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('469ebe10-b244-3868-8a27-fd245e8986b0', 'löste auf', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'de', 'altLabel');
INSERT INTO "values" VALUES ('99d27d42-165b-35ce-854c-26a03e3573cb', 'P99 dissolveu', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('72441abb-5b9a-3e99-ae79-6d446a548272', 'dissolveu', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('1eb32448-5825-36a4-b50e-38bd162b7ce2', 'P99 解散了', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('87d15be7-b9f2-365d-8a10-24a079795b53', '解散了', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('57b0f50f-c44f-3b6f-bcbd-b5639ab6d4b9', 'This property links the disbanding or E68 Dissolution of an E74 Group to the Group itself.', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('b3cecc5f-0472-3e6f-9c5e-7d3fc8c70e49', 'P100 was death of', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('c9383a32-ec43-35d0-bada-bd084bd33b0f', 'was death of', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'en', 'altLabel');
INSERT INTO "values" VALUES ('5c14acbb-009f-34f1-9924-016a9b4956af', 'P100 a été la mort de', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('0e992c54-1621-3ddf-b850-f0d726d97514', 'a été la mort de', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('f18e40e7-532f-3e26-b958-75e33e135f03', 'P100 ήταν θάνατος του/της', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('3aad5b92-db8e-3c16-9f40-f93c93c8cf18', 'ήταν θάνατος του/της', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'el', 'altLabel');
INSERT INTO "values" VALUES ('aad026f4-ba79-3c16-9876-88bb847ef4dd', 'P100 Tod von', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('b41994e8-c353-3a09-94b1-49a0304f45d8', 'Tod von', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'de', 'altLabel');
INSERT INTO "values" VALUES ('d5d0505b-142a-3da9-b604-c966bbcd93fe', 'P100 был смертью для', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('0cb682f6-319a-30cb-af0f-efb904d9ea5e', 'был смертью для', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('b14645fd-0db0-3b57-8013-278e44ff7206', 'P100 foi a morte para ', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('67a7dad9-9215-3ec7-8797-173f01451b5b', 'foi a morte para ', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('927503a7-c6d9-31ef-8453-3ab1aeeb703c', 'P100 灭亡了', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('13fab27e-26c4-3f32-8e4c-5ea216a6ed8d', '灭亡了', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('fc8d071f-6dc4-31a6-afc9-7537fe29f2cd', 'This property property links an E69 Death event to the E21 Person that died.', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('db2dee54-c0b6-39f7-b091-1a33cae6161c', 'P101 had as general use', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('db034df6-7877-332b-b1e0-dc6fb49c8b60', 'had as general use', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'en', 'altLabel');
INSERT INTO "values" VALUES ('8e250c6a-7b54-3a94-932a-8d9841c2060f', 'P101 avait comme utilisation générale', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('735fafe0-d96b-355e-99c3-de4854b7c5e6', 'avait comme utilisation générale', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('2907ea24-4ec3-3517-88aa-c25573fe62b6', 'P101 είχε ως γενική χρήση', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('617fceb3-a73e-3d73-8204-b70ba2f66eea', 'είχε ως γενική χρήση', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'el', 'altLabel');
INSERT INTO "values" VALUES ('2f0e5817-0c8a-335b-9f9c-a51d8def6259', 'P101 hatte die allgemeine Verwendung', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('47f6ad29-b22c-3eb8-ad38-07fea8a80bbe', 'hatte die allgemeine Verwendung', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'de', 'altLabel');
INSERT INTO "values" VALUES ('a7121690-d57c-329d-b893-f4bc8a2e7559', 'P101 имел основное применение', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('d0d9bd6b-02e4-36ef-8abd-9c5a22a650ca', 'имел основное применение', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('50a8155a-1532-3e56-ba61-d86dc0aed503', 'P101 tem como uso geral', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('678b43a2-f61e-3369-9bcb-aa6c946a7f06', 'tem como uso geral', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('096cbcd0-944c-3464-94a6-28b3f515286a', 'P101 被惯用於', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('0081d711-6f4d-3a6e-92f0-a8265bc7da9b', '被惯用於', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('84506975-fb19-3786-85be-e91aa63a5399', 'This property links an instance of E70 Thing to an E55 Type of usage.
It allows the relationship between particular things, both physical and immaterial, and general methods and techniques of use to be documented. Thus it can be asserted that a baseball bat had a general use for sport and a specific use for threatening people during the Great Train Robbery.
', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('8d284ba3-c0b1-3794-8297-d51b4f53e137', 'P102 has title', '8c69765e-7827-371f-9db3-fea290f87739', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('37e55bdc-e3d5-39d6-a1c5-dc09e0da2987', 'has title', '8c69765e-7827-371f-9db3-fea290f87739', 'en', 'altLabel');
INSERT INTO "values" VALUES ('b6426bea-0b75-3d88-a6e6-823ad8455894', 'P102 имеет заголовок', '8c69765e-7827-371f-9db3-fea290f87739', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('71635a2a-3b32-3077-96eb-6b22f965c43a', 'имеет заголовок', '8c69765e-7827-371f-9db3-fea290f87739', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('d7f92c34-6d59-3097-bf32-f60f75dc668a', 'P102 trägt den Titel', '8c69765e-7827-371f-9db3-fea290f87739', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('3ef83485-5320-38da-a686-24366c501376', 'trägt den Titel', '8c69765e-7827-371f-9db3-fea290f87739', 'de', 'altLabel');
INSERT INTO "values" VALUES ('43336f8a-b88a-3484-af84-1c7e594b719a', 'P102 a pour titre', '8c69765e-7827-371f-9db3-fea290f87739', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('e3805fe4-3663-3ce3-abbe-9fcf7d24b5f9', 'a pour titre', '8c69765e-7827-371f-9db3-fea290f87739', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('66fcb547-1353-32cc-a391-9949745a697e', 'P102 έχει τίτλο', '8c69765e-7827-371f-9db3-fea290f87739', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('179d1798-253b-3d2c-b85c-96c38de50fb7', 'έχει τίτλο', '8c69765e-7827-371f-9db3-fea290f87739', 'el', 'altLabel');
INSERT INTO "values" VALUES ('e6b2b7de-c75f-3258-b93c-d5e381d00e38', 'P102 tem título', '8c69765e-7827-371f-9db3-fea290f87739', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('59c5e89e-3efc-37a9-8cd3-61fae330181c', 'tem título', '8c69765e-7827-371f-9db3-fea290f87739', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('863f10f6-3b2b-3896-b981-b5fd8137cd3b', 'P102 有标题', '8c69765e-7827-371f-9db3-fea290f87739', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('d7f9c3e3-a630-394f-8722-77816cf4d839', '有标题', '8c69765e-7827-371f-9db3-fea290f87739', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('c89c35b8-c539-3ca3-b2d2-a2f27b758689', 'This property describes the E35 Title applied to an instance of E71 Man-Made Thing. The E55 Type of Title is assigned in a sub property.
The P102.1 has type property of the P102 has title (is title of) property enables the relationship between the Title and the thing to be further clarified, for example, if the Title was a given Title, a supplied Title etc.
It allows any man-made material or immaterial thing to be given a Title. It is possible to imagine a Title being created without a specific object in mind.
', '8c69765e-7827-371f-9db3-fea290f87739', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('6012c827-e2ff-3ae2-acb8-bff8ea30ae8b', 'P103 était destiné à', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('eeba9e17-9ba3-3e95-9fb8-5fc6048e8941', 'était destiné à', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('5372ddef-2175-32f3-938b-6dc016608441', 'P103 was intended for', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('2a68683a-21e7-337f-8770-911316348b62', 'was intended for', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'en', 'altLabel');
INSERT INTO "values" VALUES ('ba5ea518-f850-38f9-a051-2edc183908c2', 'P103 bestimmt für', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('0ced0e7c-7358-390d-89a7-d61d6b6e7859', 'bestimmt für', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'de', 'altLabel');
INSERT INTO "values" VALUES ('a8c58234-011c-3c65-8cd4-10bc44de4c36', 'P103 был задуман для', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('5c9ffa55-dedc-3b36-9dde-44fea55bfcdb', 'был задуман для', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('1b82a1ec-e857-381c-ac0f-e8932d223541', 'P103 προοριζόταν για', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('8593516b-00a6-3c07-983d-82f756742151', 'προοριζόταν για', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'el', 'altLabel');
INSERT INTO "values" VALUES ('2393b34e-42ad-3e14-abc7-53d70a0eda7f', 'P103 era destinado à', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('0bdb7c25-5f69-3214-9628-9d8f42f8fbe8', 'era destinado à', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('e3e80718-905c-3a88-b06f-dee301281eec', 'P103 被制作来用於', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('49084fc1-8180-3e1e-bf69-c1a9887c5c5a', '被制作来用於', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('359a8d4c-6cd7-382d-b8b9-3ae15bcb61d4', 'This property links an instance of E71 Man-Made Thing to an E55 Type of usage. 
It creates a property between specific man-made things, both physical and immaterial, to Types of intended methods and techniques of use. Note: A link between specific man-made things and a specific use activity should be expressed using P19 was intended use of (was made for).', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('d067f779-ade5-393a-867a-619c7d5e40c8', 'P104 est sujet à', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('c3ff2b26-b6f3-3f8f-8ff0-885537ede766', 'est sujet à', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('a4d4be46-21d3-3934-9017-93cea7333e3c', 'P104 is subject to', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('7afb6f33-1991-39d0-800b-b61d7ba71d2e', 'is subject to', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'en', 'altLabel');
INSERT INTO "values" VALUES ('2f40894b-66e9-320d-8bb6-8327664d7052', 'P104 является объектом для', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('9c1d0c5f-7a23-30c9-a569-0a5e70e129cf', 'является объектом для', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('d0cf2d4d-c75b-311b-b121-46d47c5be638', 'P104 υπόκειται σε', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('673877e1-7207-3697-bd91-8973663fdd8d', 'υπόκειται σε', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'el', 'altLabel');
INSERT INTO "values" VALUES ('b5097c9b-1f59-32bd-a4c0-104c4f0782bd', 'P104 Gegenstand von', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('18058ada-60e2-37c4-858e-373d21471017', 'Gegenstand von', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'de', 'altLabel');
INSERT INTO "values" VALUES ('10bba9ca-e80e-323c-a71c-632aa350f0bc', 'P104 está sujeito à', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('17789289-7084-3bf9-8b4c-dbb3abd3a7d1', 'está sujeito à', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('26869bad-c9ab-3f23-b175-d4e2e119e0a2', 'P104 受制於', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('3d228bd5-da42-3157-85c9-009141926384', '受制於', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('1994bba8-3416-3d16-aae6-bba714672942', 'This property links a particular E72 Legal Object to the instances of E30 Right to which it is subject.
The Right is held by an E39 Actor as described by P75 possesses (is possessed by).
', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('2fa89dac-accc-3a4f-830f-47c65bcb0a0c', 'P105 право принадлежит', '140073c4-60b5-352d-a5f7-244072fc4086', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('eaac5d8d-c55f-34ea-a82d-9b52e5876d01', 'право принадлежит', '140073c4-60b5-352d-a5f7-244072fc4086', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('65f0303e-f2fc-37ab-8c78-b89f8bd5a056', 'P105 droit détenu par', '140073c4-60b5-352d-a5f7-244072fc4086', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('37c6f715-b7aa-3524-83f9-7cd3ac638ea8', 'droit détenu par', '140073c4-60b5-352d-a5f7-244072fc4086', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('a475e226-aa01-3bb0-8fb1-197ab01be76c', 'P105 Rechte stehen zu', '140073c4-60b5-352d-a5f7-244072fc4086', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('8a716dde-7e5b-35fd-8d5a-e9dc78b157dd', 'Rechte stehen zu', '140073c4-60b5-352d-a5f7-244072fc4086', 'de', 'altLabel');
INSERT INTO "values" VALUES ('3507b050-f371-3714-98d8-7558530210ea', 'P105 δικαίωμα κατέχεται από', '140073c4-60b5-352d-a5f7-244072fc4086', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('8a571eda-154c-3a3e-b458-116c37b29a33', 'δικαίωμα κατέχεται από', '140073c4-60b5-352d-a5f7-244072fc4086', 'el', 'altLabel');
INSERT INTO "values" VALUES ('0e5edf83-b12d-31ea-bff2-b9912dbb743b', 'P105 right held by', '140073c4-60b5-352d-a5f7-244072fc4086', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('0c8fb71e-af11-3694-adf0-7ab3f0e7ea08', 'right held by', '140073c4-60b5-352d-a5f7-244072fc4086', 'en', 'altLabel');
INSERT INTO "values" VALUES ('519387df-d759-37c3-ab4f-754dfd4cedf8', 'P105 são direitos de ', '140073c4-60b5-352d-a5f7-244072fc4086', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('a8f4f7f4-daac-3254-ab24-54e64a339523', 'são direitos de ', '140073c4-60b5-352d-a5f7-244072fc4086', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('eb2bcd13-c44c-3217-87f5-a0467b0d97b2', 'P105 有权限持有者', '140073c4-60b5-352d-a5f7-244072fc4086', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('94d8388e-0db2-3599-9fbe-e96dc8aa5c6d', '有权限持有者', '140073c4-60b5-352d-a5f7-244072fc4086', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('be0dd0d5-3e08-3749-a660-f988076c0be1', 'This property identifies the E39 Actor who holds the instances of E30 Right to an E72 Legal Object.
	It is a superproperty of P52 has current owner (is current owner of) because ownership is a right that is held on the owned object.
P105 right held by (has right on) is a shortcut of the fully developed path from E72 Legal Object through P104 is subject to (applies to), E30 Right, P75 possesses (is possessed by) to E39 Actor.
', '140073c4-60b5-352d-a5f7-244072fc4086', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('6259a29f-f55a-3c9a-9914-f86f7a37545b', 'P106  ist zusammengesetzt aus', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('cda6ead4-163b-3b9b-90bb-c329f2073fed', ' ist zusammengesetzt aus', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'de', 'altLabel');
INSERT INTO "values" VALUES ('f49ce88d-2c68-35ff-82ff-15b8585affc4', 'P106 составлен из', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('37ccab03-d05d-3c83-aa8f-cdb10d38365c', 'составлен из', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('87d2dcad-d9b0-3980-99d9-96c6d7de637b', 'P106 is composed of', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('097b7b83-c860-3626-b493-ab65ffb3626f', 'is composed of', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'en', 'altLabel');
INSERT INTO "values" VALUES ('56934bf6-5a19-35eb-81fd-474a0df470dc', 'P106 est composé de', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('6bf4879b-16f2-314c-b80c-066e8c0f4737', 'est composé de', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('9688cf33-ea44-3910-97d1-21c362bc1596', 'P106 αποτελείται από', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('83b58131-7018-3dde-80a4-1e1057d42b03', 'αποτελείται από', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'el', 'altLabel');
INSERT INTO "values" VALUES ('a2d1f159-14f6-36d6-87ce-e788ecbddff7', 'P106 é composto de', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('d50722e5-24db-32fb-92be-57e2f450c6c6', 'é composto de', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('a91732b3-ef98-3fc6-899e-6ac7f0bbc5de', 'P106 有组成元素', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('1d7e68d7-f080-3b2d-a8e1-a9dfa41444aa', '有组成元素', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('f89fd368-cc9f-3f23-a3a5-05531a59dd17', 'This property associates an instance of E90 Symbolic Object with a part of it that is by itself an instance of E90 Symbolic Object, such as fragments of texts or clippings from an image.
', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('f0f9ed03-0cf3-38bd-965e-61f85511a586', 'P107 a pour membre actuel ou ancien', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('da26a5cd-edf2-3974-9891-cd95c03ebdea', 'a pour membre actuel ou ancien', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('05825f9e-bc09-38ed-b846-4420386a22bb', 'P107 has current or former member', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('51def0c4-e334-33e9-9c5b-23bfa1463187', 'has current or former member', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'en', 'altLabel');
INSERT INTO "values" VALUES ('059733b6-2334-382b-8254-3111f61679e3', 'P107 έχει ή είχε μέλος', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('349c31bd-ca9d-34e8-8f22-359a5406d51e', 'έχει ή είχε μέλος', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'el', 'altLabel');
INSERT INTO "values" VALUES ('6a0ad494-dfa3-30b7-be49-a219515cc983', 'P107 имеет действующего или бывшего члена', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('d7e862ad-765c-3597-b778-8277f9e0589d', 'имеет действующего или бывшего члена', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('65d7b64d-f637-3ab2-aad3-39e3e897d1e4', 'P107 hat derzeitiges oder früheres Mitglied', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('6d4badd9-2f49-3273-a716-d4dc37135084', 'hat derzeitiges oder früheres Mitglied', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'de', 'altLabel');
INSERT INTO "values" VALUES ('eebae682-3201-3984-8678-53acbef1ed83', 'P107 tem ou teve membro', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('095361f7-441f-3d8a-90bc-fadb7058ea24', 'tem ou teve membro', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('06d24d80-b1f3-3c7b-8a47-3354d0de659b', 'P107 有现任或前任成员', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('b7e7fc5b-f863-318e-8838-c5acf5900043', '有现任或前任成员', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('7e237e10-3a2c-3af5-9df5-5fbf2fa0aaed', 'This property relates an E39 Actor to the E74 Group of which that E39 Actor is a member.
Groups, Legal Bodies and Persons, may all be members of Groups. A Group necessarily consists of more than one member.
This property is a shortcut of the more fully developed path from E74 Group through P144 joined with (gained member by), E85 Joining, P143 joined (was joined by) to E39 Actor
The property P107.1 kind of member can be used to specify the type of membership or the role the member has in the group. 
', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('8c94c677-1797-3785-aabd-72f71d87d248', 'P108 παρήγαγε', '632197f8-15a2-32b6-9886-c93e587f5b64', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('f8d8be98-9d7d-3630-a20f-d88dab47defa', 'παρήγαγε', '632197f8-15a2-32b6-9886-c93e587f5b64', 'el', 'altLabel');
INSERT INTO "values" VALUES ('42c1d8d8-9950-3618-8633-1d2b79cb3ef5', 'P108 a produit', '632197f8-15a2-32b6-9886-c93e587f5b64', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('32d99a3a-f987-3b3e-b0b0-d3af348d87a8', 'a produit', '632197f8-15a2-32b6-9886-c93e587f5b64', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('f81805bb-8128-3e37-91a1-780cea2b2432', 'P108 произвел', '632197f8-15a2-32b6-9886-c93e587f5b64', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('99d7f198-ecde-3f77-bb3b-74ef78c7573c', 'произвел', '632197f8-15a2-32b6-9886-c93e587f5b64', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('cf63f546-11ce-36ff-a6cf-811a3b58c83b', 'P108 hat hergestellt', '632197f8-15a2-32b6-9886-c93e587f5b64', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('4c7280bd-a077-349b-90b4-9826ad1916be', 'hat hergestellt', '632197f8-15a2-32b6-9886-c93e587f5b64', 'de', 'altLabel');
INSERT INTO "values" VALUES ('58eb9b59-2a91-37d6-836b-ae6fbffd7ae0', 'P108 has produced', '632197f8-15a2-32b6-9886-c93e587f5b64', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('64e1c12c-e6f8-38c9-b896-367c8d2ff03f', 'has produced', '632197f8-15a2-32b6-9886-c93e587f5b64', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c253c836-06b1-3b30-9ae5-2b915e627f7f', 'P108 produziu', '632197f8-15a2-32b6-9886-c93e587f5b64', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('c8e8a553-63a1-3c0e-b6b8-9ced8b8bbae2', 'produziu', '632197f8-15a2-32b6-9886-c93e587f5b64', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('9f1cb1f1-03c7-322d-825f-205e436a677f', 'P108 有产出物', '632197f8-15a2-32b6-9886-c93e587f5b64', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('54f2eaa2-5cac-33c1-adb3-3fd25e0cdd3a', '有产出物', '632197f8-15a2-32b6-9886-c93e587f5b64', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('89b83ac8-2959-30db-9374-8329d02fef03', 'This property identifies the E24 Physical Man-Made Thing that came into existence as a result of an E12 Production.
The identity of an instance of E24 Physical Man-Made Thing is not defined by its matter, but by its existence as a subject of documentation. An E12 Production can result in the creation of multiple instances of E24 Physical Man-Made Thing.
', '632197f8-15a2-32b6-9886-c93e587f5b64', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('ad07ff13-12fc-3265-8ae1-5fbe156a9430', 'P109 a pour conservateur actuel ou ancien', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('62dd7ffb-5c8f-3cde-92c0-2fd9570f4189', 'a pour conservateur actuel ou ancien', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('d73d2827-08c7-334c-ad82-486f00e77325', 'P109 hat derzeitigen oder früheren Kurator', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f6b75257-7c7a-3b6b-b5da-0929a489a2d3', 'hat derzeitigen oder früheren Kurator', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'de', 'altLabel');
INSERT INTO "values" VALUES ('7ed017f9-2055-3721-a5e4-e444cd1e164b', 'P109 has current or former curator', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('65c45773-2b4b-3a60-877b-9a145dcb5c20', 'has current or former curator', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'en', 'altLabel');
INSERT INTO "values" VALUES ('6ed5623f-5857-34a2-9cb9-d6618f7c3dbd', 'P109 έχει ή είχε επιμελητή', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('167eb9d0-3d56-399d-9279-796d9f4c8f7a', 'έχει ή είχε επιμελητή', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'el', 'altLabel');
INSERT INTO "values" VALUES ('9ead3908-8903-314c-9834-d71792ae2582', 'P109 имеет действующего или бывшего хранителя', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('a49acf55-38f5-390f-bd99-0a7667c0881d', 'имеет действующего или бывшего хранителя', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('7efe3c4e-f570-3ff9-8a91-d61b7e139df4', 'P109 tem ou teve curador', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('c6a8e921-f698-38d2-9ad5-e1689f08cc8a', 'tem ou teve curador', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('e5598a20-aa76-37ed-9fa0-6633be5b61fc', 'P109 有现任或前任典藏管理员', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('b972d71d-4437-38d4-8af6-682a687536e3', '有现任或前任典藏管理员', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('4406a0cb-8c2d-37b7-8fdf-e34649d84286', 'This property identifies the E39 Actor or Actors who assume or have assumed overall curatorial responsibility for an E78 Collection.

It does not allow a history of curation to be recorded. This would require use of an Event initiating a curator being responsible for  a Collection.
', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('0d637760-0b2e-3e59-9997-feaefe58b578', 'P110 увеличил', '41f65567-9d44-371a-8806-03e08d332918', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('5d718bc3-b4b2-3785-a819-f7440be5e185', 'увеличил', '41f65567-9d44-371a-8806-03e08d332918', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('b6a0b2f7-dcdd-34de-b282-137c305f737f', 'P110 a augmenté', '41f65567-9d44-371a-8806-03e08d332918', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('3bce3d90-ae6a-3280-b9f3-33f1e575022d', 'a augmenté', '41f65567-9d44-371a-8806-03e08d332918', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('fc5fbd01-2f5c-3b40-90ac-79ae0d036d21', 'P110 erweiterte', '41f65567-9d44-371a-8806-03e08d332918', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('0f767860-7b3e-3923-bf64-c3f78022f523', 'erweiterte', '41f65567-9d44-371a-8806-03e08d332918', 'de', 'altLabel');
INSERT INTO "values" VALUES ('e7882d5a-84f0-37b8-b3da-c8fd1a30ec93', 'P110 επαύξησε', '41f65567-9d44-371a-8806-03e08d332918', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('46422316-d405-3993-bdfc-e605deea74d4', 'επαύξησε', '41f65567-9d44-371a-8806-03e08d332918', 'el', 'altLabel');
INSERT INTO "values" VALUES ('5e10b6ea-e250-3dde-910e-187ad794d28e', 'P110 augmented', '41f65567-9d44-371a-8806-03e08d332918', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('233d8e3d-3142-3b62-a2a6-c5f7053eb80e', 'augmented', '41f65567-9d44-371a-8806-03e08d332918', 'en', 'altLabel');
INSERT INTO "values" VALUES ('236a22b2-bc08-3190-a0b8-4624b769f43f', 'P110 aumentou', '41f65567-9d44-371a-8806-03e08d332918', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('a5228e81-548f-372c-b5d9-479c46fb1602', 'aumentou', '41f65567-9d44-371a-8806-03e08d332918', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('a323fe92-ceea-3959-af6a-19a75e35f87b', 'P110 扩增了', '41f65567-9d44-371a-8806-03e08d332918', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('bda5b180-8538-3894-9c50-d9ef9cd4f9b2', '扩增了', '41f65567-9d44-371a-8806-03e08d332918', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('db038dbc-71bb-341f-bcab-ff4af8d3d685', 'This property identifies the E24 Physical Man-Made Thing that is added to (augmented) in an E79 Part Addition.
Although a Part Addition event normally concerns only one item of Physical Man-Made Thing, it is possible to imagine circumstances under which more than one item might be added to (augmented). For example, the artist Jackson Pollock trailing paint onto multiple canvasses.
', '41f65567-9d44-371a-8806-03e08d332918', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('702bf684-0f23-305d-be26-6c504af96d42', 'P111 fügte hinzu', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('bcccbba7-24c1-37e9-b8a1-2ce7cd555207', 'fügte hinzu', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'de', 'altLabel');
INSERT INTO "values" VALUES ('b7d8904a-8d14-3a3d-9b2e-4b4474e1acd9', 'P111 προσέθεσε', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('57291611-8472-36e9-85c7-2eb9f9ff81cb', 'προσέθεσε', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'el', 'altLabel');
INSERT INTO "values" VALUES ('87ab3da2-8ab5-3c01-8a19-3e96ea7c1748', 'P111 a ajouté', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('bfa959ec-e0e2-3166-b28f-91357aafc561', 'a ajouté', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('17a277f0-adca-3b2c-908f-c986546f4841', 'P111 added', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('6680451f-4c84-32eb-a7d2-adbb2733e103', 'added', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'en', 'altLabel');
INSERT INTO "values" VALUES ('0a0cb9a6-e06e-3cb9-aef9-0276b051b43a', 'P111 добавил', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('82f35d8f-9955-3877-bd5a-354166b1f9c2', 'добавил', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('36c2fe28-b4c8-3381-9908-dbcf586909c3', 'P111 adicionou', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('cafefc58-553e-3c55-84dd-df565a57df40', 'adicionou', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('f87f69aa-242d-3c0c-ace5-484cfdd0f5a1', 'P111 附加上部件', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('c493d353-8c3b-3518-b442-7709c21d46fd', '附加上部件', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('21117745-544f-3719-8ae3-fbceecc2ffdf', 'This property identifies the E18 Physical Thing that is added during an E79 Part Addition activity
', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('756f29eb-b6ae-3a07-873b-06bad1aa6d11', 'P112 уменьшил', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('fecd8de3-8f3d-35e1-bd44-35476682ad1a', 'уменьшил', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('d1977581-2be4-36b6-828d-4793fad49c65', 'P112 diminished', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('c3351c78-522d-3fe1-8a08-225075ac00bb', 'diminished', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'en', 'altLabel');
INSERT INTO "values" VALUES ('61c7a963-dffb-3425-8d40-c2dee0c245c2', 'P112 verminderte', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('311254ee-7ed6-3cde-bcf6-59a6731251fa', 'verminderte', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'de', 'altLabel');
INSERT INTO "values" VALUES ('811e42d1-886a-3a31-b614-018a90aa6051', 'P112 a diminué', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('233b6063-fff5-3cd7-bee2-28b6defa6172', 'a diminué', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('fb3c228f-556f-36ae-83ed-7fbc37229627', 'P112 εξάλειψε', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ec4bc823-eb63-3640-8293-fb0cdf2e8565', 'εξάλειψε', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'el', 'altLabel');
INSERT INTO "values" VALUES ('910900a7-1556-3027-ae98-315e875a3210', 'P112 diminuiu', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('ac9d7ab5-1d4d-3db6-a903-226956f6c825', 'diminuiu', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('f568c9da-f643-3d39-8286-5a303d8260cd', 'P112 缩减了', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('2ffc79b4-ef4f-351e-b91d-4aecc772126f', '缩减了', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('01dc3c4b-01ed-3eae-a368-31def961c7df', 'This property identifies the E24 Physical Man-Made Thing that was diminished by E80 Part Removal.
Although a Part removal activity normally concerns only one item of Physical Man-Made Thing, it is possible to imagine circumstances under which more than one item might be diminished by a single Part Removal activity. 
', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('a63fac3f-4941-3c09-8bbf-0a44600bf3bc', 'P113 удален', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('10c6fbed-326d-34a9-9459-bf300da26554', 'удален', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('6e432482-518c-317c-a852-4533650056d0', 'P113 entfernte', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('bd20c71a-6e3c-3be0-9b9e-1d2d98e6c2fe', 'entfernte', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'de', 'altLabel');
INSERT INTO "values" VALUES ('5080ddf2-fc18-32dd-8be9-8c81c2886da8', 'P113 removed', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('5de54fe4-d154-3eee-ac88-06d1b0073fae', 'removed', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'en', 'altLabel');
INSERT INTO "values" VALUES ('385aa41c-8040-3f04-b89d-1baee3c3a447', 'P113 αφαίρεσε', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('b9e8dfba-71fb-3787-bb39-2c8da224d35b', 'αφαίρεσε', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'el', 'altLabel');
INSERT INTO "values" VALUES ('527718d3-bfd6-3f09-9627-1895ae5632c2', 'P113 a enlevé', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('b8cb0172-c0bd-3fb9-9765-c80d6dbd5547', 'a enlevé', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('08f0e221-1979-3593-bdde-a6d03421dc3f', 'P113 removeu', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('539863f4-0aa0-393e-b16c-e35fc0d513af', 'removeu', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('eae52066-253e-39c4-a8ea-65093ded23f6', 'P113 移除了', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('6a6f967d-3d92-3c68-8e22-77263e236a43', '移除了', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('4382a087-ea98-355d-a715-f6d16066438e', 'This property identifies the E18 Physical Thing that is removed during an E80 Part Removal activity.', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('e2d0ca70-90bf-3662-9c20-e3e26b93b089', 'P114 est temporellement égale à', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('1c5296e3-4739-3e82-86f7-f731b7519eec', 'est temporellement égale à', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('670283b6-3801-3ff5-9f05-2d4f6904ac26', 'P114 zeitgleich zu', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('a9d8457a-8f86-30ce-b17b-6f8f56694b5e', 'zeitgleich zu', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'de', 'altLabel');
INSERT INTO "values" VALUES ('b9c4856e-afad-3df4-b7ab-b70086a165b8', 'P114 συμπίπτει χρονικά με', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('7f9444e5-ef85-3b67-ba43-e6e79e3c4af6', 'συμπίπτει χρονικά με', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'el', 'altLabel');
INSERT INTO "values" VALUES ('b66b4c1a-5ec5-3093-a247-0352cc4a70b4', 'P114 равен по времени', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('03702ebf-3f3c-3a24-8687-94e7a13ecb4c', 'равен по времени', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('42d2d89f-2324-32f5-b4fc-b76b105a835a', 'P114 is equal in time to', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('351d8831-ee72-3e5f-a040-c54d05e8db70', 'is equal in time to', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'en', 'altLabel');
INSERT INTO "values" VALUES ('4a83df22-a09a-3842-a200-476d168fe19c', 'P114 é temporalmente igual a', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('613fd5e2-f117-38bf-95fd-78310d05215b', 'é temporalmente igual a', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('77cd0f93-6cbd-3d95-b8e3-950bf03d99b7', 'P114 时段相同於', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('a6e66bcd-ae2e-3c4f-bbcd-f4afd9e9e224', '时段相同於', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('818af5b5-4241-3220-a300-65741a98cd34', 'This symmetric property allows the instances of E2 Temporal Entity with the same E52 Time-Span to be equated. 
This property is only necessary if the time span is unknown (otherwise the equivalence can be calculated).
This property is the same as the "equal" relationship of Allen’s temporal logic (Allen, 1983, pp. 832-843).
', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('27c7c4a4-2731-348a-bbdc-0d9ad7e64d33', 'P115 finishes', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('700f7714-d301-3023-a3ee-5ae3ac202bdd', 'finishes', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'en', 'altLabel');
INSERT INTO "values" VALUES ('284f7cc1-f658-35f0-be32-e99b33d99239', 'P115 заканчивает', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('deaffdeb-738e-3f79-b1bb-26c288910af3', 'заканчивает', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('92488f5c-23bb-34a6-8cac-329aa3fb3321', 'P115 beendet', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('de13b36b-8f59-3f0b-9e10-e952aec199a0', 'beendet', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'de', 'altLabel');
INSERT INTO "values" VALUES ('0db6ac83-0819-33fa-8937-4e2301e3db56', 'P115 termine', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5cc139ed-b5f6-3267-8b5d-c6535feabd5d', 'termine', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('126a8578-6444-3732-b87a-bc572b03ccea', 'P115 περατώνει', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('bcbdfcec-6fd2-3e15-99a0-f683d2d41fda', 'περατώνει', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'el', 'altLabel');
INSERT INTO "values" VALUES ('eba425de-37a7-3a1a-ae24-08157894d571', 'P115 finaliza', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('465f41f7-fede-31d7-82e5-a39d172dad1a', 'finaliza', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b08e0c8c-0497-35fd-a2a6-a5fe2050bb6b', 'P115 结束了', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('5d4f0543-c271-378d-8564-65c2e74747b2', '结束了', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('98cb7727-bd37-3c16-8a98-caf99a462b73', 'This property allows the ending point for a E2 Temporal Entity to be situated by reference to the ending point of another temporal entity of longer duration.  
This property is only necessary if the time span is unknown (otherwise the relationship can be calculated). This property is the same as the "finishes / finished-by" relationships of Allen’s temporal logic (Allen, 1983, pp. 832-843).
', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('bc1d5626-3c4f-3cac-87b2-07deef89764e', 'P116 commence', '61861fca-6102-3151-af0c-599e14e7a93a', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('8b65e030-2ad9-3643-a86d-6fa6d7251bc8', 'commence', '61861fca-6102-3151-af0c-599e14e7a93a', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('4c42dbd8-c1f9-3849-be7b-3d36003c65c3', 'P116 starts', '61861fca-6102-3151-af0c-599e14e7a93a', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('72661fd9-de54-3bf9-b3e3-1fb3962ab1ef', 'starts', '61861fca-6102-3151-af0c-599e14e7a93a', 'en', 'altLabel');
INSERT INTO "values" VALUES ('cbd7d2c0-b921-3c74-8549-0797df0da88f', 'P116 начинает', '61861fca-6102-3151-af0c-599e14e7a93a', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('5c9bfcf2-457d-3844-bfdf-24a93d923ee6', 'начинает', '61861fca-6102-3151-af0c-599e14e7a93a', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('701843b4-cc36-3b69-925d-17d76bae6427', 'P116 beginnt', '61861fca-6102-3151-af0c-599e14e7a93a', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('7a4bae65-b951-36c5-8986-d3acaa19708e', 'beginnt', '61861fca-6102-3151-af0c-599e14e7a93a', 'de', 'altLabel');
INSERT INTO "values" VALUES ('3643d1f3-7213-32b9-8d46-f58aa9017b77', 'P116 αρχίζει', '61861fca-6102-3151-af0c-599e14e7a93a', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('893d873c-f2e3-337b-ab4e-b9869ebb84cc', 'αρχίζει', '61861fca-6102-3151-af0c-599e14e7a93a', 'el', 'altLabel');
INSERT INTO "values" VALUES ('deb64734-a9a9-324f-a185-9542ed78735a', 'P116 inicia', '61861fca-6102-3151-af0c-599e14e7a93a', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('980fad11-6e6b-317d-a417-d5cd82d6502c', 'inicia', '61861fca-6102-3151-af0c-599e14e7a93a', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('e8d4d330-aedd-3685-ac8c-16ebdeea8c8b', 'P116 开始了', '61861fca-6102-3151-af0c-599e14e7a93a', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('81e24b4d-7ad5-36e0-b8e6-ae15597e7e7f', '开始了', '61861fca-6102-3151-af0c-599e14e7a93a', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('ae8fd38a-1977-3546-aa29-a868e1d4c01f', 'This property allows the starting point for a E2 Temporal Entity to be situated by reference to the starting point of another temporal entity of longer duration.  
This property is only necessary if the time span is unknown (otherwise the relationship can be calculated). This property is the same as the "starts / started-by" relationships of Allen’s temporal logic (Allen, 1983, pp. 832-843).
', '61861fca-6102-3151-af0c-599e14e7a93a', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('2ee14c44-33c2-3b6b-a8c7-e4fc9424649a', 'P117 fällt in', '740ab790-feb0-3700-8922-f152320272a5', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f6c6c8e5-6fcd-3590-89b2-add07a7e5e69', 'fällt in', '740ab790-feb0-3700-8922-f152320272a5', 'de', 'altLabel');
INSERT INTO "values" VALUES ('609b0a0e-5e1d-3afb-80bb-6c17e9708c83', 'P117 εμφανίζεται κατά τη διάρκεια', '740ab790-feb0-3700-8922-f152320272a5', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('2c75e740-f7ff-3cfe-a52d-71e72599a6b3', 'εμφανίζεται κατά τη διάρκεια', '740ab790-feb0-3700-8922-f152320272a5', 'el', 'altLabel');
INSERT INTO "values" VALUES ('ff5023f4-4f64-3b79-884b-69ec55a00a0c', 'P117 появляется во течение', '740ab790-feb0-3700-8922-f152320272a5', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('4cb09e35-eb76-317c-a9a6-dbe10135eb8e', 'появляется во течение', '740ab790-feb0-3700-8922-f152320272a5', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('08d30565-0be8-3cef-a811-f324506e76e5', 'P117 occurs during', '740ab790-feb0-3700-8922-f152320272a5', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('37784d47-065c-3e45-94ea-652b5307afde', 'occurs during', '740ab790-feb0-3700-8922-f152320272a5', 'en', 'altLabel');
INSERT INTO "values" VALUES ('fb55f9fa-b991-3ca6-8235-4664d4b501bc', 'P117 a lieu pendant', '740ab790-feb0-3700-8922-f152320272a5', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('e0b0c2de-dae9-3cb0-83a3-aeb7947d4e29', 'a lieu pendant', '740ab790-feb0-3700-8922-f152320272a5', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('b9b32420-a679-3560-8be1-29db36d3096d', 'P117 ocorre durante', '740ab790-feb0-3700-8922-f152320272a5', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('e7538626-f539-36f6-85ea-ddcc0ae3e3e2', 'ocorre durante', '740ab790-feb0-3700-8922-f152320272a5', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('65491445-b031-3a90-8e6e-5ce79d4af8f5', 'P117 时段被涵盖於', '740ab790-feb0-3700-8922-f152320272a5', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('3ba58369-ef20-355d-b91a-a7900e48e75b', '时段被涵盖於', '740ab790-feb0-3700-8922-f152320272a5', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('8ebf6429-22fe-3679-a6b1-5563461ea65a', 'This property allows the entire E52 Time-Span of an E2 Temporal Entity to be situated within the Time-Span of another temporal entity that starts before and ends after the included temporal entity.   
This property is only necessary if the time span is unknown (otherwise the relationship can be calculated). This property is the same as the "during / includes" relationships of Allen’s temporal logic (Allen, 1983, pp. 832-843).
', '740ab790-feb0-3700-8922-f152320272a5', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('da500475-5b76-3d76-9ab4-d6d09025e3c2', 'P118 overlaps in time with', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b143a205-a8a3-3c84-a3f3-4e711ce1cd88', 'overlaps in time with', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'en', 'altLabel');
INSERT INTO "values" VALUES ('3f84f7a8-c96f-3c3e-8783-2c4e0750699f', 'P118 перекрывает во времени', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('c4de1f20-f6c4-31b1-b26a-acc68fb3a393', 'перекрывает во времени', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('b7ef3eb0-daea-3720-b74b-de560ea18802', 'P118 προηγείται μερικώς επικαλύπτοντας', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('27d42105-86b7-3f55-a7b5-cfaf4bcfe20a', 'προηγείται μερικώς επικαλύπτοντας', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'el', 'altLabel');
INSERT INTO "values" VALUES ('be81d743-eef4-31e6-9dd6-11efaa672652', 'P118 überlappt zeitlich mit', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('c0981f26-4a25-353a-9edc-84c34c98d7c4', 'überlappt zeitlich mit', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'de', 'altLabel');
INSERT INTO "values" VALUES ('59888301-17d0-3fe4-bf32-f886b7036a5b', 'P118 est partiellement recouverte dans le temps par', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('c703b38f-8089-3931-a638-538cd655d8d4', 'est partiellement recouverte dans le temps par', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('2eda1d5d-31a8-31b1-85a7-38ae44ff7b4a', 'P118 sobrepõe temporalmente', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('efbebd7c-1bb6-3157-86c8-46e251c0949b', 'sobrepõe temporalmente', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('89d80839-6536-3321-a339-3ca7eba9e02b', 'P118 时段重叠了', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('8762367e-bbb0-323c-b0b8-78bd725ff9c1', '时段重叠了', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('333b67a2-4764-348d-8cf2-730a5ee6b2aa', 'This property identifies an overlap between the instances of E52 Time-Span of two instances of E2 Temporal Entity. 
It implies a temporal order between the two entities: if A overlaps in time B, then A must start before B, and B must end after A. This property is only necessary if the relevant time spans are unknown (otherwise the relationship can be calculated).
This property is the same as the "overlaps / overlapped-by" relationships of Allen’s temporal logic (Allen, 1983, pp. 832-843).
', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('c05deba0-1b0a-31df-86a4-15bb2d71496b', 'P119 meets in time with', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('ca5c984b-fc7e-3850-aea2-e1bdf019b374', 'meets in time with', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'en', 'altLabel');
INSERT INTO "values" VALUES ('e3fb72b6-a5fc-376d-b226-c5fa7f4425dd', 'P119 προηγείται', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('d682c996-f1d0-3565-bf23-b28450282fa1', 'προηγείται', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'el', 'altLabel');
INSERT INTO "values" VALUES ('888a8757-0d04-33fb-b215-94530ef8899a', 'P119 trifft zeitlich auf', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('03640194-66fb-3328-8d8d-2f3ae6eea672', 'trifft zeitlich auf', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'de', 'altLabel');
INSERT INTO "values" VALUES ('6b67bc9b-5df2-30e0-ac98-309fe0206bb8', 'P119 следует во времени за', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('4c86b08a-8a59-381c-9e3b-8f93de94ac9c', 'следует во времени за', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('76e9ff36-5eb3-3bd6-b524-f40f0fa8bdf2', 'P119 est temporellement contiguë avec', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('88b0d8a9-4236-3bae-970c-450581362bce', 'est temporellement contiguë avec', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('8dc66bec-ccb2-3875-ae2f-55943ba483de', 'P119 é temporalmente contíguo com', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('b3f853a8-e5b0-3450-b887-f34078a1c563', 'é temporalmente contíguo com', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('7d28634f-c1c6-381c-931b-5cf1806e4f64', 'P119 紧接续了', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('c1aeeb10-6416-3695-9f0c-c89bc42139df', '紧接续了', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('f192cecd-1e9f-386f-875b-9c5d521944a5', 'This property indicates that one E2 Temporal Entity immediately follows another. 
It implies a particular order between the two entities: if A meets in time with B, then A must precede B. This property is only necessary if the relevant time spans are unknown (otherwise the relationship can be calculated). 
This property is the same as the "meets / met-by" relationships of Allen’s temporal logic (Allen, 1983, pp. 832-843).
', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('ab16a133-aa08-3c33-a9de-1773cc869966', 'P120 появляется до', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('88808537-f657-3df8-a6eb-d18d31b0c435', 'появляется до', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('d84f64a2-4cc0-3865-9a0d-aabd0f8c27a0', 'P120 a lieu avant', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('b4fab88f-4978-393a-b504-9f05cdfc40be', 'a lieu avant', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('7b5aa32a-d7e8-3f8a-9723-7155a56439e0', 'P120 εμφανίζεται πριν', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('11dcaa26-47a1-3b63-a982-0559d9f645b1', 'εμφανίζεται πριν', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'el', 'altLabel');
INSERT INTO "values" VALUES ('e3608f3c-d5a9-3d17-85a3-8852a4da7b2a', 'P120 occurs before', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('0c8ca3d9-9a4c-3b42-82eb-b9f8efe82331', 'occurs before', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'en', 'altLabel');
INSERT INTO "values" VALUES ('941089c0-fb71-357d-8e63-94e0e8c7813a', 'P120 kommt vor', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('8a40bfbb-3fa9-32b2-9010-37d2240a96bc', 'kommt vor', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'de', 'altLabel');
INSERT INTO "values" VALUES ('e546f026-f636-3a47-a32b-9ea49b919f70', 'P120 ocorre antes', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('9735b2b5-f253-31f7-b4f9-04b0ee1620f7', 'ocorre antes', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('ed8b5949-6e09-395e-b41d-724a3ea278fe', 'P120 发生时段先於', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('4b081d20-5849-3bf8-b176-1ee5b79b83fb', '发生时段先於', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('3e234d69-941f-39d4-86b0-57f9b4e892b2', 'This property identifies the relative chronological sequence of two temporal entities. 
It implies that a temporal gap exists between the end of A and the start of B. This property is only necessary if the relevant time spans are unknown (otherwise the relationship can be calculated).
This property is the same as the "before / after" relationships of Allen’s temporal logic (Allen, 1983, pp. 832-843).
', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('e436e968-8542-3d72-8475-54b82261bcad', 'P121 επικαλύπτεται με', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('0e07fe17-0dde-3d72-b35f-e9014e18ed65', 'επικαλύπτεται με', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'el', 'altLabel');
INSERT INTO "values" VALUES ('1e3520a4-996f-3f87-9b26-a04b352f5eb8', 'P121 überlappt mit', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f43eade1-d58a-39ed-801a-fbd5ccbfee89', 'überlappt mit', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'de', 'altLabel');
INSERT INTO "values" VALUES ('927ce56d-b4d4-3748-b00b-cf860db4f943', 'P121 chevauche', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('766b5648-c65c-3706-ae9f-b83a66152ea6', 'chevauche', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('81cb5ba8-fca8-3e92-b9c7-147bf3332924', 'P121 пересекается с', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('f52a2dd7-5dac-353c-b6f5-c88ea8343ef7', 'пересекается с', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('2d643b2a-6098-369f-a4dd-b7e2a9e972e8', 'P121 overlaps with', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('1ab607fd-c791-306d-a744-7960965cd1b6', 'overlaps with', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'en', 'altLabel');
INSERT INTO "values" VALUES ('363a146b-231a-345a-a882-502ed26267d6', 'P121 sobrepõe com', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('9a599a82-556b-3436-ba25-dd76a9cf891d', 'sobrepõe com', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('67a81661-9b6f-35b9-8db8-e04a538c898d', 'P121 空间重叠于', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('d39d8678-7246-3de8-97f7-868c748dbd8f', '空间重叠于', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('49791dda-8a0d-3abf-841b-458ef7fbd59a', 'This symmetric property allows the instances of E53 Place with overlapping geometric extents to be associated with each other. 
It does not specify anything about the shared area. This property is purely spatial, in contrast to Allen operators, which are purely temporal.
', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('b8a0f8de-a5d7-34d7-9fe4-fc4f62a7f8d1', 'P122 граничит с', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('d7d057fc-95fe-3e75-9dac-3bf3b25b60c7', 'граничит с', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('bed65c54-7605-3694-898c-c04cb24ec0c2', 'P122 borders with', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('7d09d916-d263-34d1-ad9f-714d98f4d766', 'borders with', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'en', 'altLabel');
INSERT INTO "values" VALUES ('dd719788-87e3-3a41-8734-dbe0b831510d', 'P122 jouxte', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5aa5c900-fd2f-31cc-8435-4b50564b62be', 'jouxte', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('4ae153ff-053d-3656-95dc-7302fe426d12', 'P122 grenzt an', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('5514aac4-63df-32a4-ab88-759702f7d9b0', 'grenzt an', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'de', 'altLabel');
INSERT INTO "values" VALUES ('3ba00eaf-4c5a-3eb8-92ac-0d8c421297d4', 'P122 συνορεύει με', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('3273ef1b-7300-386c-99de-d7b97b9b1ab7', 'συνορεύει με', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'el', 'altLabel');
INSERT INTO "values" VALUES ('d28215b3-df4b-3e96-9461-d9179ca96ead', 'P122 fronteira com', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('1ab780b5-72bc-339c-a34a-e4c5bc965c61', 'fronteira com', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('d63d022e-8a8a-3c6c-9c27-7548000e8efc', 'P122 接壤于', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('7f3de5f1-425e-37f0-abd5-7bf97062c177', '接壤于', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('5ccc8f41-2372-3020-af14-2d8bcb5ed0e3', 'This symmetric property allows the instances of E53 Place which share common borders to be related as such. 
This property is purely spatial, in contrast to Allen operators, which are purely temporal.
', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('43fedd80-1f12-3a96-91c2-318f9910f3c9', 'P123 a eu pour résultat', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('c7e1165d-344c-3f3c-a9cf-935d9b6053b8', 'a eu pour résultat', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('eef6eab4-9c13-3d18-9af0-afda00176b43', 'P123 ergab', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('58db4d2c-bc96-3203-b6de-9e6b53bd30f3', 'ergab', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'de', 'altLabel');
INSERT INTO "values" VALUES ('48672a9d-67de-35ff-a1b2-1631288ca900', 'P123 είχε ως αποτέλεσμα', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ac906aae-48e1-3d06-a3e5-fddfd0dbdbe9', 'είχε ως αποτέλεσμα', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'el', 'altLabel');
INSERT INTO "values" VALUES ('ac07ff35-bab3-3ab5-9e48-61dd77681481', 'P123 повлек появление', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('7573e526-545d-3e77-a003-e270c9d369ba', 'повлек появление', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('906848bc-5dc4-3135-a17b-9a617d03bef3', 'P123 resulted in', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('c1801141-e54d-316d-ba2c-955e131e94b2', 'resulted in', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'en', 'altLabel');
INSERT INTO "values" VALUES ('f5ca9e31-ad7d-3241-8314-d5771301918b', 'P123 resultou em', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('3d429d33-1e2c-3501-93e9-7ce7ad8d79a3', 'resultou em', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('92bb2b12-b7a4-3611-a44d-a1b87a7da6a6', 'P123 转变出', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('3910aad6-e0b4-334e-bf0b-18f7ab3c23d6', '转变出', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('e9eb9059-b96a-39ff-83bd-cb39d0072737', 'This property identifies the E77 Persistent Item or items that are the result of an E81 Transformation. 
New items replace the transformed item or items, which cease to exist as units of documentation. The physical continuity between the old and the new is expressed by the link to the common Transformation.
', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('77bcde41-d8f5-3a55-8c9a-2df1e08b8f79', 'P124 transformed', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('8398457d-e3b9-3f2f-b311-9183022fc12e', 'transformed', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'en', 'altLabel');
INSERT INTO "values" VALUES ('2e37ad58-ed47-3b1c-b12f-2c1727cec938', 'P124 wandelte um', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('1210139a-be29-397e-9245-143b9dcb0149', 'wandelte um', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'de', 'altLabel');
INSERT INTO "values" VALUES ('fefedb2c-fc09-3faa-9df4-bb5166875318', 'P124 μετέτρεψε', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ec17141c-3512-325d-9a28-a4abd9375b04', 'μετέτρεψε', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'el', 'altLabel');
INSERT INTO "values" VALUES ('a6718aa6-26a5-3bcc-85a7-51bbcd416f1d', 'P124 трансформировал', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('cdd3fd39-4a53-379e-956e-8128cb35cfb1', 'трансформировал', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('3cb45952-d244-3f09-b196-568703de9894', 'P124 a transformé', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('44f1bdc3-0254-3427-bf93-c51efac9123a', 'a transformé', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('f1ce3cf5-1140-3660-b603-55167ccfdfef', 'P124 transformou', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('7422ea6e-c8ba-39dd-8a7c-7697d04d3b89', 'transformou', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('bb4f28a3-e91c-350c-bdcf-6a1a63717c32', 'P124 转变了', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('841c319a-1ed0-3f4a-9b9e-335061dea8cb', '转变了', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('41338bc7-776f-3d5f-8f62-4ef1091b8766', 'This property identifies the E77 Persistent Item or items that cease to exist due to a E81 Transformation. 
It is replaced by the result of the Transformation, which becomes a new unit of documentation. The continuity between both items, the new and the old, is expressed by the link to the common Transformation.
', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('1323d77a-776b-34d8-9929-1b65db21a704', 'P125 used object of type', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('58eed855-c9f8-3c7f-a688-10a09b70255f', 'used object of type', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c223261c-1cac-32a0-a6e2-bd2fdb3e7b60', 'P125 a employé un objet du type', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('66f00e7c-6bdc-3379-9db9-ed214b65bb86', 'a employé un objet du type', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('c93aae35-35fc-39bd-9205-7271d0869b04', 'P125 использовал объект типа', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('df03c0d0-8fec-36c5-bc4e-d9e4681b10fc', 'использовал объект типа', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('57f68146-c55e-3a0e-9f45-94cdcc4c4919', 'P125 benutzte Objekt des Typus', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('2b32df54-b5df-3a8e-8c8f-a6481f498e91', 'benutzte Objekt des Typus', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'de', 'altLabel');
INSERT INTO "values" VALUES ('641fd946-edd5-3f6f-8f72-c52813320041', 'P125 χρησιμοποίησε αντικείμενο τύπου', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('744b7a53-3c40-3108-bf29-39f3b0992206', 'χρησιμοποίησε αντικείμενο τύπου', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'el', 'altLabel');
INSERT INTO "values" VALUES ('d0c036e3-ed29-338f-9e5a-3b1b4ddd7896', 'P125 usou objeto do tipo', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('3d7260e2-0d8e-3792-ac38-082bc553f6da', 'usou objeto do tipo', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('2223ced1-60d8-3170-b92b-579dda8ae927', 'P125 有使用物件类型', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('8b2420e5-f41a-38df-933c-faedd87910c0', '有使用物件类型', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('1936ea85-2329-3236-8fc4-99f5436d1e4c', 'This property defines the kind of objects used in an E7 Activity, when the specific instance is either unknown or not of interest, such as use of "a hammer".
', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('d197fdec-cc20-3baf-b7b1-41938c61f2b3', 'P126 a employé', '8bfff662-9024-325a-a23a-b3c9bf509031', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('e3fd02c5-d803-3ff6-baa4-03adca7fd38c', 'a employé', '8bfff662-9024-325a-a23a-b3c9bf509031', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('0c05903d-934f-3916-98a9-5551e0311fcc', 'P126 verwendete', '8bfff662-9024-325a-a23a-b3c9bf509031', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('458bef0c-9084-3c3f-b95f-c656cb5b2676', 'verwendete', '8bfff662-9024-325a-a23a-b3c9bf509031', 'de', 'altLabel');
INSERT INTO "values" VALUES ('9b0069a0-019b-3d67-a053-e5a177a9305f', 'P126 employed', '8bfff662-9024-325a-a23a-b3c9bf509031', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('66a3ef1b-7c2e-3349-90ab-9c5649767dc8', 'employed', '8bfff662-9024-325a-a23a-b3c9bf509031', 'en', 'altLabel');
INSERT INTO "values" VALUES ('12cf33cc-38df-3901-a3cd-cbf3f7798ed7', 'P126 использовал', '8bfff662-9024-325a-a23a-b3c9bf509031', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('e1088f54-e20c-3049-b098-f4232998fc2b', 'использовал', '8bfff662-9024-325a-a23a-b3c9bf509031', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('25b922b3-c5f1-3670-8f94-2d988b53082b', 'P126 χρησιμοποίησε', '8bfff662-9024-325a-a23a-b3c9bf509031', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('2dd9e458-a4bc-3ab6-854a-9a88016b1db7', 'χρησιμοποίησε', '8bfff662-9024-325a-a23a-b3c9bf509031', 'el', 'altLabel');
INSERT INTO "values" VALUES ('1dd5b2ce-115a-3a7f-9127-1cc3c76f5c19', 'P126 empregou', '8bfff662-9024-325a-a23a-b3c9bf509031', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('e6c2f009-94e5-3260-bc85-e37c1824433b', 'empregou', '8bfff662-9024-325a-a23a-b3c9bf509031', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('d3328227-9dc3-3d2b-89d6-55c831fa963b', 'P126 采用了材料', '8bfff662-9024-325a-a23a-b3c9bf509031', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('c0814089-285e-36e7-8d5f-a78801560af2', '采用了材料', '8bfff662-9024-325a-a23a-b3c9bf509031', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('4b447189-10e3-3347-b7a7-ce6fb99852ba', 'This property identifies E57 Material employed in an E11 Modification.
The E57 Material used during the E11 Modification does not necessarily become incorporated into the E24 Physical Man-Made Thing that forms the subject of the E11 Modification.
', '8bfff662-9024-325a-a23a-b3c9bf509031', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('8f806d85-03ee-3570-b5c8-7a7702f4f3ec', 'P127 έχει ευρύτερο όρο', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('f5e0605e-2070-381d-b02c-3186e8ceef9f', 'έχει ευρύτερο όρο', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'el', 'altLabel');
INSERT INTO "values" VALUES ('46256b68-9287-37e0-985d-c16af6b6f5c5', 'P127 a pour terme générique', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('1d95045a-91aa-3b9c-94ef-4547c41239b7', 'a pour terme générique', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('956b7155-5bd2-3a49-9bd6-b075c4513b33', 'P127 hat den Oberbegriff', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('dd381c29-3f1b-3dc9-b0df-f4a4fa04170b', 'hat den Oberbegriff', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'de', 'altLabel');
INSERT INTO "values" VALUES ('e8ed7417-8b72-3c62-b83b-e83538aebba0', 'P127 has broader term', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('f4e3db3c-aeec-3154-9d1a-623c96d8dbc2', 'has broader term', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'en', 'altLabel');
INSERT INTO "values" VALUES ('0dd3c43b-c2dd-34b0-aa8f-40ad53e128c8', 'P127 имеет вышестоящий термин', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('4f5654a5-06fe-3ff9-9108-4b1a0e3ded68', 'имеет вышестоящий термин', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('bfd8f6cd-4e4c-3fb2-8e79-6d082b8a764e', 'P127 tem termo genérico', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('9e00e4cc-58c3-3d39-b0fe-66488cf83d31', 'tem termo genérico', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('5e0872ae-2ae7-35fc-b47c-e549d8bfca89', 'P127 有广义术语', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('2db6b9ce-341b-3f43-939b-36fdb224a675', '有广义术语', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('1a00d5a9-c2cc-32cf-bdba-ae15bc8249ea', 'This property identifies a super-Type to which an E55 Type is related. 
		It allows Types to be organised into hierarchies. This is the sense of "broader term generic  		(BTG)" as defined in ISO 2788
', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('17faf861-c561-39a5-ad20-53048c76ffd3', 'P128 carries', '007dac32-df80-366b-88ce-02f4c1928537', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('20e03283-8b0c-34c9-8d18-35240b3e6df6', 'carries', '007dac32-df80-366b-88ce-02f4c1928537', 'en', 'altLabel');
INSERT INTO "values" VALUES ('8a597a37-584a-3ae3-91d3-8e948153e976', 'P128 est le support de', '007dac32-df80-366b-88ce-02f4c1928537', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('0cf98aa3-721a-3191-b058-16ab3732fafa', 'est le support de', '007dac32-df80-366b-88ce-02f4c1928537', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('7e732844-765c-3338-bc54-5fdc08e853c3', 'P128 несет', '007dac32-df80-366b-88ce-02f4c1928537', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('05645204-9913-34d5-93d3-034f2a921647', 'несет', '007dac32-df80-366b-88ce-02f4c1928537', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('d598e950-6b21-3f62-b6a4-a21ba421a4ee', 'P128 φέρει', '007dac32-df80-366b-88ce-02f4c1928537', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('3a596bd1-08f8-3d18-90d4-b6686fc38d8d', 'φέρει', '007dac32-df80-366b-88ce-02f4c1928537', 'el', 'altLabel');
INSERT INTO "values" VALUES ('06ca3ef5-055f-3004-92f5-0e3633f63115', 'P128 trägt', '007dac32-df80-366b-88ce-02f4c1928537', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('93325ea2-ff6a-3327-9036-9758fcd04e50', 'trägt', '007dac32-df80-366b-88ce-02f4c1928537', 'de', 'altLabel');
INSERT INTO "values" VALUES ('81360c15-ac2d-3cc4-ae18-02d02e1170b6', 'P128 é o suporte de', '007dac32-df80-366b-88ce-02f4c1928537', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('8678706d-ead7-356d-b3a7-b3aaf3456b2d', 'é o suporte de', '007dac32-df80-366b-88ce-02f4c1928537', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('b81d4682-e8c8-3659-88e6-7c761ac53c74', 'P128 承载信息', '007dac32-df80-366b-88ce-02f4c1928537', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('4eb2d960-81fb-3dfb-962b-8aee3df79581', '承载信息', '007dac32-df80-366b-88ce-02f4c1928537', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('4d8193f5-cf81-3bfa-b553-9f5feb773df3', 'This property identifies an E90 Symbolic Object carried by an instance of E18 Physical Thing.
', '007dac32-df80-366b-88ce-02f4c1928537', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('eca77f90-ba2c-35f0-9c79-88e3ad838f3e', 'P129 est au sujet de', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('66b6c1a1-d13a-3e93-a8c6-e0988be0a844', 'est au sujet de', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('b5323003-178b-3d66-8360-a58a8dd7a1f4', 'P129 is about', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b4b87af1-b711-3f8d-a0dd-c210ceb4283e', 'is about', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'en', 'altLabel');
INSERT INTO "values" VALUES ('5d1b4678-9b01-37be-a067-204b07df8c5f', 'P129 касается', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('6480efd6-8cfd-394d-9fb1-63cb4acca738', 'касается', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('5ed428b8-7408-3c44-bf08-1c6841ac2e85', 'P129 έχει ως θέμα', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('d1fff984-5573-3a4a-9ec0-320f3fd5d0c7', 'έχει ως θέμα', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'el', 'altLabel');
INSERT INTO "values" VALUES ('2f459fa7-0020-395f-933e-199eb04d7502', 'P129 handelt über', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('8214d9a8-5706-3505-a8b8-5560bc8e665c', 'handelt über', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'de', 'altLabel');
INSERT INTO "values" VALUES ('0b95e4d3-dd72-330c-930a-1594060ed1ed', 'P129 é sobre', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('fe5f76b7-f756-3a2c-b9bc-9a46108fcb20', 'é sobre', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('0ee05410-90d9-3024-8791-0e0e1213b78f', 'P129 陈述关於', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('57676448-7b86-3a1c-afcc-69c348ae8685', '陈述关於', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('4b029823-901a-38ac-9027-e88f3a259223', 'This property documents that an E89 Propositional Object has as subject an instance of E1 CRM Entity. 
', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('871de612-9916-369e-a864-10fda93b2031', 'P130 παρουσιάζει χαρακτηριστικά του/της', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('832b2fbb-9401-3309-8ad9-0f4d06e1d08b', 'παρουσιάζει χαρακτηριστικά του/της', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'el', 'altLabel');
INSERT INTO "values" VALUES ('731bf8c2-c4c4-3128-9f74-0af33b5f0cd2', 'P130 shows features of', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('c4602c26-29ae-3858-969a-1ee61ccbd5c4', 'shows features of', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'en', 'altLabel');
INSERT INTO "values" VALUES ('a8be7333-e816-3d11-8118-81c36689548d', 'P130 демонстрирует признаки', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('bdd37cb2-6cad-3bad-b08a-b12e309ae5d4', 'демонстрирует признаки', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('1c910dec-da50-3d0f-aa83-ede8c3909f48', 'P130 présente des caractéristiques de', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('aca2d6fc-59c9-3142-927e-722d52f7da7e', 'présente des caractéristiques de', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('701819b3-78d4-3715-aaac-97d0114e553c', 'P130 zeigt Merkmale von', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('1dced750-37b8-37aa-a773-b428717a28d2', 'zeigt Merkmale von', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'de', 'altLabel');
INSERT INTO "values" VALUES ('41b7ff01-0356-337c-a406-572734c09edd', 'P130 apresenta características de', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('52fd6a5f-b17a-32d0-aa85-a1f94c279a29', 'apresenta características de', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('054f6a8f-0eef-386c-aa18-23df74821a14', 'P130 外观特征原出现於', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('89163b74-d317-3f4d-ae1e-ac2fa019b4f8', '外观特征原出现於', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('42a8db97-8828-3d5c-903d-617fbf27eac9', 'This property generalises the notions of  "copy of" and "similar to" into a dynamic, asymmetric relationship, where the domain expresses the derivative, if such a direction can be established.
Otherwise, the relationship is symmetric. It is a short-cut of P15 was influenced by (influenced) in a creation or production, if such a reason for the similarity can be verified. Moreover it expresses similarity in cases that can be stated between two objects only, without historical knowledge about its reasons.
', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('5e58b165-7e19-3861-9ae8-dc01f0853c16', 'P131 αναγνωρίζεται ως', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('5495d33a-32ad-39cd-bb3d-1bc24a6e0fe6', 'αναγνωρίζεται ως', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'el', 'altLabel');
INSERT INTO "values" VALUES ('948fb8e0-bbf5-37df-b0a8-cf58b98d8e19', 'P131 wird identifziert durch', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('228ea2e4-e666-3bfc-aa5a-cd8d6b5ebf73', 'wird identifziert durch', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'de', 'altLabel');
INSERT INTO "values" VALUES ('ad9c5e3d-0b12-3594-a3d4-97a46ac6ffd6', 'P131 is identified by', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('0780487c-ed06-378d-a5b1-dd028bc01982', 'is identified by', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'en', 'altLabel');
INSERT INTO "values" VALUES ('4dc22986-42a5-336a-99dc-b894b45ca571', 'P131 est identifié par', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('59fe0df8-1089-3ddd-836f-afa46b3a93b5', 'est identifié par', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('c312b744-07b2-31e7-a51c-e20e231c9545', 'P131 идентифицируется посредством', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('489f1269-3d89-3fb8-aed2-9c202b8574be', 'идентифицируется посредством', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('79ea7e85-a7d0-3f6e-90d2-099b11b944d8', 'P131 é identificado por', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('4157d0d0-9f23-31c4-bce7-23fd9b9c340a', 'é identificado por', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('40da3309-32ea-3ec9-9b9d-f5bf44c03d5f', 'P131 有称号', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('117f6547-d471-36e6-b573-a40620dc55a4', '有称号', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('ea8b2b0d-14b7-389d-846c-b675f46cc0d4', 'This property identifies a name used specifically to identify an E39 Actor. 
This property is a specialisation of P1 is identified by (identifies) is identified by.
', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('8780e6c2-4286-3036-a9b3-ba99e07bd310', 'P132 επικαλύπτεται με', '50060723-772d-3974-864e-8f8c326f169d', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('ba7cdc90-2c72-3147-a7a1-1238d2b08583', 'επικαλύπτεται με', '50060723-772d-3974-864e-8f8c326f169d', 'el', 'altLabel');
INSERT INTO "values" VALUES ('57e3d51d-50e5-37e2-ba02-5cc452623619', 'P132 überlappt mit', '50060723-772d-3974-864e-8f8c326f169d', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('220d55ae-bd75-37c0-b145-71e30c458bce', 'überlappt mit', '50060723-772d-3974-864e-8f8c326f169d', 'de', 'altLabel');
INSERT INTO "values" VALUES ('a70bd3a6-d07c-33c9-92dc-4ae926f20cb1', 'P132 chevauche', '50060723-772d-3974-864e-8f8c326f169d', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('e1873277-2d0f-35d9-a3f4-11fdc8fe5a74', 'chevauche', '50060723-772d-3974-864e-8f8c326f169d', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('4603d60a-ab29-3c6b-b8be-2bc920f1ddeb', 'P132 пересекается с', '50060723-772d-3974-864e-8f8c326f169d', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('c28ba82b-1a85-3b6b-afc2-62426044b5ab', 'пересекается с', '50060723-772d-3974-864e-8f8c326f169d', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('920a6c4d-3ed3-3ccc-bcf2-bad1f39525a4', 'P132 overlaps with', '50060723-772d-3974-864e-8f8c326f169d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('d0ca81b5-03e7-3023-895f-3dabafaa31c6', 'overlaps with', '50060723-772d-3974-864e-8f8c326f169d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('99e1fef6-0f5c-368a-a378-2626a94b7fdf', 'P132 sobrepõe', '50060723-772d-3974-864e-8f8c326f169d', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('7a66d540-8e7a-3ed1-85d9-4db52c7ebeb3', 'sobrepõe', '50060723-772d-3974-864e-8f8c326f169d', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('0b67b30b-2c28-388b-b10d-93f94e5bf47a', 'P132 时空重叠于', '50060723-772d-3974-864e-8f8c326f169d', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('ee1b1d39-8bd2-3246-86e3-86905fea140a', '时空重叠于', '50060723-772d-3974-864e-8f8c326f169d', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('81cd1237-f3fc-3352-908d-59fb6fa4d078', 'This symmetric property allows instances of E4 Period that overlap both temporally and spatially to be related, i,e. they share some spatio-temporal extent.
This property does not imply any ordering or sequence between the two periods, either spatial or temporal.
', '50060723-772d-3974-864e-8f8c326f169d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('896b5e11-0ded-37d8-a2eb-cf72bc7dace1', 'P133 getrennt von', '95473150-07f2-3967-88f3-20b803dd239d', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('e8b81c1d-9635-3216-bde7-dd1752ad9116', 'getrennt von', '95473150-07f2-3967-88f3-20b803dd239d', 'de', 'altLabel');
INSERT INTO "values" VALUES ('aed32438-28b0-3d7f-b3ac-43a0d6f046ba', 'P133 is separated from', '95473150-07f2-3967-88f3-20b803dd239d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('c019d176-159c-3da7-9201-793798290944', 'is separated from', '95473150-07f2-3967-88f3-20b803dd239d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('07a97ec0-1c16-38de-a2f1-84fc97144f16', 'P133 διαχωρίζεται από', '95473150-07f2-3967-88f3-20b803dd239d', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('b6a730ed-5f09-3ed2-8c9d-f3a207e07f4f', 'διαχωρίζεται από', '95473150-07f2-3967-88f3-20b803dd239d', 'el', 'altLabel');
INSERT INTO "values" VALUES ('7a6464d0-0fe0-3409-abbb-3c9fb226453c', 'P133 est séparée de', '95473150-07f2-3967-88f3-20b803dd239d', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('afe84de1-086a-3adc-a7f0-185ae73d98e0', 'est séparée de', '95473150-07f2-3967-88f3-20b803dd239d', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('c5ebb120-16d6-339e-9e5a-d428c32120bf', 'P133 отделен от', '95473150-07f2-3967-88f3-20b803dd239d', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('96e463a5-e6f6-3edd-9e20-8f7d2be01458', 'отделен от', '95473150-07f2-3967-88f3-20b803dd239d', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('8baa9e83-ad70-3d17-a5f7-ef1820c4c663', 'P133 é separado de', '95473150-07f2-3967-88f3-20b803dd239d', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('017f61f7-d67f-3254-9ca1-fa06bc729581', 'é separado de', '95473150-07f2-3967-88f3-20b803dd239d', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('97cada4e-ca35-3c91-84c7-51b3ba671b86', 'P133 时空不重叠于', '95473150-07f2-3967-88f3-20b803dd239d', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('b1043c46-26d7-3a62-9f38-faebedf8e956', '时空不重叠于', '95473150-07f2-3967-88f3-20b803dd239d', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('0eb27021-f5c8-31c3-8909-4c8889d9ce76', 'This symmetric property allows instances of E4 Period that do not overlap both temporally and spatially, to be related i,e. they do not share any spatio-temporal extent.
This property does not imply any ordering or sequence between the two periods either spatial or temporal.
', '95473150-07f2-3967-88f3-20b803dd239d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('077587aa-0047-37fd-9b9f-b03cd7d7fcdd', 'P134 setzte sich fort in', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('4f9c41cd-46b4-3b3f-bc14-c19d9c3ab94f', 'setzte sich fort in', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'de', 'altLabel');
INSERT INTO "values" VALUES ('a079d714-1980-3f5e-b160-00cab82ed017', 'P134 συνέχισε', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('e0643c93-c6fc-36df-96fe-b0d4f27d8b69', 'συνέχισε', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'el', 'altLabel');
INSERT INTO "values" VALUES ('05c46f54-c8ee-3828-abec-60c3c10f4ea0', 'P134 продолжил', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('39344cbf-9b50-302b-bec7-0e370e99db09', 'продолжил', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('380dcaf6-b8f1-3086-84f2-cbeae0041904', 'P134 est la suite de', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('49acbaaf-bf6b-3dd8-8f12-cab123cae9ea', 'est la suite de', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('e1fc83e8-bb85-312d-a402-c41e7a40e4c2', 'P134 continued', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b9bf0011-3bd6-3543-b4cb-aba4cd3b00c5', 'continued', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c229c554-a3c1-3ad3-8dfc-6a3ef1739f0a', 'P134 continuou', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('169aa1db-3015-365f-9c3e-9c234537719a', 'continuou', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('87b78fb5-a970-3d53-81fb-51aa2cf31513', 'P134 延续了', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('c87bdf58-50c2-3a93-9c77-ac7844a5a584', '延续了', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('24409add-4f3a-3ad3-ba2f-8a05bb21e9f2', 'This property associates two instances of E7 Activity, where the domain is considered as an intentional continuation of the range. A continuation of an activity may happen when the continued activity is still ongoing or after the continued activity has completely ended. The continuing activity may have started already before it decided to continue the other one. Continuation implies a coherence of intentions and outcomes of the involved activities.
', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('a0bee057-d7b4-3de1-9843-d9342324dc32', 'P135 created type', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('430f70eb-ff8a-318f-91d5-dea1434c5cd4', 'created type', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'en', 'altLabel');
INSERT INTO "values" VALUES ('01bda5eb-f7c4-3921-83a5-4741abb27b97', 'P135 erschuf Typus', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('c2857178-bf15-3205-a14b-0ce288af6c23', 'erschuf Typus', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'de', 'altLabel');
INSERT INTO "values" VALUES ('1da7c8a5-9def-3dc3-aa3f-15db232dc0bd', 'P135 δημιούργησε τύπο', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('12467882-405c-3d73-a370-ed9c493cd2b7', 'δημιούργησε τύπο', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'el', 'altLabel');
INSERT INTO "values" VALUES ('b1a5a476-423d-3df9-89b3-32138cf4dfa5', 'P135 a créé le type', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('ddfefd4c-1474-3cc8-9883-1bbbed7cd469', 'a créé le type', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('4bca8076-c023-3de5-ba51-66f45095ef42', 'P135 создал тип', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('1de42a8d-4375-3c47-b5fa-1939f4cfabdc', 'создал тип', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('b59ffae8-0676-38e9-bb64-665a561dc6e4', 'P135 criou tipo', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('18ce0536-e7aa-3abc-bf14-8d6e48a8d39b', 'criou tipo', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('2c2b40c7-c587-30b1-a7f7-63ee3dc03c84', 'P135 创造了类型', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('c25dd777-8d51-320b-b1fb-e701936be32f', '创造了类型', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('d0491e50-55db-36b5-95a6-354a9ce872fa', 'This property identifies the E55 Type, which is created in an E83Type Creation activity.', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('3d449fe0-8b16-3b50-91cf-29333839fb9e', 'P136 s’est fondée sur', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('c992a6a1-c281-36c6-84dc-b7dd9930e1cb', 's’est fondée sur', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('a5efd6db-b7dc-325f-be9e-3fdacca0f436', 'P136 был основан на', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('16689a0f-9bb8-39c2-a4e1-b4bfbc096266', 'был основан на', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('b30703fa-4c4e-3637-a76c-99d53485565c', 'P136 stützte sich auf', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('32fd0bdf-1bdf-327c-be9f-c477652c20f7', 'stützte sich auf', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'de', 'altLabel');
INSERT INTO "values" VALUES ('0f3b60c2-a846-3b3b-897f-6191a5dbc77d', 'P136 βασίστηκε σε', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('36118798-f47f-3824-9521-4c2d3b6e1271', 'βασίστηκε σε', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'el', 'altLabel');
INSERT INTO "values" VALUES ('1cafb3ce-36e2-3cff-8239-87f2cf917721', 'P136 was based on', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('c061e4bc-3b0a-3ed8-ab95-1ff70c46f62a', 'was based on', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'en', 'altLabel');
INSERT INTO "values" VALUES ('8ca6b447-28f3-34c4-9737-e38eef39e0f6', 'P136 foi baseado em', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('ec4e96dd-6d35-3566-9ef6-fc15863accbf', 'foi baseado em', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('7acd7720-48f7-32ad-84ad-5d8e40119a5e', 'P136 根据了', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('d5f72a2f-3452-3cbd-a976-a779cc5f7075', '根据了', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('076f5208-4b0f-35b7-b51c-4bfc61c634c9', 'This property identifies one or more items that were used as evidence to declare a new E55 Type.
The examination of these items is often the only objective way to understand the precise characteristics of a new Type. Such items should be deposited in a museum or similar institution for that reason. The taxonomic role renders the specific relationship of each item to the Type, such as "holotype" or "original element".
', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('0cba8ef2-0db9-36ba-be9e-e42ae1c7cfac', 'P137 exemplifies', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('3821c6eb-2861-365b-aab0-29c77ce0ea42', 'exemplifies', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'en', 'altLabel');
INSERT INTO "values" VALUES ('ddd61571-4abd-3957-87ea-24315b7966e9', 'P137 exemplifie', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5983adf5-d179-3b4f-a03a-ef197a03a231', 'exemplifie', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('21474573-ed37-3b52-bd75-4c5ffde01377', 'P137 δειγματίζει', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('1c001653-f2a6-310c-b80f-5b6438e2de39', 'δειγματίζει', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'el', 'altLabel');
INSERT INTO "values" VALUES ('7aad568b-f58e-3645-a9fc-7e6f74e6543e', 'P137 поясняет', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('e476d0ba-f59f-3c4a-ab5a-cb976997e422', 'поясняет', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('c4f7a814-f776-335e-bbdc-020d51046d18', 'P137 erläutert', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('9157a496-c4ec-30ca-b2d3-5c4562fc5590', 'erläutert', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'de', 'altLabel');
INSERT INTO "values" VALUES ('7af5872f-444b-3636-84c8-ee0babafb1d3', 'P137 é exemplificado por', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('e91ef408-4f30-3af7-97b1-d84d59a7ba13', 'é exemplificado por', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('044fd1d8-2ac4-3056-8286-2a2cc916fffb', 'P137 例示了', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('57c3e908-d0ed-3772-89f9-68f9caf4caa6', '例示了', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('2572c8d7-e7e3-38fd-87a8-afee1264b13e', 'This property allows an item to be declared as a particular example of an E55 Type or taxon
	The P137.1 in the taxonomic role property of P137 exemplifies (is exemplified by) allows differentiation of taxonomic roles. The taxonomic role renders the specific relationship of this example to the Type, such as "prototypical", "archetypical", "lectotype", etc. The taxonomic role "lectotype" is not associated with the Type Creation (E83) itself, but selected in a later phase.
', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('a5cd1d01-4366-3037-b0f7-ac99c27a0528', 'P138 παριστάνει', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('e0584ff9-9e45-348c-827a-e494fec0cb5d', 'παριστάνει', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'el', 'altLabel');
INSERT INTO "values" VALUES ('e2bc1763-fb80-369f-adc0-4bb90bbd6ce8', 'P138 represents', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('429c5f12-32f5-3429-99b0-9b19292595a4', 'represents', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'en', 'altLabel');
INSERT INTO "values" VALUES ('e4b4a3a2-7278-3eff-bcb4-1059f59eb45a', 'P138 представляет', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('10ca7ea4-cb71-382e-abc9-45a2c3c99de9', 'представляет', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('bf25b988-b69c-3b73-b61a-2c4a83ac6312', 'P138 stellt dar', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('829708f5-459a-31e3-b604-0b8b4f8a6a13', 'stellt dar', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'de', 'altLabel');
INSERT INTO "values" VALUES ('67b50f98-cda4-3546-abdb-764c98ab1d94', 'P138 représente', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('390bf817-0d17-3752-b26e-3f9647359a38', 'représente', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('f8a0ae38-5a20-3246-b76a-7574adcd1ace', 'P138 representa', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('46d0a462-15f9-3012-9cab-8aee697517b3', 'representa', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('83fb8137-f563-372e-8dbc-9581217687ec', 'P138 描绘了', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('bec2e39f-49df-3720-a421-13bbb70f917c', '描绘了', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('e57ca4eb-183b-34f3-a725-2524927615e1', 'This property establishes the relationship between an E36 Visual Item and the entity that it visually represents.
Any entity may be represented visually. This property is part of the fully developed path from E24 Physical Man-Made Thing through P65 shows visual item (is shown by), E36 Visual Item, P138 represents (has representation) to E1 CRM Entity, which is shortcut by P62depicts (is depicted by). P138.1 mode of representation allows the nature of the representation to be refined.
This property is also used for the relationship between an original and a digitisation of the original by the use of techniques such as digital photography, flatbed or infrared scanning. Digitisation is here seen as a process with a mechanical, causal component rendering the spatial distribution of structural and optical properties of the original and does not necessarily include any visual similarity identifiable by human observation.
', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('dde0b854-6190-3de3-983e-c90939865381', 'P139 a pour autre forme', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('5195c552-c162-3aa5-b234-432705d54db1', 'a pour autre forme', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('bedd615e-1cea-33ce-afc9-2d06f2606c4f', 'P139 имеет альтернативную форму', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('d70e745c-55ff-38f8-a212-4fd7103ee43f', 'имеет альтернативную форму', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('f22cbe50-71ae-3968-8770-d2be56df58b7', 'P139 has alternative form', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('f72dd510-7d95-3087-88c5-3f1b10c1d31e', 'has alternative form', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c0e66f06-9437-3348-828e-9b051cd963e6', 'P139 hat alternative Form', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('edff2d82-1c09-30b3-9e56-0e2742bffdb3', 'hat alternative Form', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'de', 'altLabel');
INSERT INTO "values" VALUES ('87db29dc-f285-3b0e-96ee-e12f93a55511', 'P139 έχει εναλλακτική μορφή', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('d7ab1406-fa6a-3310-9bbb-c09b5c51dd8b', 'έχει εναλλακτική μορφή', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'el', 'altLabel');
INSERT INTO "values" VALUES ('bf8f8743-29a3-3a8b-af5f-69abfda40ba2', 'P139 tem forma alternativa', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('7321f86b-e6d3-3274-87d4-16a090237f0e', 'tem forma alternativa', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('471ee942-5d8d-34b1-b7eb-ea91532395eb', 'P139 有替代称号', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('67a1623e-1dee-3455-b09d-936c9aa52366', '有替代称号', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('80bf82ae-390a-3bd5-a99f-740c5e24549a', 'This property establishes a relationship of equivalence between two instances of E41 Appellation independent from any item identified by them. It is a dynamic asymmetric relationship, where the range expresses the derivative, if such a direction can be established. Otherwise, the relationship is symmetric. The relationship is not transitive.
The equivalence applies to all cases of use of an instance of E41 Appellation. Multiple names assigned to an object, which are not equivalent for all things identified with a specific instance of E41 Appellation, should be modelled as repeated values of P1 is identified by (identifies). 
P139.1 has type allows the type of derivation, such as “transliteration from Latin 1 to ASCII” be refined..
', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('2d8093e9-852f-3864-a3d7-5bbfa8490bc6', 'P140 wies Merkmal zu', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('f1437ada-7eb5-36c4-be87-7555618efecc', 'wies Merkmal zu', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'de', 'altLabel');
INSERT INTO "values" VALUES ('35a2235c-fcb8-3f26-9343-130d6182067a', 'P140 απέδωσε ιδιότητα σε', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('52a85848-38b0-3b80-841e-57cd380bf99a', 'απέδωσε ιδιότητα σε', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'el', 'altLabel');
INSERT INTO "values" VALUES ('48199591-9e78-330b-9c11-90112925c03b', 'P140 assigned attribute to', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('924f30df-295a-313e-8a06-bc68d1add1ca', 'assigned attribute to', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'en', 'altLabel');
INSERT INTO "values" VALUES ('b8de4ff2-63fa-33f8-8df9-b9333bd09f75', 'P140 a affecté un attribut à', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('dbb6925e-c976-363b-9239-bcc262e3e1d8', 'a affecté un attribut à', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('69b813b2-37bc-367a-8f12-d0f113fa13ed', 'P140 присвоил атрибут для', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('b978f404-db8d-3a6d-99be-9b9924a8e5c4', 'присвоил атрибут для', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('7d2c21b2-3e71-3874-add2-07e4532d829e', 'P140 atribuiu atributo para', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('2f0a5754-edcc-3290-9679-47451650e43c', 'atribuiu atributo para', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('96a065e1-0726-3434-9d6d-bd1b6134540a', 'P140 指定属性给', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('533bd973-07b1-3164-973b-85fbf846295e', '指定属性给', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('b795d8fc-77cb-398b-a22a-521b1390ec47', 'This property indicates the item to which an attribute or relation is assigned. ', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('18d90d02-4b25-391d-89b6-474798b6e763', 'P141 assigned', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('de634100-4c32-3bb6-b700-27ab8fa0165f', 'assigned', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'en', 'altLabel');
INSERT INTO "values" VALUES ('88725af7-80f7-3a0c-b1c4-3553c309a1f3', 'P141 присвоил', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'ru', 'prefLabel');
INSERT INTO "values" VALUES ('12bb1e7e-99c8-3dbb-b372-85455e964825', 'присвоил', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'ru', 'altLabel');
INSERT INTO "values" VALUES ('84fb149b-2787-3a26-babb-6dab2824067c', 'P141 wies zu', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('78472982-e2b8-39a1-8047-0f22b4b0048c', 'wies zu', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'de', 'altLabel');
INSERT INTO "values" VALUES ('c5367ad9-3a84-3277-8902-6f095c9fc8a7', 'P141 απέδωσε', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'el', 'prefLabel');
INSERT INTO "values" VALUES ('00cd63c9-9748-33b4-a5f7-aaf7b6f23cbf', 'απέδωσε', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'el', 'altLabel');
INSERT INTO "values" VALUES ('35497a77-2110-3dd5-a981-fbca8b86e0d1', 'P141 a attribué', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'fr', 'prefLabel');
INSERT INTO "values" VALUES ('2738ad10-d43a-38a2-b1ba-31c7490eb2da', 'a attribué', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'fr', 'altLabel');
INSERT INTO "values" VALUES ('4d0d3f0c-0020-3f1b-88ed-251ae26e3eeb', 'P141 atribuiu', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'pt', 'prefLabel');
INSERT INTO "values" VALUES ('d69abf60-c1d1-3910-9640-0c79be962a72', 'atribuiu', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'pt', 'altLabel');
INSERT INTO "values" VALUES ('96a6fbe3-ebee-3b30-a912-570b956d8fb5', 'P141 指定了属性值', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('2e197433-9644-3588-8ab7-6f9e119de9e6', '指定了属性值', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('224b4cb3-e0cc-3c33-be48-3a1a800f60ea', 'This property indicates the attribute that was assigned or the item that was related to the item denoted by a property P140 assigned attribute to in an Attribute assignment action.
', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('5bd6726d-c43c-3200-bb4e-e849ab1a5642', 'P142 used constituent', 'f4734d6b-f54c-3ec2-8c0e-5f98211b13bc', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('31d41817-e9a8-30e1-a2e3-7b953db964a7', 'used constituent', 'f4734d6b-f54c-3ec2-8c0e-5f98211b13bc', 'en', 'altLabel');
INSERT INTO "values" VALUES ('4cfd02d2-4204-3e93-b47e-33c42c2a2d07', 'P142 benutzte Bestandteil', 'f4734d6b-f54c-3ec2-8c0e-5f98211b13bc', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('09ab8b9f-9320-33f3-86e1-45501f388e8e', 'benutzte Bestandteil', 'f4734d6b-f54c-3ec2-8c0e-5f98211b13bc', 'de', 'altLabel');
INSERT INTO "values" VALUES ('a25ca450-7b95-3bcd-8e3e-81112c77b218', 'P142 使用称号构成部分', 'f4734d6b-f54c-3ec2-8c0e-5f98211b13bc', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('312aaee1-1a94-3740-928e-5f56a5e4c0a7', '使用称号构成部分', 'f4734d6b-f54c-3ec2-8c0e-5f98211b13bc', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('f91b71ac-d7aa-31aa-b284-b477f0f15207', 'This property associates the event of assigning an instance of E42 Identifier to an entity, with  the instances of E41 Appellation that were used as elements of the identifier.
', 'f4734d6b-f54c-3ec2-8c0e-5f98211b13bc', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('09be84ba-6e99-3f31-8209-6a8a42fbe22d', 'P143 joined', 'aac583c1-05e4-34fe-aac2-e9bbc9c6d8fd', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('8608fb22-1b91-392a-98ce-b3b435913847', 'joined', 'aac583c1-05e4-34fe-aac2-e9bbc9c6d8fd', 'en', 'altLabel');
INSERT INTO "values" VALUES ('8b0ef780-098f-31ef-b5e9-9fd6917e2761', 'P143 verband', 'aac583c1-05e4-34fe-aac2-e9bbc9c6d8fd', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('72503f04-0fb0-3ab1-a59b-d619c4983d3b', 'verband', 'aac583c1-05e4-34fe-aac2-e9bbc9c6d8fd', 'de', 'altLabel');
INSERT INTO "values" VALUES ('98412baa-e144-34cd-afe5-98d551664063', 'P143 加入了成员', 'aac583c1-05e4-34fe-aac2-e9bbc9c6d8fd', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('fc676d72-e4c1-32b4-844f-2322690f3415', '加入了成员', 'aac583c1-05e4-34fe-aac2-e9bbc9c6d8fd', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('403990a1-d91b-3efe-8ef6-02b079b37858', 'This property identifies the instance of E39 Actor that becomes member of a E74 Group in an E85 Joining.
 	Joining events allow for describing people becoming members of a group with a more detailed path from E74 Group through P144 joined with (gained member by), E85 Joining, P143 joined (was joined by) to E39 Actor, compared to the shortcut offered by P107 has current or former member (is current or former member of).
', 'aac583c1-05e4-34fe-aac2-e9bbc9c6d8fd', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('c3fdac4d-7dbd-3f3e-be97-c16679b784f2', 'P144 joined with', '406ee11a-a430-386f-9087-30c28c677da6', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('1cfe9e87-aa69-3629-a234-3857a99c40c5', 'joined with', '406ee11a-a430-386f-9087-30c28c677da6', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c17fa818-0923-3810-8fe9-b84db069459b', 'P144 verband mit', '406ee11a-a430-386f-9087-30c28c677da6', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('926a1d33-c9ed-37cf-8172-a89886390a48', 'verband mit', '406ee11a-a430-386f-9087-30c28c677da6', 'de', 'altLabel');
INSERT INTO "values" VALUES ('8dbc5050-b501-3c13-8be0-f3e1d6e8aa96', 'P144 加入成员到', '406ee11a-a430-386f-9087-30c28c677da6', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('2cd5f977-72d6-39d7-a4d7-0218e873ae81', '加入成员到', '406ee11a-a430-386f-9087-30c28c677da6', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('37fb962d-82a7-3e33-96e6-1eccde8c4372', 'This property identifies the instance of E74 Group of which an instance of E39 Actor becomes a member through an instance of E85 Joining.
Although a Joining activity normally concerns only one instance of E74 Group, it is possible to imagine circumstances under which becoming member of one Group implies becoming member of another Group as well. 
Joining events allow for describing people becoming members of a group with a more detailed path from E74 Group through P144 joined with (gained member by), E85 Joining, P143 joined (was joined by) to E39 Actor, compared to the shortcut offered by P107 has current or former member (is current or former member of).
The property P144.1 kind of member can be used to specify the type of membership or the role the member has in the group. 
', '406ee11a-a430-386f-9087-30c28c677da6', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('5c433751-8689-372b-8beb-b524d0583b11', 'P145 separated', '7722c7a7-c2ff-3a33-8dd6-829c5b108191', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('a994c395-4cfa-3c8a-8af8-92494652c87a', 'separated', '7722c7a7-c2ff-3a33-8dd6-829c5b108191', 'en', 'altLabel');
INSERT INTO "values" VALUES ('bfa78f7e-b313-326a-a264-ae6a76ef9837', 'P145 entließ', '7722c7a7-c2ff-3a33-8dd6-829c5b108191', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('2a8cd213-bc46-3568-b4ec-7b1ec53b64bb', 'entließ', '7722c7a7-c2ff-3a33-8dd6-829c5b108191', 'de', 'altLabel');
INSERT INTO "values" VALUES ('82ea6c5c-44e9-3a5d-b6a8-fc465280bb79', 'P145 分离了成员', '7722c7a7-c2ff-3a33-8dd6-829c5b108191', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('4ce44adc-4c4a-39fe-a42d-28243563b7e3', '分离了成员', '7722c7a7-c2ff-3a33-8dd6-829c5b108191', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('653aeaba-91a5-3041-8001-1bfd5b019c80', 'This property identifies the instance of E39 Actor that leaves an instance of E74 Group through an instance of E86 Leaving.', '7722c7a7-c2ff-3a33-8dd6-829c5b108191', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('3a59e687-44d1-3ea9-9d32-43bb2ec0cd71', 'P146 separated from', '5bea9c01-5e34-32ce-a1b2-cddc51a6bc7c', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('4e293738-9ddb-326c-9f5f-54b0c8e13e36', 'separated from', '5bea9c01-5e34-32ce-a1b2-cddc51a6bc7c', 'en', 'altLabel');
INSERT INTO "values" VALUES ('dc06e3be-4a2c-3dba-9010-c65f54d17405', 'P146 entließ von', '5bea9c01-5e34-32ce-a1b2-cddc51a6bc7c', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('7336a4fa-3a24-3ee7-ab86-7a8380d4b90e', 'entließ von', '5bea9c01-5e34-32ce-a1b2-cddc51a6bc7c', 'de', 'altLabel');
INSERT INTO "values" VALUES ('1f725962-db5f-36f8-bed1-78a933cde3d0', 'P146 脱离了群组', '5bea9c01-5e34-32ce-a1b2-cddc51a6bc7c', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('31eea279-0e1e-3394-9267-258480456f5f', '脱离了群组', '5bea9c01-5e34-32ce-a1b2-cddc51a6bc7c', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('fe116b98-c0f0-3dd9-967c-5f66bfb518fb', 'This property identifies the instance of E74 Group an instance of E39 Actor leaves through an instance of E86 Leaving.
Although a Leaving activity normally concerns only one instance of E74 Group, it is possible to imagine circumstances under which leaving one E74 Group implies leaving another E74 Group as well.
', '5bea9c01-5e34-32ce-a1b2-cddc51a6bc7c', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('850e3327-b142-39e4-b1ed-292a1c83840f', 'P147 curated', '9c8d34b1-0379-35d6-9470-9ad11efdef5a', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('4a499ddd-92b7-3707-ae87-07b0d4d5d161', 'curated', '9c8d34b1-0379-35d6-9470-9ad11efdef5a', 'en', 'altLabel');
INSERT INTO "values" VALUES ('a64a6610-e4a1-322a-8cc1-88bbc2bb5f02', 'P147 betreute kuratorisch', '9c8d34b1-0379-35d6-9470-9ad11efdef5a', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('4186608e-dd54-354b-b57d-55770d4656dc', 'betreute kuratorisch', '9c8d34b1-0379-35d6-9470-9ad11efdef5a', 'de', 'altLabel');
INSERT INTO "values" VALUES ('a1b5f009-b3e8-36d0-8b50-efc0650df539', 'P147 典藏管理了', '9c8d34b1-0379-35d6-9470-9ad11efdef5a', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('fca71f64-8078-3edd-94a8-49aa78163589', '典藏管理了', '9c8d34b1-0379-35d6-9470-9ad11efdef5a', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('bddbc386-3a39-3a79-bcf7-55d3621babfb', 'This property associates an instance of E87 Curation Activity with the instance of E78 Collection that is subject of that  curation activity.
', '9c8d34b1-0379-35d6-9470-9ad11efdef5a', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('f7825a94-39a9-3280-ba2d-6e150cd57d93', 'P148 has component', 'df779f07-03dd-3ed7-91aa-025a71c95957', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('2b909a2e-5dc4-310d-8f28-6d51ee561bba', 'has component', 'df779f07-03dd-3ed7-91aa-025a71c95957', 'en', 'altLabel');
INSERT INTO "values" VALUES ('374e11a3-8e53-37b8-b4b6-d04fe9fd898e', 'P148 hat Bestandteil', 'df779f07-03dd-3ed7-91aa-025a71c95957', 'de', 'prefLabel');
INSERT INTO "values" VALUES ('3409a493-954a-3a16-a2b0-3dd04edf4482', 'hat Bestandteil', 'df779f07-03dd-3ed7-91aa-025a71c95957', 'de', 'altLabel');
INSERT INTO "values" VALUES ('5a57e1d0-b984-3305-b48f-5f0bb5bd6d80', 'P148 有组件', 'df779f07-03dd-3ed7-91aa-025a71c95957', 'zh', 'prefLabel');
INSERT INTO "values" VALUES ('f54529f5-9f3b-3afa-8a72-6b817490a087', '有组件', 'df779f07-03dd-3ed7-91aa-025a71c95957', 'zh', 'altLabel');
INSERT INTO "values" VALUES ('43b8b9c0-3b2a-3ed9-a76b-f657cdc6a0f1', 'This property associates an instance of E89 Propositional Object with a structural part of it that is by itself an instance of E89 Propositional Object.', 'df779f07-03dd-3ed7-91aa-025a71c95957', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('36e35c1c-39a6-3be1-91af-52ecc5365425', 'P149 is identified by', 'c6888cc6-3b5e-373c-a6ba-6e6bc24773c6', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('609abb23-bd80-3cfa-b3ea-d50e0aec8536', 'is identified by', 'c6888cc6-3b5e-373c-a6ba-6e6bc24773c6', 'en', 'altLabel');
INSERT INTO "values" VALUES ('71bd5632-9f0a-3689-af44-319a8d974678', 'This property identifies an instance of E28 Conceptual Object using an instance of E75 Conceptual Object Appellation.', 'c6888cc6-3b5e-373c-a6ba-6e6bc24773c6', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('a71ba302-8fd5-3661-a3bb-6bc84273994f', 'P150 defines typical parts of', '75825fa7-ab9a-3b62-b7e8-250712914631', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('7a86065f-1ab8-3c1a-a582-db3e9a971f9e', 'defines typical parts of', '75825fa7-ab9a-3b62-b7e8-250712914631', 'en', 'altLabel');
INSERT INTO "values" VALUES ('77998e48-1d36-313d-ba5a-52c7f0ab8082', 'The property "broaderPartitive" associates an instance of E55 Type “A” with an instance of E55 Type “B”, when items of type “A” typically form part of items of type “B”, such as “car motors” and “cars”.
It allows Types to be organised into hierarchies. This is the sense of "broader term partitive (BTP)" as defined in ISO 2788 and “broaderPartitive” in SKOS.
', '75825fa7-ab9a-3b62-b7e8-250712914631', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('840a1724-7412-31e6-83bd-913e3f23f4d0', 'P151 was formed from', '63c5d303-2789-3999-8496-297343edf6dc', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('5b9b7f67-618e-38aa-9a91-1e44f37aa2a3', 'was formed from', '63c5d303-2789-3999-8496-297343edf6dc', 'en', 'altLabel');
INSERT INTO "values" VALUES ('b2d75857-8317-321b-96ef-ab6a79f2628c', 'This property associates an instance of E66 Formation with an instance of E74 Group from which the new group was formed preserving a sense of continuity such as in mission, membership or tradition.
	', '63c5d303-2789-3999-8496-297343edf6dc', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('362937eb-ceaa-3517-8805-172179695bc3', 'P152 has parent', 'e28841b2-0d53-3f91-afbf-3694a6236a5d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('c14ba6c8-7352-3ac3-a4b3-0c57d9905779', 'has parent', 'e28841b2-0d53-3f91-afbf-3694a6236a5d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('27bbdc37-157a-3828-a5e5-b8919cec72da', 'This property associates an instance of E21 Person with another instance of E21 Person who plays the role of the first instance’s parent, regardless of whether the relationship is biological parenthood, assumed or pretended biological parenthood or an equivalent legal status of rights and obligations obtained by a social or legal act. 
	This property is, among others, a shortcut of the fully developed paths from ‘E21Person’ through ‘P98i was born’, ‘E67 Birth’, ‘P96 by mother’ to ‘E21 Person’, and from ‘E21Person’ through ‘P98i was born’, ‘E67 Birth’, ‘P97 from father’ to ‘E21 Person’.
	', 'e28841b2-0d53-3f91-afbf-3694a6236a5d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('08b934b5-b943-35fa-b3ed-0a4205237f5b', 'P156 occupies', '222f5899-aa3f-3d52-a784-e5a0a68722f2', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('495f2b19-77c7-378e-8b90-3dfebf6bcf73', 'occupies', '222f5899-aa3f-3d52-a784-e5a0a68722f2', 'en', 'altLabel');
INSERT INTO "values" VALUES ('9ae67291-3b9d-317b-8a07-0e04feacda62', 'This property describes the largest volume in space that an instance of E18 Physical Thing has occupied at any time during its existence, with respect to the reference space relative to itself. This allows you to describe the thing itself as a place that may contain other things, such as a box that may contain coins. In other words, it is the volume that contains all the points which the thing has covered at some time during its existence. In the case of an E26 Physical Feature the default reference space is the one in which the object that bears the feature or at least the surrounding matter of the feature is at rest. In this case there is a 1:1 relation of E26 Feature and E53 Place. For simplicity of implementation multiple inheritance (E26 Feature IsA E53 Place) may be a practical approach.

For instances of E19 Physical Objects the default reference space is the one which is at rest to the object itself, i.e. which moves together with the object. We include in the occupied space the space filled by the matter of the physical thing and all its inner spaces. 

This property is a subproperty of P161 has spatial projection because it refers to its own domain as reference space for its range, whereas P161 has spatial projection may refer to a place in terms of any reference space. For some instances of E18 Physical Object the relative stability of form may not be sufficient to define a useful local reference space, for instance for an amoeba. In such cases the fully developed path to an external reference space and using a temporal validity component may be adequate to determine the place they have occupied.

In contrast to P156  occupies, the property P53 has former or current location identifies an instance of E53 Place at which a thing is or has been for some unspecified time span.  Further it does not constrain the reference space of the referred instance of P53 Place.
	', '222f5899-aa3f-3d52-a784-e5a0a68722f2', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('282ee3f8-b9be-3afd-abaa-5365a354c00f', 'P157 is at rest relative to', 'be7f5fbc-6abd-33cd-8cb0-a7e447068b20', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('8864e85d-8518-36d0-b6ab-ef968e883c30', 'is at rest relative to', 'be7f5fbc-6abd-33cd-8cb0-a7e447068b20', 'en', 'altLabel');
INSERT INTO "values" VALUES ('8c862475-90bd-3dfe-aca7-34c86360871d', 'This property associates an instance of P53 Place with the instance of E18 Physical Thing that determines a reference space for this instance of P53 Place by being at rest with respect to this reference space. The relative stability of form of an E18 Physical Thing defines its default reference space. The reference space is not spatially limited to the referred thing. For example, a ship determines a reference space in terms of which other ships in its neighbourhood may be described. Larger constellations of matter, such as continental plates, may comprise many physical features that are at rest with them and define the same reference space.
	', 'be7f5fbc-6abd-33cd-8cb0-a7e447068b20', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('7e1b2072-c2a0-3371-8b92-224159980665', 'P160 has temporal projection', '6f3ce351-dc26-30bf-8c50-9392f873968d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('1258f1c5-d5b5-3ec8-bbf7-135cd16dfd34', 'has temporal projection', '6f3ce351-dc26-30bf-8c50-9392f873968d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('62ca2d31-c17f-3353-a76b-7900d3b1f86a', 'This property describes the temporal projection of an instance of an E92 Spacetime Volume. The property P4 has time-span is the same as P160 has temporal projection if it is used to document an instance of E4 Period or any subclass of it. 
	', '6f3ce351-dc26-30bf-8c50-9392f873968d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('f02bf8c5-b4ed-3235-acb1-78b5ab7def3f', 'P161 has spatial projection', 'db25f50b-28f3-3041-b091-8bb7d2557856', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('32e7ccd4-e243-3708-afa7-3560bfb88fbf', 'has spatial projection', 'db25f50b-28f3-3041-b091-8bb7d2557856', 'en', 'altLabel');
INSERT INTO "values" VALUES ('584854e5-18d6-34f9-accc-46f99f60e832', 'This property associates an instance of a E92 Spacetime Volume with an instance of E53 Place that is the result of the spatial projection of the instance of a E92 Spacetime Volume on a reference space. In general there can be more than one useful reference space to describe the spatial projection of a spacetime volume, such as that of a battle ship versus that of the seafloor. Therefore the projection is not unique.
This is part of the fully developed path that is shortcut by P7took place at (witnessed).The more fully developed path from E4 Period through P161 has spatial projection, E53 Place, P89 falls within (contains) to E53 Place. 
	', 'db25f50b-28f3-3041-b091-8bb7d2557856', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('59a076d3-0df2-3ae2-888e-9fe70d150437', 'P164 during', '68633428-a835-3af2-9e8e-ac1ba713d4c8', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('a88b070c-a43c-3237-b2a5-d34b3f9d727c', 'during', '68633428-a835-3af2-9e8e-ac1ba713d4c8', 'en', 'altLabel');
INSERT INTO "values" VALUES ('6e1ab909-8ef0-3460-b7fc-aca549a1d918', 'This property relates an E93 Presence with an arbitrary E52 Time-Span that defines the section of the spacetime volume that this instance of E93 Presence is related to by P166 was a presence of (had presence) that is concerned by this instance of E93 Presence. 
	', '68633428-a835-3af2-9e8e-ac1ba713d4c8', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('93324fc4-6b4c-3e12-9875-19ee22c70ef7', 'P165 incorporates', 'a5a812b2-d786-38db-928f-1df9f416ab59', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('13e9a6ff-bb58-310f-b423-f9439a5c3f39', 'incorporates', 'a5a812b2-d786-38db-928f-1df9f416ab59', 'en', 'altLabel');
INSERT INTO "values" VALUES ('fc3c9006-24db-3070-a62b-5c0c0bbc0ed8', 'This property associates an instance of E73 Information Object with an instance of E90 Symbolic Object (or any of its subclasses) that was included in it.
This property makes it possible to recognise the autonomous status of the incorporated signs, which were created in a distinct context, and can be incorporated in many distinct self-contained expressions, and to highlight the difference between structural and accidental whole-part relationships between conceptual entities.
It accounts for many cultural facts that are quite frequent and significant: the inclusion of a poem in an anthology, the re-use of an operatic aria in a new opera, the use of a reproduction of a painting for a book cover or a CD booklet, the integration of textual quotations, the presence of lyrics in a song that sets those lyrics to music, the presence of the text of a play in a movie based on that play, etc.
In particular, this property allows for modelling relationships of different levels of symbolic specificity, such as the natural language words making up a particular text, the characters making up the words and punctuation, the choice of fonts and page layout for the characters.
A digital photograph of a manuscript page incorporates the text of the manuscript page.
	', 'a5a812b2-d786-38db-928f-1df9f416ab59', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('78eb2649-56d2-30e1-95e8-e1c6257fd605', 'P166 was a presence of', '6560a44c-f6b7-3c67-bbaf-c60585bc56d9', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('80352e08-6d4c-3f87-b57c-c65622996565', 'was a presence of', '6560a44c-f6b7-3c67-bbaf-c60585bc56d9', 'en', 'altLabel');
INSERT INTO "values" VALUES ('31a625a6-af66-3de4-9189-94097df07528', 'This property relates an E93 Presence with the STV it is part of… 
	', '6560a44c-f6b7-3c67-bbaf-c60585bc56d9', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('5430949d-789a-3b8f-b41a-4b95905d21cc', 'P167 was at', 'da115774-50f3-3292-97dc-da1cbb527ca5', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('b22ff3ee-b4b2-3247-8ef3-41f1471a0347', 'was at', 'da115774-50f3-3292-97dc-da1cbb527ca5', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c1d0df03-010b-35ff-9513-d54d4084b043', 'This property points to a wider area in which my thing /event was… 
	', 'da115774-50f3-3292-97dc-da1cbb527ca5', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('a508f2c0-0872-34d3-8a78-bba28b8e0cc1', 'P168 place is defined by ', '81fd2793-2d69-37fe-8027-ff705a54ce3d', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('57cf497e-5f7e-3b9b-b093-1d354fddf9a3', 'place is defined by ', '81fd2793-2d69-37fe-8027-ff705a54ce3d', 'en', 'altLabel');
INSERT INTO "values" VALUES ('33411498-5d7b-31f3-89e6-d1a3419ad0d5', 'This property associates an instance of E53 Place with an instance of E94 Space Primitive that defines it. Syntactic variants or use of different scripts may result in multiple instances of E94 Space Primitive defining exactly the same place. Transformations between different reference systems in general result in new definitions of places approximating each other and not in alternative definitions. Note that it is possible for a place to be defined by phenomena causal to it or other forms of identification rather than by an instance of E94 Space Primitive. In this case, this property must not be used for approximating the respective instance of E53 Place with an instance of E94 Space Primitive. 
	', '81fd2793-2d69-37fe-8027-ff705a54ce3d', 'en-US', 'scopeNote');
INSERT INTO "values" VALUES ('b1c551f4-95ab-319e-b044-854dbaac0cc6', 'BM.PX is related to', '7cd91c49-743e-3eed-ad91-d993b09af867', 'en', 'prefLabel');
INSERT INTO "values" VALUES ('8b06ab46-deb0-304c-a9b3-8e7039d4f0f8', 'is related to', '7cd91c49-743e-3eed-ad91-d993b09af867', 'en', 'altLabel');
INSERT INTO "values" VALUES ('c6ae539a-c840-3ee7-aa47-301ecba86dfd', 'Relates E18 to E1', '7cd91c49-743e-3eed-ad91-d993b09af867', 'en-US', 'scopeNote');


-- Completed on 2016-05-09 13:33:50 PDT

--
-- PostgreSQL database dump complete
--


--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.1
-- Dumped by pg_dump version 9.5.1

-- Started on 2016-05-09 13:34:44 PDT

-- SET statement_timeout = 0;
-- SET lock_timeout = 0;
-- SET client_encoding = 'UTF8';
-- SET standard_conforming_strings = on;
-- SET check_function_bodies = false;
-- SET client_min_messages = warning;
-- SET row_security = off;

-- SET search_path = public, pg_catalog;

--
-- TOC entry 3857 (class 0 OID 491631)
-- Dependencies: 240
-- Data for Name: relations; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO relations VALUES ('884e96c0-95b5-4698-9e93-15ef43917309', 'c03db431-4564-34eb-ba86-4c8169e4276c', '70064b58-4490-3d09-b463-fd18defae21f', 'subClassOf');
INSERT INTO relations VALUES ('e5ac53c2-fd99-4aac-82d5-94e25ec37e4a', '70064b58-4490-3d09-b463-fd18defae21f', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'subClassOf');
INSERT INTO relations VALUES ('326c827c-121d-465b-a2a2-bd12087d7c25', '70064b58-4490-3d09-b463-fd18defae21f', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'subClassOf');
INSERT INTO relations VALUES ('e2c6109e-d1fb-4de1-ada2-d5652e8b6aef', '94ffd715-18f7-310a-bee2-010d800be058', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'subClassOf');
INSERT INTO relations VALUES ('c630c086-ad5d-40b3-9b4e-682c4d1df7c8', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'subClassOf');
INSERT INTO relations VALUES ('03e3fa57-d50e-4a25-9cad-8c5cd6d9564a', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', 'subClassOf');
INSERT INTO relations VALUES ('f2cbe1f3-22b6-4310-83d4-8c9ebe1edaa6', 'a6ef9479-248e-3847-bf68-9c9017b0add8', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'subClassOf');
INSERT INTO relations VALUES ('a63c1fb5-3b74-4043-897d-34a153a226b4', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', 'subClassOf');
INSERT INTO relations VALUES ('25b8f0ac-1d68-4969-ac07-982cdd433e37', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'subClassOf');
INSERT INTO relations VALUES ('5c3a9c48-503b-44bf-8481-901344f41c38', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'subClassOf');
INSERT INTO relations VALUES ('26bc283f-0fe6-4aee-b41d-79f609eaaedd', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'subClassOf');
INSERT INTO relations VALUES ('3101b90c-2ff7-4deb-8e2d-b1ee9b18c8ea', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'subClassOf');
INSERT INTO relations VALUES ('88f9f8a7-963b-4c22-a3d6-4291c0990ea3', '255bba42-8ffb-3796-9caa-807179a20d9a', 'f27afcc0-7657-3c5e-8314-b913c562759e', 'subClassOf');
INSERT INTO relations VALUES ('502049b1-0e84-44db-bb34-0e048edda27a', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'subClassOf');
INSERT INTO relations VALUES ('44489f96-4c2b-4360-a6ce-63f556b35bee', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'subClassOf');
INSERT INTO relations VALUES ('28fb6684-9651-4a1e-b12d-e5c6797ea7ed', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'subClassOf');
INSERT INTO relations VALUES ('ed9702fe-8eee-4f8d-bb77-8fccacbf9708', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', 'subClassOf');
INSERT INTO relations VALUES ('2364d170-36ba-4948-bb7c-533040c6521d', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'subClassOf');
INSERT INTO relations VALUES ('d19add68-ae3a-419f-ae0f-c9c10823fa06', '78b224a2-9271-3716-8c2e-c82302cdae9c', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'subClassOf');
INSERT INTO relations VALUES ('9089266d-06fd-4de6-b58a-5b7d0a621f3c', '94ffd715-18f7-310a-bee2-010d800be058', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'subClassOf');
INSERT INTO relations VALUES ('cf72528c-fcf8-47c0-b119-f5ce01aadb6a', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'subClassOf');
INSERT INTO relations VALUES ('f96f8fc1-3f3b-4e40-b88e-2ceee1e02af6', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', '2c287084-c289-36b2-8328-853e381f0ed4', 'subClassOf');
INSERT INTO relations VALUES ('c061b8a5-0d44-44e2-aa0a-58a61e647400', '2c287084-c289-36b2-8328-853e381f0ed4', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'subClassOf');
INSERT INTO relations VALUES ('eb5ff719-7187-448c-841e-9d005fb87750', 'af051b0a-be2f-39da-8f46-429a714e242c', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'subClassOf');
INSERT INTO relations VALUES ('4c679593-9894-4af7-b485-1ab0eca50ec9', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'subClassOf');
INSERT INTO relations VALUES ('d7edf5e5-147a-46db-944f-35becd5e04c4', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'subClassOf');
INSERT INTO relations VALUES ('b34466dc-1b1b-4135-a636-9e75519c7cf9', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'subClassOf');
INSERT INTO relations VALUES ('ba6b541f-6b58-4be8-ac82-d0f18246de25', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'subClassOf');
INSERT INTO relations VALUES ('307b4075-5f71-4011-b027-39ce12533469', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'subClassOf');
INSERT INTO relations VALUES ('f7103c84-63d7-42fe-b3a8-6d081b797e3a', '2bc61bb4-384d-3427-bc89-2320be9896f2', '4bb246c3-e51e-32f9-a466-3003a17493c5', 'subClassOf');
INSERT INTO relations VALUES ('18d9f7c9-8ae2-441f-8471-1c8586ceac2c', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'subClassOf');
INSERT INTO relations VALUES ('be5fb91f-5f34-409f-a74d-6ca8b04f16a4', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'a89d6e8b-6f86-33cd-9084-b6c77165bed1', 'subClassOf');
INSERT INTO relations VALUES ('c4835c89-ab3f-4e8e-9d3b-58d20c6c8291', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'subClassOf');
INSERT INTO relations VALUES ('b3418727-0f43-4f4e-bbb6-3c5698223427', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'subClassOf');
INSERT INTO relations VALUES ('f2b30b07-34c3-4b1f-ac2f-617932996bd1', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'subClassOf');
INSERT INTO relations VALUES ('5f687b6b-0f3c-49fc-b0be-451d35f4a139', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', '84a17c0c-78f2-3607-ba85-da1fc47def5a', 'subClassOf');
INSERT INTO relations VALUES ('79bd6789-1bf1-4633-a11c-45ce5c88e97e', '84a17c0c-78f2-3607-ba85-da1fc47def5a', '0df9cb10-1203-3efd-8d9e-448f5b02506b', 'subClassOf');
INSERT INTO relations VALUES ('06e2ba3e-e354-45f3-9a18-2c1d40f38322', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'subClassOf');
INSERT INTO relations VALUES ('33972aef-5f0e-41ca-b171-ae1cf3157e10', 'fa1b039d-00cd-36e8-b03c-247176a6368d', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'subClassOf');
INSERT INTO relations VALUES ('3c5d7f4c-5454-49bd-a550-89a1a61749bf', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', '21fa6d60-095b-3044-9ca3-088e2cdab1f0', 'subClassOf');
INSERT INTO relations VALUES ('e1854bfc-c2c0-471c-ab56-2a51b61cdf28', 'fa1b039d-00cd-36e8-b03c-247176a6368d', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'subClassOf');
INSERT INTO relations VALUES ('8b3db4e3-7457-4e9f-9054-c9fa0747b170', 'b43d4537-6674-37cb-af6e-834b5d63c978', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'subClassOf');
INSERT INTO relations VALUES ('abd0cfe6-46fb-4c57-b3a0-2245758808ba', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'subClassOf');
INSERT INTO relations VALUES ('5a627798-7843-4be0-9631-90317e839bc8', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', '7e62fc5e-947d-3806-bcd7-ce6bb716b6fe', 'subClassOf');
INSERT INTO relations VALUES ('f00518f9-ab2f-4dab-89f9-9146a7e4f9b2', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', '9cc69985-2a19-3fa6-abf5-addf02a52b90', 'subClassOf');
INSERT INTO relations VALUES ('fcd96a74-89e1-4e23-bcf2-84921d8a3293', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'af051b0a-be2f-39da-8f46-429a714e242c', 'subClassOf');
INSERT INTO relations VALUES ('3629f592-2a16-41e4-9be1-f29f757c41e6', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', '40a8beed-541b-35cd-b287-b7c345f998fe', 'subClassOf');
INSERT INTO relations VALUES ('2d338cc9-03fa-4fd7-ad1c-97a60fac49fe', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'subClassOf');
INSERT INTO relations VALUES ('009d9eb4-e623-4404-bc6b-7ecba0c38467', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'subClassOf');
INSERT INTO relations VALUES ('088e4a2a-1363-4d65-a7b7-ff39b51ee266', 'b43d4537-6674-37cb-af6e-834b5d63c978', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'subClassOf');
INSERT INTO relations VALUES ('a5a63d11-08b6-41f5-be41-2f07c863bd4a', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'subClassOf');
INSERT INTO relations VALUES ('d20f0d16-4615-4456-b5b5-8ebf19eea03e', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'ac777d6e-452a-3a10-80c9-5190b5d9f6f2', 'subClassOf');
INSERT INTO relations VALUES ('68e37f9c-acf1-4e7b-9a9a-641707604c4a', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'subClassOf');
INSERT INTO relations VALUES ('b759e8c0-3993-425a-aa85-f29a370581b6', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', '35bfed01-08dc-34b9-94a0-42facd1291ac', 'subClassOf');
INSERT INTO relations VALUES ('94f86512-0c35-4070-87b7-97e34265e4f1', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'e276711d-008c-3380-934b-e048a6a0d665', 'subClassOf');
INSERT INTO relations VALUES ('7f45af9f-ff4e-4860-8bc2-08c2f17cec94', 'b43d4537-6674-37cb-af6e-834b5d63c978', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'subClassOf');
INSERT INTO relations VALUES ('40953ef2-1889-488d-88ff-d4125455a3f6', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'c8b36269-f507-32fc-8624-2a9404390719', 'subClassOf');
INSERT INTO relations VALUES ('eb4bf9c2-2dad-48a0-88d4-02eb605518bf', 'b43d4537-6674-37cb-af6e-834b5d63c978', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'subClassOf');
INSERT INTO relations VALUES ('2dcfc69b-2734-40fa-9492-2c8b51c1eb56', 'c03db431-4564-34eb-ba86-4c8169e4276c', '9d55628a-0085-3b88-a939-b7a327263f53', 'subClassOf');
INSERT INTO relations VALUES ('2ab790ba-5470-4055-86a2-0473e3062649', 'c03db431-4564-34eb-ba86-4c8169e4276c', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'subClassOf');
INSERT INTO relations VALUES ('64923d59-5379-4451-b3a3-005546546b1f', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'subClassOf');
INSERT INTO relations VALUES ('e289128e-dfb2-4629-b664-d1a8143d63f5', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'subClassOf');
INSERT INTO relations VALUES ('8023688e-7c7f-4fc0-98e6-2d02e73d2bed', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'subClassOf');
INSERT INTO relations VALUES ('6c0cc4a2-de2c-4c3c-a802-6b8fd0951ff7', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'subClassOf');
INSERT INTO relations VALUES ('c33e1942-9b96-4e62-8620-768e2fa975f4', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'subClassOf');
INSERT INTO relations VALUES ('324af9b3-fc9e-4f28-a528-5de41e422e20', '8471e471-3045-3269-a9b8-86d0e6065176', '30c58f1c-03f4-36f8-9f50-4fefc84bb0a6', 'subClassOf');
INSERT INTO relations VALUES ('3e6042d9-26d1-495e-a58c-63b3ff813e1d', '8471e471-3045-3269-a9b8-86d0e6065176', 'fd8302b4-921b-300c-a9bf-c50d92418797', 'subClassOf');
INSERT INTO relations VALUES ('00cd8daa-9e6e-4a84-a939-a08d1fe0776f', '8471e471-3045-3269-a9b8-86d0e6065176', '6e30fbe8-5a0d-3de8-be79-4ec6ebf4db39', 'subClassOf');
INSERT INTO relations VALUES ('815073d7-f600-428c-bc49-0aecca6b42d3', 'a6ef9479-248e-3847-bf68-9c9017b0add8', '255bba42-8ffb-3796-9caa-807179a20d9a', 'subClassOf');
INSERT INTO relations VALUES ('f1389353-c63c-42a9-a383-5a0140d9edb0', 'a6ef9479-248e-3847-bf68-9c9017b0add8', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'subClassOf');
INSERT INTO relations VALUES ('abb9993d-79b0-4391-8340-78e3bd446303', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'subClassOf');
INSERT INTO relations VALUES ('49882509-e64d-4682-a03f-9f63646964d1', '255bba42-8ffb-3796-9caa-807179a20d9a', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', 'subClassOf');
INSERT INTO relations VALUES ('8d89c98d-0bcc-4b28-b1df-2a4d55df606d', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'subClassOf');
INSERT INTO relations VALUES ('9800acc7-871e-44d1-b1e8-ce855de898d9', '255bba42-8ffb-3796-9caa-807179a20d9a', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', 'subClassOf');
INSERT INTO relations VALUES ('8ee76e08-cfb1-4cf8-b9fe-16d9d9e2d49c', '255bba42-8ffb-3796-9caa-807179a20d9a', '07fcf604-d28f-3993-90fa-d301c4004913', 'subClassOf');
INSERT INTO relations VALUES ('d32f225e-687b-4460-8ea2-adae1bdac592', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', 'subClassOf');
INSERT INTO relations VALUES ('abcdca48-83e6-4f4e-9d48-3cb88f45285e', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'subClassOf');
INSERT INTO relations VALUES ('4b5d19f8-81fc-4789-b608-e71142fe084d', 'af1d24cc-428c-3689-bbd1-726d62ec5595', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'subClassOf');
INSERT INTO relations VALUES ('64d77c23-96e6-482a-8b8c-bcc3347bbacb', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'subClassOf');
INSERT INTO relations VALUES ('a1e24f13-22e5-47a1-b3d2-c0c90f97bd2e', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'subClassOf');
INSERT INTO relations VALUES ('e92c8954-9556-432d-95ca-9aba2bb7ad53', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'subClassOf');
INSERT INTO relations VALUES ('454e53e3-46b1-4add-b3c1-da2f759ec0b0', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'subClassOf');
INSERT INTO relations VALUES ('bd1bfc73-bf27-476c-b98d-5109024a44df', 'af051b0a-be2f-39da-8f46-429a714e242c', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'subClassOf');
INSERT INTO relations VALUES ('4daafba3-daf8-49ba-bb5c-87cb55113416', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'subClassOf');
INSERT INTO relations VALUES ('ba97cb15-baca-4d2c-816c-5891b4f2bb0a', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'subClassOf');
INSERT INTO relations VALUES ('971bb1b8-8863-4a62-b540-6ac6ad9bf8d6', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'subClassOf');
INSERT INTO relations VALUES ('2379d676-34e7-48d8-82e6-b069446f3b7d', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', '048fe43e-349a-3dda-9524-7046dcbf7287', 'subClassOf');
INSERT INTO relations VALUES ('65b32a9d-4fbe-4a09-a42a-2243b48a0719', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'subClassOf');
INSERT INTO relations VALUES ('434a0452-38fd-48c4-9824-cbc81f83c8ec', '255bba42-8ffb-3796-9caa-807179a20d9a', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'subClassOf');
INSERT INTO relations VALUES ('1534319d-44e4-4b6d-9ce1-c19afacd657b', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', 'subClassOf');
INSERT INTO relations VALUES ('89bb178a-983c-4414-aaff-3e61445b761f', 'b43d4537-6674-37cb-af6e-834b5d63c978', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'subClassOf');
INSERT INTO relations VALUES ('b0f8bb90-22eb-4499-b5ae-249e898a27c4', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'subClassOf');
INSERT INTO relations VALUES ('938cb685-0fa9-43b8-9397-f12b2cc210c6', 'fd416d6d-2d73-35c7-a9a6-6e43e89d9fe9', 'b850529a-18cd-3fbc-9ab2-e1302ee000a6', 'subClassOf');
INSERT INTO relations VALUES ('3d0b1e02-aabc-463e-9be1-e613bb211312', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'b4f509a5-bf1f-3b1b-875f-e4dade14f862', 'subClassOf');
INSERT INTO relations VALUES ('38c562e3-0600-490a-b0d5-8e007d0f09cf', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', '2c5fbf8d-b6ca-39f4-8ee7-5522732fe77e', 'subClassOf');
INSERT INTO relations VALUES ('846217fd-ed79-44b0-9574-91f321c0e6d7', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'de74c0db-a5fa-3f45-8684-344c379e6b0d', 'subClassOf');
INSERT INTO relations VALUES ('cdfc91f5-1987-4b9a-8283-d719b4e9921d', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', 'subClassOf');
INSERT INTO relations VALUES ('9609147a-cee2-4548-a10d-62691c9e894c', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'subClassOf');
INSERT INTO relations VALUES ('83c91ae3-51a3-465b-b69a-2103e2eb0d07', '78b224a2-9271-3716-8c2e-c82302cdae9c', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'subClassOf');
INSERT INTO relations VALUES ('c3cc090c-970f-4301-ab61-3aa99e30ec70', 'c03db431-4564-34eb-ba86-4c8169e4276c', '94ffd715-18f7-310a-bee2-010d800be058', 'subClassOf');
INSERT INTO relations VALUES ('262ea4a3-0124-4b7c-a49b-2f99e462d07a', '94ffd715-18f7-310a-bee2-010d800be058', 'b9af2b98-3c9d-34f1-9a87-f5eb071fb53d', 'subClassOf');
INSERT INTO relations VALUES ('3c3067d0-d887-41d6-958e-cad78a7ab249', '94ffd715-18f7-310a-bee2-010d800be058', '1036c7f1-ea95-3ad8-886f-849ca10f9584', 'subClassOf');
INSERT INTO relations VALUES ('fd0a96f2-07d8-44dd-9f30-f90b40088987', 'c03db431-4564-34eb-ba86-4c8169e4276c', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'hasDomainClass');
INSERT INTO relations VALUES ('c3253cb2-6ba6-48ba-8d7f-cbeaacba1d83', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'hasRangeClass');
INSERT INTO relations VALUES ('532466ac-179f-46af-a3bb-6f13297d090e', 'c03db431-4564-34eb-ba86-4c8169e4276c', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'hasDomainClass');
INSERT INTO relations VALUES ('9b13a363-a132-4290-8f3d-b405681957a1', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'hasRangeClass');
INSERT INTO relations VALUES ('aadfa9b7-a5ed-4cec-807b-2a5b7939ec22', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'hasDomainClass');
INSERT INTO relations VALUES ('8801789e-3448-4c84-abbd-b2c2a890c4af', 'fd06e07d-057b-38aa-99ac-1add45f9f217', '6e30fbe8-5a0d-3de8-be79-4ec6ebf4db39', 'hasRangeClass');
INSERT INTO relations VALUES ('d3fc0d31-741d-432b-b45b-a27e401cb28f', '70064b58-4490-3d09-b463-fd18defae21f', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', 'hasDomainClass');
INSERT INTO relations VALUES ('5ec9286f-6fcc-4de6-b74f-d8aaecbde3e1', 'fc174f36-37ef-3f45-aec4-5b8ebe0e7729', '9d55628a-0085-3b88-a939-b7a327263f53', 'hasRangeClass');
INSERT INTO relations VALUES ('c68e6bbd-f4c2-4e96-8040-3e28e577f509', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', 'hasDomainClass');
INSERT INTO relations VALUES ('a2954103-894a-4e11-9fc8-8c56f95059db', 'e0f3172d-f1e7-3c80-af06-eeb0a1636cfa', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'hasRangeClass');
INSERT INTO relations VALUES ('90cf0e08-109a-4b36-9971-152ad1dfa9f2', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', 'hasDomainClass');
INSERT INTO relations VALUES ('f62f5cc9-d32c-4b54-88c8-5975933d6445', 'd2a09554-6718-3230-8f6f-10ff2daab9b3', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('bd6bf9dc-f013-4d2b-8b44-620ab277185d', '0cc20557-978d-31ae-bee8-b3939398b1c8', '9f10aa95-ba46-3601-bac2-3ea828c154e6', 'hasDomainClass');
INSERT INTO relations VALUES ('2a086a82-e24e-473e-b9da-a8211e833119', '9f10aa95-ba46-3601-bac2-3ea828c154e6', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'hasRangeClass');
INSERT INTO relations VALUES ('d3482e20-7ae7-4662-93ae-a5e95402c74c', '0cc20557-978d-31ae-bee8-b3939398b1c8', '6909b643-03f7-3606-b276-2be0e8773207', 'hasDomainClass');
INSERT INTO relations VALUES ('059345c5-84aa-449b-8bfa-1e951e8a5660', '6909b643-03f7-3606-b276-2be0e8773207', '0cc20557-978d-31ae-bee8-b3939398b1c8', 'hasRangeClass');
INSERT INTO relations VALUES ('9ae5d1b0-9120-4fc0-9a58-d77ae445d17b', '94ffd715-18f7-310a-bee2-010d800be058', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', 'hasDomainClass');
INSERT INTO relations VALUES ('0d795119-c337-4559-b127-c12ac7ba9b13', 'b12aa689-98d5-39ea-ac35-cb8020da3ea4', '94ffd715-18f7-310a-bee2-010d800be058', 'hasRangeClass');
INSERT INTO relations VALUES ('58fd985c-c1db-4ade-aaf2-30a9e92447c2', '99e8de0f-fa06-381d-8406-9d467d3f96b5', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'subPropertyOf');
INSERT INTO relations VALUES ('2dcea919-39c1-4d28-b461-958955d459c1', 'a6ef9479-248e-3847-bf68-9c9017b0add8', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'hasDomainClass');
INSERT INTO relations VALUES ('b3342c5c-9012-4368-8517-7abd5d60f784', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('cca2c61d-e486-4117-8de6-57c2143a1dcd', 'a6ef9479-248e-3847-bf68-9c9017b0add8', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'hasDomainClass');
INSERT INTO relations VALUES ('87417849-54c0-41c7-b8e3-26bfeed870a5', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'hasRangeClass');
INSERT INTO relations VALUES ('9e9881db-a463-4951-9456-3b9f5caaefe1', 'f865c72a-09dd-386f-a9eb-385176727d94', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'subPropertyOf');
INSERT INTO relations VALUES ('48d310dd-64a0-4a03-843a-7b384554d701', '94b5ce18-d4ca-3ac6-b903-d68c86258f95', '0d61e94e-8834-3ba5-b51b-d55951a84fae', 'hasDomainClass');
INSERT INTO relations VALUES ('b1654533-49cc-411d-b186-a63b119cc192', '0d61e94e-8834-3ba5-b51b-d55951a84fae', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'hasRangeClass');
INSERT INTO relations VALUES ('7723be4f-3608-49e1-94a2-0972d17bb193', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'subPropertyOf');
INSERT INTO relations VALUES ('8310786f-12b1-4785-9bf3-b23db5d5e8bc', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'hasDomainClass');
INSERT INTO relations VALUES ('a45e63ba-3a67-4e21-8490-fa9a689ccbe0', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('6e911b54-113c-4558-bab8-402575970e56', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'hasDomainClass');
INSERT INTO relations VALUES ('1cba6b3c-d7bf-4370-9132-53499294cacb', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('f29a03cb-e1be-47e1-b173-9912d89b8db0', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'subPropertyOf');
INSERT INTO relations VALUES ('682be8e8-92c7-4c48-8ea5-f6e901fa0f4e', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'subPropertyOf');
INSERT INTO relations VALUES ('5808b299-4a92-4a76-af43-3e62c00b129a', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'hasDomainClass');
INSERT INTO relations VALUES ('38360c0c-8b7f-41fd-ba07-19f49062e81b', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'hasRangeClass');
INSERT INTO relations VALUES ('87446b57-7c6e-4476-b297-ddb7a6de8a90', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'subPropertyOf');
INSERT INTO relations VALUES ('96b17295-e297-4d0e-a868-4e08c176e75b', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'hasDomainClass');
INSERT INTO relations VALUES ('7bbd2819-ef34-4ef1-a15e-0ad1dfd8d7d8', '2e24daa3-5793-30a8-a96e-3710c3862af4', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('bb319e4e-8851-42a9-9377-3ed7264ee7c2', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', 'hasDomainClass');
INSERT INTO relations VALUES ('8431fd14-2b84-4156-8c85-944006fab058', '8aa15071-614f-31b9-a8d5-a60afa7b5cd6', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', 'hasRangeClass');
INSERT INTO relations VALUES ('1b3234dc-3804-4ca3-97c3-bb3e8c76e1f2', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'hasDomainClass');
INSERT INTO relations VALUES ('222379e7-1b53-4c68-aca5-319063f7ddd0', '50ac84c9-d606-34b8-8c46-f2a0c7cf07bf', 'a6ef9479-248e-3847-bf68-9c9017b0add8', 'hasRangeClass');
INSERT INTO relations VALUES ('e787bd40-5876-43d9-99ad-76afce8d8e16', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'hasDomainClass');
INSERT INTO relations VALUES ('fb20b76e-73f3-4871-a209-975d2a48d4aa', '9c11dd9d-0693-36c3-8b4a-a56e4b67daf5', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'hasRangeClass');
INSERT INTO relations VALUES ('c250790f-3137-4e3b-9d85-93b7facee5ec', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'subPropertyOf');
INSERT INTO relations VALUES ('09c1fd78-a84d-4463-853c-7c6a4eb4acd0', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'hasDomainClass');
INSERT INTO relations VALUES ('a4d31a29-0653-4eb3-bc31-1ae52058f117', '5c8d2516-e5bc-383e-ad10-a74e55cf93fe', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('faba6f3f-5126-472f-8f0a-02272394e5ee', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', '345681a7-8324-331c-94d4-1777c36538b5', 'subPropertyOf');
INSERT INTO relations VALUES ('b72f7c83-6253-43dc-ba0a-c56d9bc828fc', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', '345681a7-8324-331c-94d4-1777c36538b5', 'hasDomainClass');
INSERT INTO relations VALUES ('2847089a-4d5d-4bf2-8b8a-cdc8bc1a3f14', '345681a7-8324-331c-94d4-1777c36538b5', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('96c29026-5565-4ec0-86a3-fe799f2013d5', 'd0d1b126-40ad-3b89-a60c-c0bf6662d57a', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', 'hasDomainClass');
INSERT INTO relations VALUES ('616abccd-2ec2-4dcd-9063-223ad12c70ae', '3d2a5865-d1f0-340f-9cd7-edd19ad98119', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'hasRangeClass');
INSERT INTO relations VALUES ('398d3be4-1998-49a9-bc34-6fda2f06fecb', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'subPropertyOf');
INSERT INTO relations VALUES ('300870e2-0582-4b97-a3be-dd793968d154', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', 'hasDomainClass');
INSERT INTO relations VALUES ('cad694a8-b67c-4713-a7fb-442a7fb0d6fc', 'f05d0f06-c8b2-3cc9-bd57-9f8152f211f9', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'hasRangeClass');
INSERT INTO relations VALUES ('f0624c89-599b-4d73-a4b1-5a587034902e', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', 'hasDomainClass');
INSERT INTO relations VALUES ('71e0e458-09e0-413d-9079-34b2708bf8af', 'fa90e1e4-3906-3c8c-80f2-c51255d21fcb', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('6fd283b4-83e7-4145-acfe-034f85f1fffa', '8f400a1e-e2f6-3cd7-85ae-f0790a3aea0c', 'e94e9966-e05b-3b5a-a5f0-893166474b80', 'hasDomainClass');
INSERT INTO relations VALUES ('852562cc-de12-45d1-8a9c-e26240a3f3e9', 'e94e9966-e05b-3b5a-a5f0-893166474b80', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('c2bee7f1-3aeb-44e8-9f18-edcc09d96fd2', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', 'aad29816-af79-36cf-919e-80980f7c41a3', 'subPropertyOf');
INSERT INTO relations VALUES ('553382ec-71c3-4225-9a2b-81571ca100fc', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'aad29816-af79-36cf-919e-80980f7c41a3', 'hasDomainClass');
INSERT INTO relations VALUES ('9370b887-2642-4b2c-96fc-0ca7167e9911', 'aad29816-af79-36cf-919e-80980f7c41a3', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('5deffbfc-d218-4be1-8112-a78849efd0a3', 'f1c1e55b-4fad-3074-a49b-d08c287f3fa5', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'subPropertyOf');
INSERT INTO relations VALUES ('35f69ff8-cd49-4236-a52e-c3ea76ef5f82', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'hasDomainClass');
INSERT INTO relations VALUES ('34b229d7-f33f-4017-b527-246fae4b064c', '8d2ad7fb-6c1b-3b46-9786-4abef3688198', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('5928dcf1-b61f-4224-b405-4e194990189b', '2f277cee-3506-3366-a9b5-c4bfe7e265cb', 'f24070b3-fc3b-3838-8765-87350b40ba84', 'hasDomainClass');
INSERT INTO relations VALUES ('f634ab42-c694-4883-932c-f75678ce753d', 'f24070b3-fc3b-3838-8765-87350b40ba84', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'hasRangeClass');
INSERT INTO relations VALUES ('4ea6d197-f4ee-4db1-8ca1-a9e231682cf2', '99e8de0f-fa06-381d-8406-9d467d3f96b5', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'subPropertyOf');
INSERT INTO relations VALUES ('7c7bb5b3-d35d-4046-abed-8ecdf147de05', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'hasDomainClass');
INSERT INTO relations VALUES ('081c8d32-f252-47a6-8022-967e598dec4e', '439f0684-5ebc-3227-93a5-ae9ebca7e015', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'hasRangeClass');
INSERT INTO relations VALUES ('bb7ea5ca-f2d0-43bf-bc9c-7a1f2cfee4c6', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'subPropertyOf');
INSERT INTO relations VALUES ('a18c8e8c-98b1-49e9-8c97-4b62d59a874b', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'hasDomainClass');
INSERT INTO relations VALUES ('0133e381-5f13-49ec-9a60-f373ab5ac118', '1a5c940f-b67a-31c7-a34b-17d1fda7796b', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'hasRangeClass');
INSERT INTO relations VALUES ('3cf705d4-95e3-402e-98c7-2765f912e973', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'subPropertyOf');
INSERT INTO relations VALUES ('32958802-18cf-43b1-8643-48b3fc6af5b9', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', 'hasDomainClass');
INSERT INTO relations VALUES ('838f9433-b098-440b-9a00-c21786377fd5', 'f370e85a-d4e4-35bb-89dd-737c57eef9d5', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'hasRangeClass');
INSERT INTO relations VALUES ('4682a00f-e5e9-4259-81f9-c06861293df7', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'd9f02df8-6676-371e-8114-1f37700639b5', 'subPropertyOf');
INSERT INTO relations VALUES ('a86bda65-a236-4345-9d04-5d767cc918b5', 'c411cc1b-d477-3619-a63b-d1566635ead7', 'd9f02df8-6676-371e-8114-1f37700639b5', 'hasDomainClass');
INSERT INTO relations VALUES ('d0cdb52f-c898-4317-bd70-1607db4c05f0', 'd9f02df8-6676-371e-8114-1f37700639b5', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'hasRangeClass');
INSERT INTO relations VALUES ('78ba4c1f-725b-44d2-a874-6d58216ae34d', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'subPropertyOf');
INSERT INTO relations VALUES ('58532df9-f28c-4adb-adbb-3cc475a593ef', 'c411cc1b-d477-3619-a63b-d1566635ead7', '79183fdd-7275-32a2-a48d-bb70fe683efd', 'hasDomainClass');
INSERT INTO relations VALUES ('00f7dfc4-38fa-477d-94e4-764ebe9098bb', '79183fdd-7275-32a2-a48d-bb70fe683efd', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'hasRangeClass');
INSERT INTO relations VALUES ('22b0d8ae-9a1e-4a54-abd8-a58913dce209', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'subPropertyOf');
INSERT INTO relations VALUES ('b3cd277b-4909-416f-9eef-2c9a74b1c396', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'hasDomainClass');
INSERT INTO relations VALUES ('fc40b7fd-103d-42d0-a58b-5cfdb11c33da', 'd35815f0-0426-3ac0-b396-7ce2959ebf77', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'hasRangeClass');
INSERT INTO relations VALUES ('73263683-d6d9-4239-bfb6-64e4b22a59d5', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'subPropertyOf');
INSERT INTO relations VALUES ('074b32eb-e4e7-43b8-9841-74927a4cbd7a', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'hasDomainClass');
INSERT INTO relations VALUES ('c2eff0da-ee48-4aa7-b410-850643068676', 'caf4c608-3653-397c-a26e-6cc5135274f8', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'hasRangeClass');
INSERT INTO relations VALUES ('a5fa4b12-8662-44d3-affa-c0375d97a3b0', '839c9e24-c1ab-34b4-94da-2efb1d32af01', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'subPropertyOf');
INSERT INTO relations VALUES ('e1d95246-55f3-4a76-9bf1-5a4fc9ebc4b0', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'hasDomainClass');
INSERT INTO relations VALUES ('f39a817a-495d-4894-a07e-863dd00ed9d9', '736d6bff-30b8-34d9-aeb7-24f012968ecc', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('040f2694-7dda-439e-a3cc-1878d005ad47', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'subPropertyOf');
INSERT INTO relations VALUES ('7630e1ec-2a80-4f68-9e73-c8210a5ab65e', 'a92f95fd-aa72-3c47-bca1-3c0c9520656b', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'hasDomainClass');
INSERT INTO relations VALUES ('9838ef0b-2220-491a-8b5c-034e25f8199b', '5c72bddb-0c50-328c-a5aa-d3ce3da73f16', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'hasRangeClass');
INSERT INTO relations VALUES ('e49cc8a1-8496-4450-af44-68ef944d7ef2', '839c9e24-c1ab-34b4-94da-2efb1d32af01', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'subPropertyOf');
INSERT INTO relations VALUES ('cbaeec5e-8228-4225-9778-4234c3b2602f', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'hasDomainClass');
INSERT INTO relations VALUES ('a7fce625-4bbb-4801-b076-5a428f554d24', '8a263f1b-a5b5-34f8-a8c6-cd1879982ef0', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('f878840d-fccd-4cda-8201-870e504f6a1c', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'subPropertyOf');
INSERT INTO relations VALUES ('c3b3dcd5-3130-4a91-921b-c7e11dad3804', 'd4b331cf-09dc-3f5b-a8a9-9df1bfde30b5', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'hasDomainClass');
INSERT INTO relations VALUES ('0340c974-76ed-4e3e-86ee-de26a1c7074e', 'f7e7d2db-6b00-3f32-9337-ae46982ed7a5', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'hasRangeClass');
INSERT INTO relations VALUES ('4ba1173f-6189-4dc6-ba20-d55858c9185d', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', '167c0167-35fd-3c57-b90e-20715fd2c200', 'hasDomainClass');
INSERT INTO relations VALUES ('7681cd0a-f609-4b42-9a8d-bacb78d9e592', '167c0167-35fd-3c57-b90e-20715fd2c200', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'hasRangeClass');
INSERT INTO relations VALUES ('b1dfdec1-977d-4c2c-9c0e-3289ec3f28ba', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', 'hasDomainClass');
INSERT INTO relations VALUES ('e4ae5880-450f-4277-8cd2-40bab58dfa01', 'ada32613-4ae4-30a5-8bf0-08a51bbf636a', '12cfab6c-8a4c-37c8-9569-a7a2db3fafad', 'hasRangeClass');
INSERT INTO relations VALUES ('c7d32179-8195-46e9-99f7-a61d1cc7c86b', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', 'hasDomainClass');
INSERT INTO relations VALUES ('65fb6501-1c7d-4cff-bde3-e2730c8bc2a5', 'c4f5c11a-77fa-3601-825f-e7cac6c29d73', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'hasRangeClass');
INSERT INTO relations VALUES ('3f2c9f10-f73b-4ccf-b860-dbd1167fb909', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'hasDomainClass');
INSERT INTO relations VALUES ('0b3d519a-c86a-4015-bfad-4749f897f418', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'hasRangeClass');
INSERT INTO relations VALUES ('6bb5efef-b8f7-43f5-8334-c9a6855594bd', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', '356c8ba7-0114-32c3-861f-8432bc46e963', 'subPropertyOf');
INSERT INTO relations VALUES ('4d41ec1a-1fdb-433a-a971-0cebc6cc7650', 'c03db431-4564-34eb-ba86-4c8169e4276c', '356c8ba7-0114-32c3-861f-8432bc46e963', 'hasDomainClass');
INSERT INTO relations VALUES ('6b6858ef-f774-4b9a-b766-e02a13e6c3b6', '356c8ba7-0114-32c3-861f-8432bc46e963', 'fc4193ce-c5a3-3c1b-907f-6b4d299c8f5c', 'hasRangeClass');
INSERT INTO relations VALUES ('2c27719b-8d4f-4cad-bd40-04a3c9c215ca', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'hasDomainClass');
INSERT INTO relations VALUES ('4a30250d-2386-4387-8497-c295c84d21db', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('02761459-3c32-4f2d-9954-c3ef06619c9c', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'subPropertyOf');
INSERT INTO relations VALUES ('51eb2e64-830b-4a7e-8f21-ced8f0e3d73e', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'hasDomainClass');
INSERT INTO relations VALUES ('2390a270-5a9f-43a0-a93c-07b1066bd2d7', '2e2cce91-09c2-3160-95ad-c17efcc59ac7', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('28c55a59-fe28-4dc8-8e5f-0afd7963eb7d', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'hasDomainClass');
INSERT INTO relations VALUES ('8db086d8-855e-44bb-b09f-765d0fdef330', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('50b4f6c1-06d7-463a-a83b-320fdd5032d8', '6eaf78e8-89c1-3e66-97ed-c189478fed2f', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'subPropertyOf');
INSERT INTO relations VALUES ('81f9fb33-2254-402a-ae8a-4952bb6dd8a3', '140073c4-60b5-352d-a5f7-244072fc4086', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'subPropertyOf');
INSERT INTO relations VALUES ('055af077-88a3-411b-aa4b-9d81b7184a19', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'hasDomainClass');
INSERT INTO relations VALUES ('cb44c2b4-c0bd-4fcf-b2c9-6c8535087b21', '954c6e65-1fca-3f29-bcb8-7bc9d56fa191', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('9cdee554-025b-4cd0-82a9-74b7f0b382ca', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'hasDomainClass');
INSERT INTO relations VALUES ('b4fa5181-d872-4023-a166-37f8f992981e', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('6d61cb1e-7b22-4a3b-a080-d07a50d61503', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', 'hasDomainClass');
INSERT INTO relations VALUES ('5c70a035-9ad0-4e20-bc00-6d0b66adf6af', 'e9f7831d-a7cb-383b-8c8d-afa4f18ab124', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('6d4de559-9124-4d9a-b8e5-bee326f0dfd5', 'a343bd21-9eb3-3ab7-a2a8-f6a76abfc2f1', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'subPropertyOf');
INSERT INTO relations VALUES ('1a611ce2-1690-4267-b723-7cc2616d8654', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', 'hasDomainClass');
INSERT INTO relations VALUES ('f3d40262-d32e-4b8e-8021-d3872465dad6', 'f2565243-677f-37a3-b4dd-b3b9525f7c4c', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('dd23a250-efb9-45bb-a4a5-59daf1b8a663', 'e37e8cfe-e1b7-3335-818b-d56090f2974e', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'subPropertyOf');
INSERT INTO relations VALUES ('5c18640d-6827-4349-b55d-0f2b2454d937', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', 'hasDomainClass');
INSERT INTO relations VALUES ('96703280-51fd-476a-86bd-119f086cd417', 'e85f32d0-ac0d-3039-a95e-a1beda15fc3d', '2bc61bb4-384d-3427-bc89-2320be9896f2', 'hasRangeClass');
INSERT INTO relations VALUES ('2041cb2f-fc68-41d4-bc3f-e1881c5de512', '3f975fdf-518e-3ac6-9037-8a288f3bd6c4', '5afb86ba-c943-367b-857c-d7aaec92b5e3', 'hasDomainClass');
INSERT INTO relations VALUES ('d0be31a3-6018-4b27-8702-65be755f413d', '5afb86ba-c943-367b-857c-d7aaec92b5e3', '30c58f1c-03f4-36f8-9f50-4fefc84bb0a6', 'hasRangeClass');
INSERT INTO relations VALUES ('d0126ed0-be07-4299-9c72-ee335af04fd7', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', '89cad4c1-914c-3675-9d66-83eed1c61e3e', 'hasDomainClass');
INSERT INTO relations VALUES ('b3216d26-1864-41e2-9c50-b4e9dc2266d0', '89cad4c1-914c-3675-9d66-83eed1c61e3e', '4e3d11b3-c6a8-3838-9a62-0571b84914fa', 'hasRangeClass');
INSERT INTO relations VALUES ('80ff5894-e133-49cc-bb66-57cbe6c5ff55', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', '21f8fc78-e937-3048-95e9-e69404b1d3f1', 'hasDomainClass');
INSERT INTO relations VALUES ('612b5ee7-3920-496a-a60c-df2989c5c52d', '21f8fc78-e937-3048-95e9-e69404b1d3f1', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('2bd3233f-1604-4d57-961e-ef506d31109f', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', '05804845-b0d6-3634-a977-a5c7785d2dde', 'hasDomainClass');
INSERT INTO relations VALUES ('43d80b25-7f76-44a4-ac5f-b14553303f87', '05804845-b0d6-3634-a977-a5c7785d2dde', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('4ebb733f-f271-494f-8445-630d6875b96a', '007dac32-df80-366b-88ce-02f4c1928537', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'subPropertyOf');
INSERT INTO relations VALUES ('bf0023f0-7750-444e-afe5-7b3478d13437', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', '15f83f67-48e0-3afd-b693-605172ea3fd2', 'hasDomainClass');
INSERT INTO relations VALUES ('602ad678-879a-40f5-b129-5a73797673bc', '15f83f67-48e0-3afd-b693-605172ea3fd2', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'hasRangeClass');
INSERT INTO relations VALUES ('a4076ca9-0beb-4f7d-8ea0-2906e84d593f', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', '629ed771-13e7-397e-8345-69f6cfb3db30', 'hasDomainClass');
INSERT INTO relations VALUES ('9a57cde9-467b-4928-a179-763cd1ac6664', '629ed771-13e7-397e-8345-69f6cfb3db30', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('fe542232-cf94-4591-b27f-e5af15c5ae9a', '629ed771-13e7-397e-8345-69f6cfb3db30', '037c3de7-65ae-3002-8328-18cc33572501', 'subPropertyOf');
INSERT INTO relations VALUES ('761a0450-40a5-4e03-8da5-0b90faeb7776', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', '037c3de7-65ae-3002-8328-18cc33572501', 'hasDomainClass');
INSERT INTO relations VALUES ('3f5c8f9d-8b63-4aba-9936-ce7fb524fcea', '037c3de7-65ae-3002-8328-18cc33572501', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'hasRangeClass');
INSERT INTO relations VALUES ('ec5ddbb1-71ad-4520-af53-49094a53e409', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', 'hasDomainClass');
INSERT INTO relations VALUES ('c5556049-5e9e-42f7-89be-a47dfb41cd91', 'b92c8654-6db7-3c41-87a4-69d6ccf66e1c', '3b35ea57-508c-352e-8d98-ec5cbc29c7a7', 'hasRangeClass');
INSERT INTO relations VALUES ('b85a0cb2-ea78-4d98-af04-bbd6751631be', '629ed771-13e7-397e-8345-69f6cfb3db30', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'subPropertyOf');
INSERT INTO relations VALUES ('11d2ff5b-7dd0-4e66-b2be-bff5e7581245', '84a17c0c-78f2-3607-ba85-da1fc47def5a', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'hasDomainClass');
INSERT INTO relations VALUES ('d87c258c-1be5-4c90-8685-0b2077f6fc2c', '3ca0d5b2-a1ec-3aca-9a43-fcd160432782', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('4252c4f2-8c5e-4440-ad52-1b391b1505f6', '629ed771-13e7-397e-8345-69f6cfb3db30', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'subPropertyOf');
INSERT INTO relations VALUES ('baaec5dc-e0d6-4749-9170-157485498bd0', '0df9cb10-1203-3efd-8d9e-448f5b02506b', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'hasDomainClass');
INSERT INTO relations VALUES ('2d75d024-4ee1-4b33-a0d8-dd0ddfea7988', '549c04f2-465b-3af6-ba22-8d21aacfe0af', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('bc6b0884-0c2c-414e-b7d0-3400a909fc58', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', 'hasDomainClass');
INSERT INTO relations VALUES ('6d219b9e-1875-4490-b7a8-8c03bd06790c', 'e4096768-5cad-36ca-8ee7-d5b928a0045a', '4e75b119-d77b-3c1e-acf8-fbdfd197c9f1', 'hasRangeClass');
INSERT INTO relations VALUES ('532f1698-9786-4402-bbbe-badadbc94bb3', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'subPropertyOf');
INSERT INTO relations VALUES ('a5109d9a-4e9a-4eac-b475-c76b8fddb8aa', 'fa1b039d-00cd-36e8-b03c-247176a6368d', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'hasDomainClass');
INSERT INTO relations VALUES ('27905336-c802-4f4b-8760-ec8c8def0d64', '8a9489d3-6c67-3b70-9b4d-64980efa0879', 'fa1b039d-00cd-36e8-b03c-247176a6368d', 'hasRangeClass');
INSERT INTO relations VALUES ('a8ce4713-93f1-454c-9899-a535257d18ff', 'af051b0a-be2f-39da-8f46-429a714e242c', '5869a9ed-ebe5-3613-acc2-29c184737885', 'hasDomainClass');
INSERT INTO relations VALUES ('d4bf9fef-fb10-475c-94b4-5a691868cb09', '5869a9ed-ebe5-3613-acc2-29c184737885', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('186aaebb-3ff8-4de6-bfa1-cf70e52d8179', 'af051b0a-be2f-39da-8f46-429a714e242c', '44813770-321a-370d-bb8f-ba619bcb4334', 'hasDomainClass');
INSERT INTO relations VALUES ('b389e73b-7fef-4525-8445-b01419a91149', '44813770-321a-370d-bb8f-ba619bcb4334', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'hasRangeClass');
INSERT INTO relations VALUES ('d4d14a50-b6bf-431d-be7f-c5dd4ca7a226', 'af051b0a-be2f-39da-8f46-429a714e242c', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', 'hasDomainClass');
INSERT INTO relations VALUES ('d942a9f6-fd52-414d-9311-ea56c591f77d', 'e39e863c-0b62-39ae-8db7-e49b56fcbd1e', '7cee80d2-87e9-3a29-9d1e-f61d46d892ca', 'hasRangeClass');
INSERT INTO relations VALUES ('eb4d77d2-dd93-4a72-8866-314c485133c3', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'subPropertyOf');
INSERT INTO relations VALUES ('0c0e7fad-ebb2-4e3d-8e8e-ca7a4dd5a2ba', '9d55628a-0085-3b88-a939-b7a327263f53', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', 'hasDomainClass');
INSERT INTO relations VALUES ('a2735664-a3eb-4d92-b869-e73f92e39257', '5f425a21-ce2e-3ec6-b434-38ada47bc29c', '9ca9a75f-0eca-378a-a095-91574ad77a30', 'hasRangeClass');
INSERT INTO relations VALUES ('5ccb2d75-f150-476a-99ca-6904ea50d401', 'fd06e07d-057b-38aa-99ac-1add45f9f217', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'subPropertyOf');
INSERT INTO relations VALUES ('46fe73ae-d54d-43cd-b73e-cb2f23a4a559', '9d55628a-0085-3b88-a939-b7a327263f53', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', 'hasDomainClass');
INSERT INTO relations VALUES ('36214e0e-df6b-4f89-a0b1-76949666e12c', '2585bcd7-dcd6-3b79-b29f-f4d664a65fc9', '6e30fbe8-5a0d-3de8-be79-4ec6ebf4db39', 'hasRangeClass');
INSERT INTO relations VALUES ('8ebfa323-2363-457a-87d7-9d8e37812cf7', 'fd06e07d-057b-38aa-99ac-1add45f9f217', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'subPropertyOf');
INSERT INTO relations VALUES ('42e81a43-7063-407e-b901-c6414beb4221', '9d55628a-0085-3b88-a939-b7a327263f53', 'b1c4e551-2f6e-327b-8905-191228330e2f', 'hasDomainClass');
INSERT INTO relations VALUES ('cd68f062-ac0c-470e-9544-14f433d12597', 'b1c4e551-2f6e-327b-8905-191228330e2f', '6e30fbe8-5a0d-3de8-be79-4ec6ebf4db39', 'hasRangeClass');
INSERT INTO relations VALUES ('27af44ad-046c-47c4-97b0-60fe7a95fec3', '9d55628a-0085-3b88-a939-b7a327263f53', '6a998971-7a85-3615-9929-d613fe90391c', 'hasDomainClass');
INSERT INTO relations VALUES ('03d5b419-5c3d-4f61-abe5-c28c19ab7ba7', '6a998971-7a85-3615-9929-d613fe90391c', 'fd8302b4-921b-300c-a9bf-c50d92418797', 'hasRangeClass');
INSERT INTO relations VALUES ('05160a49-7a58-4e30-b0dc-285432b87010', '9d55628a-0085-3b88-a939-b7a327263f53', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'hasDomainClass');
INSERT INTO relations VALUES ('9cab0ebf-7340-40a4-beb1-0f9a2ea25b57', '890ddf47-6e5e-32f7-b3a8-ecd251002877', 'fd8302b4-921b-300c-a9bf-c50d92418797', 'hasRangeClass');
INSERT INTO relations VALUES ('f885c38a-cef9-4a99-86c7-349b781666d7', '9d55628a-0085-3b88-a939-b7a327263f53', 'b38666a2-59fd-3154-85c3-90edaa812979', 'hasDomainClass');
INSERT INTO relations VALUES ('c3ab16b1-0bfd-463e-b078-73c12d89488d', 'b38666a2-59fd-3154-85c3-90edaa812979', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'hasRangeClass');
INSERT INTO relations VALUES ('559436f5-39b0-43d7-a65a-bfe3d501c20b', '9d55628a-0085-3b88-a939-b7a327263f53', '86caed02-d112-3cd7-8f21-4836e4997850', 'hasDomainClass');
INSERT INTO relations VALUES ('7efe9353-2ddd-4a0a-9e0e-a9619d202ccd', '86caed02-d112-3cd7-8f21-4836e4997850', 'bdf5f93e-589c-3c63-baad-e108520c4072', 'hasRangeClass');
INSERT INTO relations VALUES ('a673208e-9aa2-4dc8-b7a2-aa9fc696dcde', '9d55628a-0085-3b88-a939-b7a327263f53', '014fefdb-ddad-368b-b69c-951a0763824d', 'hasDomainClass');
INSERT INTO relations VALUES ('f805af61-b42f-493b-87c3-1aa9f274d015', '014fefdb-ddad-368b-b69c-951a0763824d', '9d55628a-0085-3b88-a939-b7a327263f53', 'hasRangeClass');
INSERT INTO relations VALUES ('d9cb0020-c955-4b0f-b0f6-66f8f9e5dab9', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', '697dc6cc-0da6-301c-9703-78edbf812fac', 'subPropertyOf');
INSERT INTO relations VALUES ('10a740db-eb14-481e-9466-b212f9dac171', '12f08da7-e25c-3e10-8179-62ed76da5da0', '697dc6cc-0da6-301c-9703-78edbf812fac', 'hasDomainClass');
INSERT INTO relations VALUES ('f7d2ef0e-3982-44ef-8e3a-f53a2bacc2a7', '697dc6cc-0da6-301c-9703-78edbf812fac', '19e2c4fb-70b7-3913-be69-1c824a0bf23f', 'hasRangeClass');
INSERT INTO relations VALUES ('1d1a9fa9-5404-42db-8ace-57457d284531', '12f08da7-e25c-3e10-8179-62ed76da5da0', '900165c3-a630-3b9c-bb0b-572df34ea3e6', 'hasDomainClass');
INSERT INTO relations VALUES ('8ba70ff1-418d-461c-9e3a-b4bd367d4d53', '900165c3-a630-3b9c-bb0b-572df34ea3e6', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('5ba74944-474b-4d3f-8e3e-d305ce13057a', 'bdf5f93e-589c-3c63-baad-e108520c4072', '26af9ec1-e169-3486-9bb5-3c8187784c8e', 'hasDomainClass');
INSERT INTO relations VALUES ('b53a6e06-8eb1-41d3-aa81-c20bc7dbba53', '26af9ec1-e169-3486-9bb5-3c8187784c8e', '30c58f1c-03f4-36f8-9f50-4fefc84bb0a6', 'hasRangeClass');
INSERT INTO relations VALUES ('949447bd-78a2-44cd-b3cc-cc9c9fe3f835', 'bdf5f93e-589c-3c63-baad-e108520c4072', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'hasDomainClass');
INSERT INTO relations VALUES ('a1e178de-3fba-4747-b928-5261a992599f', '166f17e8-15b8-3abc-bba7-7a56c364bf42', 'c1f0e36c-770f-30f9-8241-30d44921c6c8', 'hasRangeClass');
INSERT INTO relations VALUES ('1d5e7a18-2c90-41ab-9603-caddb54d873a', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'subPropertyOf');
INSERT INTO relations VALUES ('c705b969-6de1-4987-922f-ca08d86d3634', '255bba42-8ffb-3796-9caa-807179a20d9a', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'hasDomainClass');
INSERT INTO relations VALUES ('9a6a97bf-3edd-421e-af2d-192423653743', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'hasRangeClass');
INSERT INTO relations VALUES ('f12e21de-2056-4be0-a1e8-ee29a7393ceb', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'f865c72a-09dd-386f-a9eb-385176727d94', 'subPropertyOf');
INSERT INTO relations VALUES ('a0c39eeb-0f3f-4aa9-b1e1-4cc267ed7960', '064e52a9-ae25-33fc-9c59-ad7ecbee3d42', 'f865c72a-09dd-386f-a9eb-385176727d94', 'hasDomainClass');
INSERT INTO relations VALUES ('bdc45cbd-4ff4-4c8a-a2df-653db4c14c47', 'f865c72a-09dd-386f-a9eb-385176727d94', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'hasRangeClass');
INSERT INTO relations VALUES ('76504b1d-0da9-42cc-a802-353e42826508', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'subPropertyOf');
INSERT INTO relations VALUES ('90e8c79e-a1dc-4e2b-9dea-a2e03c173edc', 'ec30d38a-0102-3a93-a31a-d596fb6def0b', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'hasDomainClass');
INSERT INTO relations VALUES ('33071dc2-ab55-4be7-b99b-77132da0b427', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'hasRangeClass');
INSERT INTO relations VALUES ('4f328876-4dc9-4254-9afc-1c2be1d9df57', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'subPropertyOf');
INSERT INTO relations VALUES ('3a7f11b2-8ccc-44e3-92e0-43a69b135f5b', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', '9623a310-4d14-33dc-ae6e-10fb48062af5', 'hasDomainClass');
INSERT INTO relations VALUES ('b4bf0dc4-5b06-423c-bad2-822322d43d30', '9623a310-4d14-33dc-ae6e-10fb48062af5', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'hasRangeClass');
INSERT INTO relations VALUES ('1462cab4-b506-4ae4-82c3-eed013144e23', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', '9e806e49-e728-32cf-821e-504ca9916afc', 'subPropertyOf');
INSERT INTO relations VALUES ('32f9da16-7cab-47ed-8f73-5f403bf7ded7', '07fcf604-d28f-3993-90fa-d301c4004913', '9e806e49-e728-32cf-821e-504ca9916afc', 'hasDomainClass');
INSERT INTO relations VALUES ('ec6ef050-f27d-4723-91bc-0321885901ea', '9e806e49-e728-32cf-821e-504ca9916afc', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'hasRangeClass');
INSERT INTO relations VALUES ('50c2e10d-7b30-4fa4-b79f-75738712037b', '07fcf604-d28f-3993-90fa-d301c4004913', '19c3c1bf-e443-3f89-a366-d3e8c645a546', 'hasDomainClass');
INSERT INTO relations VALUES ('9d94b63b-5c14-4a7e-849a-7c48366d0b72', '19c3c1bf-e443-3f89-a366-d3e8c645a546', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'hasRangeClass');
INSERT INTO relations VALUES ('9a9e912c-2f10-49b0-ac3c-2221e703cbc1', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'subPropertyOf');
INSERT INTO relations VALUES ('186a3212-e7b8-430c-bde3-7e5a920fc0a3', '07fcf604-d28f-3993-90fa-d301c4004913', 'c511a177-3e0b-3a90-babe-e951f56f18d1', 'hasDomainClass');
INSERT INTO relations VALUES ('1ddabfd7-f506-4377-b579-aa23bdde370b', 'c511a177-3e0b-3a90-babe-e951f56f18d1', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'hasRangeClass');
INSERT INTO relations VALUES ('2e129c9a-305c-43ac-81da-b7a44de8d9a4', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'subPropertyOf');
INSERT INTO relations VALUES ('f4ea79e9-bcbb-4695-9180-d899bf2663f7', 'f865c72a-09dd-386f-a9eb-385176727d94', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'subPropertyOf');
INSERT INTO relations VALUES ('b61e4a0d-507d-4229-ba3a-90bfe0b265a1', '8bba5cfd-675d-3899-8c95-03b2de2a0a31', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', 'hasDomainClass');
INSERT INTO relations VALUES ('8fccff15-6165-4d37-983a-31a8beae224c', '9a1d1b8c-4dde-3258-83d2-9a1ebe1a541e', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'hasRangeClass');
INSERT INTO relations VALUES ('8a7a8494-0f92-4848-abdc-f138d73d883f', 'f865c72a-09dd-386f-a9eb-385176727d94', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'subPropertyOf');
INSERT INTO relations VALUES ('d18629de-4787-4bfb-8a95-d97b1f7af8f4', '725afd13-ebc5-38a8-815b-d3a1e5510698', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', 'hasDomainClass');
INSERT INTO relations VALUES ('73070f34-e07b-459c-a57e-e83c8dde38f5', 'b0ed382c-8dcc-3b98-845b-c22620d5633f', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'hasRangeClass');
INSERT INTO relations VALUES ('883f1612-d5fb-4796-8cbc-2b7c7324eb42', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'hasDomainClass');
INSERT INTO relations VALUES ('9460f872-8a4f-4b14-855d-42b6b3f317aa', 'f8b28fad-0fae-3a0b-a688-8a2c259bb214', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'hasRangeClass');
INSERT INTO relations VALUES ('bb54a4c3-c5e6-453d-8971-3620448c884c', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', '8c69765e-7827-371f-9db3-fea290f87739', 'subPropertyOf');
INSERT INTO relations VALUES ('1d0ee746-9933-4dbb-81bb-8b81ec03482c', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', '8c69765e-7827-371f-9db3-fea290f87739', 'hasDomainClass');
INSERT INTO relations VALUES ('79ee9152-5806-4ed1-97e5-3de871f09f4a', '8c69765e-7827-371f-9db3-fea290f87739', '48a1d09d-dc16-3903-9ad0-f2eba8b79b20', 'hasRangeClass');
INSERT INTO relations VALUES ('094b39eb-251a-433a-9a3d-0b928ebe1af8', '558bfc6c-03fc-3f1a-81d2-95493448d4a9', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'hasDomainClass');
INSERT INTO relations VALUES ('52d5dedc-0e91-4a46-9c5d-083cbc093e10', '0fcef1a0-49b7-37cb-90c7-51dcf2cd86d7', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'hasRangeClass');
INSERT INTO relations VALUES ('4abc3739-6415-41e1-8e56-b93617b1e0c3', '78b224a2-9271-3716-8c2e-c82302cdae9c', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'hasDomainClass');
INSERT INTO relations VALUES ('cb531058-2e67-4dd2-b329-2b1ff45c48c7', 'e091bc5e-86c9-328a-8c1c-deabe778c821', 'e02834c9-ae10-3659-a8e5-ccfdc1866e87', 'hasRangeClass');
INSERT INTO relations VALUES ('2e2d6b97-a718-4995-a460-dc555537765e', '78b224a2-9271-3716-8c2e-c82302cdae9c', '140073c4-60b5-352d-a5f7-244072fc4086', 'hasDomainClass');
INSERT INTO relations VALUES ('fa1a5dc1-5574-4c70-9ac7-d1d2324c0825', '140073c4-60b5-352d-a5f7-244072fc4086', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('3edb49ee-4330-46df-aa71-6b68393f498a', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'hasDomainClass');
INSERT INTO relations VALUES ('07c486e1-1fe0-4dc1-a26f-399da0645f05', 'f677091c-aa91-3851-8aa1-1225980d5e02', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'hasRangeClass');
INSERT INTO relations VALUES ('53eaebca-eee1-4beb-82ec-7d66ef937a80', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'hasDomainClass');
INSERT INTO relations VALUES ('7ca819b8-b3d7-486c-8a19-0f1b3e6df59c', 'f24003c3-0d20-3703-b044-9ed3ee42da07', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('93183c73-52f9-4c0d-a78c-250de4d7e639', '439f0684-5ebc-3227-93a5-ae9ebca7e015', '632197f8-15a2-32b6-9886-c93e587f5b64', 'subPropertyOf');
INSERT INTO relations VALUES ('d0d6b2dc-f58b-41b4-8feb-285eaa9ec417', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', '632197f8-15a2-32b6-9886-c93e587f5b64', 'subPropertyOf');
INSERT INTO relations VALUES ('595b2347-009b-4581-81f2-fd3d7aeb1601', 'f27afcc0-7657-3c5e-8314-b913c562759e', '632197f8-15a2-32b6-9886-c93e587f5b64', 'hasDomainClass');
INSERT INTO relations VALUES ('71308b3e-26d5-4bbc-97dc-d75d2028192e', '632197f8-15a2-32b6-9886-c93e587f5b64', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'hasRangeClass');
INSERT INTO relations VALUES ('15b4d4af-98a2-439b-a34d-4cf17da9650e', '7a181c4e-57f4-3a6b-a9bf-f32f1fbb18dc', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'subPropertyOf');
INSERT INTO relations VALUES ('f90d3cab-52c4-4a37-800a-d84f27b62460', 'a9888169-3160-3403-a8a2-3fa260b1ad16', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'hasDomainClass');
INSERT INTO relations VALUES ('42a4eb19-283e-4e71-abae-a8d1146988cc', '4bc601ba-6daa-3474-82dc-e3a88fca0a93', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('98013ad6-d114-4dba-94d1-1e53fe535adc', '439f0684-5ebc-3227-93a5-ae9ebca7e015', '41f65567-9d44-371a-8806-03e08d332918', 'subPropertyOf');
INSERT INTO relations VALUES ('47c17a67-e431-4e67-9f5b-3c2f3ccde4ad', '048fe43e-349a-3dda-9524-7046dcbf7287', '41f65567-9d44-371a-8806-03e08d332918', 'hasDomainClass');
INSERT INTO relations VALUES ('f870e980-38c3-48f0-9fec-daa392151158', '41f65567-9d44-371a-8806-03e08d332918', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'hasRangeClass');
INSERT INTO relations VALUES ('e487a3b9-f3ed-4c36-9e39-e88e5b063b91', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'subPropertyOf');
INSERT INTO relations VALUES ('4395d59a-7986-454c-9a70-acad9cc61336', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'subPropertyOf');
INSERT INTO relations VALUES ('a3f65bed-c23f-4d64-b36a-cc1fb0abef5e', '048fe43e-349a-3dda-9524-7046dcbf7287', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', 'hasDomainClass');
INSERT INTO relations VALUES ('c5774a3f-9f72-49c0-8a03-de4601e00d57', 'a80e1218-6520-3b92-babc-ce2d71c2ba8c', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'hasRangeClass');
INSERT INTO relations VALUES ('080aae2a-26dd-49f7-8700-fb79b7d31d0d', '439f0684-5ebc-3227-93a5-ae9ebca7e015', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'subPropertyOf');
INSERT INTO relations VALUES ('728c798e-2cf5-44fd-89df-0bc32650dae7', '92a38250-9b25-3bc0-881b-89e778c0ac43', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'hasDomainClass');
INSERT INTO relations VALUES ('8657594b-b88e-4645-a48c-eebc02caf4b9', '87e930ce-8aef-3700-af96-dd4d420fdc0f', 'a9f055a5-3cbd-3c24-9b90-b2d422fcdaa8', 'hasRangeClass');
INSERT INTO relations VALUES ('ae4c1400-589a-4e8e-9955-83f19ccebeff', '99e8de0f-fa06-381d-8406-9d467d3f96b5', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'subPropertyOf');
INSERT INTO relations VALUES ('a13a1599-84ef-4168-b776-5efa002a1743', '92a38250-9b25-3bc0-881b-89e778c0ac43', 'f887076f-2375-38bd-b11c-e2511a59e0a2', 'hasDomainClass');
INSERT INTO relations VALUES ('bdfdc4ce-e091-4bb3-91e7-8d34da114a8e', 'f887076f-2375-38bd-b11c-e2511a59e0a2', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'hasRangeClass');
INSERT INTO relations VALUES ('0d03bf18-c2d8-4ace-9202-5f1c78c1c4c6', '70064b58-4490-3d09-b463-fd18defae21f', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', 'hasDomainClass');
INSERT INTO relations VALUES ('dfb91b24-979a-4847-810a-9d2336891de9', 'a9837ed9-5ff8-34ae-907d-2dba6012e877', '70064b58-4490-3d09-b463-fd18defae21f', 'hasRangeClass');
INSERT INTO relations VALUES ('b36d6b67-4127-4f6f-8abc-a8038a555238', '70064b58-4490-3d09-b463-fd18defae21f', '8687cd99-3201-3f8f-bb1c-241732242a8f', 'hasDomainClass');
INSERT INTO relations VALUES ('c6f4e84b-6e7d-4b6e-bfa0-ef94f9424da4', '8687cd99-3201-3f8f-bb1c-241732242a8f', '70064b58-4490-3d09-b463-fd18defae21f', 'hasRangeClass');
INSERT INTO relations VALUES ('e599e09e-eeac-442f-abf7-ffd4ee8f233e', '70064b58-4490-3d09-b463-fd18defae21f', '61861fca-6102-3151-af0c-599e14e7a93a', 'hasDomainClass');
INSERT INTO relations VALUES ('6119b2d1-5901-4829-9c9e-30533e2bd2aa', '61861fca-6102-3151-af0c-599e14e7a93a', '70064b58-4490-3d09-b463-fd18defae21f', 'hasRangeClass');
INSERT INTO relations VALUES ('ad6244e0-ed98-4216-b9f9-2836becebb6a', '70064b58-4490-3d09-b463-fd18defae21f', '740ab790-feb0-3700-8922-f152320272a5', 'hasDomainClass');
INSERT INTO relations VALUES ('6ce6fb3d-a424-4d96-94d6-cda5125a755c', '740ab790-feb0-3700-8922-f152320272a5', '70064b58-4490-3d09-b463-fd18defae21f', 'hasRangeClass');
INSERT INTO relations VALUES ('07b2afc8-9f39-4330-816a-520f3700b325', '70064b58-4490-3d09-b463-fd18defae21f', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', 'hasDomainClass');
INSERT INTO relations VALUES ('d11db9a7-f6a9-4e58-a0ca-661ed026acc8', 'b4b2a280-ac3e-3e4b-b3d2-a6fef7742a0a', '70064b58-4490-3d09-b463-fd18defae21f', 'hasRangeClass');
INSERT INTO relations VALUES ('6ac7b50e-503a-42c0-981a-88b5ea24a18a', '70064b58-4490-3d09-b463-fd18defae21f', '8b7a9392-ce48-360e-b28a-c01d70eaf672', 'hasDomainClass');
INSERT INTO relations VALUES ('a31f0ec5-d0de-44e0-bea9-344447094c89', '8b7a9392-ce48-360e-b28a-c01d70eaf672', '70064b58-4490-3d09-b463-fd18defae21f', 'hasRangeClass');
INSERT INTO relations VALUES ('c52c6030-a9dc-4028-a074-a035dc937d6f', '70064b58-4490-3d09-b463-fd18defae21f', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', 'hasDomainClass');
INSERT INTO relations VALUES ('416bb506-8199-41b3-a4b3-e37d31d111fe', '911a2bbd-3ef6-30dc-afea-ae2e80d4fac8', '70064b58-4490-3d09-b463-fd18defae21f', 'hasRangeClass');
INSERT INTO relations VALUES ('6f94d6b8-11ea-4dd0-b537-84c365c45e10', '12f08da7-e25c-3e10-8179-62ed76da5da0', '74e69af6-6a10-32be-91d3-50dd33b7876b', 'hasDomainClass');
INSERT INTO relations VALUES ('cd14ef3d-9dbe-46ce-abf0-7b0bfbdb967f', '74e69af6-6a10-32be-91d3-50dd33b7876b', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('80c0ce23-c5c2-4de6-a8c0-fceb39e22516', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', 'hasDomainClass');
INSERT INTO relations VALUES ('bedffa1c-1345-47b4-83d8-ed34a3987c4a', 'da6e698d-cb4e-31ae-8ef4-c0a219a35673', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('e5573dc4-fe4c-43cc-a3ba-78303190a755', 'c2b2aac9-2434-3e1e-b4a4-52a7a317ff72', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'subPropertyOf');
INSERT INTO relations VALUES ('8ac635b6-1ec4-4ac0-b2da-e5bbbefb289f', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'hasDomainClass');
INSERT INTO relations VALUES ('6d22c297-8c4a-4073-8700-d7d7aba977ac', '50bbc81a-fe17-3469-a055-6c821ed66db1', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'hasRangeClass');
INSERT INTO relations VALUES ('6df940e6-ca83-4584-981c-1e12a1294aa7', 'f865c72a-09dd-386f-a9eb-385176727d94', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'subPropertyOf');
INSERT INTO relations VALUES ('cd1813df-f7d3-49e1-89a4-7e8e412123ed', '32b1fbb2-0f12-3f63-9f7e-c1d4026aae57', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'hasDomainClass');
INSERT INTO relations VALUES ('e7503c7e-edad-472a-a858-3cb1a5832c86', '98e3e69e-6101-3510-9a8c-7c11e279fd95', 'af1d24cc-428c-3689-bbd1-726d62ec5595', 'hasRangeClass');
INSERT INTO relations VALUES ('181d5aef-2147-4aa8-822f-81c27f80a2ec', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'hasDomainClass');
INSERT INTO relations VALUES ('a3c4cba7-dbee-444c-b57b-1f847a5c3843', 'c1eee83b-8cd1-31e6-adf3-0ce296815ba8', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'hasRangeClass');
INSERT INTO relations VALUES ('c0bbde76-9e7d-4985-9869-8eb6555c687b', 'ecb59937-c663-313c-bfbb-7f56c7ab8c81', '8bfff662-9024-325a-a23a-b3c9bf509031', 'hasDomainClass');
INSERT INTO relations VALUES ('487e689e-ac98-4062-8c45-0fb9a84064b8', '8bfff662-9024-325a-a23a-b3c9bf509031', '15afdb47-2e96-3076-8a28-ec86a8fe4674', 'hasRangeClass');
INSERT INTO relations VALUES ('15f3ac4f-0e31-41c4-b6dd-8aa233f4d73b', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'hasDomainClass');
INSERT INTO relations VALUES ('3c2bda9f-d6de-4da3-974e-1570a72706d5', '7fdc7c54-ac81-3275-b555-9d1508bad4f9', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'hasRangeClass');
INSERT INTO relations VALUES ('c9e08b79-cde7-47e4-9c1d-f61aa8b5d91a', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', '007dac32-df80-366b-88ce-02f4c1928537', 'subPropertyOf');
INSERT INTO relations VALUES ('61096f03-1eec-4a47-815d-0993364b8c97', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', '007dac32-df80-366b-88ce-02f4c1928537', 'hasDomainClass');
INSERT INTO relations VALUES ('d0b8c1b3-515a-4cf3-be53-c8c5610c45a3', '007dac32-df80-366b-88ce-02f4c1928537', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'hasRangeClass');
INSERT INTO relations VALUES ('69bb67bd-3fac-49f8-ac25-bc36245272a1', '629ed771-13e7-397e-8345-69f6cfb3db30', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'subPropertyOf');
INSERT INTO relations VALUES ('c64aa8c7-3429-46c4-9b79-a171f2a3ea08', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'hasDomainClass');
INSERT INTO relations VALUES ('32fcb6ec-7b2a-4373-a0d4-5faa8160fa1c', 'c0db66c7-ce95-3f85-a2e3-914a7004c9cc', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('7024d7b6-eb21-4125-b43d-e6837311779c', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', 'hasDomainClass');
INSERT INTO relations VALUES ('582c819f-4697-4d68-8aee-dc4af0f7976c', 'd6d729ca-ad20-3897-afaa-8427d5771c3f', '8c2720ca-5c3f-3dd0-af7c-cf217f64babb', 'hasRangeClass');
INSERT INTO relations VALUES ('fba607a1-c841-457c-aff9-a4762f1f65d2', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'subPropertyOf');
INSERT INTO relations VALUES ('e82851d4-105c-4ab2-ac90-e1c0fb1c0627', 'af051b0a-be2f-39da-8f46-429a714e242c', '68dd1374-d854-3b4e-bca3-95d41675fb2f', 'hasDomainClass');
INSERT INTO relations VALUES ('269e0411-4194-4e23-8f41-d71e8a6a359f', '68dd1374-d854-3b4e-bca3-95d41675fb2f', '6f38d2ca-e114-33a0-b4db-4f298e53be3d', 'hasRangeClass');
INSERT INTO relations VALUES ('aa8dc3cd-7d60-48a8-a90a-710a65be1128', '94ffd715-18f7-310a-bee2-010d800be058', '50060723-772d-3974-864e-8f8c326f169d', 'hasDomainClass');
INSERT INTO relations VALUES ('1203ee2b-855f-449f-b457-0f162d38361c', '50060723-772d-3974-864e-8f8c326f169d', '94ffd715-18f7-310a-bee2-010d800be058', 'hasRangeClass');
INSERT INTO relations VALUES ('d7e825fb-bb08-4303-b0b7-b48a58d7cd6d', '94ffd715-18f7-310a-bee2-010d800be058', '95473150-07f2-3967-88f3-20b803dd239d', 'hasDomainClass');
INSERT INTO relations VALUES ('09ae32a3-1c60-4f44-bd4a-73da3fdb1093', '95473150-07f2-3967-88f3-20b803dd239d', '94ffd715-18f7-310a-bee2-010d800be058', 'hasRangeClass');
INSERT INTO relations VALUES ('70e48dff-ef1b-4b05-ae5b-a5eab8339f84', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'subPropertyOf');
INSERT INTO relations VALUES ('4859e406-368d-46e3-bfaa-0102fad9f620', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', '1051349b-b0bf-3d88-8ab7-302c5c969197', 'hasDomainClass');
INSERT INTO relations VALUES ('882b336d-2e51-45d5-8c01-aef9ac5eba18', '1051349b-b0bf-3d88-8ab7-302c5c969197', '6f647ebe-423c-3fbc-a3aa-be532a1fb772', 'hasRangeClass');
INSERT INTO relations VALUES ('e9773d3f-bb17-4a87-8280-a6f4c6aa0b99', '3d79fb08-357c-358a-a5ae-c9af6aa8051b', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'subPropertyOf');
INSERT INTO relations VALUES ('0427bbb5-cb98-4af9-b0c2-e139d8160681', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'hasDomainClass');
INSERT INTO relations VALUES ('3e0f73fb-28c8-47ce-8bde-1e375adbfd90', 'a84f68c6-b6c4-3a37-b069-e85b0b286489', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'hasRangeClass');
INSERT INTO relations VALUES ('62efd93d-cd12-498b-b055-b08a6e81b5a1', 'b9ec13a4-02ec-39f2-892d-970762c3f25d', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'subPropertyOf');
INSERT INTO relations VALUES ('2cb2abfa-b7dc-4e8c-abd6-fc3de511c6e8', '70c1d151-becb-38ad-a2b5-687c8a2e89cc', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'hasDomainClass');
INSERT INTO relations VALUES ('728cfd67-8317-4377-bead-01fcfab10177', 'ec02e000-349e-35ec-8c4e-743dc12b5e6b', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('bde694ae-0b04-4588-8a51-8329011b8f8c', '2f8fd82d-2679-3d69-b697-7efe545e76ab', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'subPropertyOf');
INSERT INTO relations VALUES ('f519309c-03b7-49da-81fa-0584230d8c42', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'hasDomainClass');
INSERT INTO relations VALUES ('3d7321bb-061a-4940-80ac-6a9d5d277f4c', 'ada26737-46ff-3a34-8aed-7b70117c34aa', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'hasRangeClass');
INSERT INTO relations VALUES ('dfdac32b-f5d7-4d04-9732-fcf082e835df', '629ed771-13e7-397e-8345-69f6cfb3db30', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'subPropertyOf');
INSERT INTO relations VALUES ('c9b0ea6e-284e-4a48-bde4-9f891c8ce321', '675b1b07-d25a-3539-b5d9-84ee73f3e39e', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'hasDomainClass');
INSERT INTO relations VALUES ('df40e17f-3e83-4c4f-b161-f4883aa1da39', 'bd92eefc-6385-33ba-b7c6-d37e1ee99ee7', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('2695d842-c7de-426f-b74a-ddb3b45dfb19', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'hasDomainClass');
INSERT INTO relations VALUES ('ffa6dd57-699f-4228-8b0a-8cab88f7e176', 'b13335f9-b208-3363-af5a-2e79fb56f7cc', 'b43d4537-6674-37cb-af6e-834b5d63c978', 'hasRangeClass');
INSERT INTO relations VALUES ('d71afb80-7eb2-4149-b50f-dc8a161e7014', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'hasDomainClass');
INSERT INTO relations VALUES ('6baac3a8-27de-47e1-8679-972c8392e3df', '839c9e24-c1ab-34b4-94da-2efb1d32af01', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('eacff540-470e-4f54-adec-018556eb2b6f', 'fe1fa40b-7b56-3a38-bbd4-09112ce28eb3', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'hasDomainClass');
INSERT INTO relations VALUES ('0a685eb7-9bc6-4612-a76e-5f4934090314', '90e33e9d-8647-3d3c-b55c-7579a5bd0ce2', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('ae72b523-fde4-4a79-91b6-ca2ef9640906', 'b51b95ee-99b0-3847-80a0-50a2bd7d00e7', 'f4734d6b-f54c-3ec2-8c0e-5f98211b13bc', 'subPropertyOf');
INSERT INTO relations VALUES ('54d3183b-822f-49ae-a624-ff7dad2816c5', '09c85414-85f5-336b-87e7-9e3f1a14faeb', 'f4734d6b-f54c-3ec2-8c0e-5f98211b13bc', 'hasDomainClass');
INSERT INTO relations VALUES ('7ddc27ec-b29f-4bba-a8b6-d44ab1686ae8', 'f4734d6b-f54c-3ec2-8c0e-5f98211b13bc', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'hasRangeClass');
INSERT INTO relations VALUES ('2bad06ec-77ea-4fd5-b659-8ab4a13447e7', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', 'aac583c1-05e4-34fe-aac2-e9bbc9c6d8fd', 'subPropertyOf');
INSERT INTO relations VALUES ('4a7632b6-4cc9-45b1-854b-5c60dca527c7', 'b4f509a5-bf1f-3b1b-875f-e4dade14f862', 'aac583c1-05e4-34fe-aac2-e9bbc9c6d8fd', 'hasDomainClass');
INSERT INTO relations VALUES ('473f1a08-9cb4-4189-8113-6eaa10c77711', 'aac583c1-05e4-34fe-aac2-e9bbc9c6d8fd', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('a5c93414-e6bb-43ec-85c8-236cb9973625', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', '406ee11a-a430-386f-9087-30c28c677da6', 'subPropertyOf');
INSERT INTO relations VALUES ('4ce3ae45-a922-4589-88ad-d5c239d8d537', 'b4f509a5-bf1f-3b1b-875f-e4dade14f862', '406ee11a-a430-386f-9087-30c28c677da6', 'hasDomainClass');
INSERT INTO relations VALUES ('20ffa682-a9ec-48a0-b9d2-1fc0bd916bba', '406ee11a-a430-386f-9087-30c28c677da6', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'hasRangeClass');
INSERT INTO relations VALUES ('0efde8b3-8f8a-43e2-8c71-95f633103db3', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', '7722c7a7-c2ff-3a33-8dd6-829c5b108191', 'subPropertyOf');
INSERT INTO relations VALUES ('665a8ee2-1f69-4bec-8f61-cc62795bf720', '2c5fbf8d-b6ca-39f4-8ee7-5522732fe77e', '7722c7a7-c2ff-3a33-8dd6-829c5b108191', 'hasDomainClass');
INSERT INTO relations VALUES ('59513ab8-7a67-4fed-b9c2-77ba0a0beed7', '7722c7a7-c2ff-3a33-8dd6-829c5b108191', 'af051b0a-be2f-39da-8f46-429a714e242c', 'hasRangeClass');
INSERT INTO relations VALUES ('46fff977-5deb-435d-9c38-de3089ae5fd3', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', '5bea9c01-5e34-32ce-a1b2-cddc51a6bc7c', 'subPropertyOf');
INSERT INTO relations VALUES ('528b8b1a-8296-462c-a926-55256295b9ca', '2c5fbf8d-b6ca-39f4-8ee7-5522732fe77e', '5bea9c01-5e34-32ce-a1b2-cddc51a6bc7c', 'hasDomainClass');
INSERT INTO relations VALUES ('7adc627e-1499-4ba1-9edc-9a9176454533', '5bea9c01-5e34-32ce-a1b2-cddc51a6bc7c', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'hasRangeClass');
INSERT INTO relations VALUES ('062c6854-ed0e-44f2-83c6-002a0df5c3bb', 'de74c0db-a5fa-3f45-8684-344c379e6b0d', '9c8d34b1-0379-35d6-9470-9ad11efdef5a', 'hasDomainClass');
INSERT INTO relations VALUES ('5a614404-1fd8-410d-a2c7-53a83756e47f', '9c8d34b1-0379-35d6-9470-9ad11efdef5a', 'a9888169-3160-3403-a8a2-3fa260b1ad16', 'hasRangeClass');
INSERT INTO relations VALUES ('f4ebb10c-14f9-40ae-8da9-298e1b5ea2ea', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', 'df779f07-03dd-3ed7-91aa-025a71c95957', 'hasDomainClass');
INSERT INTO relations VALUES ('4b381ac1-bed3-4a51-afb8-1d6c3e54c651', 'df779f07-03dd-3ed7-91aa-025a71c95957', '18a02c1c-38df-3f50-baf5-fc0b5bf2732d', 'hasRangeClass');
INSERT INTO relations VALUES ('f10f8d1b-18e7-4966-9e1d-275c8f4d0228', '9bf487d8-c0a3-3510-b228-1b5cd74f4c56', 'c6888cc6-3b5e-373c-a6ba-6e6bc24773c6', 'subPropertyOf');
INSERT INTO relations VALUES ('8c0cc0f1-2f66-4a81-853a-c309e2cf2535', '0fb4acc5-0860-3bac-a8f4-3f833baaca9d', 'c6888cc6-3b5e-373c-a6ba-6e6bc24773c6', 'hasDomainClass');
INSERT INTO relations VALUES ('1c444379-f951-4ada-b978-a643587b0dd3', 'c6888cc6-3b5e-373c-a6ba-6e6bc24773c6', 'ae27d5a7-abfc-32e3-9927-99795abc53a4', 'hasRangeClass');
INSERT INTO relations VALUES ('38d8becc-0713-4360-b3a5-e73c85fb9a38', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', '75825fa7-ab9a-3b62-b7e8-250712914631', 'hasDomainClass');
INSERT INTO relations VALUES ('c2b9e900-a091-4773-afce-4cfe514a4971', '75825fa7-ab9a-3b62-b7e8-250712914631', 'a8f7cd0b-8771-3b91-a827-422ff7a15250', 'hasRangeClass');
INSERT INTO relations VALUES ('24de73f5-a67a-4cca-8508-321b87f624bf', '338e1bb4-ccdd-3d29-9d50-96c385fc2c98', '63c5d303-2789-3999-8496-297343edf6dc', 'subPropertyOf');
INSERT INTO relations VALUES ('a94d9d4f-7db1-453d-89d5-bd618c94965c', '5f7a1d37-99f2-3560-b591-9f78fd2b77c4', '63c5d303-2789-3999-8496-297343edf6dc', 'hasDomainClass');
INSERT INTO relations VALUES ('936db822-4241-4b42-a27c-dee61d75201a', '63c5d303-2789-3999-8496-297343edf6dc', '211d0da0-5fd2-3d83-bb88-c08c71b46feb', 'hasRangeClass');
INSERT INTO relations VALUES ('310e1f92-f473-431d-8449-c29f802ace22', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'e28841b2-0d53-3f91-afbf-3694a6236a5d', 'hasDomainClass');
INSERT INTO relations VALUES ('f33bfa9d-a5f4-42cf-95a7-2ecf919c2301', 'e28841b2-0d53-3f91-afbf-3694a6236a5d', '9ff08a71-8094-35ed-9005-d94abddefdfe', 'hasRangeClass');
INSERT INTO relations VALUES ('8e029c25-be9f-4d08-98cd-b31b62614153', 'db25f50b-28f3-3041-b091-8bb7d2557856', '222f5899-aa3f-3d52-a784-e5a0a68722f2', 'subPropertyOf');
INSERT INTO relations VALUES ('ab4e6b60-097e-410d-8c2b-1bbc0930a39c', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', '222f5899-aa3f-3d52-a784-e5a0a68722f2', 'hasDomainClass');
INSERT INTO relations VALUES ('f8f9a04a-d88f-4995-81b4-bc258962f40d', '222f5899-aa3f-3d52-a784-e5a0a68722f2', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('4fb221e1-f5c8-4c09-b35c-dd41cc1c4d03', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'be7f5fbc-6abd-33cd-8cb0-a7e447068b20', 'hasDomainClass');
INSERT INTO relations VALUES ('e7c2b6e7-1e4d-4098-89c2-be2ed17a9a22', 'be7f5fbc-6abd-33cd-8cb0-a7e447068b20', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', 'hasRangeClass');
INSERT INTO relations VALUES ('04cc8ee8-f3bd-4251-9161-e0bcde539953', '94ffd715-18f7-310a-bee2-010d800be058', '6f3ce351-dc26-30bf-8c50-9392f873968d', 'hasDomainClass');
INSERT INTO relations VALUES ('ab13c65e-09c1-4238-b9f6-bc97c3e003dc', '6f3ce351-dc26-30bf-8c50-9392f873968d', '9d55628a-0085-3b88-a939-b7a327263f53', 'hasRangeClass');
INSERT INTO relations VALUES ('5683713e-a227-42c8-86c5-63f21a89d4a7', '94ffd715-18f7-310a-bee2-010d800be058', 'db25f50b-28f3-3041-b091-8bb7d2557856', 'hasDomainClass');
INSERT INTO relations VALUES ('28f6d0da-8b9e-40b5-bb04-584519bb538c', 'db25f50b-28f3-3041-b091-8bb7d2557856', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('0334d92a-52b8-4967-a5d0-60eb0974ab03', 'b9af2b98-3c9d-34f1-9a87-f5eb071fb53d', '68633428-a835-3af2-9e8e-ac1ba713d4c8', 'hasDomainClass');
INSERT INTO relations VALUES ('72ca70a7-aab1-4d9b-8fa2-7b48e585dca3', '68633428-a835-3af2-9e8e-ac1ba713d4c8', '9d55628a-0085-3b88-a939-b7a327263f53', 'hasRangeClass');
INSERT INTO relations VALUES ('b266502e-7b83-4c40-b5fb-36686fd8b539', 'f677091c-aa91-3851-8aa1-1225980d5e02', 'a5a812b2-d786-38db-928f-1df9f416ab59', 'subPropertyOf');
INSERT INTO relations VALUES ('abf73f53-d68c-4202-a8c4-7db9c0eb14fc', '31aab780-6dfa-3742-bd7a-7ef0310ed0b1', 'a5a812b2-d786-38db-928f-1df9f416ab59', 'hasDomainClass');
INSERT INTO relations VALUES ('84249fbd-a85a-41b6-8b17-73d9715cabcd', 'a5a812b2-d786-38db-928f-1df9f416ab59', '5d9e0c89-8d69-3a58-8c53-3f47236c86f7', 'hasRangeClass');
INSERT INTO relations VALUES ('72490f83-fbf1-4e1f-8c20-71e48b77cc0e', 'b9af2b98-3c9d-34f1-9a87-f5eb071fb53d', '6560a44c-f6b7-3c67-bbaf-c60585bc56d9', 'hasDomainClass');
INSERT INTO relations VALUES ('6a8e1a63-3785-4e37-985d-b50f490dbb7e', '6560a44c-f6b7-3c67-bbaf-c60585bc56d9', '94ffd715-18f7-310a-bee2-010d800be058', 'hasRangeClass');
INSERT INTO relations VALUES ('7eeb4c5d-9e02-4918-ac83-5fb0cd4bfa6e', 'b9af2b98-3c9d-34f1-9a87-f5eb071fb53d', 'da115774-50f3-3292-97dc-da1cbb527ca5', 'hasDomainClass');
INSERT INTO relations VALUES ('3b9f011a-9588-4265-a6fc-47ccbfaa43bf', 'da115774-50f3-3292-97dc-da1cbb527ca5', '12f08da7-e25c-3e10-8179-62ed76da5da0', 'hasRangeClass');
INSERT INTO relations VALUES ('ba5495dc-eb58-49a4-8e5e-c2e4341e942d', '12f08da7-e25c-3e10-8179-62ed76da5da0', '81fd2793-2d69-37fe-8027-ff705a54ce3d', 'hasDomainClass');
INSERT INTO relations VALUES ('54e65e6f-be35-48df-8d81-748de4c13a74', '81fd2793-2d69-37fe-8027-ff705a54ce3d', '1036c7f1-ea95-3ad8-886f-849ca10f9584', 'hasRangeClass');
INSERT INTO relations VALUES ('db716968-e373-413a-9a9c-aba9e80b274c', '4389f634-920e-3cbb-bc3a-2a68eaa6df24', '7cd91c49-743e-3eed-ad91-d993b09af867', 'hasDomainClass');
INSERT INTO relations VALUES ('4c88f74d-0a9d-49f0-aa2f-ed3fb9f4a0ad', '7cd91c49-743e-3eed-ad91-d993b09af867', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'hasRangeClass');
INSERT INTO relations VALUES ('ceee9586-4485-47a4-b834-9903d36c7c47', '00000000-0000-0000-0000-000000000002', 'c03db431-4564-34eb-ba86-4c8169e4276c', 'narrowerTransitive');


-- Completed on 2016-05-09 13:34:44 PDT

--
-- PostgreSQL database dump complete
--

