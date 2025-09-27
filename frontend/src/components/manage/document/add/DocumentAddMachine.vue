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
    <MachineMake :allow-unset="false" variant="ghost" :set-select="onMake" class="w-100 shrink-0"/>
    <MachineCategory :allow-unset="false" variant="ghost" :set-select="onCategory" class="w-100 shrink-0" />
    <DocumentAddMachineModel ref="modelEl" :set-select="onId" class="grow" />
  </div>
</template>