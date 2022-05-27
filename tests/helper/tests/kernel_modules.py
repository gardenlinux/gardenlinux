import helper.utils as utils


def kernel_modules(client, kernel_mod_file):
    """Validate if the wirefuard kernel module is present"""
    # Get running kernel version
    kernel_ver = utils.get_kernel_version(client)

    # Create path to wireguard kernel module
    kernel_mod_path = f"/lib/modules/{kernel_ver}/kernel/drivers/"
    kernel_module = f"{kernel_mod_path}{kernel_mod_file}"

    # Get file permission if present
    permission = utils.get_file_perm(client, kernel_module)

    assert permission is not None, f"Kernel module not found : {kernel_mod_file}"
