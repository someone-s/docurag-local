<script setup lang="ts">
import { BreadcrumbItem } from '@/components/ui/breadcrumb';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from '@/components/ui/dropdown-menu';

defineProps<{
  current: string,
  options: string[],
  setCurrent: (value: string | null) => void
}>();
</script>

<template>
  <BreadcrumbItem>
    <DropdownMenu>
      <DropdownMenuTrigger class="flex items-center gap-1">
        {{ current }}
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start">
        <DropdownMenuItem @click="() => setCurrent(null)">{{ "Unset" }}</DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem v-for="option in options" @click="() => setCurrent(option)">{{ option }}</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  </BreadcrumbItem>
</template>