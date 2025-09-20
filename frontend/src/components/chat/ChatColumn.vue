<script setup lang="ts">
import ChatBubble from './ChatBubble.vue';
import type { ChatEntry, ChatOptions } from './chat-types';
import ChatFilter from './ChatFilters.vue';
import Button from '@/components/ui/button/Button.vue';
import { ArrowRightIcon } from 'lucide-vue-next';
import { useTemplateRef, watch, type Ref } from 'vue';

const queryInput = useTemplateRef('query-input');

const chatArea = useTemplateRef('chat-area');

function scrollToBottom() {
  if (chatArea.value == null) return;

  chatArea.value.scrollTop = chatArea.value.scrollHeight;
}

defineExpose({
  scrollToBottom
})


const props = defineProps<{
  block: Ref<boolean>,
  entries: Ref<ChatEntry[]>,
  sendQuery: (query: string) => void,
  goToSegment: (documentId: number, startPage: number, endPage: number) => void,
  
  options: Ref<ChatOptions>,
  setMake: (val: string|null) => void,
  setCategory: (val: string|null) => void,
  setModel: (val: string|null) => void
}>();

watch(props.block, (val) => {
  console.log(val)
})

function onSubmit() {
  if (queryInput.value == null) return;
  if (queryInput.value.textContent.length < 2) return;
  queryInput.value.textContent = queryInput.value.textContent.substring(0, queryInput.value.textContent.length);

  const queryText = queryInput.value.textContent;

  props.sendQuery(queryText);
}
</script>

<template>
  <div class="relative h-screen">
    <div ref="chat-area" class="h-screen overflow-scroll no-scrollbar">
      <ChatBubble v-for="entry in entries.value" :entry="entry" :goToSegment="goToSegment" />
      <div class="h-36"></div>
    </div>
    <div class="absolute w-full bottom-2 flex justify-center no-drag">
      <div class="w-[90%] h-fit flex flex-row items-center">
        <div class="w-[calc(100%-48px)] border rounded-lg p-3 pl-5 pr-5 bg-pdf">
          <ChatFilter class="overflow-scroll no-scrollbar" :options="options" :setMake="setMake" :setCategory="setCategory" :setModel="setModel"></ChatFilter>
          <div class="h-3"></div>
          <div ref="query-input" class="query-entry h-fit max-h-[50vh] overflow-scroll no-scrollbar outline-0 text-md text-wrap break-all" :contenteditable="!block.value" placeholder="Enter your question..." @keyup.exact.enter="onSubmit"></div>
        </div>
        <div class=" shrink-0 w-3"></div>
        <Button class="shrink-0 size-9 rounded-4xl cursor-pointer" @click="onSubmit">
          <ArrowRightIcon class="size-4"></ArrowRightIcon>
        </Button>
      </div>
    </div>


  </div>
</template>

<style scoped>
.query-entry[contenteditable] {
  &[placeholder]:empty::before {
    content: attr(placeholder);
    z-index: 9;
    line-height: 1.7;
    color: #555;
    word-break: break-all;
    user-select: none;
  }

  &[placeholder]:empty:focus::before {
    content: "";
  }
}
</style>