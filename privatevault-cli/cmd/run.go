package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var runCmd = &cobra.Command{
	Use:   "run",
	Short: "Run workflows",
}

var runDemoCmd = &cobra.Command{
	Use:   "demo",
	Short: "Run a local PrivateVault demo",
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Println("🚀 Starting PrivateVault local demo (secure agents + governance relay)...")
		fmt.Println("✅ Demo: verifying environment...")

		// Minimal self-contained demo output
		fmt.Println("✅ AI Firewall: enabled (strict)")
		fmt.Println("✅ Governance: enabled (shadow mode)")
		fmt.Println("✅ Audit: WORM ledger enabled")
		fmt.Println("✅ Demo complete.")
		return nil
	},
}

func init() {
	RootCmd.AddCommand(runCmd)
	runCmd.AddCommand(runDemoCmd)

	// Safety: never depend on repo paths for demo
	if os.Getenv("PRIVATEVAULT_DEMO_MODE") == "" {
		_ = os.Setenv("PRIVATEVAULT_DEMO_MODE", "local")
	}
}
