/**
 * ModelSelector 组件
 * 
 * 功能：
 * - 显示所有可用的 LLM 模型
 * - 允许用户选择不同的模型
 * - 显示模型能力（思维、视觉、推理等）
 * - 智能模型建议（基于任务类型）
 * 
 * 使用示例：
 * ```tsx
 * import { ModelSelector } from '@/components/ModelSelector'
 * 
 * function ChatPage() {
 *   const [selectedModel, setSelectedModel] = useState('llama2-local')
 *   const [thinking, setThinking] = useState(false)
 *   
 *   return (
 *     <div>
 *       <ModelSelector 
 *         value={selectedModel}
 *         onChange={setSelectedModel}
 *         thinkingEnabled={thinking}
 *         onThinkingChange={setThinking}
 *       />
 *     </div>
 *   )
 * }
 * ```
 */

'use client'

import { ChevronDown, Brain, Eye, Zap } from 'lucide-react'
import React, { useEffect, useState } from 'react'

interface ModelConfig {
  name: string
  display_name: string
  description?: string
  supports_thinking: boolean
  supports_vision: boolean
  supports_reasoning_effort: boolean
}

interface ModelSelectorProps {
  value: string
  onChange: (modelName: string) => void
  thinkingEnabled?: boolean
  onThinkingChange?: (enabled: boolean) => void
  disabled?: boolean
  showRecommendations?: boolean
}

interface TaskRecommendation {
  taskType: string
  emoji: string
  models: string[]
}

