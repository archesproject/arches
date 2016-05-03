# System Design

## Architecture Diagram

## Data Model
tiles - stores instances of business data as json object. Recursive relationship supports instances of groups within groups.

nodegroups - defines the sets of nodes that should be saved in a single tile record.  For example, NAME and NAME_TYPE.  Recursive relationship supports the ability to create nodegroups within nodegroups i.e. sub-branches of condition assessment.

cards - frames widgets necessary for capturing and editing tile data.  Expecting that each nodegroup will be associated to one card.  Cards have a recursive relationship to manage wizards… cards within cards.

Keeping the tables separate because cards represent UI elements and nodegroups represent grouped data.

### Visual Data Model
![images/Arches4_ERD_20160310.jpg](https://raw.githubusercontent.com/wiki/archesproject/arches/images/Arches4_ERD_20160310.jpg)

## Graphs/Cards/Widgets/Reports

## Validation/Functions

## Search
