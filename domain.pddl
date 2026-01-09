(define (domain ricochet)
  (:requirements :strips :typing :negative-preconditions)
  
  (:types 
    robot cell direction
  )

  (:predicates
    ; --- Static Geography ---
    (next ?c1 - cell ?c2 - cell ?d - direction)
    (blocked ?c1 - cell ?c2 - cell)
    (boundary ?c - cell ?d - direction) ; <--- NEW: Marks the edge of the map
    
    ; --- Dynamic State ---
    (at ?r - robot ?c - cell)
    (occupied ?c - cell)
    
    ; --- The "Slippery" Logic ---
    (sliding ?r - robot ?d - direction)
    (idle ?r - robot)
  )

  ; Action 1: START SLIDING
  (:action start-slide
    :parameters (?r - robot ?from - cell ?to - cell ?d - direction)
    :precondition (and 
        (idle ?r)
        (at ?r ?from)
        (next ?from ?to ?d)
        (not (blocked ?from ?to))
        (not (occupied ?to))
    )
    :effect (and 
        (not (idle ?r))
        (sliding ?r ?d)
    )
  )

  ; Action 2: MOVE SLIDING
  (:action move-slide
    :parameters (?r - robot ?current - cell ?next - cell ?d - direction)
    :precondition (and 
        (sliding ?r ?d)
        (at ?r ?current)
        (next ?current ?next ?d)
        (not (blocked ?current ?next))
        (not (occupied ?next))
    )
    :effect (and 
        (not (at ?r ?current))
        (not (occupied ?current))
        (at ?r ?next)
        (occupied ?next)
    )
  )

  ; Action 3: STOP SLIDING (Wall)
  (:action stop-slide-wall
    :parameters (?r - robot ?current - cell ?next - cell ?d - direction)
    :precondition (and 
        (sliding ?r ?d)
        (at ?r ?current)
        (next ?current ?next ?d)
        (blocked ?current ?next)
    )
    :effect (and 
        (not (sliding ?r ?d))
        (idle ?r)
    )
  )
  
  ; Action 4: STOP SLIDING (Robot)
  (:action stop-slide-robot
    :parameters (?r - robot ?current - cell ?next - cell ?d - direction)
    :precondition (and 
        (sliding ?r ?d)
        (at ?r ?current)
        (next ?current ?next ?d)
        (occupied ?next)
    )
    :effect (and 
        (not (sliding ?r ?d))
        (idle ?r)
    )
  )

  ; Action 5: STOP SLIDING (Board Edge) <--- NEW ACTION
  ; If we are at a cell marked as a boundary in the sliding direction, we stop.
  (:action stop-slide-border
    :parameters (?r - robot ?current - cell ?d - direction)
    :precondition (and 
        (sliding ?r ?d)
        (at ?r ?current)
        (boundary ?current ?d)
    )
    :effect (and 
        (not (sliding ?r ?d))
        (idle ?r)
    )
  )
)