describe('Home page', function() {
  it('Visits the home page', function() {
    cy.visit('/')
  })
})

describe('Log in as admin', function() {
  it('Goes to Login page from home page', function() {
    cy.visit('/auth/?next=/index.htm')

    cy.get(':nth-child(3) > .input-group > .form-control').type("admin")
    cy.get(':nth-child(4) > .input-group > .form-control').type(`admin{enter}`)

    cy.url().should("include", "/index.htm")  // redirected back to home page
  })
})