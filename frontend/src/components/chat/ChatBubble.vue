<script setup lang="ts">
import { SquareArrowOutUpRightIcon } from 'lucide-vue-next';
import { Button } from '@/components/ui/button';
import type { ChatEntry, ChatReference } from './chat-types';

defineProps<{
  entry: ChatEntry,
  goToSegment: (documentId: number, startPage: number, endPage: number) => void
}>();
</script>

<template>
  <div :class="(entry.role == 'Assistant' ? 'justify-self-start' : 'justify-self-end') + ' max-w-[80%] p-3'">
    <p class="rounded-md border bg-pdf p-2.5 pl-3.5 pr-3.5">
      <span v-for="segment in entry.segments" class="text-justify text-base/loose whitespace-pre-line">
        {{ segment.text }}
        <Button v-if="segment.reference !== null" @click="() => {
          if (segment.reference === null) return; // Make TS not complain
          const capturedReference: ChatReference = segment.reference;
          goToSegment(capturedReference.documentId, capturedReference.startPage, capturedReference.endPage);
        }" class="rounded-sm h-[1rem] p-0 cursor-pointer">
          {{ segment.reference.documentId }}:{{ segment.reference.startPage }}-{{ segment.reference.endPage }}
          <SquareArrowOutUpRightIcon class="size-[0.75rem]" stroke-width="0.15rem"></SquareArrowOutUpRightIcon>
        </Button>
      </span>
    </p>
  </div>
</template>