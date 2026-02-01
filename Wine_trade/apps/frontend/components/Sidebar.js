'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'

export default function Sidebar({ onCollapseChange }) {
  const router = useRouter()
  const [collapsed, setCollapsed] = useState(false)
  const [expandedSections, setExpandedSections] = useState({})
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    if (onCollapseChange) {
      onCollapseChange(collapsed)
    }
  }, [collapsed, onCollapseChange])

  useEffect(() => {
    setMounted(true)
    // Auto-expand section if current route matches
    const currentPath = router.pathname
    const sections = {
      portfolio: ['/portfolio'],
      market: ['/market'],
      advisor: ['/advisor'],
      analytics: ['/analytics'],
      learning: ['/learning'],
      autonomy: ['/autonomy'],
      trust: ['/trust']
    }
    
    Object.entries(sections).forEach(([key, paths]) => {
      if (paths.some(path => currentPath.startsWith(path))) {
        setExpandedSections(prev => ({ ...prev, [key]: true }))
      }
    })
  }, [router.pathname])

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const navigationItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      ),
      path: '/dashboard',
      subItems: null
    },
    {
      id: 'portfolio',
      label: 'Portfolio',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      path: '/portfolio/holdings',
      subItems: [
        { label: 'Holdings', path: '/portfolio/holdings' },
        { label: 'Sold Holdings', path: '/portfolio/sold' },
        { label: 'Watchlist', path: '/portfolio/watchlist' },
        { label: 'Capital Summary', path: '/portfolio/capital' }
      ]
    },
    {
      id: 'market',
      label: 'Market',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      path: '/market/arbitrage',
      subItems: [
        { label: 'Arbitrage', path: '/market/arbitrage' },
        { label: 'Market Pulse', path: '/market/pulse' },
        { label: 'Alerts', path: '/market/alerts' }
      ]
    },
    {
      id: 'advisor',
      label: 'AI Advisor',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      path: '/advisor/recommendations',
      subItems: [
        { label: 'Recommendations', path: '/advisor/recommendations' },
        { label: 'Simulations', path: '/advisor/simulations' },
        { label: 'Decision Replay', path: '/advisor/decisions' }
      ]
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      path: '/analytics/performance',
      subItems: [
        { label: 'Performance', path: '/analytics/performance' },
        { label: 'Strategy', path: '/analytics/strategy' },
        { label: 'Outcomes', path: '/analytics/outcomes' }
      ]
    },
    {
      id: 'learning',
      label: 'Learning',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      path: '/learning/insights',
      subItems: [
        { label: 'Learning Insights', path: '/learning/insights' },
        { label: 'ML Models', path: '/learning/models' },
        { label: 'Knowledge Base', path: '/learning/knowledge' }
      ]
    },
    {
      id: 'autonomy',
      label: 'Autonomy',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      path: '/autonomy/control',
      subItems: [
        { label: 'Control', path: '/autonomy/control' },
        { label: 'Execution', path: '/autonomy/execution' },
        { label: 'History', path: '/autonomy/history' }
      ]
    },
    {
      id: 'trust',
      label: 'Trust & Explainability',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
      path: '/trust/replay',
      subItems: [
        { label: 'Decision Replay', path: '/trust/replay' },
        { label: 'Timeline', path: '/trust/timeline' }
      ]
    }
  ]

  const isActive = (path) => {
    if (path === '/dashboard') {
      return router.pathname === '/dashboard' || router.pathname === '/dashboard/index'
    }
    return router.pathname.startsWith(path)
  }

  const isSubItemActive = (path) => {
    return router.pathname === path
  }

  if (!mounted) {
    return null
  }

  // Wine bottle icon component
  const WineIcon = ({ className = "w-5 h-5" }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 2h6v2h-1v2h1v12a2 2 0 01-2 2h-2a2 2 0 01-2-2V6h1V4H9V2z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 2v2M12 18v2" />
    </svg>
  )

  return (
    <div className={`fixed left-0 top-0 h-screen bg-white border-r border-gray-200 text-gray-700 transition-all duration-300 ease-in-out z-40 shadow-lg flex flex-col ${
      collapsed ? 'w-0 overflow-hidden' : 'w-64'
    }`}>
      {/* Sidebar Header */}
      <div className={`h-16 flex-shrink-0 flex items-center justify-between px-4 border-b border-gray-200 transition-all duration-300 ${
        collapsed ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-gradient-to-br from-[#800020] to-[#7b1730] rounded-lg flex items-center justify-center shadow-md">
            <WineIcon className="w-5 h-5 text-white" />
          </div>
          <span className="font-cinzel font-bold text-xl text-[#800020] tracking-wide whitespace-nowrap">Wine Invest</span>
        </div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 rounded-lg hover:bg-[#800020]/10 text-gray-600 hover:text-[#800020] transition-all duration-200"
          title="Collapse sidebar"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      </div>

      {/* Expand Toggle Button (shown when collapsed) */}
      <button
        onClick={() => setCollapsed(false)}
        className={`fixed left-2 top-2 z-50 w-10 h-10 bg-[#800020] text-white rounded-lg shadow-lg hover:bg-[#7b1730] transition-all duration-300 flex items-center justify-center ${
          collapsed ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
        title="Expand sidebar"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>

      {/* Navigation Items - Scrollable Container */}
      <nav 
        className={`flex-1 min-h-0 overflow-y-auto overflow-x-hidden py-4 px-3 sidebar-scrollbar transition-all duration-300 ${
          collapsed ? 'opacity-0 pointer-events-none' : 'opacity-100'
        }`}
        style={{ 
          scrollBehavior: 'smooth',
          WebkitOverflowScrolling: 'touch',
          overscrollBehavior: 'contain'
        }}
        onWheel={(e) => {
          // Prevent main content scroll when scrolling sidebar
          e.stopPropagation()
        }}
      >
        {navigationItems.map((item) => {
          const hasSubItems = item.subItems && item.subItems.length > 0
          const isExpanded = expandedSections[item.id] || false
          const active = isActive(item.path)

          return (
            <div key={item.id} className="mb-1.5">
              {hasSubItems ? (
                <>
                  <button
                    onClick={() => toggleSection(item.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 font-lato ${
                      active
                        ? 'bg-[#800020] text-white shadow-md'
                        : 'text-gray-700 hover:bg-[#800020]/10 hover:text-[#800020]'
                    }`}
                    title={collapsed ? item.label : undefined}
                  >
                    <span className="flex-shrink-0">{item.icon}</span>
                    {!collapsed && (
                      <>
                        <span className="flex-1 text-left font-medium">{item.label}</span>
                        <svg
                          className={`w-4 h-4 transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </>
                    )}
                  </button>
                  {!collapsed && isExpanded && (
                    <div className="ml-4 mt-1.5 space-y-1">
                      {item.subItems.map((subItem) => {
                        const subActive = isSubItemActive(subItem.path)
                        return (
                          <Link
                            key={subItem.path}
                            href={subItem.path}
                            className={`block px-3 py-2 rounded-lg text-sm transition-all duration-200 font-lato ${
                              subActive
                                ? 'bg-[#800020] text-white font-semibold shadow-sm'
                                : 'text-gray-600 hover:bg-[#800020]/10 hover:text-[#800020]'
                            }`}
                          >
                            {subItem.label}
                          </Link>
                        )
                      })}
                    </div>
                  )}
                </>
              ) : (
                <Link
                  href={item.path}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 font-lato ${
                    active
                      ? 'bg-[#800020] text-white shadow-md'
                      : 'text-gray-700 hover:bg-[#800020]/10 hover:text-[#800020]'
                  }`}
                  title={collapsed ? item.label : undefined}
                >
                  <span className="flex-shrink-0">{item.icon}</span>
                  {!collapsed && <span className="font-medium">{item.label}</span>}
                </Link>
              )}
            </div>
          )
        })}
      </nav>

      {/* Sidebar Footer */}
      <div className={`flex-shrink-0 border-t border-gray-200 p-4 transition-all duration-300 ${
        collapsed ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}>
        <div className="text-xs text-gray-500 text-center font-lato tracking-wide">
          Wine Trading Platform
        </div>
      </div>
    </div>
  )
}
