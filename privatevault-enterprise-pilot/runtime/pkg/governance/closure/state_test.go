package closure

import (
	"testing"
	"time"
)

func TestHashChainIntegrity(t *testing.T) {
	cf := &CaseFile{
		CaseID:       "case-test",
		Env:          "prod",
		System:       "privatevault",
		CurrentState: StateOPEN,
		LastHash:     "",
	}

	AppendEvent(cf, ClosureEvent{
		Timestamp: time.Now().UTC(),
		Type:      EventESCALATE,
		ActorID:   "alice",
		ActorRole: "IncidentCommander",
		Reason:    "risk sequence",
		ToState:   StateESCALATED,
	})

	AppendEvent(cf, ClosureEvent{
		Timestamp: time.Now().UTC(),
		Type:      EventACK,
		ActorID:   "bob",
		ActorRole: "Approver",
		Reason:    "ack",
		ToState:   StateACKNOWLEDGED,
	})

	AppendEvent(cf, ClosureEvent{
		Timestamp: time.Now().UTC(),
		Type:      EventCLOSE,
		ActorID:   "alice",
		ActorRole: "Owner",
		Reason:    "closed",
		ToState:   StateCLOSED,
	})

	if cf.LastHash == "" {
		t.Fatal("expected chain head hash to be non-empty")
	}

	// chain links must match previous hash pointers
	prev := ""
	for i, ev := range cf.Events {
		if ev.PrevHash != prev {
			t.Fatalf("event %d prev hash mismatch: got=%s want=%s", i, ev.PrevHash, prev)
		}
		prev = ev.Hash
	}
}

func TestClosureStateTransitions(t *testing.T) {
	cf := &CaseFile{
		CaseID:       "case-state",
		Env:          "prod",
		System:       "privatevault",
		CurrentState: StateOPEN,
	}

	AppendEvent(cf, ClosureEvent{
		Timestamp: time.Now().UTC(),
		Type:      EventESCALATE,
		ActorID:   "ic",
		ActorRole: "IncidentCommander",
		Reason:    "trigger",
		ToState:   StateESCALATED,
	})
	if cf.CurrentState != StateESCALATED {
		t.Fatal("expected ESCALATED")
	}

	AppendEvent(cf, ClosureEvent{
		Timestamp: time.Now().UTC(),
		Type:      EventACK,
		ActorID:   "approver",
		ActorRole: "Approver",
		Reason:    "ack",
		ToState:   StateACKNOWLEDGED,
	})
	if cf.CurrentState != StateACKNOWLEDGED {
		t.Fatal("expected ACKNOWLEDGED")
	}

	AppendEvent(cf, ClosureEvent{
		Timestamp: time.Now().UTC(),
		Type:      EventCLOSE,
		ActorID:   "owner",
		ActorRole: "Owner",
		Reason:    "close",
		ToState:   StateCLOSED,
	})
	if cf.CurrentState != StateCLOSED {
		t.Fatal("expected CLOSED")
	}
}
