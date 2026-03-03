# Dove9-Dovecot Integration: Practical Implementation Roadmap

**Date**: January 9, 2026  
**Phase**: Milestone 1 - Mail Protocol Foundation  
**Status**: Ready to Begin

---

## Quick Start: What to Build First

This roadmap breaks down the integration into **actionable tasks** with specific code examples and testing strategies. Start here to begin implementation immediately.

---

## Phase 1A: Mail Protocol Bridge Core (Days 1-3)

### Task 1.1: Create Type Definitions

**File**: `dove9/src/types/mail.ts` (NEW)

```typescript
/**
 * Mail message structure compatible with Dove9 MessageProcess
 */
export interface MailMessage {
  messageId: string;
  threadId?: string;
  inReplyTo?: string;
  references?: string[];
  from: string;
  to: string[];
  cc?: string[];
  bcc?: string[];
  replyTo?: string;
  subject: string;
  body: string;
  bodyHtml?: string;
  headers: Map<string, string>;
  timestamp: Date;
  receivedAt: Date;
  flags?: MailFlag[];
  mailbox: string;
  size?: number;
  attachments?: MailAttachment[];
}

export interface MailAttachment {
  filename: string;
  contentType: string;
  size: number;
  content?: Buffer;
  contentId?: string;
}

export enum MailFlag {
  SEEN = '\\Seen',
  ANSWERED = '\\Answered',
  FLAGGED = '\\Flagged',
  DELETED = '\\Deleted',
  DRAFT = '\\Draft',
}

export interface MailboxMapping {
  inbox: string;       // INBOX - Pending processes
  processing: string;  // INBOX.Processing - Active processes
  sent: string;        // Sent - Completed processes
  drafts: string;      // Drafts - Suspended processes
  trash: string;       // Trash - Terminated processes
  archive: string;     // Archive - Historical processes
}

export const DEFAULT_MAILBOX_MAPPING: MailboxMapping = {
  inbox: 'INBOX',
  processing: 'INBOX.Processing',
  sent: 'Sent',
  drafts: 'Drafts',
  trash: 'Trash',
  archive: 'Archive',
};
```

**Test**: `dove9/src/__tests__/types/mail.test.ts`

```typescript
import { MailMessage, MailFlag, DEFAULT_MAILBOX_MAPPING } from '../../types/mail.js';

describe('Mail Types', () => {
  it('should create valid MailMessage', () => {
    const mail: MailMessage = {
      messageId: '<test@example.com>',
      from: 'user@example.com',
      to: ['echo@dove9.local'],
      subject: 'Test',
      body: 'Hello',
      headers: new Map([['X-Test', 'value']]),
      timestamp: new Date(),
      receivedAt: new Date(),
      mailbox: 'INBOX',
    };
    
    expect(mail.messageId).toBe('<test@example.com>');
    expect(mail.from).toBe('user@example.com');
  });
  
  it('should have default mailbox mapping', () => {
    expect(DEFAULT_MAILBOX_MAPPING.inbox).toBe('INBOX');
    expect(DEFAULT_MAILBOX_MAPPING.sent).toBe('Sent');
  });
});
```

### Task 1.2: Create Mail Protocol Bridge

**File**: `dove9/src/integration/mail-protocol-bridge.ts` (NEW)

