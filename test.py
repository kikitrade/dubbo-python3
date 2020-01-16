# @Author  : yanchunhuo
# @Time    : 2020/1/16 15:32
from dubbo.client import ZkRegister
from dubbo.client import DubboClient
if __name__=='__main__':
    zk=ZkRegister('zookeeper.szy.com:2181',application_name='auto_test')
    # dubboClient=DubboClient('com.ztjy.familybase.facade.IFamilyUserFacade',zk_register=zk,group='test')
    # result=dubboClient.call('getFamilyUser',('921a470914bb0bd6bb12',))
    # print(result)

    dubboClient = DubboClient('com.ztjy.familybase.facade.IFamilyUserFacade', zk_register=zk, group='test',dubbo_version='2.6.0')
    result = dubboClient.call('batchFamilyUserDetail', ["921a470914bb0bd6bb12","7c97d54181a1b9ef2c96"])
    print(result)