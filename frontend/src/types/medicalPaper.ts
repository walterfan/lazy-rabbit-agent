/**
 * Type definitions for the Medical Paper Writing Assistant.
 */

export type PaperType = 'rct' | 'cohort' | 'meta_analysis'

export type TaskStatus = 'pending' | 'running' | 'revision' | 'completed' | 'failed'

export type PipelineStep = 'literature' | 'stats' | 'writer' | 'compliance' | 'done'

export interface CreateTaskRequest {
  title: string
  paper_type: PaperType
  research_question: string
  study_design?: Record<string, any>
  raw_data?: Record<string, any>
}

export interface RevisionRequest {
  feedback: string
  sections_to_revise?: string[]
}

export interface PaperTask {
  id: string
  user_id: number
  title: string
  paper_type: PaperType
  status: TaskStatus
  research_question: string
  study_design?: Record<string, any>
  current_step?: PipelineStep
  revision_round: number
  manuscript?: Record<string, any>
  references?: Record<string, any>[]
  stats_report?: Record<string, any>
  compliance_report?: Record<string, any>
  created_at?: string
  updated_at?: string
  completed_at?: string
}

export interface TaskListResponse {
  tasks: PaperTask[]
  total: number
}

export interface TemplateInfo {
  paper_type: PaperType
  name: string
  description: string
  checklist: string
}

export interface TemplateListResponse {
  templates: TemplateInfo[]
}

export interface StreamEvent {
  type: 'token' | 'tool_call' | 'tool_result' | 'agent_start' | 'agent_end' | 'done' | 'error'
  content?: string
  tool?: string
  args?: Record<string, any>
  result?: string
  agent?: string
}
