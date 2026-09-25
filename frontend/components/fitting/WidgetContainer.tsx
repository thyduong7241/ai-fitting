'use client';

import React from 'react';

interface WidgetContainerProps {
  children: React.ReactNode;
  className?: string;
  showStatusBar?: boolean;
}

export function WidgetContainer({
  children,
  className = '',
  showStatusBar = true,
}: WidgetContainerProps) {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-[#E5EDF0] p-0 sm:p-4 md:p-6 lg:p-8">
      {/* 390px x 844px Mobile Viewport Container */}
      <main
        className={`relative flex h-screen w-full max-w-[430px] flex-col overflow-hidden bg-brand-canvas sm:h-[844px] sm:w-[390px] sm:rounded-[32px] sm:border sm:border-brand-border sm:shadow-widget ${className}`}
        role="region"
        aria-label="AI Precision Fit Widget"
      >
        {/* iOS Simulated Status Bar */}
        {showStatusBar && (
          <header className="flex h-11 w-full flex-shrink-0 items-center justify-between px-6 text-brand-navy select-none">
            <span className="text-xs font-semibold tracking-tight">9:41</span>
            <div className="flex items-center gap-1.5" aria-hidden="true">
              {/* Cellular signal */}
              <svg className="h-3 w-3 fill-current" viewBox="0 0 16 16">
                <path d="M1 12h2v3H1v-3zm4-3h2v6H5V9zm4-4h2v10H9V5zm4-3h2v13h-2V2z" />
              </svg>
              {/* Wifi */}
              <svg className="h-3.5 w-3.5 fill-current" viewBox="0 0 16 16">
                <path d="M8 12a1.5 1.5 0 100-3 1.5 1.5 0 000 3zm-3.5-3.5a5 5 0 017 0 .75.75 0 001.06-1.06 6.5 6.5 0 00-9.12 0 .75.75 0 001.06 1.06zm-2.5-2.5a8.5 8.5 0 0112 0 .75.75 0 001.06-1.06 10 10 0 00-14.12 0 .75.75 0 001.06 1.06z" />
              </svg>
              {/* Battery */}
              <div className="flex items-center">
                <div className="h-2.5 w-5 rounded-[3px] border border-current p-0.5">
                  <div className="h-full w-full rounded-[1px] bg-current" />
                </div>
                <div className="h-1 w-0.5 rounded-r bg-current" />
              </div>
            </div>
          </header>
        )}

        {/* Scrollable Widget Content */}
        <div className="flex flex-1 flex-col overflow-y-auto overflow-x-hidden no-scrollbar">
          {children}
        </div>

        {/* iOS Simulated Home Indicator */}
        <div className="hidden sm:flex h-5 w-full flex-shrink-0 items-center justify-center pb-1">
          <div className="h-1 w-32 rounded-full bg-slate-300" aria-hidden="true" />
        </div>
      </main>
    </div>
  );
}
