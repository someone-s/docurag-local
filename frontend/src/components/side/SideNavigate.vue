<script setup lang="ts">
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  type SidebarProps,
} from "@/components/ui/sidebar";
import { Search, PaperclipIcon, ChevronsUpDown, WashingMachine, BookText } from "lucide-vue-next";
import SideThemeControl from "./SideThemeControl.vue";


const props = withDefaults(defineProps<SidebarProps>(), {
  collapsible: "icon",
})
</script>

<template>
  <Sidebar v-bind="props">
    <SidebarHeader>
      <SidebarMenuButton size="lg"
        class="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground">
        <div
          class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
          <PaperclipIcon class="size-4" />
        </div>
        <div class="grid flex-1 text-left text-sm leading-tight">
          <span class="truncate font-semibold">
            DocuRAG
          </span>
          <span class="truncate text-xs">About</span>
        </div>
        <ChevronsUpDown class="ml-auto" />
      </SidebarMenuButton>
    </SidebarHeader>
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel>Workspace</SidebarGroupLabel>
        <SidebarGroupContent>

          <SidebarMenu>

            <SidebarMenuItem key="Query">
              <SidebarMenuButton asChild>
                <RouterLink to="/query">
                  <component :is="Search" />
                  <span>Query</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>

            <SidebarMenuItem key="Machine">
              <SidebarMenuButton asChild>
                <RouterLink to="/manage/machine">
                  <component :is="WashingMachine" />
                  <span>Machine</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>

            <SidebarMenuItem key="Document">
              <SidebarMenuButton asChild>
                <RouterLink to="/manage/document">
                  <component :is="BookText" />
                  <span>Document</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>

          </SidebarMenu>

        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
    <SidebarFooter>
      <div class="w-full flex items-end justify-end">
        <SidebarMenu>
          <SidebarMenuItem :key="1">
            <SidebarMenuButton asChild>
              <SideThemeControl></SideThemeControl>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </div>
    </SidebarFooter>
  </Sidebar>

</template>