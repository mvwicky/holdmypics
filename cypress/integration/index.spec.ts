const deleteAll = "{selectall}{backspace}";

describe("Index", function () {
  beforeEach(function () {
    cy.visit("/");
  });

  const getImage = () => {
    const $endpoint = Cypress.$("#endpoint");
    const src = $endpoint.text();
    cy.request({ url: src }).its("status").should("eq", 200);
  };

  ["778", "1234", "111"].forEach((sz) => {
    it(`Sets width to ${sz}`, function () {
      cy.get("#width").type(deleteAll).type(sz);
      cy.get("#endpoint").first().should("contain.text", `${sz}x`);
    });
    it(`Sets height to ${sz}`, function () {
      cy.get("#height").type(deleteAll).type(sz);
      cy.get("#endpoint").first().should("contain.text", `x${sz}`);
    });
  });

  ["fec", "000", "fff000", "abcdef", "rand"].forEach((col) => {
    it(`Sets the background color to ${col}.`, function () {
      cy.get("#bg").type(deleteAll).type(col);
      cy.get("#endpoint").contains(col);
      getImage();
    });
    it(`Sets the foreground color to ${col}.`, function () {
      cy.get("#fg").type(deleteAll).type(col);
      cy.get("#endpoint").contains(col);
      getImage();
    });
  });
  it("Copies the current link.", function () {});
});
