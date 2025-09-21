<script setup lang="ts">
import {
  SidebarMenuButton
} from "@/components/ui/sidebar";
import { Sun, Moon } from "lucide-vue-next";
import { useColorMode } from '@vueuse/core';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';

const { store, state } = useColorMode()

</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <SidebarMenuButton>
        <component :is="state == 'light' ? Sun : Moon" />
        <span>Toggle theme</span>
      </SidebarMenuButton>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      <DropdownMenuItem @click="store = 'light'">
        Light
      </DropdownMenuItem>
      <DropdownMenuItem @click="store = 'dark'">
        Dark
      </DropdownMenuItem>
      <DropdownMenuItem @click="store = 'auto'">
        System
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>