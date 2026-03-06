import re
import subprocess
from pathlib import Path

import pytest


def _extract_paths(auditd_rule):
    """
    Return a list of file paths referred by -F path= or -F dir= arguments in the auditd rule.
    """
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


def _extract_syscalls(auditd_rule):
    """
    Return a list of syscalls referred by -S arguments in the auditd rule.
    Note there can be more than one syscall following an -S argument.

    For example for an auditd_rule that contains "-S mknod,chroot,mount,umount2,mknodat,mount_setattr"
    this function will return ["mknod", "chroot", "mount", "umount2", "mknodat", "mount_setattr"]
    """
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
    """
    Return true if access types are included in full in the auditd rule.
    Here access_types is a string in the format passed to auditctl's -p option
    (see: man auditctl)

    For example, this function will return true if access_types' parameter value is "wa"
    and the auditd_rule has "wa", "war", "warx" etc,
    but will return false if auditd_rule has "w", "a" or "x" etc.
    """
    path_re = re.compile(
        r"""
        (
            -F\s*perm=(\S+)
            |
            -p\s *
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
    """
    Returns a factory function that, when called, returns an audit rule lookup function.
    Said factory function returns a file path audit rule lookup function
    if fs_watch_path and access_type arguments are not empty
    or a syscall audit rule lookup function if syscall argument is not empty.

    For a file path audit rule the lookup is successful (function return True)
    if and only if there is at least one auditd rule that covers the provided fs_watch_path
    and access_types' values. Given that auditd file path rules are recursive, a lookup for /etc/passwd
    will be successful if there's a rule for /etc with matching access_types.

    For a syscall audit rule the lookup is successful
    if there is at least one auditd rule that concerns the syscall parameter's value.

    Examples:

    assert audit_rule(fs_watch_path="/etc/passwd", access_types="wa")
    assert audit_rule(syscall="setcap")

    """

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
