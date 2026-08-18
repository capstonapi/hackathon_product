import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { getConversationMessages, streamChatMessage } from '../api/chat'
import type { ChatRequest } from '../types/chat'
import { queryKeys } from './queryKeys'

export function useConversation(conversationId: number | null) {
  return useQuery({
    queryKey: queryKeys.conversation(conversationId ?? -1),
    queryFn: () => getConversationMessages(conversationId as number),
    enabled: conversationId !== null,
  })
}

export function useSendChatMessage() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ payload, onStatus }: { payload: ChatRequest; onStatus: (status: string) => void }) => streamChatMessage(payload, onStatus),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.conversation(response.conversation_id) })
      queryClient.invalidateQueries({ queryKey: ['history'] })
    },
  })
}
