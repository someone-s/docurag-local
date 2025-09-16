import { openAsBlob } from 'node:fs';

(async () => {
    const blob = await openAsBlob('test-input-2.pdf');

    const socket = new WebSocket('ws://0.0.0.0:8081/upload');
    socket.addEventListener('open', () => {
        socket.send(blob);
    });
    socket.addEventListener('message', event => {
        try {
            const receivedData = JSON.parse(event.data);
            console.log('Received JSON:', receivedData);
        } catch (error) {
            console.error('Error parsing JSON:', error);
            console.log('Received data was:', event.data);
        }
    });
    socket.addEventListener()
})();