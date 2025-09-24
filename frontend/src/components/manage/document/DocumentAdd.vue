<script setup lang="ts">
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import Button from '@/components/ui/button/Button.vue';
import { Plus } from 'lucide-vue-next';
import AddMake from './add/AddMake.vue';


</script>

<template>
  <Popover>
    <PopoverTrigger as-child class="ml-auto cursor-pointer">
      <Button>
        Add
        <Plus class="ml-2 h-4 w-4" />
      </Button>
    </PopoverTrigger>
    <PopoverContent>
      <div></div>
      <AddMake />
    </PopoverContent>
  </Popover>
</template>