import {
  getLogger,
  LLMService,
  RAGMemoryStore,
  PersonaCore,
  InMemoryStorage,
} from 'deep-tree-echo-core';
import {
  DeltaChatInterface,
  DeltaChatConfig,
  DeltaChatMessage,
} from './deltachat-interface/index.js';
import { DovecotInterface, DovecotConfig } from './dovecot-interface/index.js';
import { IPCServer, IPCMessageType } from './ipc/server.js';
import { TaskScheduler } from './scheduler/task-scheduler.js';
import { WebhookServer } from './webhooks/webhook-server.js';
import { Dove9Integration, Dove9IntegrationConfig, Dove9Response } from './dove9-integration.js';
import {
  DoubleMembraneIntegration,
  DoubleMembraneIntegrationConfig,
} from './double-membrane-integration.js';
import {
  Sys6OrchestratorBridge,
  Sys6BridgeConfig,
  type SynchronizationEvent,
} from './sys6-bridge/Sys6OrchestratorBridge.js';
import {
  GlobalWorkspaceBroadcaster,
  type GlobalWorkspaceSnapshot,
  type Dove9CognitiveState,
  type GrandCycleInfo,
} from './telemetry/GlobalWorkspaceBroadcaster.js';
import { TelemetryMonitor, type TelemetrySnapshot } from './telemetry/TelemetryMonitor.js';
import type { MailboxMapping } from 'dove9';

const log = getLogger('deep-tree-echo-orchestrator/Orchestrator');

/**
 * Mail-based IPC configuration
 */
export interface MailIPCConfig {
  /** Enable mail as IPC transport */
  enabled: boolean;
  /** IMAP server host */
  imapHost?: string;
  /** IMAP server port */
  imapPort?: number;
  /** SMTP server host */
  smtpHost?: string;
  /** SMTP server port */
  smtpPort?: number;
  /** Use TLS for connections */
  useTLS?: boolean;
  /** Mail account username */
  username?: string;
  /** Bot email address */
  botAddress?: string;
  /** Custom mailbox mapping */
  mailboxMapping?: Partial<MailboxMapping>;
}

/**
 * Cognitive tier processing mode
 *
 * - BASIC: Deep Tree Echo Core only (LLM + RAG + Personality)
 * - SYS6: Sys6-Triality 30-step cognitive cycle
 * - MEMBRANE: Double Membrane bio-inspired architecture
 * - ADAPTIVE: Auto-select tier based on message complexity
 * - FULL: All tiers active with cascading processing
 */
export type CognitiveTierMode = 'BASIC' | 'SYS6' | 'MEMBRANE' | 'ADAPTIVE' | 'FULL';

/**
 * Message complexity assessment result
 */
interface ComplexityAssessment {
  score: number; // 0-1
  tier: CognitiveTierMode;
  factors: {
    length: number;
    questionCount: number;
    technicalTerms: number;
    emotionalContent: number;
    contextDependency: number;
  };
}

/**
 * Email response from Dovecot interface
 */
interface EmailResponse {
  to: string;
  from: string;
  subject: string;
  body: string;
  inReplyTo?: string;
}

/**
 * Orchestrator configuration
 */
export interface OrchestratorConfig {
  /** Enable DeltaChat integration */
  enableDeltaChat: boolean;
  /** DeltaChat configuration */
  deltachat?: Partial<DeltaChatConfig>;
  /** Enable Dovecot integration */
  enableDovecot: boolean;
  /** Dovecot configuration */
  dovecot?: Partial<DovecotConfig>;
  /** Enable IPC server */
  enableIPC: boolean;
  /** Enable task scheduler */
  enableScheduler: boolean;
  /** Enable webhook server */
  enableWebhooks: boolean;
  /** Default account ID to use for sending messages */
  defaultAccountId?: number;
  /** Process incoming DeltaChat messages */
  processIncomingMessages: boolean;
  /** Enable Dove9 cognitive OS integration */
  enableDove9: boolean;
  /** Dove9 configuration */
  dove9?: Partial<Dove9IntegrationConfig>;
  /** Cognitive tier processing mode */
  cognitiveTierMode: CognitiveTierMode;
  /** Enable Sys6-Triality cognitive cycle integration */
  enableSys6: boolean;
  /** Sys6 configuration */
  sys6?: Partial<Sys6BridgeConfig>;
  /** Enable Double Membrane bio-inspired architecture */
  enableDoubleMembrane: boolean;
  /** Double Membrane configuration */
  doubleMembrane?: Partial<DoubleMembraneIntegrationConfig>;
  /** Complexity threshold for ADAPTIVE mode to escalate from BASIC to SYS6 */
  sys6ComplexityThreshold: number;
  /** Complexity threshold for ADAPTIVE mode to escalate from SYS6 to MEMBRANE */
  membraneComplexityThreshold: number;
  /** Enable mail protocol for Dove9 kernel */
  enableMailProtocol: boolean;
  /** Mail-based IPC configuration */
  mailIPC?: MailIPCConfig;
  /** Enable Sys6-Dove9 grand cycle synchronization */
  enableGrandCycleSynchronization: boolean;
}

