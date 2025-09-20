<script setup lang="ts">
import {
  Breadcrumb,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import ChatDropdown from './ChatDropdown.vue';
import BreadcrumbListNoWrap from '@/components/ui/breadcrumb-custom/BreadcrumbListNoWrap.vue';
import type { Reactive } from 'vue';
import type { ChatOptions } from './chat-types';

defineProps<{
  options: Reactive<ChatOptions>
}>();
</script>

<template>
  <Breadcrumb class="overflow-clip max-w-full">
    <BreadcrumbListNoWrap>
      <ChatDropdown :options="options.machineMake"></ChatDropdown>

      <BreadcrumbSeparator v-if="options.machineCategory.length > 0">|</BreadcrumbSeparator>
      <ChatDropdown :options="options.machineCategory" v-if="options.machineCategory.length > 0"></ChatDropdown>

      <BreadcrumbSeparator v-if="options.machineModel.length > 0">|</BreadcrumbSeparator>
      <ChatDropdown :options="options.machineModel" v-if="options.machineModel.length > 0"></ChatDropdown>
    </BreadcrumbListNoWrap>
  </Breadcrumb>
  
</template>