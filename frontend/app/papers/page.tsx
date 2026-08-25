"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { MessageSquare, ExternalLink, Star } from "lucide-react";
import { getTopPapers } from "@/lib/api";
import type { Paper } from "@/lib/api";

export default function PapersPage() {
  const [papers, setPapers] = useState<Paper[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPapers = async () => {
      try {
        const data = await getTopPapers(5);
        setPapers(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load papers");
      } finally {
        setLoading(false);
      }
    };
    fetchPapers();
  }, []);

  const formatRelativeTime = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.round(diffMs / (1000 * 60 * 60));
    
    if (diffHours <= 0) return "Just now";
    if (diffHours === 1) return "1h ago";
    return `${diffHours}h ago`;
  };

  const truncateText = (text: string | null, maxLength: number = 160): string => {
    if (!text) return "";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  const renderRelevanceBadge = (score: number | null) => {
    if (score === null) return null;
    return (
      <Badge variant="outline" className="font-mono text-xs">
        Score: {Math.round(score * 100)}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          <Skeleton className="h-12 w-64" />
          <Skeleton className="h-6" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-64" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-8">
        <div className="max-w-6xl mx-auto">
          <Link href="/" className="inline-flex items-center text-blue-600 hover:underline">
            ← Back to Dashboard
          </Link>
          <p className="text-red-500 mt-4">Error: {error}</p>
        </div>
      </div>
    );
  }

  if (!papers || papers.length === 0) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-8">
        <div className="max-w-6xl mx-auto">
          <Link href="/" className="inline-flex items-center text-blue-600 hover:underline">
            ← Back to Dashboard
          </Link>
          <div className="mt-8 p-8 text-center bg-zinc-100 dark:bg-zinc-900 rounded-lg">
            <p className="text-zinc-500 dark:text-zinc-400 italic">
              No papers cleared the relevance/upvote bar today — check back tomorrow
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <Link href="/" className="inline-flex items-center text-blue-600 hover:underline">
          ← Back to Dashboard
        </Link>

        <div>
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-100">Top Papers</h1>
          <p className="text-zinc-600 dark:text-zinc-400 mt-2">
            The 5 highest-relevance HuggingFace papers today with at least 10 upvotes
          </p>
        </div>

        <div className="space-y-4">
          {papers.map((paper) => (
            <Card key={paper.id} className="bg-white border-zinc-200 dark:bg-zinc-900 dark:border-zinc-800 shadow-sm rounded-xl">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-zinc-900 dark:text-zinc-100 hover:underline">
                  {paper.title}
                </CardTitle>
                <CardDescription className="text-sm text-zinc-500 dark:text-zinc-400">
                  {paper.arxiv_id} • {formatRelativeTime(paper.published_at)}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {paper.summary && (
                  <p className="text-sm text-zinc-700 dark:text-zinc-300">
                    {truncateText(paper.summary)}
                  </p>
                )}

                <div className="flex flex-wrap gap-2 items-center">
                  {renderRelevanceBadge(paper.relevance_score)}
                  {paper.ai_keywords && paper.ai_keywords.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {paper.ai_keywords.slice(0, 3).map((keyword, idx) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                      {paper.ai_keywords.length > 3 && (
                        <span className="text-xs text-zinc-500">+{paper.ai_keywords.length - 3} more</span>
                      )}
                    </div>
                  )}
                </div>

                {(paper.upvotes !== null || paper.github_stars !== null) && (
                  <div className="flex items-center gap-4 pt-2 border-t">
                    {paper.upvotes !== null && (
                      <div className="flex items-center gap-1 text-sm text-zinc-600 dark:text-zinc-400">
                        <MessageSquare className="h-4 w-4" />
                        <span>{paper.upvotes} upvotes</span>
                      </div>
                    )}
                    {paper.github_stars !== null && (
                      <div className="flex items-center gap-1 text-sm text-zinc-600 dark:text-zinc-400">
                        <Star className="h-4 w-4" />
                        <span>{paper.github_stars} stars</span>
                      </div>
                    )}
                  </div>
                )}

                {paper.url && (
                  <a
                    href={paper.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-blue-600 hover:underline text-sm"
                  >
                    Read on HuggingFace
                    <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}