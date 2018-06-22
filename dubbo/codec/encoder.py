# -*- coding: utf-8 -*-
"""
把Python的数据结构根据Hessian协议序列化为相应的字节数组
当前支持的数据类型：
* bool
* int
* long
* float
* double
* java.lang.String
* java.lang.Object
"""
import struct

from dubbo.common.constants import DEFAULT_REQUEST_META, INT_DIRECT_MAX, INT_DIRECT_MIN, BC_INT_ZERO, INT_BYTE_MAX, \
    INT_BYTE_MIN, BC_INT_BYTE_ZERO, INT_SHORT_MIN, INT_SHORT_MAX, BC_INT_SHORT_ZERO, BC_DOUBLE_ZERO, BC_DOUBLE_ONE, \
    BC_DOUBLE_BYTE, BC_DOUBLE_MILL, STRING_DIRECT_MAX, BC_STRING_DIRECT, STRING_SHORT_MAX, BC_STRING_SHORT, \
    BC_DOUBLE_SHORT, MIN_INT_32, MAX_INT_32
from dubbo.common.exceptions import HessianTypeError
from dubbo.common.util import double_to_long_bits, num_2_byte_list


class Object(object):
    """
    创建一个Java对象
    """

    def __init__(self, path):
        """
        :param path: Java对象的路径，例如：java.lang.Object
        """
        if not isinstance(path, str):
            raise ValueError('Object path {} should be string type.'.format(path))
        self.__path = path
        self.__values = {}

    def __getitem__(self, key):
        return self.__values[key]

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise ValueError('Object key {} should be string type.'.format(key))
        self.__values[key] = value

    def __delitem__(self, key):
        del self.__values[key]

    def __repr__(self):
        return '<{}>'.format(self.__path)

    def __contains__(self, key):
        return key in self.__values

    def keys(self):
        return self.__values.keys()

    def get_path(self):
        return self.__path


