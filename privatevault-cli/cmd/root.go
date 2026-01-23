package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var (
	// Injected by GoReleaser at build time
	Version   = "dev"
	Commit    = "none"
	BuildDate = "unknown"
)

var rootCmd = &cobra.Command{
	Use:   "privatevault",
	Short: "PrivateVault CLI: security control plane for AI agents",
	Long: `PrivateVault is the security control plane for AI agents:
- policy enforcement
- intent verification
- replayability
- cryptographic audit trails`,
	SilenceUsage:  true,
	SilenceErrors: true,
}

func Execute() error {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err.Error())
	}
}

func init() {
	rootCmd.AddCommand(versionCmd)
	rootCmd.AddCommand(runCmd)
	rootCmd.AddCommand(completionCmd)
}
