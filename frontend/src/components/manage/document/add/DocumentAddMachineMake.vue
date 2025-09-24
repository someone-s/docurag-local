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

const props = defineProps<{
  setSelect: (select: string|null) => void
}>();

const select: Ref<string|null> = ref(null);
const options: Ref<string[]> = ref([]);

onMounted(async () => {
  const makeResponse = await axios.get(`http://0.0.0.0:8081/machine/make/list`);
  if (!makeResponse.data.machine_makes || !Array.isArray(makeResponse.data.machine_makes)) return;
  const makes: any[] = makeResponse.data.machine_makes;
  options.value = makes.filter(make => typeof make === 'string');
});

function onSelect(value: string|null) {
  select.value = value;
  props.setSelect(value);
} 

</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="ghost" class="w-40">
        {{ select ? select : "Make" }}
        <ChevronDown class="ml-auto h-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent>
      <DropdownMenuItem v-for="option in options" @click="() => onSelect(option)">{{ option }}</DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>