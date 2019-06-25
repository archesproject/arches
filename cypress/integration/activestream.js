describe('Get the OrderedCollection representation', function() {
    it('Get and assert it has the correct type', function() {
        cy.login();
        cy.request("/history").then((response) => {
            expect(response.body.type).to.eq("OrderedCollection");
        });
    });
});

describe('Find the first OrderedCollectionPage', function() {
    it('Using the OrderedCollection object', function() {
        cy.login();
        cy.request("/history").then((response) => {
            cy.request(response.body.first.id).then((response) =>{
                expect(response.status).to.eq(200);
                expect(response.body.type).to.eq("OrderedCollectionPage");
            });
        });
    });
});

describe('Find the last OrderedCollectionPage', function() {
    it('Using the OrderedCollection object', function() {
        cy.login();
        cy.request("/history").then((response) => {
            cy.request(response.body.last.id).then((response) =>{
                expect(response.status).to.eq(200);
                expect(response.body.type).to.eq("OrderedCollectionPage");
            });
        });
    });
});

describe('Check the total number of items exists', function() {
    it('in the OrderedCollection', function() {
        cy.login();
        cy.request("/history").then((response) => {
            expect(response.body.totalItems).to.exist;
        });
    });
});

describe('Check the total number of items exists', function() {
    it('In the OrderedCollectionPage (first)', function() {
        cy.login();
        cy.request("/history").then((response) => {
            cy.request(response.body.first.id).then((response) =>{
                expect(response.body.partOf.totalItems).to.exist;
            });
        });
    });
});