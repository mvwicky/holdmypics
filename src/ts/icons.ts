import { log } from "./log";

export async function replaceIcons() {
  const feather = await import(
    /* webpackChunkName: "feather" */ "feather-icons"
  );
  log(`Replacing all icons`);
  feather.replace();
}
