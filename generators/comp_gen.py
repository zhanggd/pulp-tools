#
# Copyright (C) 2018 ETH Zurich and University of Bologna
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Authors: Germain Haugou, ETH (germain.haugou@iis.ee.ethz.ch)

import json
from collections import OrderedDict


class Interface(object):

    def __init__(self, comp, name):
        self.name = name
        self.comp = comp


class Component(object):

    def __init__(self, includes=None):
        self.__dict__['_Component__comps'] = OrderedDict()
        self.__dict__['_Component__master_itfs'] = OrderedDict()
        self.__dict__['_Component__slave_itfs'] = OrderedDict()
        self.__dict__['_Component__includes'] = includes

    def get_master_itfs(self):
        return self.__dict__['_Component__master_itfs']

    def set_name(self, name):
        self.__dict__['_Component__name'] = name

    def get_name(self):
        return self.__dict__['_Component__name']

    def get_json_config(self):
        return json.dumps(self.gen(), indent='  ')

    def __setattr__(self, name, value):
        if type(value) == Interface:
            self.__dict__['_Component__master_itfs'][name] = value
        else:
            self.__dict__['_Component__comps'][name] = value
            self.__dict__[name] = value
            value.set_name(name)

    def __getattr__(self, name):
        if self.__dict__.get(name) is None:
            itf = Interface(self, name)
            self.__dict__['_Component__slave_itfs'][name] = itf
            return itf
        else:
            return self.__dict__[name]

    def gen(self):
        result = OrderedDict()

        includes = self.__dict__['_Component__includes']
        if includes is not None:
            result["includes"] = includes

        comps = list(self.__dict__['_Component__comps'])
        if len(comps) != 0:
            result["vp_comps"] = comps

        bindings = []
        for comp_name, comp in self.__dict__['_Component__comps'].items():
            for itf_name, slave_itf in comp.get_master_itfs().items():
                if slave_itf.comp == self:
                    slave_name = 'self'
                else:
                    slave_name = slave_itf.comp.get_name()
                binding = [
                    "%s->%s" % (comp_name, itf_name),
                    "%s->%s" % (slave_name, slave_itf.name)
                ]
                bindings.append(binding)

        if len(bindings) != 0:
            result['vp_bindings'] = bindings

        for name, comp in self.__dict__['_Component__comps'].items():
            result[name] = comp.gen()

        return result
