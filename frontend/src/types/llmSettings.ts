export interface LLMSettingsUpdate {
  chat_base_url?: string | null
  chat_api_key?: string | null
  chat_model?: string | null
  chat_temperature?: number | null

  embedding_base_url?: string | null
  embedding_api_key?: string | null
  embedding_model?: string | null

  image_base_url?: string | null
  image_api_key?: string | null
  image_model?: string | null
}

export interface LLMSettingsDefaults {
  chat_base_url: string
  chat_model: string
  embedding_base_url: string
  embedding_model: string
  image_base_url: string
  image_model: string
}

export interface LLMSettingsResponse {
  chat_base_url: string | null
  chat_api_key_set: boolean
  chat_model: string | null
  chat_temperature: number | null

  embedding_base_url: string | null
  embedding_api_key_set: boolean
  embedding_model: string | null

  image_base_url: string | null
  image_api_key_set: boolean
  image_model: string | null

  defaults: LLMSettingsDefaults | null
}

export interface MaskedKeys {
  chat_api_key: string
  embedding_api_key: string
  image_api_key: string
}
