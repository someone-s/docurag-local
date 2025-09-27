<script setup lang="ts">
import { ref, useTemplateRef, type Ref } from 'vue';
import DocumentAddMachineModel from './DocumentAddMachineModel.vue';
import MachineMake from '../../filter/MachineMake.vue';
import MachineCategory from '../../filter/MachineCategory.vue';

const make: Ref<string | null> = ref(null);
const category: Ref<string | null> = ref(null);
const id: Ref<number | null> = ref(null);

const modelEl = useTemplateRef('modelEl');

function onMake(select: string | null) {
  make.value = select;
  modelEl.value?.updateOptions(make.value, category.value);
}

function onCategory(select: string | null) {
  category.value = select;
  modelEl.value?.updateOptions(make.value, category.value);
}

function onId(select: number | null) {
  id.value = select;
}

defineExpose({
  getId: () => id.value
});
</script>

<template>
  <div class="flex flex-row w-full justify-between border rounded-md max-w-screen flex-wrap">
    <MachineMake :allow-unset="false" variant="ghost" v-on:select="onMake" class="w-40 shrink-0 grow-0 rounded-r-none"/>
    <MachineCategory :allow-unset="false" variant="ghost" v-on:select="onCategory" class="w-40 shrink-0 grow-0 rounded-none border-l" />
    <DocumentAddMachineModel ref="modelEl" variant="ghost" :set-select="onId" class="min-w-40 shrink-0 grow-0 rounded-l-none border-l" />
  </div>
</template>