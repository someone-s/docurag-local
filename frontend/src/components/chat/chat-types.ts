interface ChatReference {
  documentId: number,
  startPage: number,
  endPage: number
}

interface ChatSegment {
  text: string,
  reference: ChatReference|null
}

type ChatRole = 'Assistant' | 'User'

interface ChatEntry {
  role: ChatRole,
  segments: ChatSegment[]
};

export type { ChatEntry, ChatRole, ChatSegment, ChatReference }
