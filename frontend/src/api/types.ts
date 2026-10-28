/**
 * Types transcribed from docs/project/architecture/api-contract.yaml.
 *
 * stack.md pins no OpenAPI generator: openapi-typescript 7.13.0 peers
 * TypeScript 5 only, and the other candidates are pre-1.0 or unevaluated.
 * These names, fields, enums, and operations are the contract's. A request
 * or response field that is not in that file is not declared here.
 *
 * Length keywords in the contract describe the trimmed server value. This
 * module does not reject raw input on those keywords.
 */

export const API_BASE_PATH = "/api/v1" as const;

/** CSRF guard on POST /auth/refresh and POST /auth/logout. */
export const CSRF_REQUEST_HEADER = {
  name: "X-Requested-With",
  value: "feedback-board",
} as const;

/**
 * HttpOnly refresh cookie. JavaScript cannot and must not read it.
 * The name is the contract's security scheme `refreshCookie`.
 */
export const REFRESH_COOKIE_NAME = "refresh_token" as const;

export const ERROR_CODES = [
  "VALIDATION_ERROR",
  "UNAUTHENTICATED",
  "INVALID_CREDENTIALS",
  "FORBIDDEN",
  "ORG_REQUIRED",
  "POST_NOT_FOUND",
  "INVITE_NOT_FOUND",
  "EMAIL_TAKEN",
  "ALREADY_IN_ORGANIZATION",
  "RATE_LIMITED",
  "INTERNAL_ERROR",
] as const;

export type ErrorCode = (typeof ERROR_CODES)[number];

export type ErrorDetail = {
  field?: string;
  message?: string;
};

export type ErrorBody = {
  code: ErrorCode;
  message: string;
  details: ErrorDetail[];
};

export type ErrorResponse = {
  error: ErrorBody;
};

export type PostType = "idea" | "bug";

export type PostStatus = "New" | "Planned" | "In Progress" | "Done";

export type Role = "admin" | "member";

export type UserPublic = {
  id: string;
  display_name: string;
};

export type User = {
  id: string;
  email: string;
  display_name: string;
};

export type SignupRequest = {
  email: string;
  password: string;
  display_name: string;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: User;
};

export type Organization = {
  id: string;
  name: string;
  created_at: string;
};

export type OrganizationDetail = Organization & {
  member_count: number;
  role: Role;
};

export type CreateOrganizationRequest = {
  name: string;
};

export type OrganizationSession = {
  organization: Organization;
  role: Role;
  access_token: string;
  token_type: "bearer";
  expires_in: number;
};

export type Me = {
  user: User;
  organization: Organization | null;
  role: Role | null;
};

export type Invite = {
  token: string;
  created_at: string;
};

export type InviteTokenRequest = {
  token: string;
};

export type InvitePreview = {
  organization_name: string;
};

export type CreatePostRequest = {
  title: string;
  description: string;
  type: PostType;
};

export type UpdatePostStatusRequest = {
  status: PostStatus;
};

export type Post = {
  id: string;
  title: string;
  description: string;
  type: PostType;
  status: PostStatus;
  vote_count: number;
  comment_count: number;
  has_voted: boolean;
  author: UserPublic;
  created_at: string;
  updated_at: string;
};

export type PostPage = {
  items: Post[];
};

export type VoteState = {
  post_id: string;
  vote_count: number;
  has_voted: boolean;
};

export type CreateCommentRequest = {
  body: string;
};

export type Comment = {
  id: string;
  post_id: string;
  body: string;
  author: UserPublic;
  created_at: string;
};

export type CommentPage = {
  items: Comment[];
};

export type ListPostsQuery = {
  type?: PostType;
  status?: PostStatus;
};

/** Schema names under components/schemas, in contract order. */
export const CONTRACT_SCHEMA_NAMES = [
  "ErrorResponse",
  "PostType",
  "PostStatus",
  "Role",
  "UserPublic",
  "User",
  "SignupRequest",
  "LoginRequest",
  "AuthResponse",
  "Organization",
  "OrganizationDetail",
  "CreateOrganizationRequest",
  "OrganizationSession",
  "Me",
  "Invite",
  "InviteTokenRequest",
  "InvitePreview",
  "CreatePostRequest",
  "UpdatePostStatusRequest",
  "Post",
  "PostPage",
  "VoteState",
  "CreateCommentRequest",
  "Comment",
  "CommentPage",
] as const;

export type HttpMethod = "GET" | "POST" | "PATCH" | "DELETE";

export type ApiOperation = {
  readonly operationId: string;
  readonly method: HttpMethod;
  readonly path: string;
};

