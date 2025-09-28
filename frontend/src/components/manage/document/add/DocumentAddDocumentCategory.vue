<script setup lang="ts">
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem
} from '@/components/ui/dropdown-menu';
import Button from '@/components/ui/button/Button.vue';
import { ChevronDown } from 'lucide-vue-next';
import { onMounted, ref, type Ref } from 'vue';
import { axiosInstance } from '@/components/network-instance';


const select: Ref<string|null> = ref(null);
const options: Ref<string[]> = ref([]);

onMounted(fetchOptions);

async function fetchOptions() {
  const categoryResponse = await axiosInstance.get(`/document/category/list`);
  if (!categoryResponse.data.document_categories || !Array.isArray(categoryResponse.data.document_categories)) return;
  const categories: any[] = categoryResponse.data.document_categories;
  options.value = categories.filter(category => typeof category === 'string');
}

function setCategory(value: string|null) {
  select.value = value;
}

defineExpose({
  getSelect: () => select.value,
  setSelect: setCategory,
  fetchOptions
})
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
      <DropdownMenuItem v-for="option in options" @click="() => setCategory(option)">{{ option }}</DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>