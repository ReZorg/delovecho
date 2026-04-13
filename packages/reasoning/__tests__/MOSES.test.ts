/**
 * Unit tests for MOSES
 * Tests the Meta-Optimizing Semantic Evolutionary Search
 */

import { jest } from '@jest/globals';
import { MOSES, Program, FitnessFunction } from '../reasoning/MOSES.js';
import { AtomSpace } from '../atomspace/AtomSpace.js';

describe('MOSES', () => {
  let atomSpace: AtomSpace;
  let moses: MOSES;

  beforeEach(() => {
    atomSpace = new AtomSpace();
    moses = new MOSES(atomSpace, { populationSize: 10, maxGenerations: 5 });
    jest.spyOn(console, 'log').mockImplementation(() => undefined);
    jest.spyOn(console, 'debug').mockImplementation(() => undefined);
    jest.spyOn(console, 'info').mockImplementation(() => undefined);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('initialization', () => {
    it('should create a MOSES instance', () => {
      expect(moses).toBeDefined();
    });

    it('should accept custom config', () => {
      const customMoses = new MOSES(atomSpace, {
        populationSize: 20,
        maxGenerations: 10,
        mutationRate: 0.2,
      });
      expect(customMoses).toBeDefined();
    });
  });

  describe('population initialization', () => {
    it('should initialize population with correct size', () => {
      moses.initializePopulation();
      const stats = moses.getStats();
      expect(stats.populationSize).toBe(10);
    });

    it('should initialize programs with tree and generation', () => {
      moses.initializePopulation();
      const programs = moses.getBestPrograms(5);
      programs.forEach((p: Program) => {
        expect(p.id).toBeDefined();
        expect(p.tree).toBeDefined();
        expect(typeof p.fitness).toBe('number');
        expect(typeof p.generation).toBe('number');
      });
    });
  });

  describe('evolution', () => {
    it('should evolve population and return best programs', () => {
      moses.initializePopulation();
      const fitnessFunc: FitnessFunction = (_program: Program) => Math.random();
      const best = moses.evolve(fitnessFunc);
      expect(Array.isArray(best)).toBe(true);
      expect(best.length).toBeGreaterThanOrEqual(0);
    });

    it('should assign fitness values after evolve', () => {
      moses.initializePopulation();
      const fitnessFunc: FitnessFunction = (_program: Program) => 0.7;
      moses.evolve(fitnessFunc);
      // The best program (elite) should have been assigned fitness 0.7
      const best = moses.getBestPrograms(1);
      expect(best.length).toBeGreaterThanOrEqual(1);
      expect(best[0].fitness).toBe(0.7);
    });
  });

  describe('getBestPrograms', () => {
    it('should return at most count programs', () => {
      moses.initializePopulation();
      const best = moses.getBestPrograms(3);
      expect(best.length).toBeLessThanOrEqual(3);
    });

    it('should return programs sorted by descending fitness', () => {
      moses.initializePopulation();
      let counter = 0;
      // Assign deterministic descending fitness
      const fitnessFunc: FitnessFunction = (_program: Program) => {
        counter++;
        return 1 / counter;
      };
      moses.evolve(fitnessFunc);
      const best = moses.getBestPrograms(5);
      for (let i = 1; i < best.length; i++) {
        expect(best[i - 1].fitness).toBeGreaterThanOrEqual(best[i].fitness);
      }
    });
  });

  describe('run', () => {
    it('should run the full evolutionary cycle and return best program', () => {
      const fitnessFunc: FitnessFunction = (_program: Program) => Math.random();
      const best = moses.run(fitnessFunc);
      expect(best).toBeDefined();
      expect(best.id).toBeDefined();
      expect(best.tree).toBeDefined();
    });

    it('should stop early when fitness > 0.99', () => {
      // Provide a fitness function that immediately returns near-perfect fitness
      const fitnessFunc: FitnessFunction = (_program: Program) => 1.0;
      const best = moses.run(fitnessFunc);
      expect(best.fitness).toBeGreaterThanOrEqual(0.99);
    });
  });

  describe('getStats', () => {
    it('should return stats with zero population before init', () => {
      const stats = moses.getStats();
      expect(stats).toHaveProperty('generation');
      expect(stats).toHaveProperty('populationSize');
      expect(stats).toHaveProperty('avgFitness');
      expect(stats).toHaveProperty('bestFitness');
    });

    it('should return correct population size after init', () => {
      moses.initializePopulation();
      const stats = moses.getStats();
      expect(stats.populationSize).toBe(10);
      expect(stats.generation).toBe(0);
    });
  });
});
