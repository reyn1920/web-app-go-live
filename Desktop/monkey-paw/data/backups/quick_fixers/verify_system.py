#!/usr/bin/env python3
"""
Professional system verification suite for YouTube automation platform.

Comprehensive two-pass validation system with Node.js, Python, Shell,
and LaunchAgent verification for enterprise deployment readiness.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


class SystemVerifier:
    """Professional system verification with comprehensive checks."""

    def __init__(self, workspace_path: str) -> None:
        """Initialize verifier with workspace path."""
        self.workspace = Path(workspace_path)
        self.results: Dict[str, Any] = {
            "verification_passes": [],
            "node_checks": {},
            "python_checks": {},
            "shell_checks": {},
            "launchagent_checks": {},
            "overall_status": "UNKNOWN",
            "error_count": 0,
            "warning_count": 0,
        }

    def run_command(self, cmd: List[str], cwd: Path = None) -> Dict[str, Any]:
        """Execute command and return structured result."""
        try:
            result = subprocess.run(cmd, cwd=cwd or self.workspace, capture_output=True, text=True, timeout=60)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": "Command timeout after 60 seconds", "returncode": -1}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}

    def verify_node_ecosystem(self) -> Dict[str, Any]:
        """Verify Node.js ecosystem with comprehensive checks."""
        node_results = {
            "package_json_found": False,
            "eslint_check": {"success": False, "errors": [], "warnings": []},
            "typescript_check": {"success": False, "errors": [], "warnings": []},
            "tests_check": {"success": False, "output": ""},
            "runtime_check": {"success": False, "port_8080": False},
        }

        # Check for package.json
        package_json = self.workspace / "package.json"
        if package_json.exists():
            node_results["package_json_found"] = True

            # ESLint check
            eslint_result = self.run_command(["npx", "eslint", "."])
            node_results["eslint_check"]["success"] = eslint_result["success"]
            if eslint_result["stderr"]:
                node_results["eslint_check"]["errors"].append(eslint_result["stderr"])

            # TypeScript check
            tsc_result = self.run_command(["npx", "tsc", "--noEmit"])
            node_results["typescript_check"]["success"] = tsc_result["success"]
            if tsc_result["stderr"]:
                node_results["typescript_check"]["errors"].append(tsc_result["stderr"])

            # Tests check
            test_result = self.run_command(["npm", "test"])
            node_results["tests_check"]["success"] = test_result["success"]
            node_results["tests_check"]["output"] = test_result["stdout"]

            # Runtime check on port 8080
            runtime_result = self.run_command(["npm", "start"])
            if runtime_result["success"]:
                port_check = self.run_command(["curl", "-f", "http://localhost:8080/health"])
                node_results["runtime_check"]["port_8080"] = port_check["success"]

        return node_results

    def verify_python_ecosystem(self) -> Dict[str, Any]:
        """Verify Python ecosystem with comprehensive checks."""
        python_results = {
            "ruff_check": {"success": False, "errors": [], "warnings": []},
            "mypy_check": {"success": False, "errors": [], "warnings": []},
            "pytest_check": {"success": False, "output": ""},
            "fastapi_check": {"success": False, "port_8010": False},
        }

        # Ruff formatting and linting
        ruff_check = self.run_command(["ruff", "check", "."])
        python_results["ruff_check"]["success"] = ruff_check["success"]
        if ruff_check["stdout"]:
            python_results["ruff_check"]["errors"].append(ruff_check["stdout"])

        ruff_format = self.run_command(["ruff", "format", "--check", "."])
        if not ruff_format["success"]:
            python_results["ruff_check"]["warnings"].append("Formatting issues found")

        # MyPy type checking
        mypy_result = self.run_command(["mypy", "."])
        python_results["mypy_check"]["success"] = mypy_result["success"]
        if mypy_result["stdout"]:
            python_results["mypy_check"]["errors"].append(mypy_result["stdout"])

        # Pytest execution
        pytest_result = self.run_command(["pytest", "-v"])
        python_results["pytest_check"]["success"] = pytest_result["success"]
        python_results["pytest_check"]["output"] = pytest_result["stdout"]

        # FastAPI runtime check on port 8010
        backend_path = self.workspace / "backend"
        if backend_path.exists():
            fastapi_result = self.run_command(["uvicorn", "app:app", "--port", "8010"], cwd=backend_path)
            if fastapi_result["success"]:
                port_check = self.run_command(["curl", "-f", "http://localhost:8010/api/health"])
                python_results["fastapi_check"]["port_8010"] = port_check["success"]

        return python_results

    def verify_shell_scripts(self) -> Dict[str, Any]:
        """Verify shell scripts with ShellCheck."""
        shell_results = {"scripts_found": [], "shellcheck_results": {}}

        # Find shell scripts
        for script_path in self.workspace.rglob("*.sh"):
            shell_results["scripts_found"].append(str(script_path))

            # Run shellcheck on each script
            shellcheck_result = self.run_command(["shellcheck", str(script_path)])
            shell_results["shellcheck_results"][str(script_path)] = {
                "success": shellcheck_result["success"],
                "output": shellcheck_result["stdout"],
                "errors": shellcheck_result["stderr"],
            }

        return shell_results

    def verify_launchagents(self) -> Dict[str, Any]:
        """Verify LaunchAgent plist files."""
        launchagent_results = {"plists_found": [], "validation_results": {}, "log_checks": {}}

        # Find plist files
        for plist_path in self.workspace.rglob("*.plist"):
            launchagent_results["plists_found"].append(str(plist_path))

            # Validate plist syntax
            plutil_result = self.run_command(["plutil", "-lint", str(plist_path)])
            launchagent_results["validation_results"][str(plist_path)] = {
                "success": plutil_result["success"],
                "output": plutil_result["stdout"],
            }

            # Check associated logs
            log_result = self.run_command(
                ["log", "show", "--predicate", f"process == '{plist_path.stem}'", "--last", "1h"]
            )
            launchagent_results["log_checks"][str(plist_path)] = {
                "success": log_result["success"],
                "output": log_result["stdout"],
            }

        return launchagent_results

    def count_errors_and_warnings(self) -> None:
        """Count total errors and warnings across all checks."""
        error_count = 0
        warning_count = 0

        # Count Node.js issues
        node_checks = self.results["node_checks"]
        for check_name, check_data in node_checks.items():
            if isinstance(check_data, dict) and "errors" in check_data:
                error_count += len(check_data["errors"])
            if isinstance(check_data, dict) and "warnings" in check_data:
                warning_count += len(check_data["warnings"])

        # Count Python issues
        python_checks = self.results["python_checks"]
        for check_name, check_data in python_checks.items():
            if isinstance(check_data, dict) and "errors" in check_data:
                error_count += len(check_data["errors"])
            if isinstance(check_data, dict) and "warnings" in check_data:
                warning_count += len(check_data["warnings"])

        # Count Shell issues
        shell_checks = self.results["shell_checks"]
        if "shellcheck_results" in shell_checks:
            for script, result in shell_checks["shellcheck_results"].items():
                if not result["success"]:
                    error_count += 1

        # Count LaunchAgent issues
        launchagent_checks = self.results["launchagent_checks"]
        if "validation_results" in launchagent_checks:
            for plist, result in launchagent_checks["validation_results"].items():
                if not result["success"]:
                    error_count += 1

        self.results["error_count"] = error_count
        self.results["warning_count"] = warning_count

    def perform_verification_pass(self, pass_number: int) -> None:
        """Perform a complete verification pass."""
        print(f"Starting verification pass {pass_number}...")

        # Node.js verification
        self.results["node_checks"] = self.verify_node_ecosystem()

        # Python verification
        self.results["python_checks"] = self.verify_python_ecosystem()

        # Shell script verification
        self.results["shell_checks"] = self.verify_shell_scripts()

        # LaunchAgent verification
        self.results["launchagent_checks"] = self.verify_launchagents()

        # Count issues
        self.count_errors_and_warnings()

        # Determine pass result
        pass_successful = self.results["error_count"] == 0 and self.results["warning_count"] == 0

        self.results["verification_passes"].append(
            {
                "pass_number": pass_number,
                "success": pass_successful,
                "error_count": self.results["error_count"],
                "warning_count": self.results["warning_count"],
            }
        )

        print(f"Pass {pass_number} completed: {'SUCCESS' if pass_successful else 'FAILED'}")
        print(f"Errors: {self.results['error_count']}, Warnings: {self.results['warning_count']}")

    def run_two_pass_verification(self) -> None:
        """Execute two-pass verification system."""
        # First pass
        self.perform_verification_pass(1)

        # Second pass
        self.perform_verification_pass(2)

        # Determine overall status
        all_passes_successful = all(pass_result["success"] for pass_result in self.results["verification_passes"])

        self.results["overall_status"] = "SUCCESS" if all_passes_successful else "FAILED"

    def output_json_status(self) -> None:
        """Output final JSON status only."""
        print(json.dumps(self.results, indent=2))


def main() -> None:
    """Main verification execution."""
    if len(sys.argv) != 2:
        print("Usage: verify_system.py <workspace_path>")
        sys.exit(1)

    workspace_path = sys.argv[1]

    verifier = SystemVerifier(workspace_path)
    verifier.run_two_pass_verification()
    verifier.output_json_status()


if __name__ == "__main__":
    main()
