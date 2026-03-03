/**
 * Dove9 Integration for Deep Tree Echo Orchestrator
 *
 * Integrates the Dove9 cognitive OS into the orchestrator,
 * using the full triadic cognitive loop architecture from the dove9 package.
 *
 * This module:
 * - Creates a Dove9System instance using the actual dove9 package
 * - Bridges Dovecot emails to Dove9 processes via MailProtocolBridge
 * - Routes Dove9 responses back through DeltaChat
 * - Provides metrics and monitoring
 * - Supports mail protocol for native mail-as-IPC operations
 */

import {
  getLogger,
  LLMService,
  RAGMemoryStore,
  PersonaCore,
  InMemoryStorage,
} from 'deep-tree-echo-core';
import {
  Dove9System,
  createDove9System,
  Dove9Kernel,
  KernelMetrics,
  MessageProcess,
  MailMessage,
  MailboxMapping,
  DEFAULT_MAILBOX_MAPPING,
} from 'dove9';
import { EmailMessage } from './dovecot-interface/milter-server.js';
import { EventEmitter } from 'events';

const log = getLogger('deep-tree-echo-orchestrator/Dove9Integration');

/**
 * Adapter to make LLMService compatible with Dove9's LLMServiceInterface
 */
class LLMServiceAdapter {
  private llmService: LLMService;

  constructor(llmService: LLMService) {
    this.llmService = llmService;
  }

  async generateResponse(prompt: string, context: string[]): Promise<string> {
    const result = await this.llmService.generateFullParallelResponse(
      `${prompt}\n\nContext:\n${context.join('\n')}`,
      context
    );
    return result.integratedResponse;
  }

  async generateParallelResponse(
    prompt: string,
    history: string[]
  ): Promise<{
    integratedResponse: string;
    cognitiveResponse?: string;
    affectiveResponse?: string;
    relevanceResponse?: string;
  }> {
    return this.llmService.generateFullParallelResponse(prompt, history);
  }
}

/**
 * Adapter to make RAGMemoryStore compatible with Dove9's interface
 */
class MemoryStoreAdapter {
  private memoryStore: RAGMemoryStore;

  constructor(memoryStore: RAGMemoryStore) {
    this.memoryStore = memoryStore;
  }

  async storeMemory(memory: {
    chatId: number;
    messageId: number;
    sender: string;
    text: string;
  }): Promise<void> {
    await this.memoryStore.storeMemory({
      ...memory,
      sender: memory.sender as 'user' | 'bot',
    });
  }

  retrieveRecentMemories(count: number): string[] {
    return this.memoryStore.retrieveRecentMemories(count);
  }

  async retrieveRelevantMemories(query: string, count: number): Promise<string[]> {
    return this.memoryStore.retrieveRecentMemories(count);
  }
}

/**
 * Adapter to make PersonaCore compatible with Dove9's interface
 */
class PersonaCoreAdapter {
  private personaCore: PersonaCore;

  constructor(personaCore: PersonaCore) {
    this.personaCore = personaCore;
  }

  getPersonality(): string {
    return this.personaCore.getPersonality();
  }

  getDominantEmotion(): { emotion: string; intensity: number } {
    return this.personaCore.getDominantEmotion();
  }

  async updateEmotionalState(stimuli: Record<string, number>): Promise<void> {
    await this.personaCore.updateEmotionalState(stimuli);
  }
}

/**
 * Configuration for Dove9 integration
 */
export interface Dove9IntegrationConfig {
  enabled: boolean;
  stepDuration: number;
  maxConcurrentProcesses: number;
  botEmailAddress: string;
  enableTriadicLoop: boolean;
  /** Enable mail protocol for native mail-as-IPC operations */
  enableMailProtocol: boolean;
  /** Custom mailbox mapping for mail protocol */
  mailboxMapping?: Partial<MailboxMapping>;
}

const DEFAULT_CONFIG: Dove9IntegrationConfig = {
  enabled: true,
  stepDuration: 100,
  maxConcurrentProcesses: 50,
  botEmailAddress: 'echo@localhost',
  enableTriadicLoop: true,
  enableMailProtocol: true,
};

/**
 * Response event data
 */
export interface Dove9Response {
  to: string;
  from: string;
  subject: string;
  body: string;
  inReplyTo?: string;
  processId: string;
  cognitiveMetrics: {
    emotionalValence: number;
    emotionalArousal: number;
    salienceScore: number;
    activeCouplings: string[];
  };
}

