(define (domain ricochet)
  (:requirements :strips :typing :negative-preconditions)
  
  (:types 
    robot cell direction
  )

  (:predicates
    ; --- Static Geography (The Map) ---
    (next ?c1 ?c2 - cell ?d - direction) ; c2 is next to c1 in direction d
    (blocked ?c1 ?c2)                    ; There is a wall between c1 and c2

    ; --- Dynamic State (The Pieces) ---
    (at ?r - robot ?c - cell)            ; Robot r is at cell c
    (occupied ?c - cell)                 ; Cell c has a robot (any robot)
    
    ; --- The "Slippery" Logic ---
    (sliding ?r - robot ?d - direction)  ; Robot is currently sliding in dir
    (idle ?r - robot)                    ; Robot is stopped and can choose a move
  )

  ; Action 1: START SLIDING
  ; A robot decides to move in a direction. 
  ; It can only do this if the immediate next cell is valid (not a wall, not occupied).
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
        ; We don't move yet, we just enter the "sliding" state.
        ; The actual movement happens in move-slide.
    )
  )

  ; Action 2: MOVE SLIDING
  ; If the robot is sliding, and the NEXT cell is free, it MUST move there.
  ; Note: In standard PDDL, we can't force "MUST". But because 'stop'
  ; requires an obstacle, the planner is forced to use this action to make progress.
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
  ; The robot stops if there is a WALL between current and next.
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
  ; The robot stops if the next cell is OCCUPIED by another robot.
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
  
  ; Action 5: STOP SLIDING (Edge of Board)
  ; If there is no 'next' cell defined, we are at the edge.
  ; This requires a trickier setup or explicit "border" cells.
  ; A simpler way is to model the board edge as "blocked" in the problem file.
)