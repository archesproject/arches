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
Cypress.Commands.add('login', (userType, options = {}) => {
  // this is an example of skipping your UI and logging in programmatically

  // setup some basic types
  // and user properties
  const types = {
    admin: {
      name: 'admin',
      password: 'admin',
      admin: true,
    },
    user: {
      name: 'nouser',
      password: 'nope',
      admin: false,
    }
  }

  // grab the user
  const user = types[userType]

  cy.visit('/auth/?next=' + options.next);
  cy.get(':nth-child(3) > .input-group > .form-control').type(user.name);
  cy.get(':nth-child(4) > .input-group > .form-control').type(user.password + '{enter}');
});
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This is will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })
