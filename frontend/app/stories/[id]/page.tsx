"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { MessageSquare, ExternalLink } from "lucide-react";
import { getStory } from "@/lib/api";
import type { ClusterSummary } from "@/lib/api";

export default function StoryDetailPage() {
  const params = useParams();
  const id = params.id as string;

  interface Article {
    title?: string;
    source?: string;
    published_at?: string;
    url?: string;
  }

  const [story, setStory] = useState<ClusterSummary & { member_articles: Article[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStory = async () => {
      try {
        const data = await getStory(id);
        setStory(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load story");
      } finally {
        setLoading(false);
      }
    };
    fetchStory();
  }, [id]);

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

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-8">
        <div className="max-w-4xl mx-auto space-y-8">
          <Skeleton className="h-12 w-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-8">
        <div className="max-w-4xl mx-auto">
          <p className="text-red-500">Error: {error}</p>
          <Link href="/" className="text-blue-600 hover:underline mt-4 block">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  if (!story) {
    return null;
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <Link href="/" className="inline-flex items-center text-blue-600 hover:underline">
          ← Back to Dashboard
        </Link>

        <Card>
          <CardHeader>
            <CardTitle className="text-3xl font-bold">{story.title}</CardTitle>
            {story.cluster_summary && (
              <CardDescription className="text-lg">{story.cluster_summary}</CardDescription>
            )}
          </CardHeader>
          <CardContent className="space-y-6">
            {story.why_it_matters && (
              <div className="p-4 bg-zinc-100 dark:bg-zinc-800 rounded-lg">
                <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 mb-2">Why it matters</h3>
                <p className="text-zinc-700 dark:text-zinc-300">{story.why_it_matters}</p>
              </div>
            )}

            <div className="flex flex-wrap gap-2 items-center">
              {renderActionBadge(story.action)}
              {renderConfidenceBadge(story.confidence)}
            </div>

            <div className="flex items-center gap-2">
              {renderStars(story.importance)}
              <span className="text-sm text-zinc-600 dark:text-zinc-400">
                {story.importance ? Math.round(story.importance) : 0} importance
              </span>
            </div>

            <div className="flex items-center gap-1 text-sm text-zinc-500 dark:text-zinc-400 pt-4 border-t">
              <MessageSquare className="h-4 w-4" />
              <span>{story.discussion_count} discussion{story.discussion_count !== 1 ? "s" : ""}</span>
            </div>

            <div className="pt-4 border-t">
              <h3 className="text-lg font-semibold mb-3">Member Articles</h3>
              {story.member_articles && story.member_articles.length > 0 ? (
                <ul className="space-y-3">
                  {story.member_articles.map((article: Article, idx: number) => (
                    <li key={idx} className="p-3 bg-zinc-50 dark:bg-zinc-900 rounded-lg">
                      <p className="font-medium text-zinc-900 dark:text-zinc-100">{article.title || "No title"}</p>
                      <div className="flex flex-wrap gap-2 text-sm text-zinc-600 dark:text-zinc-400 mt-1">
                        {article.source && <span className="bg-zinc-200 dark:bg-zinc-800 px-2 py-0.5 rounded">Source: {article.source}</span>}
                        {article.published_at && <span>Published: {formatDate(article.published_at)}</span>}
                      </div>
                      {article.url && (
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-blue-600 hover:underline text-sm mt-2"
                        >
                          Read original article
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      )}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-zinc-500 dark:text-zinc-400 italic">No articles linked yet.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}