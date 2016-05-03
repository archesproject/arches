# System Design

## Architecture Diagram

## Data Model
tiles - stores instances of business data as json object. Recursive relationship supports instances of groups within groups.

nodegroups - defines the sets of nodes that should be saved in a single tile record.  For example, NAME and NAME_TYPE.  Recursive relationship supports the ability to create nodegroups within nodegroups i.e. sub-branches of condition assessment.

cards - frames widgets necessary for capturing and editing tile data.  Expecting that each nodegroup will be associated to one card.  Cards have a recursive relationship to manage wizards… cards within cards.

Keeping the tables separate because cards represent UI elements and nodegroups represent grouped data.

### Visual Data Model
![images/Arches4_ERD_20160310.jpg](https://raw.githubusercontent.com/wiki/archesproject/arches/images/Arches4_ERD_20160310.jpg)

### Data Model Decisions
Within the physical data model, we will keep nodegroups and cardgroups as separate tables because it is possible that a single nodegroup can be visualized on two separate cards within two separate manifestations of the UI.  The envisioned use case is where one nodegroup is represented on one card in the web app, and in a different card in the mobile app.   Therefore, nodegroups have a one-to-many relationship with cards and require separate tables.

## Graphs/Cards/Widgets/Reports

## Validation/Functions

## Search
