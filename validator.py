#!/usr/bin/env python3
"""
Safe YOLO Agent - Permission Validator

Validates operations against allowlist before execution.
Usage: python validator.py <operation> <params>
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

class PermissionValidator:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent / "permissions" / "allowlist.json"
        
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.audit_log = Path.home() / ".safe-yolo" / "audit.log"
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)
    
    def log_operation(self, operation, params, result, reason=""):
        """Log operation to audit file"""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "operation": operation,
            "params": str(params),
            "result": result,
            "reason": reason
        }
        with open(self.audit_log, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def check_shell_command(self, command):
        """Validate shell command against allowlist"""
        shell_config = self.config["shell_allowlist"]
        
        # Check blocked patterns first
        for pattern in shell_config["blocked_patterns"]:
            if pattern in command:
                return False, f"BLOCKED: Matches dangerous pattern '{pattern}'"
        
        # Check blocked paths
        for blocked_path in shell_config["blocked_paths"]:
            if blocked_path in command:
                return False, f"BLOCKED: Access to system path '{blocked_path}'"
        
        # Check if confirmation required
        for require_confirm in shell_config["require_confirm"]:
            if command.startswith(require_confirm):
                return "CONFIRM", f"CONFIRM: '{require_confirm}' requires user approval"
        
        # Check if command is in safe list
        base_cmd = command.split()[0] if command.split() else ""
        if base_cmd in shell_config["safe_commands"]:
            return True, "ALLOWED"
        
        return False, f"BLOCKED: Command '{base_cmd}' not in allowlist"
    
    def check_file_write(self, file_path):
        """Validate file write operation"""
        file_rules = self.config["file_write_rules"]
        
        # Check blocked paths
        for blocked_path in file_rules["blocked_paths"]:
            if blocked_path in file_path:
                return False, f"BLOCKED: Cannot write to '{blocked_path}'"
        
        # Check if confirmation required
        for require_confirm in file_rules["require_confirm_paths"]:
            if require_confirm in file_path:
                return "CONFIRM", f"CONFIRM: Writing to '{require_confirm}'"
        
        # Check extension
        ext = Path(file_path).suffix
        if ext not in file_rules["allowed_extensions"]:
            return False, f"BLOCKED: Extension '{ext}' not allowed"
        
        return True, "ALLOWED"
    
    def check_network(self, url):
        """Validate network request"""
        network_rules = self.config["network_rules"]
        
        # Simple domain check
        for domain in network_rules["allowed_domains"]:
            if domain in url:
                return True, "ALLOWED"
        
        for domain in network_rules["require_confirm_domains"]:
            if domain in url:
                return "CONFIRM", f"CONFIRM: Accessing '{domain}'"
        
        return False, "BLOCKED: Domain not in allowlist"
    
    def validate(self, operation, params):
        """Main validation entry point"""
        if operation == "run_shell_command":
            result, reason = self.check_shell_command(params.get("command", ""))
        elif operation == "write_file":
            result, reason = self.check_file_write(params.get("file_path", ""))
        elif operation in ["web_fetch", "web_search"]:
            result, reason = self.check_network(params.get("url", params.get("query", "")))
        else:
            result = operation in self.config["allowed_tools"].get("read_operations", [])
            result = result or operation in self.config["allowed_tools"].get("write_operations", [])
            reason = "ALLOWED" if result else "BLOCKED: Operation not in allowlist"
        
        self.log_operation(operation, params, result, reason)
        return result, reason


def main():
    if len(sys.argv) < 3:
        print("Usage: python validator.py <operation> <params_json>")
        print("Example: python validator.py run_shell_command '{\"command\": \"ls -la\"}'")
        sys.exit(1)
    
    validator = PermissionValidator()
    operation = sys.argv[1]
    
    try:
        params = json.loads(sys.argv[2])
    except json.JSONDecodeError:
        params = {"command": sys.argv[2]}
    
    result, reason = validator.validate(operation, params)
    
    print(f"Operation: {operation}")
    print(f"Params: {params}")
    print(f"Result: {reason}")
    
    if result == "CONFIRM":
        response = input("\nProceed? (y/n): ")
        if response.lower() != "y":
            print("Operation cancelled by user")
            sys.exit(1)
    elif result is False:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
