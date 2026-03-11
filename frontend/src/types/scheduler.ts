/**
 * Type definitions for the Job Scheduler module.
 */

export interface ScheduledJob {
  id: string
  name: string
  trigger: string
  next_run_time: string | null
  pending: boolean
}

export interface JobType {
  id: string
  description: string
  agent: string
  default_trigger: 'cron' | 'interval'
  default_interval?: Record<string, number>
  default_cron?: Record<string, number>
}

export interface JobHistoryEntry {
  job_id: string
  status: 'success' | 'error' | 'missed'
  scheduled_at: string | null
  executed_at: string
  retval?: string | null
  error?: string | null
}

export interface AddJobRequest {
  job_id: string
  job_type: string
  trigger_type: 'cron' | 'interval'
  name?: string
  description?: string
  // Interval params
  seconds?: number
  minutes?: number
  hours?: number
  // Cron params
  hour?: number
  minute?: number
  day_of_week?: string
}

export interface SchedulerStatus {
  status: string
  jobs: ScheduledJob[]
}

export interface JobTypesResponse {
  job_types: JobType[]
}

export interface JobHistoryResponse {
  history: JobHistoryEntry[]
}
