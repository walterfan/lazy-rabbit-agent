import api from './api'
import type { LLMSettingsResponse, LLMSettingsUpdate, MaskedKeys } from '@/types/llmSettings'

const BASE_PATH = '/llm-settings'

async function getSettings(): Promise<LLMSettingsResponse> {
  const response = await api.get<LLMSettingsResponse>(BASE_PATH)
  return response.data
}

async function updateSettings(data: LLMSettingsUpdate): Promise<LLMSettingsResponse> {
  const response = await api.put<LLMSettingsResponse>(BASE_PATH, data)
  return response.data
}

async function getMaskedKeys(): Promise<MaskedKeys> {
  const response = await api.get<MaskedKeys>(`${BASE_PATH}/masked-keys`)
  return response.data
}

export default {
  getSettings,
  updateSettings,
  getMaskedKeys,
}
