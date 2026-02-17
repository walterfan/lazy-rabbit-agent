/**
 * Secretary chat Pinia store
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import secretaryService from '@/services/secretary.service';
import type {
  ChatSession,
  ChatSessionDetail,
  ChatRequest,
  ToolInfo,
  StreamEvent,
} from '@/types/secretary';

export const useSecretaryStore = defineStore('secretary', () => {
  // ============================================================================
  // State
  // ============================================================================
  
  const sessions = ref<ChatSession[]>([]);
  const currentSession = ref<ChatSessionDetail | null>(null);
  const tools = ref<ToolInfo[]>([]);
  
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  // Streaming state
  const isStreaming = ref(false);
  const streamingText = ref('');
  const streamingToolCalls = ref<Array<{
    tool: string;
    args: Record<string, any>;
    result?: string;
  }>>([]);

  // ============================================================================
  // Computed
  // ============================================================================
  
  const hasSessions = computed(() => sessions.value.length > 0);
  
  const currentMessages = computed(() => 
    currentSession.value?.messages || []
  );
  
  const learningTools = computed(() => 
    tools.value.filter(t => t.category === 'learning')
  );
  
  const utilityTools = computed(() => 
    tools.value.filter(t => t.category === 'utility')
  );

  // ============================================================================
  // Actions
  // ============================================================================
  
  /**
   * Send a chat message (non-streaming)
   */
  async function sendMessage(message: string, sessionId?: string | null) {
    loading.value = true;
    error.value = null;
    
    try {
      const request: ChatRequest = {
        message,
        session_id: sessionId,
      };
      
      const response = await secretaryService.chat(request);
      
      // If we have a current session, add the messages to it
      if (currentSession.value && currentSession.value.id === response.session_id) {
        // Add user message
        currentSession.value.messages.push({
          id: `user-${Date.now()}`,
          role: 'user',
          content: message,
          created_at: new Date().toISOString(),
        });
        
        // Add assistant message
        currentSession.value.messages.push({
          id: response.message_id,
          role: 'assistant',
          content: response.content,
          tool_calls: response.tool_calls,
          created_at: response.created_at,
        });
      } else {
        // Fetch the session to get full details
        await getSession(response.session_id);
      }
      
      return response;
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Failed to send message';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Send a chat message with streaming
   */
  async function sendMessageStream(
    message: string,
    sessionId?: string | null,
    onToken?: (token: string) => void,
    onToolCall?: (tool: string, args: Record<string, any>) => void,
    onToolResult?: (tool: string, result: string) => void,
    onComplete?: (sessionId: string, messageId: string) => void
  ): Promise<void> {
    isStreaming.value = true;
    streamingText.value = '';
    streamingToolCalls.value = [];
    error.value = null;
    
    // Add user message to current session immediately
    if (currentSession.value) {
      currentSession.value.messages.push({
        id: `user-${Date.now()}`,
        role: 'user',
        content: message,
        created_at: new Date().toISOString(),
      });
    }
    
    const token = localStorage.getItem('access_token') || '';
    const request: ChatRequest = {
      message,
      session_id: sessionId,
    };
    
    try {
      for await (const event of secretaryService.chatStream(request, token)) {
        const data = event as StreamEvent;
        
        switch (data.type) {
          case 'token':
            streamingText.value += data.content;
            onToken?.(data.content);
            break;
            
          case 'tool_call':
            streamingToolCalls.value.push({
              tool: data.tool,
              args: data.args,
            });
            onToolCall?.(data.tool, data.args);
            break;
            
          case 'tool_result':
            // Update the tool call with result
            const toolCall = streamingToolCalls.value.find(
              tc => tc.tool === data.tool
            );
            if (toolCall) {
              toolCall.result = data.result;
            }
            onToolResult?.(data.tool, data.result);
            break;
            
          case 'done':
            // Add assistant message to current session
            if (currentSession.value) {
              currentSession.value.messages.push({
                id: data.message_id,
                role: 'assistant',
                content: streamingText.value,
                tool_calls: streamingToolCalls.value.length > 0 
                  ? streamingToolCalls.value 
                  : undefined,
                created_at: new Date().toISOString(),
              });
              
              // Update session ID if new
              if (!sessionId && data.session_id) {
                currentSession.value.id = data.session_id;
              }
            }
            
            onComplete?.(data.session_id, data.message_id);
            break;
            
          case 'error':
            error.value = data.content;
            break;
        }
      }
    } catch (err: any) {
      error.value = err.message || 'Streaming failed';
      throw err;
    } finally {
      isStreaming.value = false;
    }
  }
  
  /**
   * List chat sessions
   */
  async function listSessions(page: number = 1, pageSize: number = 20) {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await secretaryService.listSessions(page, pageSize);
      sessions.value = response.sessions;
      return response;
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Failed to list sessions';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Get a session with messages
   */
  async function getSession(sessionId: string) {
    loading.value = true;
    error.value = null;
    
    try {
      currentSession.value = await secretaryService.getSession(sessionId);
      return currentSession.value;
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Failed to get session';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Delete a session
   */
  async function deleteSession(sessionId: string) {
    loading.value = true;
    error.value = null;
    
    try {
      await secretaryService.deleteSession(sessionId);
      
      // Remove from list
      sessions.value = sessions.value.filter(s => s.id !== sessionId);
      
      // Clear current if it was the deleted one
      if (currentSession.value?.id === sessionId) {
        currentSession.value = null;
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Failed to delete session';
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  /**
   * Start a new session
   */
  function startNewSession() {
    currentSession.value = {
      id: '',
      title: null,
      messages: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    streamingText.value = '';
    streamingToolCalls.value = [];
  }
  
  /**
   * Load available tools
   */
  async function loadTools() {
    try {
      const response = await secretaryService.listTools();
      tools.value = response.tools;
    } catch (err: any) {
      console.error('Failed to load tools:', err);
    }
  }
  
  /**
   * Clear error
   */
  function clearError() {
    error.value = null;
  }
  
  /**
   * Stop streaming
   */
  function stopStreaming() {
    isStreaming.value = false;
  }

  return {
    // State
    sessions,
    currentSession,
    tools,
    loading,
    error,
    isStreaming,
    streamingText,
    streamingToolCalls,
    
    // Computed
    hasSessions,
    currentMessages,
    learningTools,
    utilityTools,
    
    // Actions
    sendMessage,
    sendMessageStream,
    listSessions,
    getSession,
    deleteSession,
    startNewSession,
    loadTools,
    clearError,
    stopStreaming,
  };
});
