package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

// RunCmd: minimal standalone runner (does NOT depend on RootCmd).
// This avoids goreleaser build failures if RootCmd is missing/renamed.
func RunCmd(args []string) error {
	if len(args) == 0 {
		return fmt.Errorf("missing args: expected `run demo`")
	}

	switch args[0] {
	case "demo":
		return runDemo()
	default:
		return fmt.Errorf("unknown run subcommand: %s (supported: demo)", args[0])
	}
}

func runDemo() error {
	// Try common locations:
	// 1) repo checkout path (dev)
	// 2) brew install path won’t have demo scripts, so we message clearly
	repoRoot, _ := os.Getwd()

	candidates := []string{
		filepath.Join(repoRoot, "demo", "local-demo.sh"),
		filepath.Join(repoRoot, "..", "demo", "local-demo.sh"),
	}

	for _, p := range candidates {
		if st, err := os.Stat(p); err == nil && !st.IsDir() {
			cmd := exec.Command("bash", p)
			cmd.Stdout = os.Stdout
			cmd.Stderr = os.Stderr
			cmd.Stdin = os.Stdin
			return cmd.Run()
		}
	}

	return fmt.Errorf("missing script: demo/local-demo.sh (this is expected in Homebrew installs; use repo checkout)")
}
