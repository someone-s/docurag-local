<script setup lang="ts">
import {
  Breadcrumb,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import ChatDropdown from './ChatDropdown.vue';
import BreadcrumbListNoWrap from '@/components/ui/breadcrumb-custom/BreadcrumbListNoWrap.vue';
import type { Ref } from 'vue';
import type { ChatOptions } from './chat-types';

defineProps<{
  options: Ref<ChatOptions>,
  setMake: (val: string|null) => void,
  setCategory: (val: string|null) => void,
  setModel: (val: string|null) => void
}>();
</script>

<template>
  <Breadcrumb class="overflow-clip max-w-full">
    <BreadcrumbListNoWrap>
      <ChatDropdown :current="options.value.makeCurrent ?? 'Specify Make'" :options="options.value.makeOptions" :set-current="setMake"></ChatDropdown>

      <BreadcrumbSeparator v-if="options.value.categoryOptions.length > 0">|</BreadcrumbSeparator>
      <ChatDropdown v-if="options.value.categoryOptions.length > 0" :current="options.value.categoryCurrent ?? 'Specify Category'" :options="options.value.categoryOptions" :set-current="setCategory"></ChatDropdown>

      <BreadcrumbSeparator v-if="options.value.modelOptions.length > 0">|</BreadcrumbSeparator>
      <ChatDropdown v-if="options.value.modelOptions.length > 0" :current="options.value.modelCurrent ?? 'Specify Model'" :options="options.value.modelOptions"  :set-current="setModel"></ChatDropdown>
    </BreadcrumbListNoWrap>
  </Breadcrumb>
  
</template>