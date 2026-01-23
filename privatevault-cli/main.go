package main

import (
	"fmt"
	"os"

	"github.com/LOLA0786/PrivateVault-Mega-Repo/privatevault-cli/cmd"
)

func main() {
	// minimal CLI:
	// privatevault run demo
	if len(os.Args) < 2 {
		fmt.Println("Usage: privatevault run demo | privatevault version")
		os.Exit(1)
	}

	switch os.Args[1] {
	case "run":
		if err := cmd.RunCmd(os.Args[2:]); err != nil {
			fmt.Println("Error:", err)
			os.Exit(1)
		}
	case "version":
		fmt.Println("PrivateVault CLI dev")
	default:
		fmt.Println("Unknown command:", os.Args[1])
		os.Exit(1)
	}
}
