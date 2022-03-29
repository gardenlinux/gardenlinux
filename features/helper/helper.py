import os
import re

class Helper:
    def get_package_list(client):
        (exit_code, output, error) = client.execute_command("dpkg -l")
        assert exit_code == 0, f"no {error=} expected"
        pkgslist = []
        for line in output.split('\n'):
            if not line.startswith('ii'):
                continue
            pkg = line.split('  ')
            if len(pkg) > 1:
                pkgslist.append(pkg[1])
        return pkgslist


    def read_test_config(features, testname, suffix):
        config = []
        for feature in features:
            path = ("/gardenlinux/features/%s/test/%s.d/%s%s" % (feature, testname, testname, suffix))
            if os.path.isfile(path):
                file = open(path, 'r')
                for line in file:
                    if line.startswith('#'):
                        continue
                    if re.match(r'^\s*$', line):
                        continue
                    config.append(line.strip('\n'))
        return config