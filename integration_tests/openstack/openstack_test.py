
def test_openstack(openstack_connection):
    counter = 0
    for image in openstack_connection.compute.images():
        assert(image)
        counter += 1
    assert(counter > 0)
