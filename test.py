# @Author  : yanchunhuo
# @Time    : 2020/1/16 15:32
from dubbo.client import ZkRegister
from dubbo.client import DubboClient
if __name__=='__main__':
    zk=ZkRegister('zookeeper.szy.com:2181',application_name='auto_test')
    dubboClient=DubboClient('com.ztjy.familybase.facade.IFamilyUserFacade',zk_register=zk)
    result=dubboClient.call('getFamilyUser',('921a470914bb0bd6bb12',))