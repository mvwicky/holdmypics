export const log = PRODUCTION
  ? console.debug.bind(console)
  : console.debug.bind(console);
