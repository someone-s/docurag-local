<script setup lang="ts">
import { Check, ChevronsUpDown, Search } from "lucide-vue-next"
import { onMounted, ref, type Ref } from "vue"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Combobox, ComboboxAnchor, ComboboxEmpty, ComboboxGroup, ComboboxInput, ComboboxItem, ComboboxItemIndicator, ComboboxList, ComboboxTrigger } from "@/components/ui/combobox"
import axios from "axios"

const select: Ref<string|null> = ref(null);
const options: Ref<string[]> = ref([]);

onMounted(async () => {
  const makeResponse = await axios.get(`http://0.0.0.0:8081/machine/make/list`);
  if (!makeResponse.data.machine_makes || !Array.isArray(makeResponse.data.machine_makes)) return;
  const makes: any[] = makeResponse.data.machine_makes;
  options.value = makes.filter(make => typeof make === 'string');
});

</script>

<template>
  <Combobox v-model="select" by="label">
    <ComboboxAnchor as-child>
      <ComboboxTrigger as-child>
        <Button variant="outline" class="justify-between">
          {{ select ?? 'Select framework' }}
          <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </ComboboxTrigger>
    </ComboboxAnchor>

    <ComboboxList>
      <div class="relative w-full max-w-sm items-center">
        <ComboboxInput class="pl-9 focus-visible:ring-0 border-0 border-b rounded-none h-10" placeholder="Select framework..." />
        <span class="absolute start-0 inset-y-0 flex items-center justify-center px-3">
          <Search class="size-4 text-muted-foreground" />
        </span>
      </div>

      <ComboboxEmpty>
        No framework found.
      </ComboboxEmpty>

      <ComboboxGroup>
        <ComboboxItem
          v-for="option in options"
          :value="option"
        >
          {{ option }}

          <ComboboxItemIndicator>
            <Check :class="cn('ml-auto h-4 w-4')" />
          </ComboboxItemIndicator>
        </ComboboxItem>
      </ComboboxGroup>
    </ComboboxList>
  </Combobox>
</template>