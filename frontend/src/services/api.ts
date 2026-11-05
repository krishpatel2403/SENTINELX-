import {
  Alert,
  AlertCreate,
  AlertFilter,
  AlertList,
  AlertUpdate,
  DashboardStats,
  DetectionRule,
  DetectionRuleCreate,
  Incident,
  IncidentCreate,
  IncidentFilter,
  IncidentList,
  IncidentNote,
  IncidentNoteCreate,
  IncidentUpdate,
  LoginRequest,
  MitreMapping,
  ReportGenerate,
  SecurityEvent,
  SecurityEventFilter,
  SecurityEventList,
  Token,
  ThreatIndicator,
  ThreatIndicatorCreate,
  ThreatIndicatorFilter,
  ThreatIndicatorList,
  User,
} from "../types";

export type { Token };

const API_BASE = (import.meta.env?.VITE_API_BASE_URL as string | undefined) || "/api";

function headers(token?: string | null): HeadersInit {
  const h: HeadersInit = { "Content-Type": "application/json" };
  if (token) h["Authorization"] = `Bearer ${token}`;
  return h;
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("sentinelx_token");
}

async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const token = getToken();
  const res = await fetch(API_BASE + path, {
    ...init,
    headers: { ...headers(token), ...init.headers },
  });
  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      detail = body?.message || body?.detail || JSON.stringify(body);
    } catch {
      detail = res.statusText;
    }
    throw new Error(detail || `Request failed ${res.status}`);
  }
  if (res.status === 204) return undefined as unknown as T;
  return res.json();
}

// --- Auth ---
export const authApi = {
  login: (data: LoginRequest): Promise<Token> =>
    request<Token>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  register: (data: {
    username: string;
    email: string;
    password: string;
    role?: string;
  }): Promise<User> =>
    request<User>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  me: (): Promise<User> => request<User>("/api/v1/auth/me"),
  logout: (): Promise<{ message: string }> =>
    request<{ message: string }>("/api/v1/auth/logout", { method: "POST" }),
};

// --- Events ---
export const eventsApi = {
  list: (params: SecurityEventFilter): Promise<SecurityEventList> => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
    });
    return request<SecurityEventList>("/api/v1/events/?" + qs.toString());
  },
  get: (id: number): Promise<SecurityEvent> =>
    request<SecurityEvent>("/api/v1/events/" + id),
  summary: (): Promise<{
    total_events: number;
    by_severity: Record<string, number>;
  }> => request("/api/v1/events/stats/summary"),
};

// --- Ingestion ---
export const ingestionApi = {
  upload: (
    file: File,
    source?: string,
  ): Promise<{
    filename: string;
    total_records: number;
    accepted: number;
    rejected: number;
    skipped: number;
    duplicates: number;
    results: Array<{
      line_number: number;
      accepted: boolean;
      event_id?: string | null;
      reason?: string | null;
    }>;
  }> => {
    const fd = new FormData();
    fd.append("file", file);
    if (source) fd.append("source", source);
    return request("/api/v1/ingestion/upload", {
      method: "POST",
      body: fd as unknown as BodyInit,
      headers: {} as HeadersInit, // let browser set Content-Type
    });
  },
  sources: (): Promise<{ sources: Array<{ id: string; label: string }> }> =>
    request("/api/v1/ingestion/sources"),
};

// --- Detection rules ---
export const rulesApi = {
  list: (
    enabled?: boolean,
  ): Promise<DetectionRule[]> =>
    request<DetectionRule[]>(
      "/api/v1/rules/" + (enabled !== undefined ? "?enabled=" + enabled : ""),
    ),
  get: (id: number): Promise<DetectionRule> =>
    request<DetectionRule>("/api/v1/rules/" + id),
  create: (data: DetectionRuleCreate): Promise<DetectionRule> =>
    request<DetectionRule>("/api/v1/rules/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: Partial<DetectionRuleCreate>): Promise<DetectionRule> =>
    request<DetectionRule>("/api/v1/rules/" + id, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  remove: (id: number): Promise<void> =>
    request<void>("/api/v1/rules/" + id, { method: "DELETE" }),
  evaluate: (): Promise<{
    created_alerts: number;
    alerts: Array<{
      id: number;
      alert_id: string;
      rule_id: number;
      title: string;
      severity: string;
      status: string;
    }>;
  }> => request("/api/v1/rules/evaluate", { method: "POST" }),
};

// --- Alerts ---
export const alertsApi = {
  list: (params: AlertFilter): Promise<AlertList> => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
    });
    return request<AlertList>("/api/v1/alerts/?" + qs.toString());
  },
  get: (id: number): Promise<Alert> =>
    request<Alert>("/api/v1/alerts/" + id),
  create: (data: AlertCreate): Promise<Alert> =>
    request<Alert>("/api/v1/alerts/", { method: "POST", body: JSON.stringify(data) }),
  update: (id: number, data: AlertUpdate): Promise<Alert> =>
    request<Alert>("/api/v1/alerts/" + id, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};