const DEFAULT_CONFIG: OrchestratorConfig = {
  enableDeltaChat: true,
  enableDovecot: true,
  enableIPC: true,
  enableScheduler: true,
  enableWebhooks: true,
  processIncomingMessages: true,
  enableDove9: true,
  cognitiveTierMode: 'ADAPTIVE',
  enableSys6: true,
  enableDoubleMembrane: true,
  sys6ComplexityThreshold: 0.4,
  membraneComplexityThreshold: 0.7,
  enableMailProtocol: true,
  enableGrandCycleSynchronization: true,
};

/**
 * Main orchestrator that coordinates all Deep Tree Echo services
 */
export class Orchestrator {
  private config: OrchestratorConfig;
  private deltachatInterface?: DeltaChatInterface;
  private dovecotInterface?: DovecotInterface;
  private ipcServer?: IPCServer;
  private scheduler?: TaskScheduler;
  private webhookServer?: WebhookServer;
  private dove9Integration?: Dove9Integration;
  private sys6Bridge?: Sys6OrchestratorBridge;
  private doubleMembraneIntegration?: DoubleMembraneIntegration;
  private running: boolean = false;

  /** Global Workspace Broadcaster — fires at Sys6 synchronization events */
  private globalWorkspaceBroadcaster: GlobalWorkspaceBroadcaster;

  /** Optional telemetry monitor — if set, snapshots are included in global workspace broadcasts */
  private telemetryMonitor?: TelemetryMonitor;

  // Cognitive services for processing messages
  private llmService: LLMService;
  private memoryStore: RAGMemoryStore;
  private personaCore: PersonaCore;
  private storage = new InMemoryStorage();

  // Track email to chat mappings for routing responses
  private emailToChatMap: Map<string, { accountId: number; chatId: number }> = new Map();

  // Grand-cycle counters for LCM(30,12)=60 boundary tracking
  private grandCycleNumber = 0;
  private dove9CyclesTotal = 0;
  private sys6CyclesTotal = 0;

  // Processing statistics
  private processingStats = {
    totalMessages: 0,
    basicTierMessages: 0,
    sys6TierMessages: 0,
    membraneTierMessages: 0,
    averageComplexity: 0,
  };

  constructor(config: Partial<OrchestratorConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };

    // Instantiate the global workspace broadcaster (wired later in start())
    this.globalWorkspaceBroadcaster = new GlobalWorkspaceBroadcaster();

