import re

def _seconds(token):
	if token.endswith("ms"):
		return float(token[:-2]) / 1000
	if token.endswith("s"):
		return float(token[:-1])
	raise ValueError(f"Unknown time unit in '{token}'")

def get_startup_durations(shell):
	output = shell("systemd-analyze", capture_output=True).stdout
	summary = output.splitlines()[0]

	m = re.search(
		r"([\d.]+[a-z]+)\s+\(kernel\).*?"
		r"([\d.]+[a-z]+)\s+\(initrd\).*?"
		r"([\d.]+[a-z]+)\s+\(userspace\)",
		summary,
	)
	if not m:
		raise ValueError(f"Unexpected systemd-analyze output: {summary}")

	return tuple(_seconds(v) for v in m.groups())
