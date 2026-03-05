import re
import subprocess
from pathlib import Path

import pytest


def _extract_paths(auditd_rule):
    path_re = re.compile(
        r"""
        (
            -F\s*
            (?:path|dir)=([^ ]+)
        )
        """,
        re.VERBOSE,
    )
    return [match[0] for match in path_re.findall(auditd_rule)]


# support for this format: -S mknod,chroot,mount,umount2,mknodat,mount_setattr
def _extract_syscalls(auditd_rule):
    sc_re = re.compile(
        r"""
        (
            -S\s*
            (\S+)
        )
        """,
        re.VERBOSE,
    )
    return [
        syscall
        for match in sc_re.findall(auditd_rule)
        for syscall in match[0].split(",")
    ]


def _access_types_included(auditd_rule, access_types):
    path_re = re.compile(
        r"""
        (
            -F\s*perm=
            (\S+)
            |
            -p\s*
            (\S+)
        )
        """,
        re.VERBOSE,
    )
    results = [
        match
        for match in path_re.findall(auditd_rule)
        if set(access_types).issubset(set(match[0]))
    ]
    return bool(results)


@pytest.fixture
def audit_rule():
    def _audit_rule(syscall=None, access_types=None, fs_watch_path=None):
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
        rules = result.stdout.splitlines()

        def file_path_audit_rule():
            print(
                f"File path audit rule for {fs_watch_path} with access {access_types}"
            )
            file_path_rules = [
                rule
                for rule in rules
                if rule.startswith("-w ")
                if Path(fs_watch_path).is_relative_to(  # pyright: ignore
                    rule.split()[1]
                )
                if _access_types_included(rule, access_types)
            ]
            if file_path_rules:
                print(f"Matched file path rules: {file_path_rules}")
                return True

            file_syscall_rules = [
                rule for rule in rules if "-F path=" in rule or "-F dir=" in rule
            ]
            matching_file_syscall_rules = [
                rule
                for rule in file_syscall_rules
                for path in _extract_paths(rule)
                if Path(fs_watch_path).is_relative_to(path)  # pyright: ignore
                if _access_types_included(rule, access_types)
            ]
            if matching_file_syscall_rules:
                print(f"Matched file syscall rules: {matching_file_syscall_rules}")
                return True
            return False

        def syscall_audit_rule():
            print(f"Syscall audit rule for {syscall}")
            matched_rules = [
                rule
                for rule in rules
                for rule_syscall in _extract_syscalls(rule)
                if syscall in rule_syscall
            ]
            if matched_rules:
                print(f"Matched syscall rules: {matched_rules}")
                return True
            return False

        if fs_watch_path and access_types:
            return file_path_audit_rule()
        if syscall:
            return syscall_audit_rule()

    return _audit_rule
