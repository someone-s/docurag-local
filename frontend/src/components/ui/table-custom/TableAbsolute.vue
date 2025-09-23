<script setup lang="ts">
import type { HTMLAttributes } from "vue"
import { cn } from "@/lib/utils"

const props = defineProps<{
  containerClass?: HTMLAttributes["class"],
  class?: HTMLAttributes["class"]
}>()
</script>

<template>
  <div data-slot="table-container" :class="cn('relative w-full h-fit max-h-full overflow-y-scroll', props.containerClass)">
    <table data-slot="table" :class="cn('caption-bottom text-sm rounded-md w-full h-full', props.class)">
      <slot />
    </table>
  </div>
</template>
