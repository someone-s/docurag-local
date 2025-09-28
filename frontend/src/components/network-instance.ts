import axios from "axios";

export const axiosInstance = axios.create({
  baseURL: import.meta.env.DEV ? 'http://localhost:8081' : '/api'
});

export const getStatusSocket = () => 
  new WebSocket(`${import.meta.env.DEV ? 'ws://localhost:8081' : '/api'}/document/upload/status`);

export const getQuerySocket = () => 
  new WebSocket(`${import.meta.env.DEV ? 'ws://localhost:8081' : '/api'}/query`);