package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/spf13/cobra"
)

var runCmd = &cobra.Command{
	Use:   "run [demo|agent|firewall|...]",
	Short: "Run a PrivateVault component or demo",
	Long:  "Run a quick local demo of the secure agent stack, or start specific components.",
	Args:  cobra.MinimumNArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		switch args[0] {
		case "demo":
			fmt.Println("🚀 Starting PrivateVault local demo (secure agents + governance relay)...")
			return runShellScript("demo/local-demo.sh")
		default:
			return fmt.Errorf("unknown target: %s", args[0])
		}
	},
}

func runShellScript(relPath string) error {
	abs, err := filepath.Abs(relPath)
	if err != nil {
		return err
	}
	if _, err := os.Stat(abs); err != nil {
		return fmt.Errorf("missing script: %s", abs)
	}
	c := exec.Command("bash", abs)
	c.Stdout = os.Stdout
	c.Stderr = os.Stderr
	return c.Run()
}
