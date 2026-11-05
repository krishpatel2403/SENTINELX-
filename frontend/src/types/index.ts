export type Role = "admin" | "analyst";

export interface User {
  id: number;
  username: string;
  email: string;
  role: Role;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface SecurityEvent {
  id: number;
  event_id: string;
  timestamp: string;
  source: string;
  hostname?: string | null;
  username?: string | null;
  source_ip?: string | null;
  destination_ip?: string | null;
  event_type: string;
  severity: string;
  description: string;
  raw_event: any;
  event_metadata: any;
  is_duplicate: boolean;
  original_event_id?: string | null;
  created_at: string;
}

export interface SecurityEventFilter {
  source?: string;
  severity?: string;
  event_type?: string;
  username?: string;
  source_ip?: string;
  start_time?: string;
  end_time?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface SecurityEventList {
  items: SecurityEvent[];
  total: number;
  page: number;
  page_size: number;
}

export interface DetectionRule {
  id: number;
  name: string;
  description: string;
  mitre_technique_id?: string | null;
  mitre_tactic?: string | null;
  severity: string;
  threshold: number;
  time_window: number;
  enabled: boolean;
  rule_type: string;
  config: any;
  created_at: string;
  updated_at: string;
}

export interface DetectionRuleCreate {
  name: string;
  description: string;
  mitre_technique_id?: string;
  mitre_tactic?: string;
  severity?: string;
  threshold?: number;
  time_window?: number;
  enabled?: boolean;
  rule_type: string;
  config?: any;
}

export interface Alert {
  id: number;
  alert_id: string;
  rule_id: number;
  event_id: number;
  title: string;
  description: string;
  severity: string;
  status: string;
  assigned_to?: number | null;
  resolved_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertCreate {
  rule_id: number;
  event_id: number;
  title: string;
  description: string;
  severity: string;
  status?: string;
  assigned_to?: number;
}

export interface AlertUpdate {
  title?: string;
  description?: string;
  severity?: string;
  status?: string;
  assigned_to?: number;
}

export interface AlertFilter {
  status?: string;
  severity?: string;
  assigned_to?: number;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface AlertList {
  items: Alert[];
  total: number;
  page: number;
  page_size: number;
}

export interface Incident {
  id: number;
  incident_id: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  assigned_to?: number | null;
  resolution?: string | null;
  closed_at?: string | null;
  created_at: string;
  updated_at: string;
  alerts: Alert[];
}

export interface IncidentCreate {
  title: string;
  description: string;
  severity: string;
  status?: string;
  assigned_to?: number;
  alert_ids?: number[];
}

export interface IncidentUpdate {
  title?: string;
  description?: string;
  severity?: string;
  status?: string;
  assigned_to?: number;
  resolution?: string;
}

export interface IncidentList {
  items: Incident[];
  total: number;
  page: number;
  page_size: number;
}

export interface IncidentNote {
  id: number;
  incident_id: number;
  user_id: number;
  note: string;
  created_at: string;
}

export interface IncidentNoteCreate {
  note: string;
}

export interface ThreatIndicator {
  id: number;
  indicator_type: string;
  indicator_value: string;
  classification: string;
  reputation?: string | null;
  source?: string | null;
  confidence?: number | null;
  first_seen?: string | null;
  last_seen?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ThreatIndicatorCreate {
  indicator_type: string;
  indicator_value: string;
  classification?: string;
  reputation?: string;
  source?: string;
  confidence?: number;
  first_seen?: string;
  last_seen?: string;
}

export interface ThreatIndicatorFilter {
  indicator_type?: string;
  classification?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface IncidentFilter {
  status?: string;
  severity?: string;
  assigned_to?: number;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface ThreatIndicatorList {
  items: ThreatIndicator[];
  total: number;
  page: number;
  page_size: number;
}

export interface EnrichResult {
  indicator_type: string;
  indicator_value: string;
  classification: string;
  reputation?: string | null;
  source?: string | null;
  confidence?: number | null;
  first_seen?: string | null;
  last_seen?: string | null;
  available: boolean;
}

export interface MitreTechnique {
  technique_id: string;
  technique_name: string;
  tactic: string;
  description: string;
  detection_rule_types: string[];
}

export interface RuleMapping {
  rule_id: number;
  rule_name: string;
  rule_type: string;
  technique: MitreTechnique | null;
}

export interface MitreMapping {
  techniques: MitreTechnique[];
  rule_mapping: RuleMapping[];
}

export interface DashboardStats {
  total_events: number;
  critical_alerts: number;
  high_alerts: number;
  medium_alerts: number;
  low_alerts: number;
  active_incidents: number;
  resolved_incidents: number;
  auth_failures: number;
  suspicious_ips: number;
}

export interface ReportGenerate {
  format: "pdf" | "json" | "csv";
  period_start?: string;
  period_end?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
