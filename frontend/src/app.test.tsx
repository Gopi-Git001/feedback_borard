import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { renderToStaticMarkup } from "react-dom/server";
import { createMemoryRouter, RouterProvider } from "react-router";
import { describe, expect, it } from "vitest";
import { API_OPERATIONS, CONTRACT_SCHEMA_NAMES, ERROR_CODES } from "./api/types";
import type {
  AuthResponse,
  Comment,
  CommentPage,
  CreateCommentRequest,
  CreateOrganizationRequest,
  CreatePostRequest,
  ErrorResponse,
  Invite,
  InvitePreview,
  InviteTokenRequest,
  LoginRequest,
  Me,
  Organization,
  OrganizationDetail,
  OrganizationSession,
  Post,
  PostPage,
  SignupRequest,
  UpdatePostStatusRequest,
  User,
  UserPublic,
  VoteState,
} from "./api/types";
import { createAppRouter } from "./router";
import { AppShell } from "./shell";

const contractPath = resolve(
  dirname(fileURLToPath(import.meta.url)),
  "../../docs/project/architecture/api-contract.yaml",
);

function readContract(): string {
  return readFileSync(contractPath, "utf8");
}

function operationRecords(yaml: string): { operationId: string; method: string; path: string }[] {
  const records: { operationId: string; method: string; path: string }[] = [];
  let path = "";
  let method = "";
  for (const line of yaml.split("\n")) {
    const pathMatch = /^ {2}(\/[^:]+):$/.exec(line);
    if (pathMatch?.[1] !== undefined) {
      path = pathMatch[1];
      method = "";
      continue;
    }
    const methodMatch = /^ {4}(get|post|patch|delete):$/.exec(line);
    if (methodMatch?.[1] !== undefined) {
      method = methodMatch[1].toUpperCase();
      continue;
    }
    const idMatch = /^ {6}operationId: ([A-Za-z0-9]+)$/.exec(line);
    if (idMatch?.[1] !== undefined) {
      records.push({ operationId: idMatch[1], method, path });
    }
  }
  return records;
}

function schemaNames(yaml: string): string[] {
  const start = yaml.indexOf("\n  schemas:\n");
  if (start < 0) {
    return [];
  }
  const section = yaml.slice(start);
  const names: string[] = [];
  for (const line of section.split("\n")) {
    if (line.startsWith("  securitySchemes:") || line.startsWith("  headers:")) {
      break;
    }
    const match = /^ {4}([A-Za-z0-9]+):$/.exec(line);
    if (match?.[1] !== undefined) {
      names.push(match[1]);
    }
  }
  return names;
}

function errorCodes(yaml: string): string[] {
  const marker = "description: Stable machine-readable code.";
  const start = yaml.indexOf(marker);
  if (start < 0) {
    return [];
  }
  const codes: string[] = [];
  let inEnum = false;
  for (const line of yaml.slice(start).split("\n")) {
    if (!inEnum) {
      if (line.includes("enum:")) {
        inEnum = true;
      }
      continue;
    }
    const match = /^\s+- ([A-Z_]+)$/.exec(line);
    if (match?.[1] !== undefined) {
      codes.push(match[1]);
      continue;
    }
    break;
  }
  return codes;
}

function browserWindow(): Window {
  let historyState: unknown = null;
  const location = {
    pathname: "/",
    search: "",
    hash: "",
    href: "http://localhost/",
    origin: "http://localhost",
    assign() {
      return undefined;
    },
  };
  const history = {
    get state() {
      return historyState;
    },
    length: 1,
    scrollRestoration: "auto" as const,
    replaceState(state: unknown) {
      historyState = state;
    },
    pushState(state: unknown) {
      historyState = state;
    },
    go() {
      return undefined;
    },
  };
  const listeners = new Map<string, Set<EventListener>>();
  const win = {
    location,
    history,
    addEventListener(type: string, listener: EventListener) {
      const set = listeners.get(type) ?? new Set<EventListener>();
      set.add(listener);
      listeners.set(type, set);
    },
    removeEventListener(type: string, listener: EventListener) {
      listeners.get(type)?.delete(listener);
    },
  };
  return win as unknown as Window;
}

