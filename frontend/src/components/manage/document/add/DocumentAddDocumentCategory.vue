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
import { onMounted, ref, type Ref } from 'vue';


const select: Ref<string|null> = ref(null);
const options: Ref<string[]> = ref([]);

onMounted(async () => {
  const categoryResponse = await axios.get(`http://0.0.0.0:8081/document/category/list`);
  if (!categoryResponse.data.document_categories || !Array.isArray(categoryResponse.data.document_categories)) return;
  const categories: any[] = categoryResponse.data.document_categories;
  options.value = categories.filter(category => typeof category === 'string');
});

function onSelect(value: string|null) {
  select.value = value;
}

defineExpose({
  getCategory: () => select.value
})
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="ghost" class="w-40 border">
        {{ select ? select : "Category" }}
        <ChevronDown class="ml-auto h-4 w-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent>
      <DropdownMenuItem v-for="option in options" @click="() => onSelect(option)">{{ option }}</DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>