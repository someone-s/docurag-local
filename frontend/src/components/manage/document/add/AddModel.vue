<script setup lang="ts">
import { ChevronsUpDown, Search } from "lucide-vue-next"
import { onMounted, ref, watch, type Ref } from "vue"
import { Button } from "@/components/ui/button"
import { Combobox, ComboboxAnchor, ComboboxEmpty, ComboboxGroup, ComboboxInput, ComboboxItem, ComboboxList, ComboboxTrigger } from "@/components/ui/combobox"
import { axiosInstance } from "@/components/network-instance"

interface OptionPair {
  model: string,
  id: number
}

const options: Ref<OptionPair[]> = ref([]);

const props = defineProps<{
  make: string | null,
  category: string | null,
  select: OptionPair | null,
  setSelect: (id: OptionPair | null) => void,
}>();

const update = async (currentMake: string | null, currentCategory: string | null) => {
  if (!currentMake || !currentCategory) {
    options.value = [];
  }
  else {

    const params: { [key: string]: any } = {};
    params.machine_make = currentMake;
    params.machine_category = currentCategory;

    const machineResponse = await axiosInstance.get(`/machine/search`, { params: params });
    if (!machineResponse.data.machines || !Array.isArray(machineResponse.data.machines)) return;
    const machines: any[] = machineResponse.data.machines;
    options.value = machines
      .filter(machine => typeof machine === 'object' && typeof machine.model === 'string' && typeof machine.id === 'number' && Number.isInteger(machine.id))
      .map(machine => { return { model: machine.model, id: machine.id } });
  }
}

onMounted(async () => {
  await update(props.make, props.category);
})

watch(() => [props.make, props.category], async ([currentMake, currentCategory]) => {
  await update(currentMake, currentCategory);
});

</script>

<template>
  <Combobox @update:model-value="(val) => setSelect(val as OptionPair | null)">
    <ComboboxAnchor as-child>
      <ComboboxTrigger as-child>
        <Button variant="ghost" class="justify-between">
          {{ select?.model ?? 'Select model' }}
          <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </ComboboxTrigger>
    </ComboboxAnchor>

    <ComboboxList>
      <div class="relative w-full max-w-sm items-center">
        <ComboboxInput class="pl-9 focus-visible:ring-0 border-0 border-b rounded-none h-10"
          placeholder="Select model..." />
        <span class="absolute start-0 inset-y-0 flex items-center justify-center px-3">
          <Search class="size-4 text-muted-foreground" />
        </span>
      </div>

      <ComboboxEmpty>
        No framework found.
      </ComboboxEmpty>

      <ComboboxGroup>
        <ComboboxItem v-for="option in options" :value="option">
          {{ option.model }}
        </ComboboxItem>
      </ComboboxGroup>
    </ComboboxList>
  </Combobox>
</template>