```typescript
/**
 * MailProtocolBridge - Bidirectional bridge between mail and Dove9 processes
 */

import { Dove9Kernel } from '../core/kernel.js';
import { MessageProcess, ProcessState, CognitiveContext } from '../types/index.js';
import { MailMessage, MailboxMapping, MailFlag, DEFAULT_MAILBOX_MAPPING } from '../types/mail.js';
import { getLogger } from '../utils/logger.js';

const logger = getLogger('MailProtocolBridge');

export interface MailProtocolBridgeConfig {
  mailboxes: MailboxMapping;
  botEmailAddress: string;
  enableAutoResponse: boolean;
  priorityKeywords: {
    urgent: string[];
    important: string[];
    low: string[];
  };
}

const DEFAULT_CONFIG: MailProtocolBridgeConfig = {
  mailboxes: DEFAULT_MAILBOX_MAPPING,
  botEmailAddress: 'echo@dove9.local',
  enableAutoResponse: true,
  priorityKeywords: {
    urgent: ['urgent', 'asap', 'emergency'],
    important: ['important', 'priority'],
    low: ['fyi', 'when you can'],
  },
};

export class MailProtocolBridge {
  private kernel: Dove9Kernel;
  private config: MailProtocolBridgeConfig;
  private messageToProcessMap: Map<string, string> = new Map();
  private processToMessageMap: Map<string, string> = new Map();
  
  constructor(kernel: Dove9Kernel, config?: Partial<MailProtocolBridgeConfig>) {
    this.kernel = kernel;
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.setupKernelEventHandlers();
  }
  
  /**
   * Convert incoming mail message to Dove9 process
   */
  public mailMessageToProcess(mail: MailMessage): MessageProcess {
    logger.info(`Converting mail ${mail.messageId} to process`);
    
    // Extract priority from mail
    const priority = this.extractPriority(mail);
    
    // Create process through kernel
    const process = this.kernel.createProcess(
      mail.messageId,
      mail.from,
      mail.to,
      mail.subject,
      mail.body,
      priority
    );
    
    // Store bidirectional mapping
    this.messageToProcessMap.set(mail.messageId, process.id);
    this.processToMessageMap.set(process.id, mail.messageId);
    
    // Enhance cognitive context with mail metadata
    process.cognitiveContext = this.enhanceContextFromMail(
      process.cognitiveContext,
      mail
    );
    
    // Set process metadata
    if (!process.metadata) {
      process.metadata = {};
    }
    process.metadata.mailbox = mail.mailbox;
    process.metadata.threadId = mail.threadId;
    process.metadata.inReplyTo = mail.inReplyTo;
    
    return process;
  }
  
  /**
   * Convert Dove9 process to outgoing mail message
   */
  public processToMailMessage(process: MessageProcess): MailMessage {
    logger.info(`Converting process ${process.id} to mail message`);
    
    const originalMessageId = this.processToMessageMap.get(process.id);
    
    return {
      messageId: this.generateMessageId(process),
      threadId: process.metadata?.threadId,
      inReplyTo: originalMessageId,
      references: originalMessageId ? [originalMessageId] : undefined,
      from: this.config.botEmailAddress,
      to: [process.from], // Reply to sender
      subject: this.generateSubject(process),
      body: this.formatProcessOutput(process),
      bodyHtml: this.formatProcessOutputHtml(process),
      headers: this.buildHeaders(process),
      timestamp: new Date(),
      receivedAt: new Date(),
      flags: this.determineFlags(process),
      mailbox: this.determineMailbox(process),
    };
  }
  
  /**
   * Extract priority from mail (1-10, higher = more urgent)
   */
  private extractPriority(mail: MailMessage): number {
    // Check X-Priority header (1=highest, 5=lowest)
    const xPriority = mail.headers.get('X-Priority');
    if (xPriority) {
      const num = parseInt(xPriority, 10);
      if (!isNaN(num) && num >= 1 && num <= 5) {
        return 11 - (num * 2); // Convert 1-5 to 10-2
      }
    }
    
    // Check for priority keywords in subject
    const subjectLower = mail.subject.toLowerCase();
    
    for (const keyword of this.config.priorityKeywords.urgent) {
      if (subjectLower.includes(keyword)) return 9;
    }
    
    for (const keyword of this.config.priorityKeywords.important) {
      if (subjectLower.includes(keyword)) return 7;
    }
    
    for (const keyword of this.config.priorityKeywords.low) {
      if (subjectLower.includes(keyword)) return 3;
    }
    
    return 5; // Default medium priority
  }
  
  /**
   * Enhance cognitive context with mail metadata
   */
  private enhanceContextFromMail(
    context: CognitiveContext,
    mail: MailMessage
  ): CognitiveContext {
    return {
      ...context,
      metadata: {
        ...context.metadata,
        source: 'email',
        mailMessageId: mail.messageId,
        mailFrom: mail.from,
        mailSubject: mail.subject,
        mailTimestamp: mail.timestamp.toISOString(),
        mailHeaders: Object.fromEntries(mail.headers),
      },
    };
  }
  
  /**
   * Determine mailbox for process based on state
   */
  private determineMailbox(process: MessageProcess): string {
    switch (process.state) {
      case ProcessState.PENDING:
        return this.config.mailboxes.inbox;
      case ProcessState.ACTIVE:
      case ProcessState.PROCESSING:
        return this.config.mailboxes.processing;
      case ProcessState.COMPLETED:
        return this.config.mailboxes.sent;
      case ProcessState.SUSPENDED:
        return this.config.mailboxes.drafts;
      case ProcessState.TERMINATED:
        return this.config.mailboxes.trash;
      default:
        return this.config.mailboxes.inbox;
    }
  }
  
  /**
   * Determine mail flags for process
   */
  private determineFlags(process: MessageProcess): MailFlag[] {
    const flags: MailFlag[] = [];
    
    if (process.state === ProcessState.COMPLETED) {
      flags.push(MailFlag.SEEN);
      flags.push(MailFlag.ANSWERED);
    }
    
    if (process.state === ProcessState.SUSPENDED) {
      flags.push(MailFlag.DRAFT);
    }
    
    if (process.priority >= 8) {
      flags.push(MailFlag.FLAGGED);
    }
    
    return flags;
  }
  
  /**
   * Generate Message-ID for process
   */
  private generateMessageId(process: MessageProcess): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 10);
    return `<${process.id}.${timestamp}.${random}@dove9.local>`;
  }
  
  /**
   * Generate subject for response
   */
  private generateSubject(process: MessageProcess): string {
    if (process.subject.toLowerCase().startsWith('re:')) {
      return process.subject;
    }
    return `Re: ${process.subject}`;
  }
  
  /**
   * Format process output as plain text
   */
  private formatProcessOutput(process: MessageProcess): string {
    const lastRecord = process.executionHistory[process.executionHistory.length - 1];
    
    if (!lastRecord || !lastRecord.output) {
      return 'Process completed without output.';
    }
    
    // Extract response from cognitive context
    const context = lastRecord.output as CognitiveContext;
    
    let output = '';
    
    // Add response text
    if (context.thoughtData) {
      output += Array.isArray(context.thoughtData)
        ? context.thoughtData.join('\n\n')
        : context.thoughtData;
      output += '\n\n';
    }
    
    // Add cognitive metrics
    output += '---\n';
    output += `Cognitive Metrics:\n`;
    output += `- Emotional Valence: ${context.emotionalValence.toFixed(2)}\n`;
    output += `- Emotional Arousal: ${context.emotionalArousal.toFixed(2)}\n`;
    output += `- Salience Score: ${context.salienceScore.toFixed(2)}\n`;
    output += `- Processing Time: ${lastRecord.duration}ms\n`;
    
    return output;
  }
  
  /**
   * Format process output as HTML
   */
  private formatProcessOutputHtml(process: MessageProcess): string {
    const plainText = this.formatProcessOutput(process);
    
    return `<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; }
    .metrics { background: #f4f4f4; padding: 10px; border-radius: 5px; }
  </style>
</head>
<body>
  <pre>${plainText}</pre>
</body>
</html>`;
  }
  
  /**
   * Build mail headers for process
   */
  private buildHeaders(process: MessageProcess): Map<string, string> {
    const headers = new Map<string, string>();
    
    headers.set('X-Dove9-Process-Id', process.id);
    headers.set('X-Dove9-State', process.state);
    headers.set('X-Dove9-Priority', process.priority.toString());
    headers.set('X-Dove9-Cycle', process.currentStep.toString());
    
    if (process.cognitiveContext) {
      headers.set(
        'X-Dove9-Emotional-Valence',
        process.cognitiveContext.emotionalValence.toFixed(2)
      );
      headers.set(
        'X-Dove9-Salience',
        process.cognitiveContext.salienceScore.toFixed(2)
      );
    }
    
    return headers;
  }
  
  /**
   * Setup kernel event handlers
   */
  private setupKernelEventHandlers(): void {
    this.kernel.on('process_completed', (event: any) => {
      logger.info(`Process ${event.processId} completed`);
      
      if (this.config.enableAutoResponse) {
        const process = this.kernel.getProcess(event.processId);
        if (process) {
          const mailMessage = this.processToMailMessage(process);
          this.kernel.emit('mail_message_ready', mailMessage);
        }
      }
    });
  }
  
  /**
   * Get process ID for mail message
   */
  public getProcessIdForMessage(messageId: string): string | undefined {
    return this.messageToProcessMap.get(messageId);
  }
  
  /**
   * Get message ID for process
   */
  public getMessageIdForProcess(processId: string): string | undefined {
    return this.processToMessageMap.get(processId);
  }
}
```

**Test**: `dove9/src/__tests__/integration/mail-protocol-bridge.test.ts`

```typescript
import { MailProtocolBridge } from '../../integration/mail-protocol-bridge.js';
import { Dove9Kernel } from '../../core/kernel.js';
import { MailMessage } from '../../types/mail.js';
import { ProcessState } from '../../types/index.js';

// Mock processor
const mockProcessor = {
  processT1Perception: jest.fn().mockResolvedValue({}),
  processT2IdeaFormation: jest.fn().mockResolvedValue({}),
  processT4SensoryInput: jest.fn().mockResolvedValue({}),
  processT5ActionSequence: jest.fn().mockResolvedValue({}),
  processT7MemoryEncoding: jest.fn().mockResolvedValue({}),
  processT8BalancedResponse: jest.fn().mockResolvedValue({}),
};

describe('MailProtocolBridge', () => {
  let kernel: Dove9Kernel;
  let bridge: MailProtocolBridge;
  
  beforeEach(() => {
    kernel = new Dove9Kernel(mockProcessor as any);
    bridge = new MailProtocolBridge(kernel);
  });
  
  describe('mailMessageToProcess', () => {
    it('should convert mail message to process', () => {
      const mail: MailMessage = {
        messageId: '<test@example.com>',
        from: 'user@example.com',
        to: ['echo@dove9.local'],
        subject: 'Test Subject',
        body: 'Test body content',
        headers: new Map(),
        timestamp: new Date(),
        receivedAt: new Date(),
        mailbox: 'INBOX',
      };
      
      const process = bridge.mailMessageToProcess(mail);
      
      expect(process.messageId).toBe('<test@example.com>');
      expect(process.from).toBe('user@example.com');
      expect(process.subject).toBe('Test Subject');
      expect(process.content).toBe('Test body content');
      expect(process.state).toBe(ProcessState.PENDING);
    });
    
    it('should extract urgent priority from subject', () => {
      const mail: MailMessage = {
        messageId: '<urgent@example.com>',
        from: 'user@example.com',
        to: ['echo@dove9.local'],
        subject: 'URGENT: Critical issue',
        body: 'This is urgent!',
        headers: new Map(),
        timestamp: new Date(),
        receivedAt: new Date(),
        mailbox: 'INBOX',
      };
      
      const process = bridge.mailMessageToProcess(mail);
      
      expect(process.priority).toBe(9);
    });
    
    it('should extract priority from X-Priority header', () => {
      const mail: MailMessage = {
        messageId: '<priority@example.com>',
        from: 'user@example.com',
        to: ['echo@dove9.local'],
        subject: 'Test',
        body: 'Test',
        headers: new Map([['X-Priority', '1']]),
        timestamp: new Date(),
        receivedAt: new Date(),
        mailbox: 'INBOX',
      };
      
      const process = bridge.mailMessageToProcess(mail);
      
      expect(process.priority).toBe(10);
    });
  });
  
  describe('processToMailMessage', () => {
    it('should convert process to mail message', () => {
      const mail: MailMessage = {
        messageId: '<original@example.com>',
        from: 'user@example.com',
        to: ['echo@dove9.local'],
        subject: 'Original Subject',
        body: 'Original body',
        headers: new Map(),
        timestamp: new Date(),
        receivedAt: new Date(),
        mailbox: 'INBOX',
      };
      
      const process = bridge.mailMessageToProcess(mail);
      process.state = ProcessState.COMPLETED;
      
      const responseMessage = bridge.processToMailMessage(process);
      
      expect(responseMessage.to).toEqual(['user@example.com']);
      expect(responseMessage.subject).toBe('Re: Original Subject');
      expect(responseMessage.inReplyTo).toBe('<original@example.com>');
      expect(responseMessage.mailbox).toBe('Sent');
    });
    
    it('should set correct mailbox based on process state', () => {
      const process = kernel.createProcess(
        'test',
        'user@example.com',
        ['echo@dove9.local'],
        'Test',
        'Test',
        5
      );
      
      process.state = ProcessState.PENDING;
      expect(bridge.processToMailMessage(process).mailbox).toBe('INBOX');
      
      process.state = ProcessState.PROCESSING;
      expect(bridge.processToMailMessage(process).mailbox).toBe('INBOX.Processing');
      
      process.state = ProcessState.COMPLETED;
      expect(bridge.processToMailMessage(process).mailbox).toBe('Sent');
      
      process.state = ProcessState.SUSPENDED;
      expect(bridge.processToMailMessage(process).mailbox).toBe('Drafts');
    });
  });
  
  describe('bidirectional mapping', () => {
    it('should maintain message-process mapping', () => {
      const mail: MailMessage = {
        messageId: '<mapping@example.com>',
        from: 'user@example.com',
        to: ['echo@dove9.local'],
        subject: 'Test',
        body: 'Test',
        headers: new Map(),
        timestamp: new Date(),
        receivedAt: new Date(),
        mailbox: 'INBOX',
      };
      
      const process = bridge.mailMessageToProcess(mail);
      
      expect(bridge.getProcessIdForMessage('<mapping@example.com>')).toBe(process.id);
      expect(bridge.getMessageIdForProcess(process.id)).toBe('<mapping@example.com>');
    });
  });
});
```

### Task 1.3: Add Mail Protocol Support to Dove9 Kernel

**File**: `dove9/src/core/kernel.ts` (MODIFY)

Add these methods to the existing `Dove9Kernel` class:

```typescript
import { MailProtocolBridge } from '../integration/mail-protocol-bridge.js';
import { MailMessage, MailboxMapping } from '../types/mail.js';

export class Dove9Kernel extends EventEmitter {
  // ... existing fields
  private mailBridge?: MailProtocolBridge;
  
  // ... existing methods
  
  /**
   * Enable mail protocol integration
   */
  public enableMailProtocol(mailboxes?: MailboxMapping, botEmail?: string): void {
    this.mailBridge = new MailProtocolBridge(this, {
      mailboxes,
      botEmailAddress: botEmail,
    });
    
    logger.info('Mail protocol enabled');
  }
  
  /**
   * Create process from incoming mail message
   */
  public createProcessFromMail(mail: MailMessage): MessageProcess {
    if (!this.mailBridge) {
      throw new Error('Mail protocol not enabled. Call enableMailProtocol() first.');
    }
    
    return this.mailBridge.mailMessageToProcess(mail);
  }
  
  /**
   * Get mail message for process
   */
  public getMailMessageForProcess(processId: string): MailMessage | null {
    if (!this.mailBridge) return null;
    
    const process = this.getProcess(processId);
    if (!process) return null;
    
    return this.mailBridge.processToMailMessage(process);
  }
  
  /**
   * Get processes by mailbox
   */
  public getProcessesByMailbox(mailbox: string): MessageProcess[] {
    return this.getAllProcesses().filter((process) => {
      if (!this.mailBridge) return false;
      const mail = this.mailBridge.processToMailMessage(process);
      return mail.mailbox === mailbox;
    });
  }
  
  /**
   * Check if mail protocol is enabled
   */
  public isMailProtocolEnabled(): boolean {
    return this.mailBridge !== undefined;
  }
}
```

**Test**: Add to `dove9/src/__tests__/core/kernel.test.ts`

```typescript
describe('Dove9Kernel - Mail Protocol', () => {
  let kernel: Dove9Kernel;
  
  beforeEach(() => {
    kernel = new Dove9Kernel(mockProcessor as any);
  });
  
  it('should enable mail protocol', () => {
    expect(kernel.isMailProtocolEnabled()).toBe(false);
    
    kernel.enableMailProtocol();
    
    expect(kernel.isMailProtocolEnabled()).toBe(true);
  });
  
  it('should create process from mail', () => {
    kernel.enableMailProtocol();
    
    const mail: MailMessage = {
      messageId: '<test@example.com>',
      from: 'user@example.com',
      to: ['echo@dove9.local'],
      subject: 'Test',
      body: 'Test body',
      headers: new Map(),
      timestamp: new Date(),
      receivedAt: new Date(),
      mailbox: 'INBOX',
    };
    
    const process = kernel.createProcessFromMail(mail);
    
    expect(process).toBeDefined();
    expect(process.from).toBe('user@example.com');
  });
  
  it('should throw error if mail protocol not enabled', () => {
    const mail: MailMessage = {
      messageId: '<test@example.com>',
      from: 'user@example.com',
      to: ['echo@dove9.local'],
      subject: 'Test',
      body: 'Test',
      headers: new Map(),
      timestamp: new Date(),
      receivedAt: new Date(),
      mailbox: 'INBOX',
    };
    
    expect(() => kernel.createProcessFromMail(mail)).toThrow(
      'Mail protocol not enabled'
    );
  });
});
```

---

## Phase 1B: Export and Index Updates (Day 4)

### Task 1.4: Update dove9 Exports

**File**: `dove9/src/types/index.ts` (MODIFY)

Add mail types export:

```typescript
// ... existing exports

// Mail protocol types
export * from './mail.js';
```

**File**: `dove9/src/integration/index.ts` (NEW)

```typescript
/**
 * Integration modules for external systems
 */

export * from './mail-protocol-bridge.js';
```

**File**: `dove9/src/index.ts` (MODIFY)

Add integration exports:

```typescript
// ... existing exports

// Integration modules
export * from './integration/index.js';
```

---

## Phase 1C: Integration Testing & Documentation (Day 5)

### Task 1.5: Create End-to-End Integration Test

**File**: `dove9/src/__tests__/e2e/mail-to-process.e2e.test.ts` (NEW)

```typescript
/**
 * End-to-end test: Mail message → Dove9 process → Response mail
 */

import { Dove9Kernel } from '../../core/kernel.js';
import { MailMessage } from '../../types/mail.js';
import { ProcessState } from '../../types/index.js';

describe('E2E: Mail to Process', () => {
  let kernel: Dove9Kernel;
  
  beforeEach(async () => {
    const mockProcessor = {
      processT1Perception: jest.fn().mockResolvedValue({ 
        relevantMemories: [],
        emotionalValence: 0.5,
        emotionalArousal: 0.5,
        salienceScore: 0.7,
        attentionWeight: 1.0,
        activeCouplings: [],
        thoughtData: 'Processed successfully',
      }),
      processT2IdeaFormation: jest.fn().mockResolvedValue({}),
      processT4SensoryInput: jest.fn().mockResolvedValue({}),
      processT5ActionSequence: jest.fn().mockResolvedValue({}),
      processT7MemoryEncoding: jest.fn().mockResolvedValue({}),
      processT8BalancedResponse: jest.fn().mockResolvedValue({}),
    };
    
    kernel = new Dove9Kernel(mockProcessor as any);
    kernel.enableMailProtocol();
    await kernel.start();
  });
  
  afterEach(async () => {
    await kernel.stop();
  });
  
  it('should process mail end-to-end', async () => {
    // 1. Incoming mail
    const incomingMail: MailMessage = {
      messageId: '<user@example.com>',
      from: 'user@example.com',
      to: ['echo@dove9.local'],
      subject: 'Hello Dove9',
      body: 'What can you do?',
      headers: new Map(),
      timestamp: new Date(),
      receivedAt: new Date(),
      mailbox: 'INBOX',
    };
    
    // 2. Create process from mail
    const process = kernel.createProcessFromMail(incomingMail);
    
    expect(process.state).toBe(ProcessState.PENDING);
    expect(process.from).toBe('user@example.com');
    
    // 3. Wait for processing
    const responsePromise = new Promise((resolve) => {
      kernel.once('mail_message_ready', resolve);
    });
    
    // Process should complete automatically
    await new Promise((resolve) => setTimeout(resolve, 200));
    
    // 4. Check response mail
    const responseMail = await responsePromise as MailMessage;
    
    expect(responseMail.to).toEqual(['user@example.com']);
    expect(responseMail.subject).toBe('Re: Hello Dove9');
    expect(responseMail.inReplyTo).toBe('<user@example.com>');
    expect(responseMail.mailbox).toBe('Sent');
  });
  
  it('should handle high-priority mail', async () => {
    const urgentMail: MailMessage = {
      messageId: '<urgent@example.com>',
      from: 'user@example.com',
      to: ['echo@dove9.local'],
      subject: 'URGENT: System failure',
      body: 'Critical issue needs immediate attention',
      headers: new Map([['X-Priority', '1']]),
      timestamp: new Date(),
      receivedAt: new Date(),
      mailbox: 'INBOX',
    };
    
    const process = kernel.createProcessFromMail(urgentMail);
    
    expect(process.priority).toBeGreaterThanOrEqual(9);
  });
});
```

### Task 1.6: Create Documentation

**File**: `dove9/docs/mail-protocol-integration.md` (NEW)

```markdown
# Mail Protocol Integration

## Overview

Dove9 kernel can operate natively on mail protocols, treating email messages as cognitive process threads. This enables the "mail server as CPU" paradigm.

## Quick Start

```typescript
import { Dove9Kernel, MailMessage } from 'dove9';

// Create kernel
const kernel = new Dove9Kernel(processor);

// Enable mail protocol
kernel.enableMailProtocol();

// Start kernel
await kernel.start();

// Process incoming mail
const mail: MailMessage = {
  messageId: '<user@example.com>',
  from: 'user@example.com',
  to: ['echo@dove9.local'],
  subject: 'Hello',
  body: 'How are you?',
  headers: new Map(),
  timestamp: new Date(),
  receivedAt: new Date(),
  mailbox: 'INBOX',
};

const process = kernel.createProcessFromMail(mail);

// Listen for response
kernel.on('mail_message_ready', (responseMail) => {
  console.log('Response:', responseMail.body);
});
```

## Protocol Mapping

| Mail Concept | Dove9 Concept | Description |
|--------------|---------------|-------------|
| Message | Process | Each mail message becomes a cognitive process |
| Mailbox | Process Queue | Different mailboxes represent process states |
| Message-ID | Process ID | Unique identifier for tracking |
| Subject | Process Descriptor | Human-readable summary |
| Body | Process Payload | Input data for processing |
| Headers | Process Metadata | Additional context and routing info |
| Flags | Process State | Process lifecycle indicators |

## Mailbox Structure

- **INBOX**: Pending processes
- **INBOX.Processing**: Active processes
- **Sent**: Completed processes
- **Drafts**: Suspended processes
- **Trash**: Terminated processes
- **Archive**: Historical processes

## Priority Extraction

Priority is extracted from:

1. `X-Priority` header (1-5, lower is higher priority)
2. Keywords in subject:
   - Urgent: "urgent", "asap", "emergency" → Priority 9
   - Important: "important", "priority" → Priority 7
   - Low: "fyi", "when you can" → Priority 3
3. Default: Priority 5

## Response Generation

Response mails include:

- Original message reference (In-Reply-To)
- Subject with "Re:" prefix
- Cognitive processing results
- Metrics (emotional valence, salience, processing time)
- Custom headers (X-Dove9-*)

## Advanced Features

### Custom Mailbox Mapping

```typescript
kernel.enableMailProtocol({
  inbox: 'INBOX',
  processing: 'Work.InProgress',
  sent: 'Work.Completed',
  drafts: 'Work.Drafts',
  trash: 'Deleted',
  archive: 'Archive.2024',
});
```

### Query Processes by Mailbox

```typescript
const activeProcesses = kernel.getProcessesByMailbox('INBOX.Processing');
```

### Manual Response Generation

```typescript
const process = kernel.getProcess(processId);
const responseMail = kernel.getMailMessageForProcess(process.id);

// Send via your mail transport
await smtpClient.send(responseMail);
```

## Integration with Orchestrator

See [Orchestrator Integration Guide](../../deep-tree-echo-orchestrator/docs/dove9-mail-integration.md)
```

---

## Validation & Completion Checklist

### Phase 1 Complete When: ✅ COMPLETE (March 2, 2026)

- [x] All type definitions created and tested
- [x] MailProtocolBridge implemented and tested
- [x] Dove9 Kernel enhanced with mail methods
- [x] All unit tests passing (>80% coverage)
- [x] E2E integration test passing
- [x] Documentation complete
- [x] Exports and index files updated
- [x] Build succeeds without errors
- [x] No ESLint warnings

### Phase 2 Complete When: ✅ COMPLETE (March 3, 2026)

- [x] DovecotIPCTransport implemented
- [x] MembraneMailBridge implemented
- [x] Mailbox ↔ IPC channel mapping
- [x] Real-time subscription system
- [x] Unit tests passing (219 tests)
- [x] Documentation complete

### Phase 3 & 4 Complete: ✅ COMPLETE (March 3, 2026)

- [x] MilterServer (full protocol implementation)
- [x] LMTPServer (local mail delivery)
- [x] EmailProcessor (LLM-powered responses)
- [x] DovecotInterface (unified API)
- [x] Double Membrane integration
- [x] 649 total tests passing

### Run Validation

```bash
cd dove9

# Build
pnpm build

# Test
pnpm test

# Coverage
pnpm test:coverage

# Lint
pnpm lint
```

---

## Status Update (March 3, 2026)

**Phases 1-4 are now complete!**

The following components have been fully implemented and tested:
- `dove9/src/types/mail.ts` - Complete mail type system
- `dove9/src/integration/mail-protocol-bridge.ts` - Mail ↔ process conversion
- `dove9/src/core/kernel.ts` - Mail protocol methods added
- `packages/double-membrane/src/ipc/DovecotIPCTransport.ts` - Mail-based IPC
- `packages/double-membrane/src/ipc/MembraneMailBridge.ts` - Membrane integration
- `deep-tree-echo-orchestrator/src/dovecot-interface/` - Milter, LMTP, Email processor

**Next**: Proceed to Phase 5 (Sys6 Operadic Overlay) and Phase 6 (Production Hardening).

See `DOVE9_DOVECOT_INTEGRATION_STATUS.md` for full details.

---

## Next Steps After Phase 4

**Phase 5**: Sys6 Operadic Overlay (2 weeks)
- Create Sys6Dove9Synchronizer
- Implement 60-step grand cycle (LCM of 12 and 30)
- Apply operadic scheduling to mail processing
- Create visualization tools

**Phase 6**: Production Hardening (2 weeks)
- Security audit
- Performance optimization
- Rate limiting
- Monitoring/telemetry
- Email content sanitization
- Production deployment guide

See `DOVE9_DOVECOT_INTEGRATION_STRATEGY.md` for full roadmap.

---

## Quick Reference Commands

### Create new files:
```bash
# Types
mkdir -p dove9/src/types
touch dove9/src/types/mail.ts

# Integration module
mkdir -p dove9/src/integration
touch dove9/src/integration/mail-protocol-bridge.ts
touch dove9/src/integration/index.ts

# Tests
mkdir -p dove9/src/__tests__/types
mkdir -p dove9/src/__tests__/integration
mkdir -p dove9/src/__tests__/e2e
touch dove9/src/__tests__/types/mail.test.ts
touch dove9/src/__tests__/integration/mail-protocol-bridge.test.ts
touch dove9/src/__tests__/e2e/mail-to-process.e2e.test.ts

# Documentation
mkdir -p dove9/docs
touch dove9/docs/mail-protocol-integration.md
```

### Build and test:
```bash
cd dove9
pnpm build
pnpm test
pnpm test:watch  # For development
```

---

*This roadmap provides concrete, actionable tasks to begin implementation immediately. Each phase builds on the previous, ensuring stable progress toward the complete vision.*
