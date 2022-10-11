import pytest
import re
from helper.sshclient import RemoteClient

def test_random(client, non_metal):
    (exit_code, output, error) = client.execute_command("time dd if=/dev/random of=/dev/null bs=8k count=1000 iflag=fullblock", disable_sudo=True)
    """ Output should be like this:
# time dd if=/dev/random of=/dev/null bs=8k count=1000 iflag=fullblock
1000+0 records in
1000+0 records out
8192000 bytes (8.2 MB, 7.8 MiB) copied, 0.0446423 s, 184 MB/s

real    0m0.046s
user    0m0.004s
sys     0m0.042s
"""

    assert exit_code == 0, f"no {error=} expected"
    lines = error.splitlines()
    bycount = lines[2].split(" ")[0]
    assert bycount == "8192000", "byte cound expected to be 8192000 but is %s" % bycount
    real = lines[4].split()[1]
    pt=r'(\d+)m(\d+)'
    m=re.search(pt, real)
    duration = (int(m.group(1)) * 60) + int(m.group(2))
    assert duration == 0, "runtime of test expected to be below one second %s" % m.group(1)

    (exit_code, output, error) = client.execute_command("time rngtest --blockcount=9000  < /dev/random", disable_sudo=True)
    """ Output should be like this:
# time rngtest --blockcount=9000  < /dev/random
rngtest 5
Copyright (c) 2004 by Henrique de Moraes Holschuh
This is free software; see the source for copying conditions.  There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

rngtest: starting FIPS tests...
rngtest: bits received from input: 180000032
rngtest: FIPS 140-2 successes: 8992
rngtest: FIPS 140-2 failures: 8
rngtest: FIPS 140-2(2001-10-10) Monobit: 1
rngtest: FIPS 140-2(2001-10-10) Poker: 2
rngtest: FIPS 140-2(2001-10-10) Runs: 2
rngtest: FIPS 140-2(2001-10-10) Long run: 3
rngtest: FIPS 140-2(2001-10-10) Continuous run: 0
rngtest: input channel speed: (min=167.311; avg=1321.184; max=1467.191)Mibits/s
rngtest: FIPS tests speed: (min=24.965; avg=138.842; max=145.599)Mibits/s
rngtest: Program run time: 1367504 microseconds

real    0m1.370s
user    0m1.260s
sys     0m0.108s
"""
    # a few test will most certainly always fail, therefore we expect an
    # error
    # assert exit_code == 0, f"no {error=} expected"
    p_succ=r'rngtest: FIPS 140-2 successes: (\d+)'
    m=re.search(p_succ, error)
    successes = int(m.group(1))
    assert successes >8980, "Number of successes expected to be greater than 8980"

    p_fail=r'rngtest: FIPS 140-2 failures: (\d+)'
    m=re.search(p_fail, error)
    failures = int(m.group(1))
    assert failures <= 20, "Number of failures expected ot be less than or equal to 20"

    assert successes + failures == 9000, "sanity check failed"

    p_real=r'real\s+(\d+)m(\d+)'
    m=re.search(p_real, error)
    duration = (int(m.group(1)) * 60) + int(m.group(2))
    assert duration < 5, "Expected the test to run in less than 5 seconds"
