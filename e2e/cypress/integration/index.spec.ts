const deleteAll = "{selectall}{backspace}";

describe("Index", function () {
  beforeEach(function () {
    cy.visit("/");
    cy.dataCy("endpoint-url").as("endpoint");
  });

  const getImage = () => {
    cy.get("@endpoint").then(function (elem) {
      cy.request({ url: elem.text() }).its("status").should("eq", 200);
    });
  };

  it("Has a maximum width.", function () {
    cy.get("[data-cy=width]").should(($elem) => {
      expect($elem.attr("max")).to.not.be.undefined;
    });
  });

  ["300", "250", "111"].forEach((sz) => {
    it(`Sets width to ${sz}`, function () {
      cy.get("[data-cy=width]").type(deleteAll).type(sz);
      cy.get("@endpoint").should("contain.text", `${sz}x`);
      getImage();
    });
    it(`Sets height to ${sz}`, function () {
      cy.get("[data-cy=height]").type(deleteAll).type(sz);
      cy.get("@endpoint").should("contain.text", `x${sz}`);
      getImage();
      cy.screenshot();
    });
  });

  it("Enables random text", function () {
    cy.get("[data-cy=randomText]").click();
    cy.get("@endpoint")
      .should("contain.text", "random_text")
      .then(($elem) => {
        cy.request({ url: $elem.text() }).then(function (res) {
          expect(res.status).to.equal(200);
          expect(res.headers).to.have.property("x-random-text");
        });
      });
  });

  ["fec", "000", "fff000", "abcdef", "rand"].forEach((col) => {
    it(`Sets the background color to ${col}.`, function () {
      cy.get("[data-cy=bg]").type(deleteAll).type(col);
      cy.get("@endpoint").contains(col);
      getImage();
    });
    it(`Sets the foreground color to ${col}.`, function () {
      cy.get("[data-cy=fg]").type(deleteAll).type(col);
      cy.get("@endpoint").contains(col);
      getImage();
    });
  });
});
