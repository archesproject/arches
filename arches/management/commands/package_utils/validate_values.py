import os
import arches.app.models.models as models
from django.db.models import Q
from arches.app.models.concept import Concept
from .. import utils

import logging

# look at all domain entity values, and flag any where the value concept is not related to the entity type's concept (i.e. not part of the correct collection)
def validate_values(settings=None):
    if not settings:
        from django.conf import settings
        
    # ensure that all domain values chosen for entities are of the correct concept
    
    # get all domains entries
    # MAX_TO_CHECK = 10000
    MAX_TO_CHECK = False
    domains = models.Domains.objects.all().order_by('pk')
    if MAX_TO_CHECK:
        domains = domains[:10000]
    logging.warning("validating %s values", len(domains))
    
    invalid_values = []
    
    # for each domain entry
    for domain in domains:
        # Get the expected associated root concept via domain -> entity -> entity_type -> concept
        expected_concept  = domain.entityid.entitytypeid.conceptid
        # Get the chosen concept via domain -> value -> concept
        selected_concept = domain.val.conceptid
        
        # Check that the chosen concept is related to the entity type's concept (may be indirect)
        direct_relations = models.ConceptRelations.objects.filter( (Q(conceptidfrom=expected_concept.pk) & Q(conceptidto=selected_concept.pk))  |  Q(conceptidfrom=selected_concept.pk) & Q(conceptidto=expected_concept.pk))
        if len(direct_relations) == 0:
            # the value isn't a direct child, but may be a grandchild or more distant relative. Check the whole tree of the parent concept to be sure.
            
            # logging.warning("chosen value not directly related to parent concept. Checking full concept tree")
            full_concept = Concept()
            full_concept.get(expected_concept.pk, include_subconcepts=True, semantic=False)
            all_related = full_concept.flatten()
            all_related_ids = [x.id for x in all_related]
            if selected_concept.pk not in all_related_ids:
                entry = (domain.entityid.pk, domain.entityid.entitytypeid.pk, expected_concept.legacyoid, domain.val.conceptid.legacyoid, domain.val.value)
                invalid_values.append(entry)
                logging.warning("chosen value not related to parent concept.")
                logging.warning(",".join(entry))
                
    if len(invalid_values):
        print "invalid values were found. See logs/concept_value_errors.txt"
        utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'concept_value_errors.txt'), '')
        utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'concept_value_errors.txt'), 'entity id, entity type, expected parent concept (collection), selected value concept, value')
        invalid_values_strings = [','.join(v) for v in invalid_values]
        utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'concept_value_errors.txt'), '\n'.join(invalid_values_strings))
    else:
        print "All values were found to be valid"
    
# identify any entity types for which no actual entities exist
def find_unused_entity_types(settings=None):
    if not settings:
        from django.conf import settings
        
    unused_types = []

    for entity_type in models.EntityTypes.objects.all():
        entities = models.Entities.objects.filter(entitytypeid=entity_type)
        if not len(entities):
            unused_types.append(entity_type.pk)
            
    if len(unused_types):
        print "Some unused entity types were identified. See logs/unused_entity_types.txt"
        utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'unused_entity_types.txt'), '')
        utils.write_to_file(os.path.join(settings.PACKAGE_ROOT, 'logs', 'unused_entity_types.txt'), '\n'.join(unused_types))
    else:
        print "No unused entity types found"

