package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/spf13/cobra"
)

// runCmd is referenced by cmd/root.go.
// We must define it or goreleaser build will fail.
var runCmd = &cobra.Command{
	Use:   "run",
	Short: "Run PrivateVault operations",
}

var runDemoCmd = &cobra.Command{
	Use:   "demo",
	Short: "Run the local PrivateVault demo (repo checkout only)",
	RunE: func(cmd *cobra.Command, args []string) error {
		return runDemo()
	},
}

func init() {
	runCmd.AddCommand(runDemoCmd)
}

// runDemo runs demo/local-demo.sh if present.
// In Homebrew installs, repo demo scripts aren't present: we fail gracefully.
func runDemo() error {
	wd, _ := os.Getwd()

	candidates := []string{
		filepath.Join(wd, "demo", "local-demo.sh"),
		filepath.Join(wd, "..", "demo", "local-demo.sh"),
	}

	for _, p := range candidates {
		if st, err := os.Stat(p); err == nil && !st.IsDir() {
			c := exec.Command("bash", p)
			c.Stdout = os.Stdout
			c.Stderr = os.Stderr
			c.Stdin = os.Stdin
			return c.Run()
		}
	}

	return fmt.Errorf("missing script: demo/local-demo.sh (expected in repo checkout; not bundled in brew install)")
}
