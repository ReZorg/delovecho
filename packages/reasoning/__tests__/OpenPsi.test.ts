/**
 * Unit tests for OpenPsi
 * Tests the motivational and emotional system
 */

import { jest } from '@jest/globals';
import { OpenPsi, Goal, Drive, Emotion } from '../reasoning/OpenPsi.js';
import { AtomSpace } from '../atomspace/AtomSpace.js';

describe('OpenPsi', () => {
  let atomSpace: AtomSpace;
  let openPsi: OpenPsi;

  beforeEach(() => {
    atomSpace = new AtomSpace();
    openPsi = new OpenPsi(atomSpace);
    jest.spyOn(console, 'log').mockImplementation(() => undefined);
    jest.spyOn(console, 'debug').mockImplementation(() => undefined);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('initialization', () => {
    it('should create an OpenPsi instance', () => {
      expect(openPsi).toBeDefined();
    });

    it('should initialize default drives', () => {
      const state = openPsi.getState();
      expect(state.drives.length).toBeGreaterThan(0);
    });
  });

  describe('drive management', () => {
    it('should add a new drive', () => {
      openPsi.addDrive('curiosity', 0.5, 0, 1, 0.01);
      const state = openPsi.getState();
      expect(state.drives.some((d: Drive) => d.name === 'curiosity')).toBe(true);
    });

    it('should satisfy a drive', () => {
      openPsi.addDrive('testDrive', 0.3, 0, 1, 0.01);
      openPsi.satisfyDrive('testDrive', 0.4);
      const state = openPsi.getState();
      const drive = state.drives.find((d: Drive) => d.name === 'testDrive');
      expect(drive?.value).toBeCloseTo(0.7, 5);
    });

    it('should cap drive value at max', () => {
      openPsi.addDrive('capped', 0.9, 0, 1, 0.01);
      openPsi.satisfyDrive('capped', 0.5);
      const state = openPsi.getState();
      const drive = state.drives.find((d: Drive) => d.name === 'capped');
      expect(drive?.value).toBe(1.0);
    });

    it('should return false when satisfying non-existent drive', () => {
      const result = openPsi.satisfyDrive('nonexistent', 0.5);
      expect(result).toBe(false);
    });

    it('should decay drives on update', () => {
      openPsi.addDrive('decayDrive', 1.0, 0, 1, 0.1);
      openPsi.updateDrives();
      const state = openPsi.getState();
      const drive = state.drives.find((d: Drive) => d.name === 'decayDrive');
      expect(drive?.value).toBeLessThan(1.0);
    });
  });

  describe('goal management', () => {
    it('should create a goal', () => {
      const goal = openPsi.createGoal('explore', 0.8);
      expect(goal).toBeDefined();
      expect(goal.name).toBe('explore');
      expect(goal.priority).toBe(0.8);
    });

    it('should update goal satisfaction', () => {
      const goal = openPsi.createGoal('testGoal', 0.5);
      openPsi.updateGoalSatisfaction(goal.id, 0.9);
      const state = openPsi.getState();
      const updated = state.goals.find((g: Goal) => g.id === goal.id);
      expect(updated?.satisfaction).toBeCloseTo(0.9, 5);
    });

    it('should select highest priority goal', () => {
      openPsi.createGoal('lowPriority', 0.2);
      openPsi.createGoal('highPriority', 0.9);
      const selected = openPsi.selectGoal();
      expect(selected?.name).toBe('highPriority');
    });

    it('should return false when updating non-existent goal', () => {
      const result = openPsi.updateGoalSatisfaction('nonexistent', 0.5);
      expect(result).toBe(false);
    });
  });

  describe('emotion modeling', () => {
    it('should add emotions', () => {
      openPsi.addEmotion('joy', 0.8, 0.7, 10);
      const state = openPsi.getState();
      expect(state.emotions.some((e: Emotion) => e.name === 'joy')).toBe(true);
    });

    it('should return dominant emotion by arousal', () => {
      openPsi.addEmotion('calm', 0.5, 0.2, 10);
      openPsi.addEmotion('excited', 0.9, 0.9, 10);
      const dominant = openPsi.getDominantEmotion();
      expect(dominant?.name).toBe('excited');
    });

    it('should return null dominant emotion when no emotions present', () => {
      const dominant = openPsi.getDominantEmotion();
      expect(dominant).toBeNull();
    });

    it('should expire emotions with zero duration after update', () => {
      openPsi.addEmotion('fleeting', 0.5, 0.5, 1);
      openPsi.updateEmotions();
      const state = openPsi.getState();
      expect(state.emotions.some((e: Emotion) => e.name === 'fleeting')).toBe(false);
    });

    it('should clamp emotion valence to [-1, 1]', () => {
      openPsi.addEmotion('overflowed', 2.0, 0.5, 10);
      const state = openPsi.getState();
      const emotion = state.emotions.find((e: Emotion) => e.name === 'overflowed');
      expect(emotion?.valence).toBe(1.0);
    });

    it('should clamp emotion arousal to [0, 1]', () => {
      openPsi.addEmotion('clampedArousal', 0.5, -0.5, 10);
      const state = openPsi.getState();
      const emotion = state.emotions.find((e: Emotion) => e.name === 'clampedArousal');
      expect(emotion?.arousal).toBe(0.0);
    });
  });

  describe('action execution', () => {
    it('should execute an action cycle without throwing', () => {
      expect(() => openPsi.executeAction()).not.toThrow();
    });

    it('should update drives during executeAction', () => {
      const stateBefore = openPsi.getState();
      const energyBefore = stateBefore.drives.find((d: Drive) => d.name === 'energy')?.value ?? 1;
      openPsi.executeAction();
      const stateAfter = openPsi.getState();
      const energyAfter = stateAfter.drives.find((d: Drive) => d.name === 'energy')?.value ?? 1;
      expect(energyAfter).toBeLessThanOrEqual(energyBefore);
    });
  });

  describe('getState', () => {
    it('should return complete state object', () => {
      const state = openPsi.getState();
      expect(state).toHaveProperty('goals');
      expect(state).toHaveProperty('drives');
      expect(state).toHaveProperty('emotions');
      expect(state).toHaveProperty('dominantEmotion');
    });

    it('should reflect current goals drives and emotions in state', () => {
      openPsi.createGoal('stateGoal', 0.6);
      openPsi.addDrive('stateDrive', 0.5, 0, 1, 0.01);
      openPsi.addEmotion('stateEmotion', 0.4, 0.3, 5);
      const state = openPsi.getState();
      expect(state.goals.some((g: Goal) => g.name === 'stateGoal')).toBe(true);
      expect(state.drives.some((d: Drive) => d.name === 'stateDrive')).toBe(true);
      expect(state.emotions.some((e: Emotion) => e.name === 'stateEmotion')).toBe(true);
    });
  });
});
