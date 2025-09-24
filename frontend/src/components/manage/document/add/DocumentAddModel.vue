<script setup lang="ts">
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem
} from '@/components/ui/dropdown-menu';
import Button from '@/components/ui/button/Button.vue';
import { ChevronDown } from 'lucide-vue-next';
import axios from 'axios';
import { ref, type Ref } from 'vue';

interface Option {
  id: number,
  model: string
}

const props = defineProps<{
  setSelect: (id: number|null) => void
}>();

const select: Ref<Option|null> = ref(null);
const options: Ref<Option[]> = ref([]);

function onSelect(value: Option|null) {
  select.value = value;
  props.setSelect(value?.id ?? null);
}

const updateOptions = async (currentMake: string | null, currentCategory: string | null) => {
  if (!currentMake || !currentCategory) {
    options.value = [];
  }
  else {

    const params: { [key: string]: any } = {};
    params.machine_make = currentMake;
    params.machine_category = currentCategory;

    const machineResponse = await axios.get(`http://0.0.0.0:8081/machine/search`, { params: params });
    if (!machineResponse.data.machines || !Array.isArray(machineResponse.data.machines)) return;
    const machines: any[] = machineResponse.data.machines;
    options.value = machines
      .filter(machine => typeof machine === 'object' && typeof machine.model === 'string' && typeof machine.id === 'number' && Number.isInteger(machine.id))
      .map(machine => { return { id: machine.id, model: machine.model } });
  }
  onSelect(null);
}

defineExpose({
  updateOptions
});
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="ghost"  class="grow">
        {{ select?.model ?? "Model" }}
        <ChevronDown class="ml-auto h-4 w-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent>
      <DropdownMenuItem v-for="option in options" @click="() => onSelect(option)">{{ option.model }}</DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>