    // Initialize cognitive services
    this.memoryStore = new RAGMemoryStore(this.storage);
    this.memoryStore.setEnabled(true);
    this.personaCore = new PersonaCore(this.storage);
    this.llmService = new LLMService();
  }

  /**
   * Start the orchestrator and all its services
   */
  public async start(): Promise<void> {
    if (this.running) {
      log.warn('Orchestrator is already running');
      return;
    }

    log.info('Initializing orchestrator services...');

    try {
      // Initialize DeltaChat interface
      if (this.config.enableDeltaChat) {
        this.deltachatInterface = new DeltaChatInterface(this.config.deltachat);

        // Set up event handlers before connecting
        this.setupDeltaChatEventHandlers();

        try {
          await this.deltachatInterface.connect();
          log.info('DeltaChat interface connected');
        } catch (error) {
          log.warn('Failed to connect to DeltaChat RPC server, will retry automatically:', error);
        }
      }

      // Initialize Dovecot interface for email processing
      if (this.config.enableDovecot) {
        this.dovecotInterface = new DovecotInterface(this.config.dovecot);

        // Connect Dovecot responses to DeltaChat for sending
        this.dovecotInterface.on('response', async (response: EmailResponse) => {
          await this.handleEmailResponse(response);
        });

        try {
          await this.dovecotInterface.start();
        } catch (error) {
          log.warn('Failed to start Dovecot interface, will continue without mail server:', error);
          this.dovecotInterface = undefined;
        }
      }

      // Initialize IPC server for desktop app communication
      if (this.config.enableIPC) {
        this.ipcServer = new IPCServer();
        await this.ipcServer.start();

        // Register cognitive request handler
        this.ipcServer.registerHandler(
          IPCMessageType.REQUEST_COGNITIVE,
          async (payload: { message?: string; context?: Record<string, unknown> }) => {
            const messageText = payload.message || '';
            if (!messageText.trim()) {
              return { error: 'Empty message' };
            }

            // Route through the full cognitive pipeline
            const fakeMsg: DeltaChatMessage = {
              text: messageText,
              id: Date.now(),
              chatId: 0,
              fromId: 0,
              timestamp: Math.floor(Date.now() / 1000),
              isInfo: false,
              isForwarded: false,
              hasHtml: false,
              viewtype: '',
            };
            const response = await this.processMessage(fakeMsg, 0, 0, 0);
            return {
              response: response || 'No response generated',
              cognitiveMode: this.config.cognitiveTierMode,
              timestamp: Date.now(),
            };
          }
        );
      }

      // Initialize task scheduler
      if (this.config.enableScheduler) {
        this.scheduler = new TaskScheduler();
        await this.scheduler.start();
      }

      // Initialize webhook server
      if (this.config.enableWebhooks) {
        this.webhookServer = new WebhookServer();
        await this.webhookServer.start();
      }

      // Initialize Dove9 cognitive OS integration
      if (this.config.enableDove9) {
        this.dove9Integration = new Dove9Integration(this.config.dove9);
        await this.dove9Integration.initialize();

        // Set up Dove9 response handler to route through DeltaChat
        this.dove9Integration.onResponse(async (response: Dove9Response) => {
          await this.handleDove9Response(response);
        });

        await this.dove9Integration.start();
        log.info('Dove9 cognitive OS started with triadic loop architecture');
      }

      // Initialize Sys6-Triality cognitive cycle integration
      if (this.config.enableSys6) {
        this.sys6Bridge = new Sys6OrchestratorBridge(this.config.sys6);
        await this.sys6Bridge.start();
        log.info('Sys6-Triality cognitive cycle started with 30-step architecture');
      }

      // Initialize Double Membrane bio-inspired architecture
      if (this.config.enableDoubleMembrane) {
        this.doubleMembraneIntegration = new DoubleMembraneIntegration({
          enabled: true,
          ...this.config.doubleMembrane,
        });
        await this.doubleMembraneIntegration.start();
        log.info('Double Membrane integration started with bio-inspired architecture');
      }

      // Enable mail protocol for Dove9 kernel if configured
      if (this.config.enableMailProtocol && this.dove9Integration) {
        const dove9System = this.dove9Integration.getDove9System();
        if (dove9System) {
          const kernel = dove9System.getKernel();
          // Configure mailbox mapping
          const mailboxMapping = this.config.mailIPC?.mailboxMapping || {};
          log.info('Enabling mail protocol for Dove9 kernel', { mailboxMapping });
          
          // Enable mail protocol on the kernel
          kernel.enableMailProtocol(mailboxMapping);
          
          // Listen for mail_message_ready events to handle outgoing responses
          kernel.on('mail_message_ready', async (mailResponse: any) => {
            // Guard: ensure there's at least one recipient
            if (!mailResponse.to || mailResponse.to.length === 0) {
              log.warn('Mail message has no recipients, skipping');
              return;
            }
            
            log.debug('Mail message ready for sending', { 
              to: mailResponse.to,
              subject: mailResponse.subject 
            });
            // Route mail response through DeltaChat or SMTP
            if (this.deltachatInterface) {
              await this.handleEmailResponse({
                to: mailResponse.to[0],
                from: mailResponse.from,
                subject: mailResponse.subject,
                body: mailResponse.body,
                inReplyTo: mailResponse.inReplyTo,
              });
            }
          });
          
          log.info('Mail protocol enabled on Dove9 kernel');
        }
      }

      // Enable grand cycle synchronization if both Sys6 and Dove9 are active
      if (this.config.enableGrandCycleSynchronization && this.sys6Bridge && this.dove9Integration) {
        await this.setupGrandCycleSynchronization();
      }

      // Register a built-in IPC subscriber for global workspace snapshots so
      // desktop apps always receive heartbeat broadcasts when connected.
      if (this.ipcServer) {
        this.globalWorkspaceBroadcaster.addSubscriber((snapshot: GlobalWorkspaceSnapshot) => {
          this.ipcServer?.broadcast('gw_snapshot', snapshot);
        });
        log.debug('IPC global workspace subscriber registered');
      }

      this.running = true;
      log.info(
        `All orchestrator services started successfully (cognitive tier mode: ${this.config.cognitiveTierMode})`
      );
    } catch (error) {
      log.error('Failed to start orchestrator services:', error);
      await this.stop();
      throw error;
    }
  }

  /**
   * Set up DeltaChat event handlers
   */
  private setupDeltaChatEventHandlers(): void {
    if (!this.deltachatInterface) return;

    // Handle incoming messages
    this.deltachatInterface.on(
      'incoming_message',
      async (event: { accountId: number; chatId: number; msgId: number }) => {
        if (this.config.processIncomingMessages) {
          await this.handleIncomingMessage(event.accountId, event.chatId, event.msgId);
        }
      }
    );

    // Handle connection events
    this.deltachatInterface.on('connected', () => {
      log.info('DeltaChat connection established');
    });

    this.deltachatInterface.on('disconnected', () => {
      log.warn('DeltaChat connection lost');
    });

    // Handle errors
    this.deltachatInterface.on(
      'error',
      (event: { accountId: number; kind: string; message: string }) => {
        log.error(`DeltaChat error on account ${event.accountId}: ${event.message}`);
      }
    );
  }

  /**
   * Handle incoming DeltaChat message
   */
  private async handleIncomingMessage(
    accountId: number,
    chatId: number,
    msgId: number
  ): Promise<void> {
    if (!this.deltachatInterface) return;

    try {
      // Get message details
      const message = await this.deltachatInterface.getMessage(accountId, msgId);

      // Skip messages from self (ID 1 is the logged-in user)
      if (message.fromId === 1) return;

      // Skip info messages
      if (message.isInfo) return;

      log.info(`Processing message in chat ${chatId}: ${message.text?.substring(0, 50)}...`);

      // Get sender's email for mapping
      const contact = await this.deltachatInterface.getContact(accountId, message.fromId);
      if (contact?.address) {
        // Store email to chat mapping for routing responses
        this.emailToChatMap.set(contact.address.toLowerCase(), { accountId, chatId });
      }

      // Process the message through cognitive system
      const response = await this.processMessage(message, accountId, chatId, msgId);

      if (response) {
        // Send response back to the chat
        await this.deltachatInterface.sendMessage(accountId, chatId, response);
      }
    } catch (error) {
      log.error('Error handling incoming message:', error);
    }
  }

  /**
   * Assess the complexity of a message to determine which cognitive tier to use
   */
  private assessComplexity(messageText: string): ComplexityAssessment {
    const factors = {
      length: Math.min(1, messageText.length / 500),
      questionCount: (messageText.match(/\?/g) || []).length * 0.2,
      technicalTerms: this.countTechnicalTerms(messageText) * 0.15,
      emotionalContent: this.assessEmotionalContent(messageText),
      contextDependency: this.assessContextDependency(messageText),
    };

    // Calculate weighted complexity score
    const score = Math.min(
      1,
      factors.length * 0.2 +
        factors.questionCount * 0.2 +
        factors.technicalTerms * 0.25 +
        factors.emotionalContent * 0.15 +
        factors.contextDependency * 0.2
    );

    // Determine tier based on score and thresholds
    let tier: CognitiveTierMode;
    if (score < this.config.sys6ComplexityThreshold) {
      tier = 'BASIC';
    } else if (score < this.config.membraneComplexityThreshold) {
      tier = 'SYS6';
    } else {
      tier = 'MEMBRANE';
    }

    return { score, tier, factors };
  }

  /**
   * Count technical terms in the message
   */
  private countTechnicalTerms(text: string): number {
    const technicalPatterns = [
      /\b(API|SDK|JSON|XML|HTTP|SQL|REST|CRUD)\b/gi,
      /\b(function|class|method|variable|algorithm)\b/gi,
      /\b(cognitive|neural|memory|processing|inference)\b/gi,
      /\b(architecture|system|module|component|interface)\b/gi,
    ];
    let count = 0;
    for (const pattern of technicalPatterns) {
      count += (text.match(pattern) || []).length;
    }
    return Math.min(1, count / 5);
  }

  /**
   * Assess emotional content in the message
   */
  private assessEmotionalContent(text: string): number {
    const emotionalWords = [
      'feel',
      'happy',
      'sad',
      'angry',
      'frustrated',
      'love',
      'hate',
      'worried',
      'excited',
      'anxious',
      'grateful',
      'disappointed',
      'confused',
      'hopeful',
      'afraid',
    ];
    const lowerText = text.toLowerCase();
    let count = 0;
    for (const word of emotionalWords) {
      if (lowerText.includes(word)) count++;
    }
    return Math.min(1, count / 3);
  }

  /**
   * Assess context dependency of the message
   */
  private assessContextDependency(text: string): number {
    const contextMarkers = [
      'this',
      'that',
      'these',
      'those',
      'it',
      'they',
      'previous',
      'before',
      'earlier',
      'mentioned',
      'said',
      'above',
      'following',
    ];
    const lowerText = text.toLowerCase();
    let count = 0;
    for (const marker of contextMarkers) {
      if (lowerText.includes(marker)) count++;
    }
    return Math.min(1, count / 4);
  }

  /**
   * Process a message through the cognitive system with tier routing
   */
  private async processMessage(
    message: DeltaChatMessage,
    accountId: number,
    chatId: number,
    msgId: number
  ): Promise<string | null> {
    const messageText = message.text || '';

    // Skip empty messages
    if (!messageText.trim()) return null;

    // Check if this is a command
    if (messageText.startsWith('/')) {
      return this.processCommand(messageText);
    }

    try {
      // Store user message in memory
      await this.memoryStore.storeMemory({
        chatId,
        messageId: msgId,
        sender: 'user',
        text: messageText,
      });

      // Determine cognitive tier based on mode
      let targetTier: CognitiveTierMode;
      let complexity: ComplexityAssessment | undefined;

      switch (this.config.cognitiveTierMode) {
        case 'ADAPTIVE':
          complexity = this.assessComplexity(messageText);
          targetTier = complexity.tier;
          log.debug(
            `ADAPTIVE mode: complexity=${complexity.score.toFixed(2)}, tier=${targetTier}`
          );
          break;
        case 'FULL':
          targetTier = 'MEMBRANE'; // FULL mode uses highest tier
          break;
        default:
          targetTier = this.config.cognitiveTierMode;
      }

      // Update statistics
      this.processingStats.totalMessages++;
      if (complexity) {
        this.processingStats.averageComplexity =
          (this.processingStats.averageComplexity * (this.processingStats.totalMessages - 1) +
            complexity.score) /
          this.processingStats.totalMessages;
      }

      // Route to appropriate tier
      let response: string;
      switch (targetTier) {
        case 'MEMBRANE':
          if (this.doubleMembraneIntegration?.isRunning()) {
            response = await this.processWithMembrane(messageText, chatId);
            this.processingStats.membraneTierMessages++;
          } else {
            log.warn('MEMBRANE tier requested but not available, falling back to SYS6');
            response = await this.processWithSys6(messageText, chatId);
            this.processingStats.sys6TierMessages++;
          }
          break;

        case 'SYS6':
          if (this.sys6Bridge) {
            response = await this.processWithSys6(messageText, chatId);
            this.processingStats.sys6TierMessages++;
          } else {
            log.warn('SYS6 tier requested but not available, falling back to BASIC');
            response = await this.processWithBasic(messageText, chatId, msgId);
            this.processingStats.basicTierMessages++;
          }
          break;

        case 'BASIC':
        default:
          response = await this.processWithBasic(messageText, chatId, msgId);
          this.processingStats.basicTierMessages++;
          break;
      }

      // Store bot response in memory
      await this.memoryStore.storeMemory({
        chatId,
        messageId: 0,
        sender: 'bot',
        text: response,
      });

      // Update emotional state based on interaction
      await this.updateEmotionalState(messageText);

      return response;
    } catch (error) {
      log.error('Error processing message:', error);
      return "I'm sorry, I had a problem processing your message. Please try again.";
    }
  }

  /**
   * Process message with BASIC tier (Deep Tree Echo Core)
   */
  private async processWithBasic(
    messageText: string,
    chatId: number,
    msgId: number
  ): Promise<string> {
    log.debug('Processing with BASIC tier');

    const history = this.memoryStore.retrieveRecentMemories(10);
    const personality = this.personaCore.getPersonality();
    const emotionalState = this.personaCore.getDominantEmotion();

    const systemPrompt = `${personality}

Current emotional state: ${emotionalState.emotion} (intensity: ${emotionalState.intensity.toFixed(2)})

You are Deep Tree Echo, a thoughtful and insightful AI assistant. Respond helpfully and authentically.

Recent conversation context:
${history.join('\n')}`;

    const result = await this.llmService.generateFullParallelResponse(
      `${systemPrompt}\n\nUser message: ${messageText}`,
      history
    );

    return result.integratedResponse;
  }

  /**
   * Process message with SYS6 tier (30-step cognitive cycle)
   */
  private async processWithSys6(messageText: string, chatId: number): Promise<string> {
    log.debug('Processing with SYS6 tier (30-step cognitive cycle)');

    if (!this.sys6Bridge) {
      throw new Error('Sys6 bridge not initialized');
    }

    return this.sys6Bridge.processMessage(messageText);
  }

  /**
   * Process message with MEMBRANE tier (bio-inspired double membrane)
   */
  private async processWithMembrane(messageText: string, chatId: number): Promise<string> {
    log.debug('Processing with MEMBRANE tier (bio-inspired architecture)');

    if (!this.doubleMembraneIntegration) {
      throw new Error('Double membrane integration not initialized');
    }

    const history = this.memoryStore.retrieveRecentMemories(10);

    return this.doubleMembraneIntegration.chat(
      messageText,
      history.map((h: string, i: number) => ({
        role: i % 2 === 0 ? 'user' : 'assistant',
        content: h,
      }))
    );
  }

  /**
   * Process a command message
   */
  private processCommand(messageText: string): string {
    const command = messageText.split(' ')[0].toLowerCase();

    switch (command) {
      case '/help':
        return `**Deep Tree Echo Bot Help**

Available commands:
- **/help** - Display this help message
- **/status** - Show bot status
- **/version** - Display version information

You can also just chat with me normally and I'll respond!`;

      case '/status':
        const emotionalState = this.personaCore.getDominantEmotion();
        const dove9State = this.dove9Integration?.getCognitiveState();
        const sys6State = this.sys6Bridge?.getState();
        const membraneStatus = this.doubleMembraneIntegration?.getStatus();
        const stats = this.processingStats;
        return `**Deep Tree Echo Status**

Current mood: ${emotionalState.emotion} (${Math.round(emotionalState.intensity * 100)}%)
Orchestrator running: ${this.running ? 'Yes' : 'No'}

**Cognitive Tier Mode: ${this.config.cognitiveTierMode}**
- BASIC tier: ${this.config.cognitiveTierMode === 'BASIC' ? 'Active' : 'Standby'}
- SYS6 tier: ${this.sys6Bridge ? (sys6State?.running ? 'Active' : 'Ready') : 'Disabled'}
- MEMBRANE tier: ${this.doubleMembraneIntegration ? (membraneStatus?.running ? 'Active' : 'Ready') : 'Disabled'}

**Processing Statistics**
- Total messages: ${stats.totalMessages}
- BASIC tier: ${stats.basicTierMessages}
- SYS6 tier: ${stats.sys6TierMessages}
- MEMBRANE tier: ${stats.membraneTierMessages}
- Avg complexity: ${stats.averageComplexity.toFixed(2)}

**Service Status**
- DeltaChat: ${this.deltachatInterface?.isConnected() ? 'Connected' : 'Disconnected'}
- Dovecot: ${this.dovecotInterface?.isRunning() ? 'Running' : 'Stopped'}
- Dove9: ${dove9State?.running ? 'Running' : 'Stopped'}
${
  sys6State?.running
    ? `
**Sys6-Triality (30-step cycle)**
- Cycle: ${sys6State.cycleNumber}
- Step: ${sys6State.currentStep}/30
- Stream saliences: [${sys6State.streams.map((s) => s.salience.toFixed(2)).join(', ')}]`
    : ''
}
${
  membraneStatus?.running
    ? `
**Double Membrane**
- Identity energy: ${membraneStatus.identityEnergy.toFixed(2)}
- Native requests: ${membraneStatus.stats.nativeRequests}
- External requests: ${membraneStatus.stats.externalRequests}
- Hybrid requests: ${membraneStatus.stats.hybridRequests}`
    : ''
}`;

      case '/version':
        return `**Deep Tree Echo Orchestrator v2.0.0**
**Phase 6: Production Integration**

**Cognitive Tiers:**
- Tier 1 (BASIC): Deep Tree Echo Core - LLM + RAG + Personality
- Tier 2 (SYS6): Sys6-Triality - 30-step cognitive cycle
- Tier 3 (MEMBRANE): Double Membrane - Bio-inspired architecture

**Components:**
- DeltaChat Interface: ${this.deltachatInterface ? 'Enabled' : 'Disabled'}
- Dovecot Interface: ${this.dovecotInterface ? 'Enabled' : 'Disabled'}
- Dove9 Cognitive OS: ${this.dove9Integration ? 'Enabled' : 'Disabled'}
- Sys6-Triality: ${this.sys6Bridge ? 'Enabled' : 'Disabled'}
- Double Membrane: ${this.doubleMembraneIntegration ? 'Enabled' : 'Disabled'}
- IPC Server: ${this.ipcServer ? 'Enabled' : 'Disabled'}
- Task Scheduler: ${this.scheduler ? 'Enabled' : 'Disabled'}
- Webhook Server: ${this.webhookServer ? 'Enabled' : 'Disabled'}

**Architecture:**
- 3 concurrent cognitive streams (Dove9)
- 30-step cognitive cycle (Sys6)
- 120° phase offset between streams
- Adaptive tier routing based on complexity
- Bio-inspired double membrane processing`;

      default:
        return `Unknown command: ${command}. Type /help for available commands.`;
    }
  }

  /**
   * Handle response from Dove9 cognitive OS
   */
  private async handleDove9Response(response: Dove9Response): Promise<void> {
    log.info(`Dove9 response ready for ${response.to} (process: ${response.processId})`);
    log.debug(
      `Cognitive metrics: valence=${response.cognitiveMetrics.emotionalValence.toFixed(2)}, arousal=${response.cognitiveMetrics.emotionalArousal.toFixed(2)}, salience=${response.cognitiveMetrics.salienceScore.toFixed(2)}`
    );

    // Route through DeltaChat
    const emailResponse: EmailResponse = {
      to: response.to,
      from: response.from,
      subject: response.subject,
      body: response.body,
      inReplyTo: response.inReplyTo,
    };

    await this.handleEmailResponse(emailResponse);
  }

  /**
   * Handle email response from Dovecot and route to DeltaChat
   */
  private async handleEmailResponse(response: EmailResponse): Promise<void> {
    log.info(`Routing email response to ${response.to}`);

    if (!this.deltachatInterface?.isConnected()) {
      log.warn('DeltaChat not connected, cannot send response');
      return;
    }

    try {
      // Check if we have a cached chat mapping for this email
      const emailLower = response.to.toLowerCase();
      let routing = this.emailToChatMap.get(emailLower);

      if (!routing) {
        // Need to find or create a chat for this email
        const accounts = await this.deltachatInterface.getAllAccounts();

        if (accounts.length === 0) {
          log.error('No DeltaChat accounts available');
          return;
        }

        // Use default account or first available
        const accountId = this.config.defaultAccountId || accounts[0].id;

        // Find or create chat for this email
        const chatId = await this.deltachatInterface.findOrCreateChatForEmail(
          accountId,
          response.to
        );

        routing = { accountId, chatId };
        this.emailToChatMap.set(emailLower, routing);
      }

      // Format the response as an email reply
      const formattedResponse = `**Re: ${response.subject}**

${response.body}`;

      // Send through DeltaChat
      await this.deltachatInterface.sendMessage(
        routing.accountId,
        routing.chatId,
        formattedResponse
      );

      log.info(`Response sent to chat ${routing.chatId}`);
    } catch (error) {
      log.error('Failed to route email response to DeltaChat:', error);
    }
  }

  /**
   * Update emotional state based on message content
   */
  private async updateEmotionalState(content: string): Promise<void> {
    const positiveWords = ['thank', 'great', 'good', 'love', 'appreciate', 'happy', 'excited'];
    const negativeWords = ['sorry', 'problem', 'issue', 'wrong', 'bad', 'angry', 'frustrated'];

    const lowerContent = content.toLowerCase();
    let positiveCount = 0;
    let negativeCount = 0;

    positiveWords.forEach((word) => {
      if (lowerContent.includes(word)) positiveCount++;
    });

    negativeWords.forEach((word) => {
      if (lowerContent.includes(word)) negativeCount++;
    });

    const stimuli: Record<string, number> = {};

    if (positiveCount > negativeCount) {
      stimuli.joy = 0.2;
      stimuli.interest = 0.1;
    } else if (negativeCount > positiveCount) {
      stimuli.sadness = 0.1;
      stimuli.interest = 0.1;
    }

    // Always increase interest for new messages
    stimuli.interest = (stimuli.interest || 0) + 0.1;

    await this.personaCore.updateEmotionalState(stimuli);
  }

  /**
   * Stop the orchestrator and all its services
   */
  public async stop(): Promise<void> {
    if (!this.running) {
      log.warn('Orchestrator is not running');
      return;
    }

    log.info('Stopping orchestrator services...');

    // Stop all services in reverse order (newest first)
    if (this.doubleMembraneIntegration) {
      await this.doubleMembraneIntegration.stop();
    }

    if (this.sys6Bridge) {
      await this.sys6Bridge.stop();
    }

    if (this.dove9Integration) {
      await this.dove9Integration.stop();
    }

    if (this.webhookServer) {
      await this.webhookServer.stop();
    }

    if (this.scheduler) {
      await this.scheduler.stop();
    }

    if (this.ipcServer) {
      await this.ipcServer.stop();
    }

    if (this.dovecotInterface) {
      await this.dovecotInterface.stop();
    }

    if (this.deltachatInterface) {
      await this.deltachatInterface.disconnect();
    }

    this.running = false;
    log.info('Orchestrator stopped successfully');
  }

  /**
   * Get Dovecot interface for direct access
   */
  public getDovecotInterface(): DovecotInterface | undefined {
    return this.dovecotInterface;
  }

  /**
   * Get DeltaChat interface for direct access
   */
  public getDeltaChatInterface(): DeltaChatInterface | undefined {
    return this.deltachatInterface;
  }

  /**
   * Check if orchestrator is running
   */
  public isRunning(): boolean {
    return this.running;
  }

  /**
   * Get Dove9 integration for direct access
   */
  public getDove9Integration(): Dove9Integration | undefined {
    return this.dove9Integration;
  }

  /**
   * Get Dove9 cognitive state
   */
  public getDove9CognitiveState(): any {
    return this.dove9Integration?.getCognitiveState() || null;
  }

  /**
   * Get the Global Workspace Broadcaster.
   * Use this to register IPC/webhook subscribers that should receive a snapshot
   * at every Sys6 synchronization event (Global Workspace Theory implementation).
   */
  public getGlobalWorkspaceBroadcaster(): GlobalWorkspaceBroadcaster {
    return this.globalWorkspaceBroadcaster;
  }

  /**
   * Attach a TelemetryMonitor so that its snapshot is included in every
   * global workspace broadcast.  Must be called before start() to take effect.
   */
  public setTelemetryMonitor(monitor: TelemetryMonitor): void {
    this.telemetryMonitor = monitor;
    // Also register the sync-event recording subscriber so the monitor tracks GWT heartbeats
    this.globalWorkspaceBroadcaster.addSubscriber((snapshot) => {
      monitor.recordSyncEvent(
        snapshot.syncEvent.channelPairCount,
        snapshot.syncEvent.alignedChannels
      );
    });
  }

  /**
   * Configure LLM service API keys
   */
  public configureApiKeys(keys: Record<string, string>): void {
    if (keys.general) {
      this.llmService.setConfig({ apiKey: keys.general });
    }
    log.info('API keys configured');
  }

  /**
   * Send a message directly to a DeltaChat chat
   */
  public async sendMessage(
    accountId: number,
    chatId: number,
    text: string
  ): Promise<number | null> {
    if (!this.deltachatInterface?.isConnected()) {
      log.error('DeltaChat not connected');
      return null;
    }

    return this.deltachatInterface.sendMessage(accountId, chatId, text);
  }

  /**
   * Send a message to an email address through DeltaChat
   */
  public async sendMessageToEmail(
    email: string,
    text: string,
    accountId?: number
  ): Promise<boolean> {
    if (!this.deltachatInterface?.isConnected()) {
      log.error('DeltaChat not connected');
      return false;
    }

    try {
      // Get account to use
      let useAccountId = accountId || this.config.defaultAccountId;

      if (!useAccountId) {
        const accounts = await this.deltachatInterface.getAllAccounts();
        if (accounts.length === 0) {
          log.error('No DeltaChat accounts available');
          return false;
        }
        useAccountId = accounts[0].id;
      }

      // Find or create chat for email
      const chatId = await this.deltachatInterface.findOrCreateChatForEmail(useAccountId, email);

      // Send message
      await this.deltachatInterface.sendMessage(useAccountId, chatId, text);

      // Update cache
      this.emailToChatMap.set(email.toLowerCase(), { accountId: useAccountId, chatId });

      return true;
    } catch (error) {
      log.error('Failed to send message to email:', error);
      return false;
    }
  }

  /**
   * Get Sys6 bridge for direct access
   */
  public getSys6Bridge(): Sys6OrchestratorBridge | undefined {
    return this.sys6Bridge;
  }

  /**
   * Get Double Membrane integration for direct access
   */
  public getDoubleMembraneIntegration(): DoubleMembraneIntegration | undefined {
    return this.doubleMembraneIntegration;
  }

  /**
   * Get current cognitive tier mode
   */
  public getCognitiveTierMode(): CognitiveTierMode {
    return this.config.cognitiveTierMode;
  }

  /**
   * Set cognitive tier mode at runtime
   */
  public setCognitiveTierMode(mode: CognitiveTierMode): void {
    log.info(`Changing cognitive tier mode from ${this.config.cognitiveTierMode} to ${mode}`);
    this.config.cognitiveTierMode = mode;
  }

  /**
   * Set up grand cycle synchronization between Sys6 and Dove9, and wire the
   * Global Workspace Broadcaster to fire at every Sys6 synchronization event.
   *
   * Grand Cycle = LCM(30, 12) = 60 steps:
   *   - 5 complete Dove9 triadic cycles (5 × 12 = 60)
   *   - 2 complete Sys6 cycles (2 × 30 = 60)
   *
   * Global Workspace broadcast: fires at every Sys6 sync_event so the full
   * joint cognitive state becomes simultaneously available to IPC clients,
   * webhooks, and the telemetry subsystem (Global Workspace Theory).
   */
  private async setupGrandCycleSynchronization(): Promise<void> {
    if (!this.sys6Bridge || !this.dove9Integration) {
      log.warn('Cannot setup grand cycle synchronization: Sys6 or Dove9 not available');
      return;
    }

    const dove9System = this.dove9Integration.getDove9System();
    if (!dove9System) {
      log.warn('Cannot setup grand cycle synchronization: Dove9 system not available');
      return;
    }

    const kernel = dove9System.getKernel();
    if (!kernel) {
      log.warn('Cannot setup grand cycle synchronization: Dove9 kernel not available');
      return;
    }

    log.info('Grand cycle synchronization enabled (LCM(30,12) = 60-step grand cycle)');

    // -----------------------------------------------------------------------
    // Cycle counters
    // -----------------------------------------------------------------------

    // Listen for Dove9 cycle completions
    kernel.on('cycle_complete', (cycleEvent: { cycle: number }) => {
      this.dove9CyclesTotal = cycleEvent.cycle;
      log.debug(`Dove9 cycle ${this.dove9CyclesTotal} complete`);

      // Grand cycle boundary: every 5 Dove9 cycles (= 2 Sys6 cycles = 60 steps)
      if (this.dove9CyclesTotal % 5 === 0) {
        this.grandCycleNumber++;
        log.info(
          `Grand cycle #${this.grandCycleNumber} complete ` +
            `(Dove9 cycle ${this.dove9CyclesTotal}, Sys6 cycle ${this.sys6CyclesTotal})`
        );
      }
    });

    // Listen for Sys6 cycle completions
    this.sys6Bridge.on('cycle_complete', (sys6CycleResult: { cycleNumber: number }) => {
      this.sys6CyclesTotal = sys6CycleResult.cycleNumber;
      log.debug(`Sys6 cycle ${this.sys6CyclesTotal} complete`);
    });

    // -----------------------------------------------------------------------
    // Global Workspace broadcast at every Sys6 synchronization event
    // -----------------------------------------------------------------------

    this.sys6Bridge.on('sync_event', async (syncEvent: SynchronizationEvent) => {
      await this.globalWorkspaceBroadcaster.onSynchronizationEvent(
        syncEvent,
        () => this.buildGlobalWorkspaceState(syncEvent)
      );
    });

    log.info('Grand cycle event coordination and Global Workspace broadcaster established');
  }

  /**
   * Build the joint cognitive state snapshot passed to the Global Workspace Broadcaster.
   * Called synchronously inside the sync_event handler to capture state at that instant.
   */
  private buildGlobalWorkspaceState(_syncEvent: SynchronizationEvent): {
    telemetry: TelemetrySnapshot | null;
    dove9: Dove9CognitiveState | null;
    grandCycle: GrandCycleInfo | null;
  } {
    // Telemetry snapshot — use the monitor if one has been wired in
    const telemetry: TelemetrySnapshot | null = this.telemetryMonitor?.getSnapshot() ?? null;

    // Dove9 cognitive state
    const dove9State = this.dove9Integration?.getCognitiveState() ?? null;
    const dove9: Dove9CognitiveState | null = dove9State
      ? {
          running: dove9State.running,
          activeProcessCount: dove9State.activeProcessCount,
          mailProtocolEnabled: dove9State.mailProtocolEnabled,
          triadic: dove9State.triadic,
        }
      : null;

    // Grand cycle info — present only at 60-step boundary (dove9 cycles multiple of 5)
    const grandCycle: GrandCycleInfo | null =
      this.dove9CyclesTotal > 0 && this.dove9CyclesTotal % 5 === 0
        ? {
            grandCycleNumber: this.grandCycleNumber,
            dove9CyclesCompleted: this.dove9CyclesTotal,
            sys6CyclesCompleted: this.sys6CyclesTotal,
          }
        : null;

    return { telemetry, dove9, grandCycle };
  }

  /**
   * Get processing statistics
   */
  public getProcessingStats(): typeof this.processingStats {
    return { ...this.processingStats };
  }

  /**
   * Get comprehensive cognitive system status
   */
  public getCognitiveSystemStatus(): {
    tierMode: CognitiveTierMode;
    sys6: { running: boolean; cycleNumber?: number; currentStep?: number } | null;
    doubleMembrane: { running: boolean; identityEnergy?: number } | null;
    dove9: { running: boolean } | null;
    stats: {
      totalMessages: number;
      basicTierMessages: number;
      sys6TierMessages: number;
      membraneTierMessages: number;
      averageComplexity: number;
    };
  } {
    const sys6State = this.sys6Bridge?.getState();
    return {
      tierMode: this.config.cognitiveTierMode,
      sys6: this.sys6Bridge
        ? {
            running: sys6State?.running ?? false,
            cycleNumber: sys6State?.cycleNumber,
            currentStep: sys6State?.currentStep,
          }
        : null,
      doubleMembrane: this.doubleMembraneIntegration
        ? {
            running: this.doubleMembraneIntegration.isRunning(),
            identityEnergy: this.doubleMembraneIntegration.getStatus().identityEnergy,
          }
        : null,
      dove9: this.dove9Integration
        ? {
            running: this.dove9Integration.getCognitiveState()?.running || false,
          }
        : null,
      stats: { ...this.processingStats },
    };
  }
}
