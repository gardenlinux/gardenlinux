import itertools
import logging
import subprocess
from pathlib import Path

import pytest
from plugins.dpkg import Dpkg

logger = logging.getLogger(__name__)


class AuditRule:
    def __init__(self):
        if not Dpkg().package_is_installed("auditd"):
            raise RuntimeError("auditd is not installed")
        try:
            result = subprocess.run(
                ["auditctl", "-l"],
                capture_output=True,
                text=True,
                check=True,
            )
        except FileNotFoundError:
            raise RuntimeError("auditctl not found in PATH")
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"auditctl failed (exit {exc.returncode})\n"
                f"stderr: {exc.stderr.strip()}"
            )
        self.rules = self._parse(result.stdout.splitlines())

    def _parse(self, auditctl_lines):
        return [self._parse_line(line) for line in auditctl_lines]

    def _parse_line(self, auditctl_line):
        """
        Split a line looking like this

        -a exit,always -S open,unlink,rmdir -S truncate -F dir=/etc -F success=0

        into a dict like this

        {'-a': ['exit', 'always'],
         '-S': ['open', 'unlink', 'rmdir', 'truncate'],
         '-F': ['dir=/etc', 'success=0']}
        """
        result = {}
        for key, value in itertools.batched(auditctl_line.split(), 2):
            result.setdefault(key, []).extend(value.split(","))
        return result

    def _extract_paths(self, auditd_rule):
        """
        Return a list of file paths referred by -F path= or -F dir= arguments in the auditd rule.
        """
        return [
            field.split("=")[1]
            for field in auditd_rule["-F"]
            if "path=" in field or "dir=" in field
        ]

    def _filter_by_rule_fields(self, rules, rule_fields):
        if not rule_fields:
            return rules
        return [
            rule
            for rule_field in rule_fields
            for rule in rules
            if "-F" in rule.keys()
            if rule_field in rule["-F"]
        ]

    def file_path_audit_rule(self, fs_watch_path, access_types):
        logger.debug(
            f"File path audit rule for {fs_watch_path} with access {access_types}"
        )
        file_path_rules = [
            rule
            for rule in self.rules
            if "-w" in rule.keys()
            if Path(fs_watch_path).is_relative_to(rule["-w"][0])  # pyright: ignore
            if set(access_types).issubset(rule["-p"][0])
        ]
        if file_path_rules:
            logger.debug(f"Matched file path rules: {file_path_rules}")
            return True

        file_syscall_rules = [
            rule
            for rule in self.rules
            if "-F" in rule
            if "path=" in rule["-F"] or "dir=" in rule["-F"]
        ]
        matching_file_syscall_rules = [
            rule
            for rule in file_syscall_rules
            for path in self._extract_paths(rule)
            if Path(fs_watch_path).is_relative_to(path)  # pyright: ignore
            if set(access_types).issubset(rule["-p"][0])
        ]
        if matching_file_syscall_rules:
            logger.debug(f"Matched file syscall rules: {matching_file_syscall_rules}")
            return True
        return False

    def syscall_audit_rule(self, syscall, rule_fields):
        logger.debug(f"Syscall audit rule for {syscall}")
        matched_rules = [
            rule for rule in self.rules if "-S" in rule.keys() if syscall in rule["-S"]
        ]

        filtered_rules = self._filter_by_rule_fields(matched_rules, rule_fields)

        if filtered_rules:
            logger.debug(f"Matched syscall rules: {filtered_rules}")
            return True
        return False

    def binary_call_audit_rule(self, binary_path, rule_fields):
        logger.debug(f"Binary call audit rule for {binary_path} | {rule_fields=}")
        matched_rules = [
            rule
            for rule in self.rules
            if "-S" in rule.keys()
            if "-F" in rule.keys()
            if "execve" in rule["-S"]
            if f"exe={binary_path}" in rule["-F"]
        ]

        filtered_rules = self._filter_by_rule_fields(matched_rules, rule_fields)

        if filtered_rules:
            logger.debug(f"Matched binary call rules: {filtered_rules}")
            return True
        return False

    def __call__(
        self,
        syscall=None,
        access_types=None,
        fs_watch_path=None,
        binary_call=None,
        rule_fields=[],
    ):
        logger.debug("In AuditRule.__call__")
        if fs_watch_path and access_types:
            return self.file_path_audit_rule(fs_watch_path, access_types)
        if syscall:
            return self.syscall_audit_rule(syscall, rule_fields)
        if binary_call:
            return self.binary_call_audit_rule(binary_call, rule_fields)


@pytest.fixture
def audit_rule():
    """
    Returns an object that, when called, returns an audit rule lookup function.
    Said object calls a file path audit rule lookup function
    if fs_watch_path and access_type arguments are not empty
    or a syscall audit rule lookup function if syscall argument is not empty.

    For a file path audit rule the lookup is successful (function return True)
    if and only if there is at least one auditd rule that covers the provided fs_watch_path
    and access_types' values. Given that auditd file path rules are recursive, a lookup for /etc/passwd
    will be successful if there's a rule for /etc with matching access_types.

    For a syscall audit rule the lookup is successful
    if there is at least one auditd rule that concerns the syscall parameter's value.

    For an audit rule that tracks when a certain binary is executed the lookup is successful
    if a rule with 'execve' syscall and the provided binary path (binary_call argument) is found.

    Examples:

    assert audit_rule(fs_watch_path="/etc/passwd", access_types="wa")
    assert audit_rule(syscall="setcap", rule_fields=["auid>=1000", "auid!=1"])
    assert audit_rule(binary_call="/usr/bin/passwd")
    """
    return AuditRule()
