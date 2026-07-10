"use client";

import React, { useState, useEffect } from "react";
import { Bell } from "lucide-react";
import { getDashboard, DailyBriefSummary } from "@/lib/api";

export function Header() {
  const [brief, setBrief] = useState<DailyBriefSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("Erum");
  const [date, setDate] = useState(() => {
    const now = new Date();
    return now.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });
  });

  useEffect(() => {
    // Fetch dashboard data
    const fetchDashboard = async () => {
      try {
        const data = await getDashboard();
        setBrief(data.brief);
      } catch (error) {
        console.error("Failed to fetch dashboard:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  const readTime = loading || !brief?.estimated_read_time_minutes
    ? "--"
    : brief.estimated_read_time_minutes.toString();

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between fixed top-0 left-[260px] right-0 z-10">
      <div className="flex items-center gap-4">
        <div>
          <div className="text-sm text-slate-500">
            Good Morning, {name}
          </div>
          <div className="text-xs text-slate-400">{date}</div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Notification Bell */}
        <div className="group relative">
          <button className="relative p-2 rounded-lg hover:bg-slate-100 text-slate-600">
            <Bell className="w-5 h-5" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
          <div className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 hidden group-hover:block px-2 py-1 bg-slate-800 text-white text-xs rounded">
            Coming soon
          </div>
        </div>

        {/* Email Notification Status */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-50 border border-green-100">
          <span className="relative flex w-2 h-2">
            <span className="animate-ping absolute inline-flex w-full h-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full w-2 h-2 bg-green-500"></span>
          </span>
          <span className="text-xs font-medium text-green-700">Daily Email Active</span>
        </div>

        {/* User Avatar */}
        <div className="group relative">
          <div className="w-9 h-9 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-medium text-sm">
            {name.charAt(0)}
          </div>
          <div className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 hidden group-hover:block px-2 py-1 bg-slate-800 text-white text-xs rounded">
            Coming soon
          </div>
        </div>

        {/* Read Time Badge */}
        <div className="hidden md:flex items-center gap-2 pl-4 border-l border-slate-200">
          <span className="text-xs text-slate-500">
            {readTime} min to read today
          </span>
        </div>
      </div>
    </header>
  );
}