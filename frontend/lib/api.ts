// API_BASE_URL: Use proxy path during development, direct URL in production
export const API_BASE_URL = typeof window === "undefined" 
  ? "http://localhost:8000/api/v1"  // Server-side: use direct URL
  : "/api";  // Client-side: use Next.js proxy

// Types matching backend Pydantic models

export interface ClusterSummary {
  id: string;
  title: string;
  cluster_summary: string | null;
  why_it_matters: string | null;
  importance: number | null;
  confidence: "low" | "medium" | "high" | "very_high" | null;
  sentiment: "positive" | "neutral" | "negative" | "mixed" | null;
  action: "read_now" | "weekend" | "ignore" | null;
  discussion_count: number;
  created_at: string;
}

export interface TrendSummary {
  id: string;
  name: string;
  mentions_today: number | null;
  mentions_7d_avg: number | null;
  growth_rate: number | null;
  status: "exploding" | "rising" | "stable" | "declining" | null;
}

export interface DailyBriefSummary {
  id: string;
  date: string;
  summary: string | null;
  estimated_read_time_minutes: number | null;
  stories_analyzed: number | null;
  stories_filtered: number | null;
  stories_selected: number | null;
}

interface PaginatedResponse<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

interface DashboardResponse {
  brief: DailyBriefSummary | null;
  top_clusters: ClusterSummary[];
  trend_highlights: TrendSummary[];
}

interface WeeklyTotals {
  stories_analyzed: number;
  stories_filtered: number;
  stories_selected: number;
  avg_read_time_minutes: number;
}

interface WeeklyReportResponse {
  briefs: DailyBriefSummary[];
  totals: WeeklyTotals;
}

// Helper to build URL with query params
function buildUrl(path: string, params?: Record<string, string | number | undefined>): string {
  // Ensure path starts with a single slash
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(API_BASE_URL + normalizedPath, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        url.searchParams.append(key, String(value));
      }
    });
  }
  return url.toString();
}

// API functions

export async function getDashboard(): Promise<DashboardResponse> {
  const response = await fetch(buildUrl("/dashboard"));
  if (!response.ok) {
    throw new Error(`Dashboard fetch failed: ${response.status}`);
  }
  return response.json();
}

export async function getStories(
  page?: number,
  page_size?: number
): Promise<PaginatedResponse<ClusterSummary>> {
  const response = await fetch(buildUrl("/clusters", { page, page_size }));
  if (!response.ok) {
    throw new Error(`Stories fetch failed: ${response.status}`);
  }
  return response.json();
}

export async function getStory(id: string): Promise<ClusterSummary & { member_articles: unknown[] }> {
  const response = await fetch(buildUrl(`/stories/${id}`));
  if (!response.ok) {
    throw new Error(`Story fetch failed: ${response.status}`);
  }
  return response.json();
}

export async function getTrends(
  page?: number,
  page_size?: number
): Promise<PaginatedResponse<TrendSummary>> {
  const response = await fetch(buildUrl("/trends", { page, page_size }));
  if (!response.ok) {
    throw new Error(`Trends fetch failed: ${response.status}`);
  }
  return response.json();
}

export async function getDailyBrief(date?: string): Promise<DailyBriefSummary> {
  const response = await fetch(buildUrl("/daily-brief", { date }));
  if (!response.ok) {
    throw new Error(`Daily brief fetch failed: ${response.status}`);
  }
  return response.json();
}

export async function getWeeklyReport(): Promise<WeeklyReportResponse> {
  const response = await fetch(buildUrl("/weekly-report"));
  if (!response.ok) {
    throw new Error(`Weekly report fetch failed: ${response.status}`);
  }
  return response.json();
}