"use client";

import React from "react";
import Link from "next/link";
import {
  LayoutGrid,
  TrendingUp,
  FileText,
  BarChart,
  Bookmark,
  Settings,
} from "lucide-react";

const navItems = [
  { name: "Dashboard", icon: LayoutGrid, href: "/" },
  { name: "Trending", icon: TrendingUp, href: "#" },
  { name: "Papers", icon: FileText, href: "#" },
  { name: "Weekly Reports", icon: BarChart, href: "#" },
  { name: "Bookmarks", icon: Bookmark, href: "#" },
  { name: "Settings", icon: Settings, href: "#" },
];

const topics = ["Agents", "LLMs", "Infrastructure"];

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-full w-[260px] flex flex-col border-r border-slate-200 bg-white">
      {/* Logo Section */}
      <div className="p-6">
        <div className="font-bold text-xl text-slate-900">AI DevPulse</div>
        <div className="text-sm text-slate-500 mt-1">
          Personal Intelligence Terminal
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-2 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors text-slate-700 hover:bg-slate-50"
          >
            <item.icon className="w-5 h-5 text-slate-500" />
            <span>{item.name}</span>
          </Link>
        ))}
      </nav>

      {/* User Info */}
      <div className="px-4 py-3 border-t border-slate-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-medium">
            E
          </div>
          <div>
            <div className="text-sm font-medium text-slate-900">Erum</div>
            <div className="text-xs text-slate-500">AI Engineer</div>
          </div>
        </div>
      </div>

      {/* Topics */}
      <div className="px-4 py-3 border-t border-slate-200">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
          TOPICS
        </div>
        <div className="flex flex-wrap gap-2">
          {topics.map((topic) => (
            <span
              key={topic}
              className="px-2.5 py-1 rounded-md bg-slate-100 text-xs font-medium text-slate-700"
            >
              {topic}
            </span>
          ))}
        </div>
      </div>
    </aside>
  );
}