package authority

import (
	"context"
	"encoding/json"
	"net/http"
	"strings"

	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
)

type Resolver struct {
	client *kubernetes.Clientset
}

type Req struct {
	UserID  string `json:"user_id"`
	Env     string `json:"env"`
	System  string `json:"system"`
}

type Resp struct {
	UserID string   `json:"user_id"`
	Roles  []string `json:"roles"`
}

func NewResolver() (*Resolver, error) {
	cfg, err := rest.InClusterConfig()
	if err != nil { return nil, err }
	cs, err := kubernetes.NewForConfig(cfg)
	if err != nil { return nil, err }
	return &Resolver{client: cs}, nil
}

func (r *Resolver) Handle(w http.ResponseWriter, req *http.Request) {
	var in Req
	_ = json.NewDecoder(req.Body).Decode(&in)

	abs, err := r.client.RESTClient().Get().
		AbsPath("/apis/governance.privatevault.io/v1alpha1").
		Namespace("governance").
		Resource("authoritybindings").
		DoRaw(context.Background())
	if err != nil {
		http.Error(w, err.Error(), 500); return
	}

	var obj map[string]any
	_ = json.Unmarshal(abs, &obj)

	items, _ := obj["items"].([]any)
	rolesSet := map[string]bool{}

	for _, it := range items {
		m := it.(map[string]any)
		spec := m["spec"].(map[string]any)

		sub := spec["subject"].(map[string]any)
		id := sub["id"].(string)
		typ := sub["type"].(string)

		if typ != "user" || id != in.UserID { continue }

		scope := spec["scope"].(map[string]any)
		if scope["env"] != in.Env || scope["system"] != in.System { continue }

		rs := spec["roles"].([]any)
		for _, r := range rs {
			rolesSet[r.(string)] = true
		}
	}

	var roles []string
	for k := range rolesSet { roles = append(roles, k) }

	out := Resp{UserID: in.UserID, Roles: roles}
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(out)
}

func (r *Resolver) RolesHeader(user, env, system string) string {
	// used later if needed
	return strings.Join([]string{}, ",")
}

