<script setup lang="ts">
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator
} from '@/components/ui/dropdown-menu';
import Button from '@/components/ui/button/Button.vue';
import { ChevronDown } from 'lucide-vue-next';
import axios from 'axios';
import { onMounted, ref, type Ref } from 'vue';

const props = defineProps<{
  allowUnset: boolean,
  onSelect: (select: string|null) => void
}>();

const select: Ref<string|null> = ref(null);
const options: Ref<string[]> = ref([]);

async function fetchOptions() {
  const categoryResponse = await axios.get(`http://0.0.0.0:8081/machine/category/list`);
  if (!categoryResponse.data.machine_categories || !Array.isArray(categoryResponse.data.machine_categories)) return;
  const categories: any[] = categoryResponse.data.machine_categories;
  options.value = categories.filter(category => typeof category === 'string');
}

function setSelect(value: string|null) {
  select.value = value;
  props.onSelect(value);
}

onMounted(fetchOptions);

defineExpose({
  getSelect: () => select.value,
  setSelect,
  fetchOptions
});
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button v-bind="$attrs">
        {{ select ? select : "Category" }}
        <ChevronDown class="ml-auto h-4 w-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent>
      <DropdownMenuItem v-if="allowUnset" @click="() => setSelect(null)">{{ "Unset" }}</DropdownMenuItem>
      <DropdownMenuSeparator v-if="allowUnset" />
      <DropdownMenuItem v-for="option in options" @click="() => setSelect(option)">{{ option }}</DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>