/**
 * Dove9Integration
 *
 * Manages the Dove9 cognitive OS within the orchestrator.
 * Uses the actual Dove9System from the dove9 package with full mail protocol support.
 */
export class Dove9Integration {
  private config: Dove9IntegrationConfig;
  private dove9: Dove9System | null = null;
  private storage = new InMemoryStorage();
  private llmService: LLMService;
  private memoryStore: RAGMemoryStore;
  private personaCore: PersonaCore;
  private running: boolean = false;

  // Event handlers
  private responseHandlers: ((response: Dove9Response) => void)[] = [];
  private metricsHandlers: ((metrics: KernelMetrics) => void)[] = [];

  constructor(config: Partial<Dove9IntegrationConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };

    // Initialize cognitive services
    this.memoryStore = new RAGMemoryStore(this.storage);
    this.memoryStore.setEnabled(true);
    this.personaCore = new PersonaCore(this.storage);
    this.llmService = new LLMService();
  }

  /**
   * Initialize Dove9 system
   */
  public async initialize(): Promise<void> {
    if (!this.config.enabled) {
      log.info('Dove9 integration disabled');
      return;
    }

    log.info('Initializing Dove9 cognitive OS...');

    // Create adapters for the Dove9 system
    const llmAdapter = new LLMServiceAdapter(this.llmService);
    const memoryAdapter = new MemoryStoreAdapter(this.memoryStore);
    const personaAdapter = new PersonaCoreAdapter(this.personaCore);

    // Create the actual Dove9System from the dove9 package
    this.dove9 = createDove9System(llmAdapter, memoryAdapter, personaAdapter, {
      stepDuration: this.config.stepDuration,
      maxConcurrentProcesses: this.config.maxConcurrentProcesses,
      enableParallelCognition: this.config.enableTriadicLoop,
    });

    // Enable mail protocol if configured
    if (this.config.enableMailProtocol) {
      const kernel = this.dove9.getKernel();
      kernel.enableMailProtocol(this.config.mailboxMapping || {});
      log.info('Mail protocol enabled on Dove9 kernel');

      // Listen for mail_message_ready events to send responses
      kernel.on('mail_message_ready', (mailResponse: MailMessage) => {
        this.handleMailMessageReady(mailResponse);
      });
    }

    // Set up event handlers
    this.setupEventHandlers();

    log.info('Dove9 cognitive OS initialized');
  }

  /**
   * Handle mail message ready event from kernel
   */
  private handleMailMessageReady(mailResponse: MailMessage): void {
    log.debug('Mail message ready for sending', { 
      messageId: mailResponse.messageId,
      to: mailResponse.to,
      subject: mailResponse.subject 
    });

    // Convert to Dove9Response format
    const response: Dove9Response = {
      to: mailResponse.to[0],
      from: mailResponse.from,
      subject: mailResponse.subject,
      body: mailResponse.body,
      inReplyTo: mailResponse.inReplyTo,
      processId: mailResponse.headers?.get('X-Dove9-Process-Id') || 'unknown',
      cognitiveMetrics: {
        emotionalValence: 0,
        emotionalArousal: 0.5,
        salienceScore: 0.5,
        activeCouplings: [],
      },
    };

    // Notify handlers
    for (const handler of this.responseHandlers) {
      handler(response);
    }
  }

  /**
   * Set up Dove9 event handlers
   */
  private setupEventHandlers(): void {
    if (!this.dove9) return;

    // Handle response ready from the Dove9System
    this.dove9.on(
      'response_ready',
      (data: {
        processId: string;
        originalMail: MailMessage;
        response: { subject: string; body: string };
        cognitiveResult?: {
          emotionalValence?: number;
          emotionalArousal?: number;
          salienceScore?: number;
          activeCouplings?: string[];
        };
      }) => {
        const response: Dove9Response = {
          to: data.originalMail.from,
          from: this.config.botEmailAddress,
          subject: data.response.subject,
          body: data.response.body,
          inReplyTo: data.originalMail.messageId,
          processId: data.processId,
          cognitiveMetrics: {
            emotionalValence: data.cognitiveResult?.emotionalValence || 0,
            emotionalArousal: data.cognitiveResult?.emotionalArousal || 0.5,
            salienceScore: data.cognitiveResult?.salienceScore || 0.5,
            activeCouplings: data.cognitiveResult?.activeCouplings || [],
          },
        };

        // Notify handlers
        for (const handler of this.responseHandlers) {
          handler(response);
        }
      }
    );

    // Handle cycle completion
    this.dove9.on('cycle_complete', (data: { cycle: number; metrics: KernelMetrics }) => {
      log.debug(`Dove9 cycle ${data.cycle} complete`);

      // Notify metrics handlers
      for (const handler of this.metricsHandlers) {
        handler(data.metrics);
      }
    });

    // Handle triadic sync
    this.dove9.on('triad_sync', (triad: { timePoint: number }) => {
      log.debug(`Triadic convergence at time point ${triad.timePoint}`);
    });

    // Handle kernel events
    this.dove9.on('kernel_event', (event: any) => {
      log.debug('Kernel event', { type: event.type });
    });
  }

  /**
   * Start Dove9 integration
   */
  public async start(): Promise<void> {
    if (!this.dove9) {
      await this.initialize();
    }

    if (!this.dove9 || this.running) return;

    await this.dove9.start();
    this.running = true;

    log.info('Dove9 cognitive OS started');
  }

  /**
   * Stop Dove9 integration
   */
  public async stop(): Promise<void> {
    if (!this.dove9 || !this.running) return;

    await this.dove9.stop();
    this.running = false;

    log.info('Dove9 cognitive OS stopped');
  }

  /**
   * Process an email through Dove9
   */
  public async processEmail(email: EmailMessage): Promise<MessageProcess | null> {
    if (!this.dove9) {
      log.warn('Dove9 not initialized, cannot process email');
      return null;
    }

    // Check if email is for the bot
    const isForBot = email.to.some(
      (addr) => addr.toLowerCase() === this.config.botEmailAddress.toLowerCase()
    );

    if (!isForBot) {
      return null;
    }

    log.info(`Processing email from ${email.from} through Dove9`);

    // Convert EmailMessage to dove9 MailMessage format
    const mailMessage: MailMessage = {
      messageId: email.messageId || `<${Date.now()}@dove9.local>`,
      from: email.from,
      to: email.to,
      subject: email.subject,
      body: email.body,
      headers: email.headers,
      timestamp: email.receivedAt,
      receivedAt: email.receivedAt,
      mailbox: 'INBOX',
    };

    // Process through Dove9 using the mail protocol bridge
    const kernel = this.dove9.getKernel();
    if (this.config.enableMailProtocol && kernel.isMailProtocolEnabled()) {
      // Use native mail protocol processing
      return kernel.createProcessFromMail(mailMessage);
    } else {
      // Fallback to standard processing
      return this.dove9.processMailMessage(mailMessage);
    }
  }

  /**
   * Register response handler
   */
  public onResponse(handler: (response: Dove9Response) => void): void {
    this.responseHandlers.push(handler);
  }

  /**
   * Register metrics handler
   */
  public onMetrics(handler: (metrics: KernelMetrics) => void): void {
    this.metricsHandlers.push(handler);
  }

  /**
   * Configure LLM API keys
   */
  public configureApiKeys(keys: Record<string, string>): void {
    if (keys.general) {
      this.llmService.setConfig({ apiKey: keys.general });
    }
    log.info('API keys configured for Dove9');
  }

  /**
   * Get current metrics
   */
  public getMetrics(): KernelMetrics | null {
    return this.dove9?.getMetrics() || null;
  }

  /**
   * Get active processes
   */
  public getActiveProcesses(): MessageProcess[] {
    return this.dove9?.getActiveProcesses() || [];
  }

  /**
   * Check if running
   */
  public isRunning(): boolean {
    return this.running;
  }

  /**
   * Get the Dove9 system
   */
  public getDove9System(): Dove9System | null {
    return this.dove9;
  }

  /**
   * Get the Dove9 kernel for advanced operations
   */
  public getKernel(): Dove9Kernel | null {
    return this.dove9?.getKernel() || null;
  }

  /**
   * Get cognitive state summary
   */
  public getCognitiveState(): {
    running: boolean;
    metrics: KernelMetrics | null;
    activeProcessCount: number;
    mailProtocolEnabled: boolean;
    triadic: {
      currentStep: number;
      cycleNumber: number;
      streamCount: number;
    } | null;
  } {
    const metrics = this.getMetrics();
    const state = this.dove9?.getState();
    const kernel = this.dove9?.getKernel();

    return {
      running: this.running,
      metrics,
      activeProcessCount: this.getActiveProcesses().length,
      mailProtocolEnabled: kernel?.isMailProtocolEnabled() || false,
      triadic: state
        ? {
            currentStep: state.currentStep,
            cycleNumber: state.cycleNumber,
            streamCount: state.streams?.size || 3,
          }
        : null,
    };
  }
}
