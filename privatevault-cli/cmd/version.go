package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Print version info",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Printf("PrivateVault CLI %s\n", Version)
		fmt.Printf("Commit: %s\n", Commit)
		fmt.Printf("BuildDate: %s\n", BuildDate)
	},
}
