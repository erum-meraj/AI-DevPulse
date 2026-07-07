"use client";

import React from "react";
import {
  LayoutGrid,
  TrendingUp,
  FileText,
  BarChart,
  Bookmark,
  Settings,
} from "lucide-react";

const navItems = [
  { name: "Dashboard", icon: LayoutGrid },
  { name: "Trending", icon: TrendingUp },
  { name: "Papers", icon: FileText },
  { name: "Weekly Reports", icon: BarChart },
  { name: "Bookmarks", icon: Bookmark },
  { name: "Settings", icon: Settings },
];

const topics = ["Agents", "LLMs", "Infrastructure"];

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-full w-[260px] flex flex-col border-r border-gray-200 bg-white">
      {/* Logo Section */}
      <div className="p-6">
        <div className="font-bold text-xl text-gray-900">AI DevPulse</div>
        <div className="text-sm text-gray-500 mt-1">
          Personal Intelligence Terminal
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-2 space-y-1">
        {navItems.map((item) => (
          <a
            key={item.name}
            href="#"
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors"
          >
            <item.icon className="w-4 h-4 text-gray-500" />
            <span className="text-gray-700">{item.name}</span>
          </a>
        ))}
      </nav>

      {/* User Info */}
      <div className="px-4 py-3 border-t border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-medium">
            E
          </div>
          <div>
            <div className="text-sm font-medium text-gray-900">Erum</div>
            <div className="text-xs text-gray-500">AI Engineer</div>
          </div>
        </div>
      </div>

      {/* Topics */}
      <div className="px-4 py-3 border-t border-gray-200">
        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
          TOPICS
        </div>
        <div className="flex flex-wrap gap-2">
          {topics.map((topic) => (
            <span
              key={topic}
              className="px-2.5 py-1 rounded-md bg-gray-100 text-xs font-medium text-gray-700"
            >
              {topic}
            </span>
          ))}
        </div>
      </div>
    </aside>
  );
}