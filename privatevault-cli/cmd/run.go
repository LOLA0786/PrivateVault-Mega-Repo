package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var runCmd = &cobra.Command{
	Use:   "run [demo]",
	Short: "Run PrivateVault components or demo",
	RunE: func(cmd *cobra.Command, args []string) error {
		if len(args) == 0 {
			return cmd.Usage()
		}

		switch args[0] {
		case "demo":
			fmt.Println("🚀 PrivateVault Demo (standalone)")

			encrypted := "encrypted-secret"
			relayed := "relayed-" + encrypted
			verified := true

			fmt.Println("Encrypted:", encrypted)
			fmt.Println("Relayed:", relayed)
			if verified {
				fmt.Println("Verified: OK")
			} else {
				fmt.Println("Verified: Failed")
			}

			fmt.Println("Done – pro for more: privatevault pro signup")
			return nil

		default:
			return fmt.Errorf("unknown: %s", args[0])
		}
	},
}

func init() {
	rootCmd.AddCommand(runCmd)
}
