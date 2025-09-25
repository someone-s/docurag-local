<script setup lang="ts">

import { cn } from '@/lib/utils';
// @ts-expect-error
import { SelfBuildingSquareSpinner } from 'epic-spinners';
import { onMounted, onUnmounted, ref, type Ref } from 'vue';
import { toast } from 'vue-sonner';

interface Progress {
  id: string,
  fileName: string
}

const progresses: Ref<Progress[]> = ref([]);
let newSocket: WebSocket;

onMounted(() => {
  newSocket = new WebSocket("ws://0.0.0.0:8081/document/upload/status");
  newSocket.addEventListener('message', (event: MessageEvent) => {
    const json = JSON.parse(event.data);
    switch (json.type) {
      case 'add':
        progresses.value.push({
          id: json.id,
          fileName: json.file_name
        });
        break;
      case 'remove':
        const progressIndex = progresses.value.findIndex(progress => progress.id == json.id);
        if (progressIndex != -1) {
          const progress = progresses.value[progressIndex];
          progresses.value.splice(progressIndex, 1);
          toast('File ready', {
            description: `${progress.fileName} is now ready`,
          })
        }
        break;
    }
  });
});

onUnmounted(() => {
  newSocket?.close();
});
</script>

<template>
  <div v-if="progresses.length > 0" class="border rounded-md text-sm">
    <div class="border-b p-2 text-muted-foreground">
      Processing
    </div>
    <div v-for="progress, index in progresses" :key="progress.id"
      :class="cn((index < progresses.length - 1 ? 'border-b' : ''), 'flex flex-row justify-between items-center p-2 text-sm')">
      <span>
        {{ progress.fileName }}
      </span>
      <SelfBuildingSquareSpinner :animation-duration="6000" :size="16" color="var(--foreground)" class="shrink-0" />
    </div>
  </div>
</template>