class Request(object):
    def __init__(self, request):
        self.__body = request
        self.__classes = []

    def encode(self):
        """
        把请求序列化为字节数组
        :return:
        """
        request_body = self._encode_request_body()
        request_head = DEFAULT_REQUEST_META + get_request_body_length(request_body)
        return bytearray(request_head + request_body)

    @staticmethod
    def _get_parameter_types(arguments):
        """
        针对所有的参数计算得到参数类型字符串
        :param arguments:
        :return:
        """
        parameter_types = ''
        # 判断并得出参数的类型
        for argument in arguments:
            if isinstance(argument, bool):  # bool类型的判断必须放在int类型判断的前面
                parameter_types += 'Z'
            elif isinstance(argument, int):
                if MIN_INT_32 <= argument <= MAX_INT_32:
                    parameter_types += 'I'
                else:
                    parameter_types += 'J'
            elif isinstance(argument, float):
                parameter_types += 'D'
            elif isinstance(argument, str):
                parameter_types += 'Ljava/lang/String;'
            elif isinstance(argument, Object):
                path = argument.get_path()
                path = 'L' + path.replace('.', '/') + ';'
                parameter_types += path
            else:
                raise HessianTypeError('Unknown argument type: {0}'.format(argument))
        return parameter_types

    def _encode_request_body(self):
        """
        对所有的已知的参数根据dubbo协议进行编码
        :return:
        """
        dubbo_version = self.__body['dubbo_version']
        path = self.__body['path']
        version = self.__body['version']
        method = self.__body['method']
        arguments = self.__body['arguments']

        body = []
        body.extend(self._encode_single_value(dubbo_version))
        body.extend(self._encode_single_value(path))
        body.extend(self._encode_single_value(version))
        body.extend(self._encode_single_value(method))
        body.extend(self._encode_single_value(self._get_parameter_types(arguments)))
        for argument in arguments:
            body.extend(self._encode_single_value(argument))

        attachments = {
            'path': path,
            'interface': path,
            'version': version
        }
        # attachments参数以H开头，以Z结尾
        body.append(ord('H'))
        for key in attachments.keys():
            value = attachments[key]
            body.extend(self._encode_single_value(key))
            body.extend(self._encode_single_value(value))
        body.append(ord('Z'))

        # 因为在上面的逻辑中没有对byte大小进行检测，所以在这里进行统一的处理
        for i in range(len(body)):
            body[i] = body[i] & 0xff
        return body

    def _encode_single_value(self, value):
        """
        根据hessian协议对单个变量进行编码
        :param value:
        :return:
        """
        result = []
        # 布尔类型
        if isinstance(value, bool):
            if value:
                result.append(ord('T'))
            else:
                result.append(ord('F'))
            return result
        # 整型（包括长整型）
        elif isinstance(value, int):
            if value > MAX_INT_32 or value < MIN_INT_32:
                result.append(ord('L'))
                result.extend(list(bytearray(struct.pack('>q', value))))
                return result

            if INT_DIRECT_MIN <= value <= INT_DIRECT_MAX:
                result.append(value + BC_INT_ZERO)
            elif INT_BYTE_MIN <= value <= INT_BYTE_MAX:
                result.append(BC_INT_BYTE_ZERO + (value >> 8))
                result.append(value)
            elif INT_SHORT_MIN <= value <= INT_SHORT_MAX:
                result.append(BC_INT_SHORT_ZERO + (value >> 16))
                result.append(value >> 8)
                result.append(value)
            else:
                result.append(ord('I'))
                result.append(value >> 24)
                result.append(value >> 16)
                result.append(value >> 8)
                result.append(value)
            return result
        # 浮点类型
        elif isinstance(value, float):
            int_value = int(value)
            if int_value == value:
                if int_value == 0:
                    result.append(BC_DOUBLE_ZERO)
                    return result
                elif int_value == 1:
                    result.append(BC_DOUBLE_ONE)
                    return result
                elif -0x80 <= int_value < 0x80:
                    result.append(BC_DOUBLE_BYTE)
                    result.append(int_value)
                    return result
                elif -0x8000 <= int_value < 0x8000:
                    result.append(BC_DOUBLE_SHORT)
                    result.append(int_value >> 8)
                    result.append(int_value)
                    return result

            mills = int(value * 1000)
            if 0.001 * mills == value and MIN_INT_32 <= mills <= MAX_INT_32:
                result.append(BC_DOUBLE_MILL)
                result.append(mills >> 24)
                result.append(mills >> 16)
                result.append(mills >> 8)
                result.append(mills)
                return result

            bits = double_to_long_bits(value)
            result.append(ord('D'))
            result.append(bits >> 56)
            result.append(bits >> 48)
            result.append(bits >> 40)
            result.append(bits >> 32)
            result.append(bits >> 24)
            result.append(bits >> 16)
            result.append(bits >> 8)
            result.append(bits)
            return result
        # 字符串类型
        elif isinstance(value, str):
            # 根据hessian协议这里的长度必须是字符串长度而不是字节长度，所以需要Unicode类型
            length = len(value.decode('utf-8'))
            if length <= STRING_DIRECT_MAX:
                result.append(BC_STRING_DIRECT + length)
            elif length <= STRING_SHORT_MAX:
                result.append(BC_STRING_SHORT + (length >> 8))
                result.append(length)
            else:
                result.append(ord('S'))
                result.append(length >> 8)
                result.append(length)
            result.extend(list(bytearray(value)))  # 加上变量数组
            return result
        # 对象类型
        elif isinstance(value, Object):
            path = value.get_path()
            field_names = value.keys()

            if path not in self.__classes:
                result.append(ord('C'))
                result.extend(self._encode_single_value(path))

                result.extend(self._encode_single_value(len(field_names)))

                for field_name in field_names:
                    result.extend(self._encode_single_value(field_name))
                self.__classes.append(path)
            class_id = self.__classes.index(path)
            if class_id <= 0xf:
                class_id += 0x60
                class_id &= 0xff
                result.append(class_id)
            else:
                result.append(ord('O'))
                result.extend(self._encode_single_value(class_id))
            for field_name in field_names:
                result.extend(self._encode_single_value(value[field_name]))
            return result
        else:
            raise HessianTypeError('Unknown argument type: {0}'.format(value))


def get_request_body_length(body):
    """
    获取body的长度，并将其转为长度为4个字节的字节数组
    :param body:
    :return:
    """
    request_body_length = num_2_byte_list(len(body))
    # 用4个字节表示请求body的长度
    while len(request_body_length) < 4:
        request_body_length = [0] + request_body_length
    return request_body_length


if __name__ == '__main__':
    o = Object('java.lang.Object')
    o['name'] = '张三'
    o['age'] = 20
    print o.keys()
    print '111' in o
    print o