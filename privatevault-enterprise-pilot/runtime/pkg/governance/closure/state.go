package closure

import (
	"crypto/sha256"
	"encoding/hex"
	"time"
)

type ClosureState string

const (
	StateOPEN         ClosureState = "OPEN"
	StateESCALATED    ClosureState = "ESCALATED"
	StateACKNOWLEDGED ClosureState = "ACKNOWLEDGED"
	StateCLOSED       ClosureState = "CLOSED"
)

type ClosureEventType string

const (
	EventESCALATE ClosureEventType = "ESCALATE"
	EventACK      ClosureEventType = "ACKNOWLEDGE"
	EventCLOSE    ClosureEventType = "CLOSE"
)

type ClosureEvent struct {
	Timestamp time.Time        `json:"timestamp"`
	Type      ClosureEventType `json:"type"`
	ActorID   string           `json:"actor_id"`
	ActorRole string           `json:"actor_role"`
	Reason    string           `json:"reason"`
	ToState   ClosureState     `json:"to_state"`
	Hash      string           `json:"hash"`
	PrevHash  string           `json:"prev_hash"`
}

type CaseFile struct {
	CaseID       string        `json:"case_id"`
	Env          string        `json:"env"`
	System       string        `json:"system"`
	CurrentState ClosureState  `json:"current_state"`
	OwnerID      string        `json:"owner_id,omitempty"`
	AssigneeID   string        `json:"assignee_id,omitempty"`
	Events       []ClosureEvent`json:"events"`
	LastHash     string        `json:"last_hash"`
}

func hashEvent(prev string, e ClosureEvent) string {
	sum := sha256.Sum256([]byte(
		prev + "|" +
			string(e.Type) + "|" +
			e.ActorID + "|" +
			e.ActorRole + "|" +
			e.Reason + "|" +
			string(e.ToState) + "|" +
			e.Timestamp.UTC().Format(time.RFC3339Nano),
	))
	return hex.EncodeToString(sum[:])
}

func AppendEvent(cf *CaseFile, e ClosureEvent) {
	e.PrevHash = cf.LastHash
	e.Hash = hashEvent(cf.LastHash, e)
	cf.LastHash = e.Hash
	cf.Events = append(cf.Events, e)
	cf.CurrentState = e.ToState
}