describe("app shell", () => {
  it("renders a named main region and one heading", () => {
    const html = renderToStaticMarkup(<AppShell />);
    expect(html).toContain('id="main"');
    expect(html).toContain('tabindex="-1"');
    expect(html).toContain("<h1>Team Feedback Board</h1>");
    expect(html).toContain("Skip to content");
    expect(html).toContain("App shell placeholder");
    expect(html.match(/<h1/g)).toHaveLength(1);
  });

  it("matches the placeholder route with createBrowserRouter", () => {
    const fakeWindow = browserWindow();
    const previous = globalThis.window;
    Object.defineProperty(globalThis, "window", {
      value: fakeWindow,
      configurable: true,
      writable: true,
    });
    try {
      const router = createAppRouter(fakeWindow);
      expect(router.state.location.pathname).toBe("/");
      expect(router.state.matches[0]?.route.path).toBe("/");
    } finally {
      if (previous === undefined) {
        Reflect.deleteProperty(globalThis, "window");
      } else {
        Object.defineProperty(globalThis, "window", {
          value: previous,
          configurable: true,
          writable: true,
        });
      }
    }
  });

  it("renders the shell for the index route", () => {
    const router = createMemoryRouter(
      [
        {
          path: "/",
          Component: AppShell,
        },
      ],
      { initialEntries: ["/"] },
    );
    const html = renderToStaticMarkup(<RouterProvider router={router} />);
    expect(html).toContain("Team Feedback Board");
    expect(html).toContain("App shell placeholder");
  });
});

describe("api contract types", () => {
  const yaml = readContract();

  it("lists the same operations as api-contract.yaml", () => {
    expect(operationRecords(yaml)).toEqual([...API_OPERATIONS]);
  });

  it("lists the same schema names as api-contract.yaml", () => {
    expect(schemaNames(yaml)).toEqual([...CONTRACT_SCHEMA_NAMES]);
  });

  it("lists the same error codes as api-contract.yaml", () => {
    expect(errorCodes(yaml)).toEqual([...ERROR_CODES]);
  });

  it("accepts contract-shaped values", () => {
    const user = { id: "0192f1c0-0000-7000-8000-000000000001", email: "ana@example.com", display_name: "Ana" } satisfies User;
    const author = { id: user.id, display_name: user.display_name } satisfies UserPublic;
    const organization = {
      id: "0192f1c0-0000-7000-8000-0000000000a1",
      name: "Platform Team",
      created_at: "2026-10-27T18:30:00Z",
    } satisfies Organization;
    const auth = {
      access_token: "token",
      token_type: "bearer",
      expires_in: 900,
      user,
    } satisfies AuthResponse;
    const signup = { email: user.email, password: "correct-horse-battery", display_name: "Ana" } satisfies SignupRequest;
    const login = { email: user.email, password: "correct-horse-battery" } satisfies LoginRequest;
    const created = { name: "Platform Team" } satisfies CreateOrganizationRequest;
    const session = {
      organization,
      role: "admin",
      access_token: auth.access_token,
      token_type: "bearer",
      expires_in: 900,
    } satisfies OrganizationSession;
    const detail = { ...organization, member_count: 3, role: "admin" } satisfies OrganizationDetail;
    const me = { user, organization, role: "admin" } satisfies Me;
    const noOrg = { user, organization: null, role: null } satisfies Me;
    const invite = { token: "PNqzMLttQPIF8nHKGWLPGIMzyUHw8lLpXulro9uECFo", created_at: organization.created_at } satisfies Invite;
    const inviteBody = { token: invite.token } satisfies InviteTokenRequest;
    const preview = { organization_name: organization.name } satisfies InvitePreview;
    const postBody = { title: "Dark mode", description: "Please add a dark theme.", type: "idea" } satisfies CreatePostRequest;
    const statusBody = { status: "In Progress" } satisfies UpdatePostStatusRequest;
    const post = {
      id: "0192f1c0-0000-7000-8000-0000000000c1",
      title: postBody.title,
      description: postBody.description,
      type: "idea",
      status: "New",
      vote_count: 0,
      comment_count: 0,
      has_voted: false,
      author,
      created_at: organization.created_at,
      updated_at: organization.created_at,
    } satisfies Post;
    const page = { items: [post] } satisfies PostPage;
    const vote = { post_id: post.id, vote_count: 1, has_voted: true } satisfies VoteState;
    const commentBody = { body: "Would love this too." } satisfies CreateCommentRequest;
    const comment = {
      id: "0192f1c0-0000-7000-8000-0000000000d1",
      post_id: post.id,
      body: commentBody.body,
      author,
      created_at: organization.created_at,
    } satisfies Comment;
    const comments = { items: [comment] } satisfies CommentPage;
    const error = {
      error: { code: "VALIDATION_ERROR", message: "Request validation failed.", details: [{ field: "title", message: "too long" }] },
    } satisfies ErrorResponse;

    expect(signup.display_name).toBe("Ana");
    expect(login.email).toBe(user.email);
    expect(created.name).toBe("Platform Team");
    expect(detail.member_count).toBe(3);
    expect(me.role).toBe("admin");
    expect(noOrg.organization).toBeNull();
    expect(inviteBody.token).toBe(invite.token);
    expect(preview.organization_name).toBe("Platform Team");
    expect(statusBody.status).toBe("In Progress");
    expect(page.items).toHaveLength(1);
    expect(vote.has_voted).toBe(true);
    expect(comments.items[0]?.body).toBe("Would love this too.");
    expect(session.token_type).toBe("bearer");
    expect(error.error.code).toBe("VALIDATION_ERROR");
  });
});
