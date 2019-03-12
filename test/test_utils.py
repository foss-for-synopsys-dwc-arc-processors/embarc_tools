from __future__ import print_function, division
from embarc_tools.utils import *
from embarc_tools.osp import osp
import unittest
import os


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def test_flatten(self):
        l1 = [['aa', 'bb', ['cc', 'dd', 'ee'], ['ee', 'ff'], 'gg']]
        assert list(flatten(l1)) == ['aa', 'bb', 'cc', 'dd', 'ee', 'ee', 'ff', 'gg']
        assert uniqify(flatten(l1)) == ['aa', 'bb', 'cc', 'dd', 'ee', 'ff', 'gg']

    def test_uniqify(self):
        l1 = ['a', 'b', 'b', 'c', 'b', 'd', 'c', 'e', 'f', 'a']
        assert uniqify(l1) == ['a', 'b', 'c', 'd', 'e', 'f']

    def test_load_yaml_records(self):
        ospclass = osp.OSP()
        f = [os.path.join(ospclass.path, ospclass.file)]
        dictionaries = load_yaml_records(f)
        assert len(dictionaries) > 0

    def test_merge_recursive(self):
        data1 = {"a": 1, "b": 2}
        data2 = {"c": 3, "b": 2}
        output = merge_recursive(data1, data2)
        print(output)
        data3 = [4, 5]
        output = merge_recursive(data1, data2)
        print(output)

    def test_popen(self):
        command = ["python", "-V"]
        self.assertIsNone(popen(command))

    def test_pquery(self):
        command = ["python", "-V"]
        output = pquery(command)
        print(output)
        # self.assertEqual(output, ".0.0.1")

    def tearDown(self):
        pass