// --- Incidents ---
export const incidentsApi = {
  list: (params: IncidentFilter): Promise<IncidentList> => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
    });
    return request<IncidentList>("/api/v1/incidents/?" + qs.toString());
  },
  get: (id: number): Promise<Incident> =>
    request<Incident>("/api/v1/incidents/" + id),
  create: (data: IncidentCreate): Promise<Incident> =>
    request<Incident>("/api/v1/incidents/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: number, data: IncidentUpdate): Promise<Incident> =>
    request<Incident>("/api/v1/incidents/" + id, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  addNote: (incidentId: number, data: IncidentNoteCreate): Promise<IncidentNote> =>
    request<IncidentNote>(
      "/api/v1/incidents/" + incidentId + "/notes",
      { method: "POST", body: JSON.stringify(data) },
    ),
};

// --- Intelligence ---
export const intelligenceApi = {
  listIndicators: (
    params: ThreatIndicatorFilter,
  ): Promise<ThreatIndicatorList> => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
    });
    return request<ThreatIndicatorList>(
      "/api/v1/intelligence/indicators?" + qs.toString(),
    );
  },
  enrich: (
    indicatorType: string,
    indicatorValue: string,
  ): Promise<{
    indicator_type: string;
    indicator_value: string;
    classification: string;
    reputation?: string | null;
    source?: string | null;
    confidence?: number | null;
    first_seen?: string | null;
    last_seen?: string | null;
    available: boolean;
  }> =>
    request(
      "/api/v1/intelligence/enrich/" +
        encodeURIComponent(indicatorType) +
        "/" +
        encodeURIComponent(indicatorValue),
    ),
  upsertIndicator: (
    data: ThreatIndicatorCreate,
  ): Promise<ThreatIndicator> =>
    request<ThreatIndicator>("/api/v1/intelligence/indicators", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// --- MITRE ---
export const mitreApi = {
  techniques: (): Promise<Array<{
    technique_id: string;
    technique_name: string;
    tactic: string;
    description: string;
    detection_rule_types: string[];
  }>> => request("/api/v1/mitre/techniques"),
  mapping: (): Promise<MitreMapping> =>
    request<MitreMapping>("/api/v1/mitre/mapping"),
};

// --- Dashboard ---
export const dashboardApi = {
  stats: (): Promise<DashboardStats> =>
    request<DashboardStats>("/api/v1/dashboard/stats"),
  eventsOverTime: (days?: number): Promise<Array<{ date: string; count: number }>> => {
    const qs = days !== undefined ? "?days=" + days : "";
    return request("/api/v1/dashboard/events-over-time" + qs);
  },
};

// --- Users ---
export const usersApi = {
  list: (): Promise<User[]> => request<User[]>("/api/v1/users/"),
  create: (data: {
    username: string;
    email: string;
    password: string;
    role?: string;
  }): Promise<User> =>
    request<User>("/api/v1/users/", { method: "POST", body: JSON.stringify(data) }),
  update: (id: number, data: Partial<User>): Promise<User> =>
    request<User>("/api/v1/users/" + id, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  remove: (id: number): Promise<void> =>
    request<void>("/api/v1/users/" + id, { method: "DELETE" }),
};

// --- Reports ---
export const reportsApi = {
  generate: (data: ReportGenerate): Promise<{
    report_id: string;
    format: string;
    download_url?: string;
  }> =>
    request("/api/v1/reports/generate", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  list: (): Promise<Array<{
    id: number;
    report_id: string;
    format: string;
    period_start?: string | null;
    period_end?: string | null;
    checksum?: string | null;
    created_at: string;
  }>> => request("/api/v1/reports/"),
};
