
def test_vms(compute_client):
    vm_list = compute_client.virtual_machines.list_all()
    assert(vm_list)
    for vm in vm_list:
        assert(vm)
        assert(len(vm.name) > 0)

def test_storage(storage_client):
    accounts =  storage_client.storage_accounts.list_by_resource_group('garden-linux')
    assert(accounts)
    # for account in accounts:
    #     print(account)
    account_name = accounts.next().name
    print(account_name)
    container_items = storage_client.blob_containers.list(
        resource_group_name='garden-linux',
        account_name=account_name #'gardenlinuxdev'
    )
    
    counter = 0
    for item in container_items:
        counter += 1
        print(f'{item.name=}')
    assert(counter > 0)        