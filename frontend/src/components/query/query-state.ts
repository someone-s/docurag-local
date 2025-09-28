import type { ChatEntry, ChatSegment, ChatReference } from "@/components/chat/chat-types";
import { parse, Allow } from "partial-json";
import { ref, type Ref } from "vue";
import { getQuerySocket } from "../network-instance";

class QueryState {

  activeSocket: WebSocket | null = null;
  partialResponse: string = "";
  entries: Ref<ChatEntry[]> = ref([]);

  connecting: boolean = false;
  processing: Ref<boolean> = ref(false);

  queue: ((ws: WebSocket) => void)[] = [];

  onDocumentRequest: (documentId: number, documentCategory: string, machineMake: string, machineCategory: string, machineModel: string) => void;
  onChatComplete: () => void;

  constructor(
    onDocumentRequest: (documentId: number, documentCategory: string, machineMake: string, machineCategory: string, machineModel: string) => void,
    onChatComplete: () => void
  ) {
    this.onDocumentRequest = onDocumentRequest;
    this.onChatComplete = onChatComplete
  }

  public onDocument(data: any) {
    this.onDocumentRequest(data.document_id, data.machine_make, data.machine_category, data.machine_model, data.document_category);
  }

  public onGenerate(data: any) {
    this.partialResponse += data.delta;
    const partialObject = parse(this.partialResponse, Allow.STR | Allow.OBJ | Allow.ARR);
    if (partialObject.segments === undefined) return;

    const segments: any[] = partialObject.segments;
    this.entries.value[this.entries.value.length - 1].segments = segments
      .filter(inputSegment => inputSegment.text !== undefined)
      .map<ChatSegment>(inputSegment => {

        let reference: ChatReference | null = null;
        if (
          inputSegment.documentId !== undefined &&
          inputSegment.startPage !== undefined &&
          inputSegment.endPage !== undefined
        ) {
          reference = {
            documentId: inputSegment.documentId,
            startPage: inputSegment.startPage,
            endPage: inputSegment.endPage
          }
        }

        return {
          text: inputSegment.text,
          reference: reference
        };
      });
  }

  public onComplete() {
    this.partialResponse = "";
    this.processing.value = false;

    this.onChatComplete();
  }

  public onMessage(event: MessageEvent<any>) {
    try {
      const data = JSON.parse(event.data);
      switch (data.type) {
        case 'document':
          this.onDocument(data);
          break;
        case 'generate':
          this.onGenerate(data);
          break;
        case 'complete':
          this.onComplete();
          break;
      }
    }
    catch (e) {
      console.error(e);
    }
  }

  private connect() {
    if (this.connecting) return;
    this.connecting = true;

    const newSocket = getQuerySocket();
    const obj = this;
    this.activeSocket = null;
    newSocket.addEventListener('open', _ => {

      obj.activeSocket?.close(); // active socket may be null or not opened
      obj.activeSocket = newSocket;
      obj.partialResponse = "";
      obj.entries.value = [];

      obj.connecting = false;

      newSocket.addEventListener('message', event => obj.onMessage(event));
      newSocket.addEventListener('close', _ => {
        obj.activeSocket = null;
        obj.queue = [];
      });
      newSocket.addEventListener('error', _ => {
        obj.activeSocket = null;
        obj.queue = [];
      });

      obj.flush();
    });

  }

  // assume activeSocket is set
  private flush() {
    if (!this.activeSocket) return;
    let callback: ((ws: WebSocket) => void) | undefined;
    while ((callback = this.queue.shift()) !== undefined)
      callback(this.activeSocket);
  }

  private enqueueCallback(callback: (ws: WebSocket) => void) {
    this.queue.push(callback);
    if (this.activeSocket == null)
      this.connect();
    else
      this.flush();
  }

  private enqueueMessage(message: string) {
    this.enqueueCallback((_) => this.activeSocket?.send(message));
  }

  public setEmpty() {
    this.enqueueMessage(JSON.stringify({ type: 'data', parameter: 'empty' }));
  }
  public setMachineMake(machineMake: string) {
    this.enqueueMessage(JSON.stringify({ type: 'data', parameter: 'machine_make', value: machineMake }));
  }
  public setMachineName(machineName: string) {
    this.enqueueMessage(JSON.stringify({ type: 'data', parameter: 'machine_name', value: machineName }));
  }
  public setMachineCategory(machineCategory: string) {
    this.enqueueMessage(JSON.stringify({ type: 'data', parameter: 'machine_category', value: machineCategory }));
  }
  public setMachineModel(machineModel: string) {
    this.enqueueMessage(JSON.stringify({ type: 'data', parameter: 'machine_model', value: machineModel }));
  }

  public sendQuery(query: string) {
    const obj = this;
    this.enqueueCallback((ws) => {
      ws.send(JSON.stringify({ type: 'command', action: 'generate', query: query }));
      obj.activeSocket
      obj.entries.value.push({
        role: 'User',
        segments: [
          {
            text: query,
            reference: null
          }
        ]
      });
      obj.entries.value.push({
        role: 'Assistant',
        segments: []
      });
      obj.processing.value = true;
    });
  }
  public sendExit() {
    this.enqueueMessage(JSON.stringify({ type: 'command', action: 'exit' }));
  }
}

export { QueryState }