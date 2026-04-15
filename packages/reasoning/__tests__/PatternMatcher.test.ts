/**
 * Unit tests for PatternMatcher
 * Tests the hypergraph pattern matching system
 */

import { PatternMatcher, Pattern, MatchResult } from '../atomspace/PatternMatcher.js';
import { AtomSpace } from '../atomspace/AtomSpace.js';

describe('PatternMatcher', () => {
  let atomSpace: AtomSpace;
  let patternMatcher: PatternMatcher;

  beforeEach(() => {
    atomSpace = new AtomSpace();
    patternMatcher = new PatternMatcher(atomSpace);
  });

  describe('initialization', () => {
    it('should create a PatternMatcher with AtomSpace', () => {
      expect(patternMatcher).toBeDefined();
    });
  });

  describe('basic pattern matching', () => {
    it('should find atoms matching a simple type pattern', () => {
      const cat = atomSpace.addNode('ConceptNode', 'cat');
      const dog = atomSpace.addNode('ConceptNode', 'dog');
      const mammal = atomSpace.addNode('ConceptNode', 'mammal');

      atomSpace.addLink('InheritanceLink', [cat.id, mammal.id]);
      atomSpace.addLink('InheritanceLink', [dog.id, mammal.id]);

      const pattern: Pattern = { type: 'InheritanceLink' };
      const results = patternMatcher.match(pattern);

      expect(results.length).toBe(2);
    });

    it('should find ConceptNode atoms by type', () => {
      atomSpace.addNode('ConceptNode', 'a');
      atomSpace.addNode('ConceptNode', 'b');
      atomSpace.addNode('PredicateNode', 'p');

      const pattern: Pattern = { type: 'ConceptNode' };
      const results = patternMatcher.match(pattern);

      expect(results.length).toBe(2);
    });

    it('should find atom by exact name', () => {
      atomSpace.addNode('ConceptNode', 'cat');
      atomSpace.addNode('ConceptNode', 'dog');

      const pattern: Pattern = { type: 'ConceptNode', name: 'cat' };
      const results = patternMatcher.match(pattern);

      expect(results.length).toBe(1);
      expect(results[0].matches[0].name).toBe('cat');
    });

    it('should return empty array when no atoms match type', () => {
      atomSpace.addNode('ConceptNode', 'test');

      const pattern: Pattern = { type: 'PredicateNode' };
      const results = patternMatcher.match(pattern);

      expect(results).toEqual([]);
    });

    it('should return empty array when name does not match', () => {
      atomSpace.addNode('ConceptNode', 'test');

      const pattern: Pattern = { type: 'ConceptNode', name: 'nonexistent' };
      const results = patternMatcher.match(pattern);

      expect(results).toEqual([]);
    });
  });

  describe('variable binding', () => {
    it('should bind a variable to matching atoms', () => {
      atomSpace.addNode('ConceptNode', 'cat');
      atomSpace.addNode('ConceptNode', 'dog');

      const pattern: Pattern = { type: 'ConceptNode', variable: true, name: '$X' };
      const results = patternMatcher.match(pattern);

      expect(results.length).toBe(2);
      results.forEach((r: MatchResult) => {
        expect(r.bindings.has('$X')).toBe(true);
      });
    });

    it('should return MatchResult objects with bindings and matches', () => {
      atomSpace.addNode('ConceptNode', 'cat');

      const pattern: Pattern = { type: 'ConceptNode', name: 'cat' };
      const results = patternMatcher.match(pattern);

      expect(results.length).toBe(1);
      const result = results[0];
      expect(result).toHaveProperty('bindings');
      expect(result).toHaveProperty('matches');
      expect(result.matches[0].name).toBe('cat');
    });
  });

  describe('link outgoing patterns', () => {
    it('should match links with specific outgoing structure', () => {
      const cat = atomSpace.addNode('ConceptNode', 'cat');
      const mammal = atomSpace.addNode('ConceptNode', 'mammal');
      atomSpace.addLink('InheritanceLink', [cat.id, mammal.id]);

      const pattern: Pattern = {
        type: 'InheritanceLink',
        outgoing: [
          { type: 'ConceptNode', name: 'cat' },
          { type: 'ConceptNode', name: 'mammal' },
        ],
      };

      const results = patternMatcher.match(pattern);
      expect(results.length).toBe(1);
    });

    it('should not match links with wrong outgoing structure', () => {
      const cat = atomSpace.addNode('ConceptNode', 'cat');
      const mammal = atomSpace.addNode('ConceptNode', 'mammal');
      atomSpace.addLink('InheritanceLink', [cat.id, mammal.id]);

      const pattern: Pattern = {
        type: 'InheritanceLink',
        outgoing: [
          { type: 'ConceptNode', name: 'dog' },
          { type: 'ConceptNode', name: 'mammal' },
        ],
      };

      const results = patternMatcher.match(pattern);
      expect(results.length).toBe(0);
    });
  });

  describe('complex scenarios', () => {
    it('should match multiple inheritance links', () => {
      const cat = atomSpace.addNode('ConceptNode', 'cat');
      const dog = atomSpace.addNode('ConceptNode', 'dog');
      const mammal = atomSpace.addNode('ConceptNode', 'mammal');

      atomSpace.addLink('InheritanceLink', [cat.id, mammal.id]);
      atomSpace.addLink('InheritanceLink', [dog.id, mammal.id]);

      const pattern: Pattern = { type: 'InheritanceLink' };
      const results = patternMatcher.match(pattern);

      expect(results.length).toBe(2);
      results.forEach((r: MatchResult) => {
        expect(r.matches[0].outgoing?.length).toBe(2);
      });
    });

    it('should return results with correct atom data', () => {
      const a = atomSpace.addNode('ConceptNode', 'specificNode');

      const pattern: Pattern = { type: 'ConceptNode', name: 'specificNode' };
      const results = patternMatcher.match(pattern);

      expect(results.length).toBe(1);
      expect(results[0].matches[0].id).toBe(a.id);
      expect(results[0].matches[0].type).toBe('ConceptNode');
    });

    it('should handle empty atomspace', () => {
      const pattern: Pattern = { type: 'ConceptNode' };
      const results = patternMatcher.match(pattern);
      expect(results).toEqual([]);
    });
  });
});
