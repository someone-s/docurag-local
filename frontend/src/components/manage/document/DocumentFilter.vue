<script setup lang="ts">
import Input from '@/components/ui/input/Input.vue';
import type { Table } from '@tanstack/vue-table';
import type { PageMachine } from '../machine-types';
import DocumentAdd from './DocumentAdd.vue';
import DocumentMake from './DocumentMake.vue';
import DocumentCategory from './DocumentCategory.vue';
import { fetchAllMachine } from '../machine-state';
import { ref, watch, type Ref } from 'vue';

const props = defineProps<{
  table: Table<any>,
  setMachines: (machines: PageMachine[]|null) => void
}>();

const make: Ref<string|null> = ref(null);
const category: Ref<string|null> = ref(null);
const model: Ref<string> = ref('');

function onMake(select: string|null) {
  make.value = select;
}

function onCategory(select: string|null) {
  category.value = select;
}

function onModel(select: string) {
  model.value = select;
}

watch([make, category, model], async ([currentMake, currentCategory, currentModel]) => {
  console.log(currentMake)
  console.log(currentCategory)
  console.log(currentModel)
  if (!currentMake && !currentCategory && currentModel.length == 0)
    props.setMachines(null);
  else {
    const response = await fetchAllMachine(currentMake, currentCategory, currentModel);
    console.log(response)
    props.setMachines(response.machines);
  }
})
</script>

<template>
  <div class="flex items-center py-4 gap-2 flex-wrap">
    <DocumentMake :set-select="onMake" />
    <DocumentCategory :set-select="onCategory" />
    <Input class="max-w-3xs" placeholder="Model" @update:model-value="onModel($event as string)" />
    <DocumentAdd />
  </div>
</template>