<script setup lang="ts">
import {
  Breadcrumb,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import ChatDropdown from './ChatDropdown.vue';
import BreadcrumbListNoWrap from '@/components/ui/breadcrumb-custom/BreadcrumbListNoWrap.vue';

</script>

<template>
  <Breadcrumb class="overflow-clip max-w-full">
    <BreadcrumbListNoWrap>
      <ChatDropdown :options="[]"></ChatDropdown>
      <BreadcrumbSeparator>|</BreadcrumbSeparator>
      <ChatDropdown :options="[]"></ChatDropdown>
      <BreadcrumbSeparator>|</BreadcrumbSeparator>
      <ChatDropdown :options="[]"></ChatDropdown>
    </BreadcrumbListNoWrap>
  </Breadcrumb>
  
</template>