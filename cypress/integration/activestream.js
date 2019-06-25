describe('Get the OrderedCollection representation', function() {
  it('Get and assert it has the correct type', function() {
    cy.login();
    cy.request("/history").then((response) => {
      expect(response.body.type).to.eq("OrderedCollection"); // true
    });
  });
});

describe('Find the first OrderedCollectionPage', function() {
  it('Usingthe OrderedCollection object', function() {
    cy.login();
    cy.request("/history").then((response) => {
      cy.request(response.body.first.id).then((response) =>{
        expect(response.status).to.eq(200);
        expect(response.body.type).to.eq("OrderedCollectionPage");
      });
    });
  });
});