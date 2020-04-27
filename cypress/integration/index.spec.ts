const deleteAll = "{selectall}{backspace}";

describe("Index", function () {
  beforeEach(function () {
    cy.visit("/");
    cy.get("#endpoint-url").as("endpoint");
  });

  const getImage = () => {
    cy.get("@endpoint").then(function (elem) {
      cy.request({ url: elem.text() }).its("status").should("eq", 200);
    });
  };

  it("Has a maximum width.", function () {
    cy.get("#width").then(function (elem) {
      expect(elem.attr("max")).to.not.be.undefined;
    });
  });

  ["300", "250", "111"].forEach((sz) => {
    it(`Sets width to ${sz}`, function () {
      cy.get("#width").type(deleteAll).type(sz);
      cy.get("#endpoint-url").first().should("contain.text", `${sz}x`);
      getImage();
    });
    it(`Sets height to ${sz}`, function () {
      cy.get("#height").type(deleteAll).type(sz);
      cy.get("#endpoint-url").first().should("contain.text", `x${sz}`);
      getImage();
      cy.screenshot();
    });
  });

  it("Enables random text", function () {
    cy.get("#randomText").click();
    cy.get("@endpoint").then(function (elem) {
      cy.request({ url: elem.text() })
        .debug()
        .then(function (res) {
          expect(res.status).to.equal(200);
          expect(res.headers).to.have.property("X-Random-Text");
        });
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
});
