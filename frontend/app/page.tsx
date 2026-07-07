"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { getDashboard } from "@/lib/api";
import type { DashboardResponse, ClusterSummary, TrendSummary } from "@/lib/api";

export default function HomePage() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const data = await getDashboard();
        setDashboard(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  const renderStars = (importance: number | null) => {
    const stars = Math.round((importance ?? 0) / 20);
    return (
      <div className="flex items-center gap-1">
        {Array.from({ length: 5 }).map((_, i) => (
          <span key={i} className={i < (stars || 0) ? "text-yellow-500" : "text-zinc-300 dark:text-zinc-700"}>
            ★
          </span>
        ))}
      </div>
    );
  };

  const renderActionBadge = (action: string | null) => {
    switch (action) {
      case "read_now":
        return <Badge variant="destructive">Read Now</Badge>;
      case "weekend":
        return <Badge variant="secondary">Weekend</Badge>;
      case "ignore":
        return <Badge variant="outline">Ignore</Badge>;
      default:
        return null;
    }
  };

  const renderStatusBadge = (status: string | null) => {
    switch (status) {
      case "exploding":
        return <Badge variant="destructive">Exploding</Badge>;
      case "rising":
        return <Badge variant="default">Rising</Badge>;
      case "stable":
        return <Badge variant="outline">Stable</Badge>;
      case "declining":
        return <Badge variant="outline" className="text-blue-600">Declining</Badge>;
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          <Skeleton className="h-12 w-64" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-8">
        <div className="max-w-6xl mx-auto">
          <p className="text-red-500">Error: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Today's Intelligence Brief */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Today' Intelligence Brief</h2>
          <Card>
            {dashboard?.brief ? (
              <>
                <CardHeader>
                  <CardTitle>Summary</CardTitle>
                  <CardDescription>{dashboard.brief.date}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {dashboard.brief.summary && (
                    <p className="text-zinc-700 dark:text-zinc-300">{dashboard.brief.summary}</p>
                  )}
                  <div className="flex flex-wrap gap-2 text-sm text-zinc-500 dark:text-zinc-400">
                    {dashboard.brief.stories_analyzed !== null && (
                      <span>Stories Analyzed: {dashboard.brief.stories_analyzed}</span>
                    )}
                    {dashboard.brief.stories_filtered !== null && (
                      <span>Stories Filtered: {dashboard.brief.stories_filtered}</span>
                    )}
                    {dashboard.brief.stories_selected !== null && (
                      <span>Stories Selected: {dashboard.brief.stories_selected}</span>
                    )}
                    {dashboard.brief.estimated_read_time_minutes !== null && (
                      <span>Read Time: {dashboard.brief.estimated_read_time_minutes} min</span>
                    )}
                  </div>
                </CardContent>
              </>
            ) : (
              <CardContent>
                <p className="text-zinc-500">No brief generated yet today.</p>
              </CardContent>
            )}
          </Card>
        </section>

        {/* Top Stories */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Top Stories</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {dashboard?.top_clusters.map((cluster) => (
              <Card key={cluster.id} className="flex flex-col">
                <CardHeader>
                  <CardTitle>{cluster.title}</CardTitle>
                </CardHeader>
                <CardContent className="flex-1 space-y-4">
                  {cluster.cluster_summary && (
                    <p className="text-sm text-zinc-600 dark:text-zinc-400 line-clamp-3">
                      {cluster.cluster_summary}
                    </p>
                  )}
                  <div className="flex flex-wrap gap-2">
                    {cluster.confidence && <Badge>{cluster.confidence}</Badge>}
                    {renderActionBadge(cluster.action)}
                  </div>
                  {renderStars(cluster.importance)}
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Emerging Trends */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Emerging Trends</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {dashboard?.trend_highlights.map((trend) => (
              <Card key={trend.id} size="sm" className="flex flex-col">
                <CardHeader>
                  <CardTitle>{trend.name}</CardTitle>
                </CardHeader>
                <CardContent className="flex items-center justify-between">
                  <span className="text-sm text-zinc-500 dark:text-zinc-400">
                    Growth: {trend.growth_rate !== null ? `${trend.growth_rate > 0 ? "+" : ""}${Math.round(trend.growth_rate)}%` : "N/A"}
                  </span>
                  {renderStatusBadge(trend.status)}
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}