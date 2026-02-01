# Closure Workflow — DESIGN

## Purpose
Formalize escalation + acknowledgement + closure with role-based responsibility.

## State Machine
OPEN -> ESCALATED -> ACKNOWLEDGED -> CLOSED

## Contract
Inputs:
- command: ESCALATE | ACKNOWLEDGE | CLOSE
- actor_id + role
Outputs:
- updated CaseFile
- hash-chained closure event stream

## Invariants
- No ACK before ESCALATE
- No CLOSE before ACK
- Actor role must authorize action

## Evidence
- CaseFile is hash-chained; head hash proves integrity
