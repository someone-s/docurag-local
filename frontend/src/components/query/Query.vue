<script setup lang="ts">
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable'

import PDFViewer from '@/components/pdf/PDFViewer.vue';
import type { PDFDocument } from '@/components/pdf/pdf-types';
import ChatColumn from '@/components/chat/ChatColumn.vue';
import axios from 'axios';
import { reactive, useTemplateRef, type Reactive } from 'vue';
import { QueryState } from './query-state';
import type { ChatOptions } from '../chat/chat-types';

const documents: PDFDocument[] = [];

async function fetchDocument(id: number, name: string) {
  navigator.locks.request('fetchDocument', async (_) => {
    if (!Number.isInteger(id)) return;

    if (documents.some(document => document.id == id)) return;


    const listResponse = await axios.get(`http://0.0.0.0:8081/document/fetch/${id}`,
      {
        responseType: 'arraybuffer',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/pdf'
        }
      });
    documents.push({
      name: name,
      id: id,
      file: listResponse.data
    });
  });
}

const viewer = useTemplateRef('viewer');

function goToSegment(documentId: number, startPage: number, _endPage: number) {
  if (viewer.value == null) return;
  viewer.value.goToDocumentPage(documentId, startPage);
}

const chat = useTemplateRef('chat');



const queryState = new QueryState(
  (documentId, documentCategory, machineMake, machineCategory, machineModel) => fetchDocument(documentId, `${machineMake} ${machineCategory} ${machineModel} ${documentCategory}`),
  () => chat.value?.scrollToBottom()
);

const options: Reactive<ChatOptions> = reactive({
  machineMake: [],
  machineCategory: [],
  machineModel: []
});
</script>

<template>
  <ResizablePanelGroup direction="horizontal">
    <ResizablePanel>
      <ChatColumn ref="chat" class="h-full" 
        :block="queryState.processing"
        :entries="queryState.entries" 
        :send-query="query => queryState.sendQuery(query)" 
        :goToSegment="goToSegment"
        :options="options" />
    </ResizablePanel>
    <ResizableHandle with-handle />
    <ResizablePanel>
      <PDFViewer ref="viewer" class="h-full" :documents="documents" />
    </ResizablePanel>
  </ResizablePanelGroup>
</template>