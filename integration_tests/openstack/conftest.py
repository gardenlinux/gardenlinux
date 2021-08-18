from dataclasses import dataclass
import glci.util
import ci.util
import  openstack
import pytest

# https://docs.openstack.org/openstacksdk/latest/user/index.html
 
@dataclass
class OpenstackCfg:
    auth_url: str
    domain: str
    project_name: str
    password: str
    region_name: str
    username: str


@pytest.fixture(scope="session")
def openstack_cfg(): 
    cfg_factory = ci.util.ctx().cfg_factory()
    cicd_cfg = glci.util.cicd_cfg()
    openstack_environments_cfg = cfg_factory.ccee(cicd_cfg.publish.openstack.environment_cfg_name)

    test_region = 'eu-de-1'
    openstack_envs = [project for project in openstack_environments_cfg.projects() 
                        if project.region() == test_region]
    if  not openstack_envs:
        print(f'Could not find region for testing: {test_region}')
        return
    assert(openstack_envs)

    openstack_env = openstack_envs[0] # model.ccee.CCEEProject
    return OpenstackCfg(
        auth_url=openstack_env.auth_url(),
        domain=openstack_env.domain(),
        project_name=openstack_env.name(),
        password=openstack_environments_cfg.credentials().passwd(),
        region_name=openstack_env.region(),
        username=openstack_environments_cfg.credentials().username(),
    )


@pytest.fixture(scope="session")
def openstack_connection(openstack_cfg): 
    return openstack.connect(
                auth_url=openstack_cfg.auth_url,
                project_name=openstack_cfg.project_name,
                username=openstack_cfg.username,
                password=openstack_cfg.password,
                region_name=openstack_cfg.region_name,
                user_domain_name=openstack_cfg.domain,
                project_domain_name=openstack_cfg.domain,
            )
