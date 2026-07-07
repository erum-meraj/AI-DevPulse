"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { MessageSquare, TrendingUp, TrendingDown, Minus, Lightbulb } from "lucide-react";
import { getDashboard, getStories } from "@/lib/api";
import type { DashboardResponse, ClusterSummary, TrendSummary } from "@/lib/api";

export default function HomePage() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [topStories, setTopStories] = useState<{ items: ClusterSummary[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Helper function to format relative time
  const formatRelativeTime = (dateString: string): string => {
    const createdDate = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - createdDate.getTime();
    const diffHours = Math.round(diffMs / (1000 * 60 * 60));
    
    if (diffHours <= 0) return "Just now";
    if (diffHours === 1) return "1h ago";
    return `${diffHours}h ago`;
  };

  // Get accent color based on importance (star rating proxy)
  const getAccentColor = (importance: number | null): string => {
    const stars = Math.round((importance ?? 0) / 20);
    if (stars >= 5) return "bg-red-500";
    if (stars >= 3) return "bg-orange-500";
    return "bg-gray-400";
  };

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [dashboardData, storiesData] = await Promise.all([
          getDashboard(),
          getStories(1, 8)
        ]);
        setDashboard(dashboardData);
        setTopStories(storiesData);
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

  const renderConfidenceBadge = (confidence: string | null) => {
    switch (confidence) {
      case "very_high":
      case "high":
        return <Badge className="bg-green-600 hover:bg-green-700">High Confidence</Badge>;
      case "medium":
        return <Badge className="bg-yellow-500 hover:bg-yellow-600">Medium Confidence</Badge>;
      case "low":
        return <Badge className="bg-gray-500 hover:bg-gray-600">Low Confidence</Badge>;
      default:
        return null;
    }
  };

  const renderStatusBadge = (status: string | null, name: string) => {
    const statusColors: Record<string, { variant: string; Icon: any }> = {
      exploding: { variant: "destructive", Icon: TrendingUp },
      rising: { variant: "default", Icon: TrendingUp },
      stable: { variant: "outline", Icon: Minus },
      declining: { variant: "outline", Icon: TrendingDown },
    };
    const config = statusColors[status || ""] || { variant: "outline", Icon: Minus };
    return (
                    <Badge variant={config.variant as "destructive" | "default" | "outline"} className="flex items-center gap-1">
        <config.Icon className="h-3 w-3" />
        {name}
      </Badge>
    );
  };

  // Get trend accent color and icon based on status
  const getTrendColor = (status: string | null): string => {
    switch (status) {
      case "exploding": return "bg-red-500";
      case "rising": return "bg-orange-500";
      case "declining": return "bg-blue-500";
      default: return "bg-gray-400";
    }
  };

  const getTrendIcon = (status: string | null) => {
    switch (status) {
      case "exploding": return TrendingUp;
      case "rising": return TrendingUp;
      case "stable": return Minus;
      case "declining": return TrendingDown;
      default: return Minus;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          <Skeleton className="h-12 w-64" />
          <div className="grid grid-cols-1 lg:grid-cols-[7fr_3fr] gap-6 items-start">
            <Skeleton className="h-64" />
            <Skeleton className="h-64" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 p-8">
        <div className="max-w-6xl mx-auto">
          <p className="text-red-500">Error: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Top section: Two-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-[7fr_3fr] gap-6 items-start">
          {/* LEFT COLUMN: Today's Intelligence Brief */}
          <section>
            <h2 className="text-2xl font-bold mb-4">Today's Intelligence Brief</h2>
            <Card className="bg-white border-slate-200 shadow-sm rounded-xl">
              {dashboard?.brief ? (
                <>
                  <CardHeader>
                    <CardTitle className="text-3xl font-bold">
                      You missed {dashboard.brief.stories_analyzed} stories.
                    </CardTitle>
                    <CardDescription className="text-lg">
                      We have filtered them to the {dashboard.brief.stories_selected} developments that actually matter.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex flex-wrap gap-4 text-sm">
                      <span className="text-slate-600 dark:text-slate-400">
                        {dashboard.brief.estimated_read_time_minutes} min estimated read
                      </span>
                      <span className="text-slate-500 dark:text-slate-500">
                        Stories Analyzed: {dashboard.brief.stories_analyzed}
                      </span>
                      <span className="text-slate-500 dark:text-slate-500">
                        Stories Filtered: {dashboard.brief.stories_filtered}
                      </span>
                      <span className="text-slate-500 dark:text-slate-500">
                        Stories Selected: {dashboard.brief.stories_selected}
                      </span>
                    </div>
                  </CardContent>
                </>
              ) : (
                <CardContent>
                  <p className="text-slate-500">No brief generated yet today.</p>
                </CardContent>
              )}
            </Card>
          </section>

          {/* RIGHT COLUMN: Trust Metrics */}
          <section className="space-y-6">
            <h2 className="text-2xl font-bold mb-4">Trust Metrics</h2>
            <Card className="bg-white border-slate-200 shadow-sm rounded-xl">
              <CardHeader>
                <CardTitle>Overview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-slate-600 dark:text-slate-400">Stories Analyzed</span>
                  <span className="font-semibold text-lg">{dashboard?.brief?.stories_analyzed ?? 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-600 dark:text-slate-400">Stories Filtered</span>
                  <span className="font-semibold text-lg">{dashboard?.brief?.stories_filtered ?? 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-600 dark:text-slate-400">Surfaced</span>
                  <span className="font-semibold text-lg">{dashboard?.brief?.stories_selected ?? 0}</span>
                </div>
              </CardContent>
            </Card>
          </section>
        </div>

        {/* Action Items - Full Width, 3 Column Grid */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Action Items</h2>
          <Card className="bg-white border-slate-200 shadow-sm rounded-xl">
            <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* READ NOW column */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <div className="h-4 w-2 bg-red-500 rounded-full" />
                  <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">READ NOW</span>
                </div>
                <div className="space-y-1">
                  {topStories?.items
                    .filter((item) => item.action === "read_now")
                    .map((item) => (
                      <Link key={item.id} href={`/stories/${item.id}`} className="block text-sm text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:underline">
                        {item.title}
                      </Link>
                    ))}
                  {topStories?.items.filter((item) => item.action === "read_now").length === 0 && (
                    <span className="text-sm text-slate-400 italic">No items</span>
                  )}
                </div>
              </div>

              {/* SAVE FOR WEEKEND column */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <div className="h-4 w-2 bg-orange-500 rounded-full" />
                  <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">SAVE FOR WEEKEND</span>
                </div>
                <div className="space-y-1">
                  {topStories?.items
                    .filter((item) => item.action === "weekend")
                    .map((item) => (
                      <Link key={item.id} href={`/stories/${item.id}`} className="block text-sm text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:underline">
                        {item.title}
                      </Link>
                    ))}
                  {topStories?.items.filter((item) => item.action === "weekend").length === 0 && (
                    <span className="text-sm text-slate-400 italic">No items</span>
                  )}
                </div>
              </div>

              {/* IGNORE column */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <div className="h-4 w-2 bg-gray-400 rounded-full" />
                  <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">IGNORE</span>
                </div>
                <div className="text-sm text-slate-500 dark:text-slate-400">
                  {dashboard?.brief?.stories_filtered ?? 0} filtered stories
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Top Stories - Full Width */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Top Stories</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
            {topStories?.items.length} of {dashboard?.brief?.stories_analyzed} stories
          </p>
          <div className="space-y-4">
            {topStories?.items.map((cluster: ClusterSummary) => (
              <Link key={cluster.id} href={`/stories/${cluster.id}`} className="block">
                <Card className="bg-white border-slate-200 shadow-sm rounded-xl flex flex-col hover:shadow-md transition-shadow pl-2 relative">
                  <div className={`absolute left-0 top-0 bottom-0 w-1 ${getAccentColor(cluster.importance)} rounded-l-xl`} />
                  <CardHeader>
                    <CardTitle className="text-xl font-bold hover:underline">{cluster.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {cluster.cluster_summary && (
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        {cluster.cluster_summary}
                      </p>
                    )}
                    {cluster.why_it_matters && (
                      <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
                        <span className="inline-flex items-center gap-1 text-blue-600">
                          <Lightbulb className="h-4 w-4" />
                          Why it matters:
                        </span> 
                        <span className="font-normal ml-1">{cluster.why_it_matters}</span>
                      </p>
                    )}
                    <div className="flex flex-wrap gap-2 items-center">
                      {renderActionBadge(cluster.action)}
                      {renderConfidenceBadge(cluster.confidence)}
                    </div>
                    <div className="flex items-center gap-2">
                      {renderStars(cluster.importance)}
                      <span className="text-xs text-slate-500 dark:text-slate-400">
                        {cluster.importance ? Math.round(cluster.importance) : 0} importance
                      </span>
                    </div>
                    <div className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400 pt-2 border-t">
                      <MessageSquare className="h-3 w-3" />
                      <span>{cluster.discussion_count} discussion{cluster.discussion_count !== 1 ? "s" : ""}</span>
                      <span className="text-slate-400 mx-1">•</span>
                      <span>{formatRelativeTime(cluster.created_at)}</span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </section>

        {/* Emerging Trends - Full Width */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Emerging Trends</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {dashboard?.trend_highlights.map((trend: TrendSummary) => (
                <Card key={trend.id} className="bg-white border-slate-200 shadow-sm rounded-xl flex flex-col relative">
                <div className={`h-full w-1.5 absolute left-0 rounded-l-xl ${getTrendColor(trend.status)}`} />
                <CardHeader>
                  <CardTitle className="text-base font-bold pl-4">{trend.name}</CardTitle>
                </CardHeader>
                <CardContent className="flex items-center justify-between pl-4">
                  <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                    {trend.growth_rate !== null ? `${trend.growth_rate > 0 ? "+" : ""}${(trend.growth_rate * 100).toFixed(0)}%` : "N/A"}
                  </span>
                  {(() => {
                    const Icon = getTrendIcon(trend.status);
                    return (
                      <Badge variant="outline" className="flex items-center gap-1">
                        <Icon className="h-3 w-3" />
                        {trend.status || "Unknown"}
                      </Badge>
                    );
                  })()}
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}