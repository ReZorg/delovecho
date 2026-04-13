/**
 * Live2DAvatar — barrel export
 */

export { Live2DAvatar } from './Live2DAvatar.js';
export { EndocrineExpressionBridge } from './EndocrineExpressionBridge.js';
export { MiaraManifest } from './MiaraManifest.js';
export { AionManifest } from './AionManifest.js';
export { LorenzChaoticDriver } from './LorenzChaoticDriver.js';
export {
  NeuroChaoCognitiveDriver,
  NEURO_CHAO_DEFAULTS,
  AION_QUANTUM_DEFAULTS,
} from './NeuroChaoCognitiveDriver.js';
export { useScriptLoader } from './useScriptLoader.js';

export type {
  Live2DAvatarProps,
  EndocrineState,
  CharacterManifest,
  CubismParameterTarget,
  OCEANPersonality,
  MotionMapping,
  ExpressionMapping,
  ScriptLoadState,
} from './types.js';

export type {
  LorenzConfig,
} from './LorenzChaoticDriver.js';

export type {
  NeuroChaoPersonality,
  AionQuantumTraits,
  CognitivePipelinePhase,
  EchobeatsPhase,
  FourECognitionMetrics,
  AestheticParameters,
  IntrospectiveState,
  CognitiveState,
} from './NeuroChaoCognitiveDriver.js';
