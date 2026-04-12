#!/usr/bin/env node
/**
 * Quick IPC test client — sends ping + status request to the running daemon
 */
import * as net from 'net';

const socket = net.connect(9876, '127.0.0.1', () => {
  console.log('Connected to Deep Tree Echo IPC server');

  // Send ping
  const ping = JSON.stringify({
    id: 'test-ping-1',
    type: 'ping',
    payload: {},
    timestamp: Date.now(),
  }) + '\n';
  socket.write(ping);
  console.log('Sent: PING');

  // Send status request
  const status = JSON.stringify({
    id: 'test-status-1',
    type: 'request_status',
    payload: {},
    timestamp: Date.now(),
  }) + '\n';
  socket.write(status);
  console.log('Sent: STATUS REQUEST');

  // Send cognitive request (this may not have a handler, but let's see)
  const cognitive = JSON.stringify({
    id: 'test-cognitive-1',
    type: 'request_cognitive',
    payload: {
      message: 'Hello Deep Tree Echo! Are you alive?',
      context: { source: 'ipc-test' },
    },
    timestamp: Date.now(),
  }) + '\n';
  socket.write(cognitive);
  console.log('Sent: COGNITIVE REQUEST');
});

let buffer = '';
socket.on('data', (data) => {
  buffer += data.toString();
  const lines = buffer.split('\n');
  buffer = lines.pop() || '';

  for (const line of lines) {
    if (line.trim()) {
      try {
        const msg = JSON.parse(line);
        console.log(`\nResponse [${msg.id}]:`);
        console.log(JSON.stringify(msg, null, 2));
      } catch {
        console.log('Raw:', line);
      }
    }
  }
});

socket.on('error', (err) => {
  console.error('Connection error:', err.message);
});

// Close after 3 seconds
setTimeout(() => {
  console.log('\nTest complete. Disconnecting.');
  socket.end();
  process.exit(0);
}, 3000);
