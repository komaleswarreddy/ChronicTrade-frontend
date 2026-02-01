'use client'

export default function CitationDisplay({ citations = [] }) {
  if (!citations || citations.length === 0) {
    return null
  }

  const getSourceTypeColor = (sourceType) => {
    switch (sourceType) {
      case 'compliance_rule':
        return {
          bg: 'bg-gradient-to-br from-blue-50 to-blue-100',
          border: 'border-blue-200',
          text: 'text-blue-700',
          badge: 'bg-blue-500 text-white',
          icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z'
        }
      case 'risk_policy':
        return {
          bg: 'bg-gradient-to-br from-red-50 to-red-100',
          border: 'border-red-200',
          text: 'text-red-700',
          badge: 'bg-red-500 text-white',
          icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'
        }
      case 'strategy_doc':
        return {
          bg: 'bg-gradient-to-br from-green-50 to-green-100',
          border: 'border-green-200',
          text: 'text-green-700',
          badge: 'bg-green-500 text-white',
          icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'
        }
      case 'execution_constraint':
        return {
          bg: 'bg-gradient-to-br from-yellow-50 to-yellow-100',
          border: 'border-yellow-200',
          text: 'text-yellow-700',
          badge: 'bg-yellow-500 text-white',
          icon: 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
        }
      default:
        return {
          bg: 'bg-gradient-to-br from-gray-50 to-gray-100',
          border: 'border-gray-200',
          text: 'text-gray-700',
          badge: 'bg-gray-500 text-white',
          icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
        }
    }
  }

  const getSourceTypeLabel = (sourceType) => {
    switch (sourceType) {
      case 'compliance_rule':
        return 'Compliance Rule'
      case 'risk_policy':
        return 'Risk Policy'
      case 'strategy_doc':
        return 'Strategy Document'
      case 'execution_constraint':
        return 'Execution Constraint'
      default:
        return sourceType
    }
  }

  // Clean markdown and format content
  const formatContent = (content) => {
    if (!content) return []
    
    // Remove markdown headers (##, ###, etc.) and convert to readable format
    let cleaned = content
      .replace(/^#{1,6}\s+(.+)$/gm, '<strong class="text-gray-900 font-semibold">$1</strong>') // Convert headers to bold
      .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>') // Bold
      .replace(/\*(.+?)\*/g, '<em class="italic">$1</em>') // Italic
      .replace(/`(.+?)`/g, '<code class="bg-gray-200 px-1.5 py-0.5 rounded text-xs font-mono text-gray-800">$1</code>') // Inline code
      .replace(/^- (.+)$/gm, '<span class="flex items-start"><span class="mr-2 text-gray-400">•</span><span>$1</span></span>') // Bullet points
      .replace(/\n\n+/g, '\n\n') // Multiple newlines to double
      .trim()
    
    // Split into paragraphs and format
    const paragraphs = cleaned
      .split('\n\n')
      .filter(p => p.trim())
      .map(p => {
        // If it's a list item, wrap it properly
        if (p.includes('<span class="flex items-start">')) {
          return `<div class="ml-2">${p}</div>`
        }
        return p
      })
    
    return paragraphs
  }

  return (
    <div className="mt-4">
      <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        Knowledge Sources
      </h4>
      <div className="space-y-4">
        {citations.map((citation, index) => {
          const colors = getSourceTypeColor(citation.source_type)
          const paragraphs = formatContent(citation.content)
          
          return (
            <div
              key={index}
              className={`${colors.bg} ${colors.border} border-2 rounded-xl p-5 shadow-sm hover:shadow-md transition-all duration-200 transform hover:scale-[1.01]`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3 flex-1">
                  <div className={`${colors.badge} p-2 rounded-lg`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={colors.icon} />
                    </svg>
                  </div>
                  <div>
                    <h5 className="font-bold text-gray-900">{getSourceTypeLabel(citation.source_type)}</h5>
                    <p className="text-xs text-gray-600 mt-0.5">{citation.title}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 bg-white/60 backdrop-blur-sm px-3 py-1.5 rounded-full border border-white/80">
                  <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <span className="text-sm font-bold text-gray-800">
                    {Math.round(citation.confidence * 100)}%
                  </span>
                  <span className="text-xs text-gray-500">match</span>
                </div>
              </div>
              
              <div className="prose prose-sm max-w-none">
                {paragraphs.map((para, pIndex) => (
                  <div 
                    key={pIndex} 
                    className="text-sm text-gray-700 leading-relaxed mb-3 last:mb-0"
                    dangerouslySetInnerHTML={{ __html: para }}
                  />
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
