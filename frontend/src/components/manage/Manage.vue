<script setup lang="ts">
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable'
import LayoutHeader from '../layout/LayoutHeader.vue';

</script>

<template>
  <LayoutHeader header-text="Manage" />
  <ResizablePanelGroup direction="horizontal" class="h-full" auto-save-id="query-group">
    <ResizablePanel :min-size="40">
      
    </ResizablePanel>
    <ResizableHandle with-handle />
    <ResizablePanel :min-size="20">
      
    </ResizablePanel>
  </ResizablePanelGroup>
</template>