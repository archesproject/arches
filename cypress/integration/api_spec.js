describe("Test listing of resources", function() {
  it("checks the form of the JSON LDP response", function() {
    cy.login("admin", {'next':'/index.htm'})
    cy.request('GET', '/resources/').then((response) => {
      // response.body should be as JSON
      expect(response.body).to.have.property("@type", "ldp:BasicContainer");
      expect(response.body).to.have.property("@context");
    });
  });
});

describe("Test listing of resources, filtered by a graph_id", function() {
  it("needs a valid response, and that the graph_id is a label", function() {
    cy.login("admin", {'next':'/index.htm'})
    cy.request({method: 'GET',
                url: '/resources/',
                qs: {'graph_id':'5999bc6e-549d-11e9-8b9e-0242ac1b0007'}}).then((response) => {
      // response.body should be as JSON
      expect(response.body).to.have.property("@type", "ldp:BasicContainer");
      expect(response.body).to.have.property("@context");
      expect(response.body).to.have.property("label", "Graph ID: 5999bc6e-549d-11e9-8b9e-0242ac1b0007");

    });
  });
});

