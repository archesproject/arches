// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })


Cypress.Commands.add("login", () => {
    cy.visit('/auth/?next=/index.htm');

    cy.get(':nth-child(3) > .input-group > .form-control').type("admin");
    cy.get(':nth-child(4) > .input-group > .form-control').type(`admin{enter}`);
  
});