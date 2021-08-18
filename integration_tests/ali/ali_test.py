import json
import pytest
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest

def test_ali_instances(ali_client):
    region_id = ali_client.get_region_id()
    assert(region_id == 'eu-central-1')
    
    request = DescribeInstancesRequest.DescribeInstancesRequest()
    request.set_PageSize(10)

    response = ali_client.do_action_with_exception(request)
    instances_dict = json.loads(response.decode())
    assert(len(instances_dict) > 0)
    inst = instances_dict['Instances']['Instance'][0]
    assert(inst)
    assert(inst['RegionId'] == region_id)