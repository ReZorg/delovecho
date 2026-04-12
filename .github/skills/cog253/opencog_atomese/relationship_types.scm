; OpenCog Atomese - Pattern Relationship Types
; Defines different types of relationships between patterns
; Generated schema for pattern conflicts and complements

; === RELATIONSHIP TYPE DEFINITIONS ===

; Relationship Types
(ConceptNode "RelationType-Dependency")

(ConceptNode "RelationType-Complement")

(ConceptNode "RelationType-Conflict")

(ConceptNode "RelationType-Alternative")


; Relationship Type Descriptions
(EvaluationLink
  (PredicateNode "has-description")
  (ListLink
    (ConceptNode "RelationType-Dependency")
    (ConceptNode "One pattern must precede or follow another in sequence")
  )
)

(EvaluationLink
  (PredicateNode "has-description")
  (ListLink
    (ConceptNode "RelationType-Complement")
    (ConceptNode "Patterns that work well together and enhance each other")
  )
)

(EvaluationLink
  (PredicateNode "has-description")
  (ListLink
    (ConceptNode "RelationType-Conflict")
    (ConceptNode "Patterns that contradict or cannot coexist in the same design")
  )
)

(EvaluationLink
  (PredicateNode "has-description")
  (ListLink
    (ConceptNode "RelationType-Alternative")
    (ConceptNode "Patterns that provide alternative solutions to similar problems")
  )
)


; === EXAMPLE RELATIONSHIPS ===

; Example: Pattern-1 and Pattern-7 complement each other
(EvaluationLink
  (PredicateNode "has-relationship")
  (ListLink
    (ConceptNode "Pattern-1")
    (ConceptNode "Pattern-7")
    (ConceptNode "RelationType-Complement")
  )
)

; === USAGE INSTRUCTIONS ===
;
; To add a complement relationship:
; (EvaluationLink
;   (PredicateNode "has-relationship")
;   (ListLink
;     (ConceptNode "Pattern-X")
;     (ConceptNode "Pattern-Y")
;     (ConceptNode "RelationType-Complement")))
;
; To add a conflict relationship:
; (EvaluationLink
;   (PredicateNode "has-relationship")
;   (ListLink
;     (ConceptNode "Pattern-X")
;     (ConceptNode "Pattern-Y")
;     (ConceptNode "RelationType-Conflict")))
;
; Query patterns with complement relationships:
; (GetLink
;   (VariableNode "$complement")
;   (EvaluationLink
;     (PredicateNode "has-relationship")
;     (ListLink
;       (ConceptNode "Pattern-1")
;       (VariableNode "$complement")
;       (ConceptNode "RelationType-Complement"))))
