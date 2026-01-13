package main

import (
	"log"
	"net/http"

	"github.com/LOLA0786/PrivateVault-Mega-Repo/pkg/governance/authority"
)

func main() {
	res, err := authority.NewResolver()
	if err != nil {
		log.Fatal(err)
	}

	http.HandleFunc("/resolve", res.Handle)
	log.Println("pv-authority-resolver listening on :8081")
	log.Fatal(http.ListenAndServe(":8081", nil))
}
