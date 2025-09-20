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

interface ChatOptions {
  makeCurrent: string|null,
  makeOptions: string[],
  categoryCurrent: string|null,
  categoryOptions: string[],
  modelCurrent: string|null,
  modelOptions: string[]
}

export type { ChatEntry, ChatRole, ChatSegment, ChatReference, ChatOptions }
