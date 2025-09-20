import type { ChatEntry, ChatSegment, ChatReference } from "@/components/chat/chat-types";
import { parse, Allow } from "partial-json";

class QueryState {

  activeSocket: WebSocket | null = null;
  partialResponse: string = "";
  entries: ChatEntry[] = [];
  processing: boolean = false;

  onDocumentRequest: (documentId: number, documentCategory: string, machineMake: string, machineCategory: string, machineModel: string) => void;
  onChatUpdate: () => void;
  onChatComplete: () => void;

  sendQueue: string[] = []

  constructor(
    onDocumentRequest: (documentId: number, documentCategory: string, machineMake: string, machineCategory: string, machineModel: string) => void,
    onChatUpdate: () => void,
    onChatComplete: () => void
  ) {
    this.onDocumentRequest = onDocumentRequest;
    this.onChatUpdate = onChatUpdate;
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
    this.entries[this.entries.length - 1].segments = segments
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
    this.onChatUpdate();
  }

  public onComplete() {
    this.partialResponse = "";

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
          this.onChatComplete();
          break;
      }
    }
    catch (e) {
      console.error(e);
    }
  }

  public connect() {
    const newSocket = new WebSocket("ws://0.0.0.0:8081/query");
    const obj = this;
    this.activeSocket = null;
    newSocket.addEventListener('open', _ => {
      obj.activeSocket?.close(); // active socket may be null or not opened
      obj.activeSocket = newSocket;
      obj.partialResponse = "";
      obj.entries = [];
      console.log(obj.activeSocket);
    });
    newSocket.addEventListener('message', event => this.onMessage(event));
    newSocket.addEventListener('close', _ => {
       obj.activeSocket = null;
       obj.sendQueue = [];
    });
  }

  public setMachineMake(machineMake: string) {
    if (this.activeSocket == null) return;
    this.activeSocket.send(JSON.stringify({ type: 'data', parameter: 'machine_make', value: machineMake }));
  }
  public setMachineName(machineName: string) {
    if (this.activeSocket == null) return;
    this.activeSocket.send(JSON.stringify({ type: 'data', parameter: 'machine_name', value: machineName }));
  }
  public setMachineCategory(machineCategory: string) {
    if (this.activeSocket == null) return;
    this.activeSocket.send(JSON.stringify({ type: 'data', parameter: 'machine_category', value: machineCategory }));
  }
  public setMachineModel(machineModel: string) {
    if (this.activeSocket == null) return;
    this.activeSocket.send(JSON.stringify({ type: 'data', parameter: 'machine_model', value: machineModel }));
  }

  public sendQuery(query: string) {
    if (this.activeSocket == null) return;
    this.activeSocket.send(JSON.stringify({ type: 'command', action: 'generate', query: query }));
    this.entries.push({
      role: 'User',
      segments: [
        {
          text: query,
          reference: null
        }
      ]
    });
    this.entries.push({
      role: 'Assistant',
      segments: []
    });
    this.onChatUpdate();
  }
  public sendExit() {
    if (this.activeSocket == null) return;
    this.activeSocket.send(JSON.stringify({ type: 'command', action: 'exit' }));
  }
}

export { QueryState }