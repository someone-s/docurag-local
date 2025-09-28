import { ref, type Ref } from "vue";
import type { ChatOptions } from "../chat/chat-types";
import { axiosInstance } from "../network-instance";

class QueryFilter {

  options: Ref<ChatOptions> = ref({
    makeCurrent: null,
    makeOptions: [],
    categoryCurrent: null,
    categoryOptions: [],
    modelCurrent: null,
    modelOptions: []
  });

  onMakeChange: (make: string|null, options: ChatOptions) => void;
  onCategoryChange: (make: string|null, options: ChatOptions) => void;
  onModelChange: (make: string|null, options: ChatOptions) => void;

  constructor(
    onMakeChange: (make: string|null, options: ChatOptions) => void,
    onCategoryChange: (make: string|null, options: ChatOptions) => void,
    onModelChange: (make: string|null, options: ChatOptions) => void
  ) {
    this.onMakeChange = onMakeChange;
    this.onCategoryChange = onCategoryChange;
    this.onModelChange = onModelChange;


    const obj = this;
    (async () => {
      const makeResponse = await axiosInstance.get(`/machine/make/list`);
      if (!makeResponse.data.machine_makes || !Array.isArray(makeResponse.data.machine_makes)) return;
      const makes: any[] = makeResponse.data.machine_makes;
      obj.options.value.makeOptions = makes.filter(make => typeof make === 'string');
    })();
    (async () => {
      const categoryResponse = await axiosInstance.get(`/machine/category/list`);
      if (!categoryResponse.data.machine_categories || !Array.isArray(categoryResponse.data.machine_categories)) return;
      const categories: any[] = categoryResponse.data.machine_categories;
      obj.options.value.categoryOptions = categories.filter(category => typeof category === 'string');
    })();
  }

  public async setMake(make: string | null) {
    this.options.value.makeCurrent = make;

    this.updateModel();

    this.onMakeChange(make, this.options.value);
  }

  public setCategory(category: string | null) {
    this.options.value.categoryCurrent = category;

    this.updateModel();

    this.onCategoryChange(category, this.options.value);
  }

  private async updateModel() {

    this.options.value.modelCurrent = null;
    this.options.value.modelOptions = [];

    const params: { [key: string]: any } = {};


    const make = this.options.value.makeCurrent;
    const category = this.options.value.categoryCurrent;
    if (!make && !category) return;

    if (make)
      params.machine_make = make;

    if (category)
      params.machine_category = category;

    const searchResponse = await axiosInstance.get(`/machine/search`, {
      params: params
    });
    if (!searchResponse.data.machines || !Array.isArray(searchResponse.data.machines)) return;
    const machines: any[] = searchResponse.data.machines;

    for (const machine of machines) {
      if (typeof machine.model !== 'string') continue;
      this.options.value.modelOptions.push(machine.model);
    }
  }


  public setModel(model: string | null) {
    this.options.value.modelCurrent = model;

    this.onModelChange(model, this.options.value);
  }
}

export { QueryFilter }