import { createBrowserRouter, type RouteObject } from "react-router";
import { AppShell } from "./shell";

export const appRoutes: RouteObject[] = [
  {
    path: "/",
    Component: AppShell,
  },
];

export function createAppRouter(window?: Window): ReturnType<typeof createBrowserRouter> {
  if (window === undefined) {
    return createBrowserRouter(appRoutes);
  }
  return createBrowserRouter(appRoutes, { window });
}
