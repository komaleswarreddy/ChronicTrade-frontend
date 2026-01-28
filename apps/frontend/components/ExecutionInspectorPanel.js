'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { X, Clock, CheckCircle2, XCircle, AlertCircle } from 'lucide-react'

export default function ExecutionInspectorPanel({ selectedNode, onClose }) {
  if (!selectedNode) {
    return (
      <div className="w-80 bg-white border-l border-gray-200 p-4 flex items-center justify-center text-gray-500">
        <div className="text-center">
          <p className="text-sm">Select a node to view details</p>
        </div>
      </div>
    )
  }

  const nodeData = selectedNode.data || {}
  const nodeType = selectedNode.type || 'unknown'

  const renderNodeDetails = () => {
    switch (nodeType) {
      case 'execution_step':
        return (
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-sm text-gray-700 mb-2">Step Information</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Step Name:</span>
                  <span className="font-medium">{nodeData.stepName || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Step Order:</span>
                  <span className="font-medium">{nodeData.stepOrder || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className={`font-medium ${
                    nodeData.status === 'SUCCESS' ? 'text-green-600' :
                    nodeData.status === 'FAILED' ? 'text-red-600' :
                    nodeData.status === 'IN_PROGRESS' ? 'text-blue-600' :
                    'text-gray-600'
                  }`}>
                    {nodeData.status || 'PENDING'}
                  </span>
                </div>
                {nodeData.startedAt && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Started:</span>
                    <span className="font-medium text-xs">
                      {new Date(nodeData.startedAt).toLocaleString()}
                    </span>
                  </div>
                )}
                {nodeData.completedAt && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Completed:</span>
                    <span className="font-medium text-xs">
                      {new Date(nodeData.completedAt).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
            
            {nodeData.failureReason && (
              <div className="bg-red-50 border border-red-200 rounded p-3">
                <div className="flex items-start gap-2">
                  <XCircle className="w-4 h-4 text-red-600 mt-0.5" />
                  <div>
                    <div className="font-semibold text-sm text-red-800 mb-1">Failure Reason</div>
                    <div className="text-xs text-red-700">{nodeData.failureReason}</div>
                  </div>
                </div>
              </div>
            )}
            
            {nodeData.stepData && (
              <div>
                <h4 className="font-semibold text-sm text-gray-700 mb-2">Step Data</h4>
                <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto max-h-40">
                  {JSON.stringify(nodeData.stepData, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )
      
      case 'compliance_gate':
        return (
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-sm text-gray-700 mb-2">Compliance Evaluation</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Overall Result:</span>
                  <span className={`font-medium ${
                    nodeData.overallResult === 'PASS' ? 'text-green-600' :
                    nodeData.overallResult === 'FAIL' ? 'text-red-600' :
                    'text-yellow-600'
                  }`}>
                    {nodeData.overallResult || 'CONDITIONAL'}
                  </span>
                </div>
                {nodeData.evaluatedAt && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Evaluated:</span>
                    <span className="font-medium text-xs">
                      {new Date(nodeData.evaluatedAt).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
            
            {nodeData.failedRules && nodeData.failedRules.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded p-3">
                <div className="font-semibold text-sm text-red-800 mb-2">Failed Rules</div>
                <ul className="space-y-1 text-xs text-red-700">
                  {nodeData.failedRules.map((rule, idx) => (
                    <li key={idx}>• {rule}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {nodeData.explanation && (
              <div>
                <h4 className="font-semibold text-sm text-gray-700 mb-2">Explanation</h4>
                <p className="text-xs text-gray-600">{nodeData.explanation}</p>
              </div>
            )}
          </div>
        )
      
      case 'execution_gate':
        return (
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-sm text-gray-700 mb-2">Execution Gate</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Gate Type:</span>
                  <span className="font-medium">{nodeData.gateType || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className={`font-medium ${
                    nodeData.status === 'PASSED' ? 'text-green-600' :
                    nodeData.status === 'BLOCKED' ? 'text-red-600' :
                    'text-gray-600'
                  }`}>
                    {nodeData.status || 'PENDING'}
                  </span>
                </div>
              </div>
            </div>
            
            {nodeData.blockReason && (
              <div className="bg-red-50 border border-red-200 rounded p-3">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-red-600 mt-0.5" />
                  <div>
                    <div className="font-semibold text-sm text-red-800 mb-1">Block Reason</div>
                    <div className="text-xs text-red-700">{nodeData.blockReason}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )
      
      case 'logistics_event':
        return (
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-sm text-gray-700 mb-2">Logistics Event</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Event Type:</span>
                  <span className="font-medium">{nodeData.eventType || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className="font-medium">{nodeData.status || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Risk Level:</span>
                  <span className={`font-medium ${
                    nodeData.riskLevel === 'HIGH' ? 'text-red-600' :
                    nodeData.riskLevel === 'MEDIUM' ? 'text-yellow-600' :
                    'text-green-600'
                  }`}>
                    {nodeData.riskLevel || 'LOW'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )
      
      case 'counterfactual_node':
        return (
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-sm text-gray-700 mb-2">Counterfactual Analysis</h4>
              <div className="space-y-2 text-sm">
                {nodeData.roiDelta !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">ROI Delta:</span>
                    <span className={`font-medium ${
                      nodeData.roiDelta > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {nodeData.roiDelta > 0 ? '+' : ''}{nodeData.roiDelta?.toFixed(2)}%
                    </span>
                  </div>
                )}
                {nodeData.riskDelta !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Risk Delta:</span>
                    <span className="font-medium">{nodeData.riskDelta?.toFixed(2)}</span>
                  </div>
                )}
                {nodeData.opportunityCost !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Opportunity Cost:</span>
                    <span className="font-medium">${nodeData.opportunityCost?.toFixed(2)}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )
      
      default:
        return (
          <div className="text-sm text-gray-600">
            <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto max-h-96">
              {JSON.stringify(nodeData, null, 2)}
            </pre>
          </div>
        )
    }
  }

  return (
    <motion.div
      initial={{ x: 320 }}
      animate={{ x: 0 }}
      exit={{ x: 320 }}
      className="w-80 bg-white border-l border-gray-200 h-full overflow-y-auto"
    >
      <div className="sticky top-0 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <h3 className="font-semibold text-sm text-gray-900">Node Details</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      
      <div className="p-4">
        <div className="mb-4">
          <div className="text-xs text-gray-500 mb-1">Node Type</div>
          <div className="font-medium text-sm text-gray-900 capitalize">
            {nodeType.replace('_', ' ')}
          </div>
        </div>
        
        {renderNodeDetails()}
      </div>
    </motion.div>
  )
}
