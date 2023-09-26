# CSS Style Guide for Arches 7.x
## Definitions

### RTL Styling
RTL (Right to Left) interfaces for internationalization are supported in Arches 7.x.  
Some languages used in Arches (Hebrew, Arabic) have different UI needs because they 
are read from right to left.  The guidelines in this document will help conform to 
generally accepted RTL interface design principles.

### Responsive Design
Responsive design means that the interface of Arches should respond to changes in 
size (specifically width).  This helps to accommodate differing screen sizes 
(including very small screens, like mobile devices).

## Guidelines
### General advice:
- Use scss to group related styles together through nesting.
- Use rtl.scss as a last resort to overriding styles in arches.scss for RTL.  
- Test styles by using the “dir” attribute of the body HTML tag of the page being 
worked on.  Change it to “rtl” and the page will mirror as an RTL user would see 
the page. (Note that it’s necessary to actually change the page language in the 
Arches language dropdown in order to have rtl.scss included)
- To get an idea about how RTL interfaces are different from LTR interfaces (and 
how to convert one to the other) consult the following guides.  Material Style 
Guide RTL Styling Guide
- As a general rule try to adhere to the following rules, but there may be times 
when it’s not possible.  In that case at least confirm that the site renders 
reasonably in RTL as well as LTR.  Reach out for help if you need it.
- Combine selectors with redundant rules.
- Use shorthand css rules where applicable.
- Remove unused CSS rulesets.

### Prefer using:
- Flex and Grid Layouts have great inherent RTL support.  When building out new 
components, use them wherever possible. 
- Left and right margins should be equal whenever possible
- Alignment properties (align-items, justify-content, etc) versus padding and 
margin to align content CSS overrides using specificity (example: .test 
.test2 overrides .test2)

### Avoid using:
- CSS “float”
- Positioning elements (eg: fixed, absolute, etc..)  that break RTL or responsive guidelines
- Negative margins and negative padding
- Empty rulesets
- !important - it interrupts natural CSS overrides