/** The 18 operations in api-contract.yaml. Paths are relative to API_BASE_PATH. */
export const API_OPERATIONS = [
  { operationId: "signup", method: "POST", path: "/auth/signup" },
  { operationId: "login", method: "POST", path: "/auth/login" },
  { operationId: "refreshToken", method: "POST", path: "/auth/refresh" },
  { operationId: "logout", method: "POST", path: "/auth/logout" },
  { operationId: "getMe", method: "GET", path: "/auth/me" },
  { operationId: "createOrganization", method: "POST", path: "/organizations" },
  { operationId: "getCurrentOrganization", method: "GET", path: "/organizations/current" },
  { operationId: "getOrCreateInvite", method: "POST", path: "/organizations/current/invite" },
  { operationId: "previewInvite", method: "POST", path: "/invites/preview" },
  { operationId: "acceptInvite", method: "POST", path: "/invites/accept" },
  { operationId: "listPosts", method: "GET", path: "/posts" },
  { operationId: "createPost", method: "POST", path: "/posts" },
  { operationId: "getPost", method: "GET", path: "/posts/{post_id}" },
  { operationId: "deletePost", method: "DELETE", path: "/posts/{post_id}" },
  { operationId: "updatePostStatus", method: "PATCH", path: "/posts/{post_id}/status" },
  { operationId: "toggleVote", method: "POST", path: "/posts/{post_id}/vote" },
  { operationId: "listComments", method: "GET", path: "/posts/{post_id}/comments" },
  { operationId: "createComment", method: "POST", path: "/posts/{post_id}/comments" },
] as const satisfies readonly ApiOperation[];

export type ApiOperationId = (typeof API_OPERATIONS)[number]["operationId"];

type JsonStatus = 200 | 201 | 204 | 400 | 401 | 403 | 404 | 409 | 429;

type OperationShape = {
  readonly body?: unknown;
  readonly query?: unknown;
  readonly responses: Partial<Record<JsonStatus, unknown>>;
};

/**
 * JSON bodies and success/error schemas declared on each operation.
 * 415 is a convention for a non-JSON Content-Type and is not listed per
 * operation in the contract, so it is not a key here.
 */
export type ApiOperationMap = {
  signup: {
    body: SignupRequest;
    responses: { 201: AuthResponse; 400: ErrorResponse; 409: ErrorResponse; 429: ErrorResponse };
  };
  login: {
    body: LoginRequest;
    responses: { 200: AuthResponse; 400: ErrorResponse; 401: ErrorResponse; 429: ErrorResponse };
  };
  refreshToken: {
    responses: { 200: AuthResponse; 401: ErrorResponse; 403: ErrorResponse; 429: ErrorResponse };
  };
  logout: {
    responses: { 204: undefined; 403: ErrorResponse };
  };
  getMe: {
    responses: { 200: Me; 401: ErrorResponse };
  };
  createOrganization: {
    body: CreateOrganizationRequest;
    responses: {
      201: OrganizationSession;
      400: ErrorResponse;
      401: ErrorResponse;
      409: ErrorResponse;
      429: ErrorResponse;
    };
  };
  getCurrentOrganization: {
    responses: { 200: OrganizationDetail; 401: ErrorResponse; 403: ErrorResponse };
  };
  getOrCreateInvite: {
    responses: { 200: Invite; 401: ErrorResponse; 403: ErrorResponse };
  };
  previewInvite: {
    body: InviteTokenRequest;
    responses: { 200: InvitePreview; 400: ErrorResponse; 404: ErrorResponse; 429: ErrorResponse };
  };
  acceptInvite: {
    body: InviteTokenRequest;
    responses: {
      200: OrganizationSession;
      400: ErrorResponse;
      401: ErrorResponse;
      404: ErrorResponse;
      409: ErrorResponse;
      429: ErrorResponse;
    };
  };
  listPosts: {
    query: ListPostsQuery;
    responses: { 200: PostPage; 400: ErrorResponse; 401: ErrorResponse; 403: ErrorResponse };
  };
  createPost: {
    body: CreatePostRequest;
    responses: { 201: Post; 400: ErrorResponse; 401: ErrorResponse; 403: ErrorResponse };
  };
  getPost: {
    responses: {
      200: Post;
      400: ErrorResponse;
      401: ErrorResponse;
      403: ErrorResponse;
      404: ErrorResponse;
    };
  };
  deletePost: {
    responses: { 204: undefined; 400: ErrorResponse; 401: ErrorResponse; 403: ErrorResponse; 404: ErrorResponse };
  };
  updatePostStatus: {
    body: UpdatePostStatusRequest;
    responses: {
      200: Post;
      400: ErrorResponse;
      401: ErrorResponse;
      403: ErrorResponse;
      404: ErrorResponse;
    };
  };
  toggleVote: {
    responses: {
      200: VoteState;
      400: ErrorResponse;
      401: ErrorResponse;
      403: ErrorResponse;
      404: ErrorResponse;
    };
  };
  listComments: {
    responses: {
      200: CommentPage;
      400: ErrorResponse;
      401: ErrorResponse;
      403: ErrorResponse;
      404: ErrorResponse;
    };
  };
  createComment: {
    body: CreateCommentRequest;
    responses: {
      201: Comment;
      400: ErrorResponse;
      401: ErrorResponse;
      403: ErrorResponse;
      404: ErrorResponse;
    };
  };
};

type AssertSameKeys<A, B> = Exclude<keyof A, keyof B> extends never
  ? Exclude<keyof B, keyof A> extends never
    ? true
    : never
  : never;

const operationMapMatchesCatalog: AssertSameKeys<ApiOperationMap, Record<ApiOperationId, OperationShape>> = true;

void operationMapMatchesCatalog;