const TASK_RECOMMENDATIONS: TaskRecommendation[] = [
  {
    taskType: '推理',
    emoji: '🧠',
    models: ['deepseek-r1', 'claude-3-5-sonnet', 'claude-3-opus']
  },
  {
    taskType: '视觉',
    emoji: '👁️',
    models: ['gpt-4', 'claude-3-5-sonnet', 'gemini-2.5-pro']
  },
  {
    taskType: '代码',
    emoji: '💻',
    models: ['gpt-4', 'claude-3-5-sonnet', 'claude-3-opus']
  },
  {
    taskType: '快速',
    emoji: '⚡',
    models: ['llama2-local', 'gpt-4o-mini', 'deepseek-v3']
  },
  {
    taskType: '经济',
    emoji: '💰',
    models: ['llama2-local', 'gpt-4o-mini', 'deepseek-v3']
  }
]

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  value,
  onChange,
  thinkingEnabled = false,
  onThinkingChange,
  disabled = false,
  showRecommendations = true
}) => {
  const [models, setModels] = useState<ModelConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [selectedTask, setSelectedTask] = useState<string | null>(null)

  // 获取可用模型列表
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch('/api/models')
        if (!response.ok) throw new Error('Failed to fetch models')
        const data = await response.json()
        setModels(data.models ?? [])
        setLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        setLoading(false)
      }
    }

    void fetchModels()
  }, [])

  const currentModel = models.find((m) => m.name === value)
  const supportsThinking = currentModel?.supports_thinking ?? false

  // 获取任务推荐的模型
  const getRecommendedModels = (): ModelConfig[] => {
    if (!selectedTask) return models

    const recommendation = TASK_RECOMMENDATIONS.find(
      (r) => r.taskType === selectedTask
    )
    if (!recommendation) return models

    return models.filter((m) =>
      recommendation.models.includes(m.name)
    )
  }

  const filteredModels = getRecommendedModels()

  return (
    <div className="space-y-4">
      {/* 主选择器 */}
      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          AI 模型
        </label>

        <button
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          className="w-full px-4 py-2 text-left bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed flex items-center justify-between"
        >
          <span>
            {loading ? (
              <span className="text-gray-400">加载中...</span>
            ) : currentModel ? (
              <div>
                <div className="font-medium">{currentModel.display_name}</div>
                {currentModel.description && (
                  <div className="text-xs text-gray-500">
                    {currentModel.description}
                  </div>
                )}
              </div>
            ) : (
              <span className="text-gray-400">选择一个模型</span>
            )}
          </span>
          <ChevronDown
            className={`w-5 h-5 text-gray-400 transition-transform ${
              isOpen ? 'transform rotate-180' : ''
            }`}
          />
        </button>

        {/* 下拉菜单 */}
        {isOpen && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
            {error && (
              <div className="px-4 py-3 text-sm text-red-600 border-b border-gray-200">
                错误: {error}
              </div>
            )}

            {loading ? (
              <div className="px-4 py-3 text-sm text-gray-500">加载中...</div>
            ) : filteredModels.length === 0 ? (
              <div className="px-4 py-3 text-sm text-gray-500">
                没有可用的模型
              </div>
            ) : (
              <div className="max-h-96 overflow-y-auto">
                {filteredModels.map((model) => (
                  <button
                    key={model.name}
                    onClick={() => {
                      onChange(model.name)
                      setIsOpen(false)
                      setSelectedTask(null) // 清除任务过滤
                    }}
                    className={`w-full px-4 py-3 text-left hover:bg-blue-50 border-b border-gray-100 last:border-0 ${
                      value === model.name ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="font-medium">{model.display_name}</div>
                    {model.description && (
                      <div className="text-xs text-gray-500 mt-1">
                        {model.description}
                      </div>
                    )}
                    {/* 能力标签 */}
                    <div className="flex gap-2 mt-2 flex-wrap">
                      {model.supports_thinking && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded">
                          <Brain className="w-3 h-3" /> 思维
                        </span>
                      )}
                      {model.supports_vision && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                          <Eye className="w-3 h-3" /> 视觉
                        </span>
                      )}
                      {model.supports_reasoning_effort && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-green-100 text-green-700 rounded">
                          <Zap className="w-3 h-3" /> 推理
                        </span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 思维模式开关 */}
      {supportsThinking && onThinkingChange && (
        <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
          <input
            type="checkbox"
            id="thinking-mode"
            checked={thinkingEnabled}
            onChange={(e) => onThinkingChange(e.target.checked)}
            className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
          />
          <label
            htmlFor="thinking-mode"
            className="flex items-center gap-2 cursor-pointer text-sm font-medium text-gray-700"
          >
            <Brain className="w-4 h-4 text-purple-600" />
            启用深度思考模式
          </label>
          <span className="text-xs text-gray-500 ml-auto">
            需要更长时间但结果更准确
          </span>
        </div>
      )}

      {/* 任务推荐 */}
      {showRecommendations && (
        <div className="border-t pt-4">
          <p className="text-sm font-medium text-gray-700 mb-2">快速选择（按任务类型）</p>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {TASK_RECOMMENDATIONS.map((rec) => (
              <button
                key={rec.taskType}
                onClick={() => setSelectedTask(rec.taskType)}
                className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                  selectedTask === rec.taskType
                    ? 'bg-blue-100 border-blue-300 text-blue-700'
                    : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                }`}
              >
                <span>{rec.emoji}</span> {rec.taskType}
              </button>
            ))}
          </div>
          {selectedTask && (
            <button
              onClick={() => setSelectedTask(null)}
              className="mt-2 text-xs text-gray-500 hover:text-gray-700 underline"
            >
              清除过滤
            </button>
          )}
        </div>
      )}

      {/* 当前模型详情 */}
      {currentModel && !loading && (
        <div className="text-xs text-gray-500 p-2 bg-gray-50 rounded">
          <p>
            <strong>当前模型:</strong> {currentModel.name}
          </p>
          <p>
            <strong>支持功能:</strong>
            {[
              currentModel.supports_thinking && '思维',
              currentModel.supports_vision && '视觉',
              currentModel.supports_reasoning_effort && '推理'
            ]
              .filter(Boolean)
              .join('、') || '无特殊功能'}
          </p>
        </div>
      )}
    </div>
  )
}

export default ModelSelector
