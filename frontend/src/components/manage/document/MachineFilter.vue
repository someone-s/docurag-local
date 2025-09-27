<script setup lang="ts">
import Input from '@/components/ui/input/Input.vue';
import type { Table } from '@tanstack/vue-table';
import type { PageMachine } from './machine-types';
import MachineMake from '../filter/MachineMake.vue';
import MachineCategory from '../filter/MachineCategory.vue';
import { fetchAllMachine } from './machine-state';
import { onMounted, ref, watch, type Ref } from 'vue';
import { useRoute } from 'vue-router';

const props = defineProps<{
  table: Table<any>,
  setMachines: (machines: PageMachine[]|null) => void,
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
  if (!currentMake && !currentCategory && currentModel.length == 0)
    props.setMachines(null);
  else {
    const response = await fetchAllMachine(currentMake, currentCategory, currentModel);
    props.setMachines(response.machines);
  }
});

const route = useRoute();

onMounted(() => {
  const queryModelObject = route.query.model;
  if (!queryModelObject || typeof queryModelObject !== 'string') return;

  model.value = queryModelObject as string;
});
</script>

<template>
    <MachineMake :allow-unset="true" variant="outline" v-on:select="onMake" />
    <MachineCategory :allow-unset="true" variant="outline" v-on:select="onCategory" />
    <Input class="max-w-3xs" placeholder="Model" :model-value="model" @update:model-value="onModel($event as string)" />
</template>