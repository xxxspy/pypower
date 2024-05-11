
import os
import copy
os.environ['R_HOME']=r'D:\Program Files\R\R-4.3.3'

from rpy2.robjects.packages import importr

import pandas as pd
from pathlib import Path
HERE = Path(__file__).parent.absolute()
from typing import List
from functools import cached_property
import plotly.graph_objects as go
from rpy2.robjects import conversion, default_converter




CommonParams = dict(
    siglevel = {
        'name': 'sig.level',
        'description': '显著性水平 (I型错误发生概率，常用0.05)',
        'default': 0.05,
        'enum': [0.05, 0.01, 0.001],
        'type': 'number',
    },
    alpha = {
        'name': 'alpha',
        'description': '显著性水平 (I型错误发生概率，常用0.05)',
        'enum': [0.05, 0.01, 0.001],
        'type': 'number',
        'default': 0.05,
    },
    power = {
        'name': 'power',
        'description': '统计功效(Ⅱ型正确的发生概率，常用0.8)',
        'type': 'number',
        'default': 0.8,
        'maximum': 1,
        'minimum': 0,
    },
    d = dict(
        name='d',
        description="效应量(Cohen's d) ",
        type='number',
        maximum= 1,
        minimum= 0,
    ),
    f = dict(
        name='f',
        description="效应量f",
        type='number',
        maximum= 1,
        minimum= 0,
    ),
    f2 = dict(
        name='f2',
        description="效应量f2",
        type='number',
        maximum= 1,
        minimum= 0,
    ),
    n = dict(
        name='n',
        description="样本量 ",
        type='number',
        required=False,
    ),
    ng = dict(
        name='ng',
        description="分组个数",
        type='number',
        required=False,
    ),
    N = dict(
        name='N',
        description="总样本量",
        type='number',
        required=False,
    ),
    df = dict(
        name='df',
        description="自由度",
        type='number',
        required=False,
    ),
    k = dict(
        name='k',
        description="分组个数",
        type='number',
        required=False,
    ),
    alternative={
        'name': 'alternative',
        'description': '双侧检验还是单侧检验（默认双侧）',
        'enum': ["two.sided", "less", "greater"],
        'type': 'string',
        'default': 'two.sided',
    },
)


Parameters = {
    'pwr.pwr.t.test': [
        CommonParams['n'],
        CommonParams['d'],
        CommonParams['power'],
        CommonParams['siglevel'],
        {
        'name': 'type',
        'description': 'T检验的类型',
        'enum': ["two.sample", "one.sample", "paired"],
        'type': 'string',
        'default': 'two.sample',
        },CommonParams['alternative'],
    ],
    'pwr.pwr.anova.test':[
        CommonParams['k'],
        CommonParams['n'],
        CommonParams['f'],
        CommonParams['power'],
        CommonParams['siglevel'],
    ],
    'pwr.pwr.p.test':[
        {
        'name': 'h',
        'description': '效应量h',
        'type': 'number',
        },
        CommonParams['n'],
        CommonParams['power'],
        CommonParams['siglevel'],
        CommonParams['alternative'],
    ],
    'pwr.pwr.2p.test':[
        {
        'name': 'h',
        'description': '效应量h',
        'type': 'number',
        },
        CommonParams['n'],
        CommonParams['power'],
        CommonParams['siglevel'],
        CommonParams['alternative'],
    ],
    'pwr.pwr.chisq.test':[
        {
        'name': 'w',
        'description': '效应量w',
        'type': 'number',
        },
        CommonParams['N'],
        CommonParams['df'],
        CommonParams['power'],
        CommonParams['siglevel'],
    ],
    'pwr.pwr.f2.test':[
        {
        'name': 'u',
        'description': '分子自由度=变量个数-1',
        'type': 'number',
        },
        {
        'name': 'v',
        'description': '分母自由度=样本量-变量个数',
        'type': 'number',
        },
        CommonParams['f2'],
        CommonParams['power'],
        CommonParams['siglevel'],
    ],
    'pwr.pwr.r.test':[
        CommonParams['n'],
        {
        'name': 'r',
        'description': '效应量（相关系数r）',
        'type': 'number',
        'maximum': 1,
        'minimum': 0,
        },
        CommonParams['power'],
        CommonParams['siglevel'],
        CommonParams['alternative'],
    ],
    'WebPower.wp.rmanova':[
        CommonParams['n'],
        CommonParams['ng'],
        {
        'name': 'nm',
        'description': '重复测量次数',
        'type': 'number',
        },
        CommonParams['f'],
        CommonParams['power'],
        CommonParams['alpha'],
        {
        'name': 'type',
        'description': '分析方法：0（默认值）代表组间效应，1代表组内效应，2代表交互效应',
        'type': 'number',
        'emum': [0,1,2],
        'default': 0,
        },
    ],
    'WebPower.wp.kanova':[
        CommonParams['n'],
        {
        'name': 'ndf',
        'description': '分子自由度',
        'type': 'number',
        },
        CommonParams['ng'],
        CommonParams['f'],
        CommonParams['power'],
        CommonParams['alpha'],
    ],
    'WebPower.wp.logistic':[
        CommonParams['n'],
        {
        'name': 'p0',
        'description': 'Prob(Y=1|X=0)：当预测变量 X 等于 0 时，结果变量 Y 观察到 1 的概率。',
        'type': 'number',
        },
        {
        'name': 'p1',
        'description': 'Prob(Y=1|X=1)：当预测变量 X 等于 1 时，结果变量 Y 观察到 1 的概率。',
        'type': 'number',
        },
        CommonParams['power'],
        CommonParams['alpha'],
        CommonParams['alternative'],
        {
        'name': 'family',
        'description': '分布总体',
        'type': 'string',
        'enum': ["Bernoulli","exponential", "lognormal", "normal", "Poisson", "uniform"],
        'default': 'Bernoulli',
        },
    ],
    'WebPower.wp.poisson':[
        CommonParams['n'],
        {
        'name': 'exp0',
        'description': '原假设下的基本利率。 它总是需要正值。 有关详细信息，请参阅 Demidenko (2007) 的文章。',
        'type': 'number',
        },
        {
        'name': 'exp1',
        'description': '事件发生率的相对增加。 它用于计算效应大小。 有关详细信息，请参阅 Demidenko (2007) 的文章。',
        'type': 'number',
        },
        CommonParams['power'],
        CommonParams['alpha'],
        CommonParams['alternative'],
        {
        'name': 'family',
        'description': 'Prob(Y=1|X=1)：当预测变量 X 等于 1 时，结果变量 Y 观察到 1 的概率。',
        'type': 'string',
        'enum': ["Bernoulli","exponential", "lognormal", "normal", "Poisson", "uniform"],
        'default': 'Bernoulli',
        },
    ],
    'WebPower.wp.crt2arm':[
        CommonParams['n'],
        CommonParams['f'],
        {
        'name': 'J',
        'description': '簇数/组数。 它告诉我们研究设计中考虑了多少个组。 至少需要两个组。',
        'type': 'number',
        },
        {
        'name': 'icc',
        'description': '组内相关性。 ICC 计算为组间方差与总方差的比率。 它量化了组内两个随机抽取的观测值的相关程度。',
        'type': 'number',
        },

        CommonParams['power'],
        CommonParams['alpha'],
        CommonParams['alternative'],
    ],
    'WebPower.wp.crt3arm':[
        CommonParams['n'],
        CommonParams['f'],
        {
        'name': 'J',
        'description': '簇数/组数。 它告诉我们研究设计中考虑了多少个组。 至少需要两个组。',
        'type': 'number',
        },
        {
        'name': 'icc',
        'description': '组内相关性。 ICC 计算为组间方差与总方差的比率。 它量化了组内两个随机抽取的观测值的相关程度。',
        'type': 'number',
        },

        CommonParams['power'],
        CommonParams['alpha'],
        CommonParams['alternative'],
        {
        'name': 'type',
        'description': '效应类型',
        'type': 'string',
        'enum': ["main" , "treatment" , "omnibus"],
        'default': 'main',
        },
    ],
    'WebPower.wp.mrt2arm':[
        CommonParams['n'],
        CommonParams['f'],
        {
        'name': 'J',
        'description': '簇数/组数。 它告诉我们研究设计中考虑了多少个组。 至少需要两个组。',
        'type': 'number',
        },
        {
        'name': 'tau00',
        'description': '组均值的方差。 它是第二层中的残差方差之一。 它的值必须是正数。',
        'type': 'number',
        },
        {
        'name': 'tau11',
        'description': '它是第二层中的残差方差之一。 它的值必须是正数。',
        'type': 'number',
        },
        {
        'name': 'sg2',
        'description': '第一层的残差方差。',
        'type': 'number',
        },

        CommonParams['power'],
        CommonParams['alpha'],
        CommonParams['alternative'],
        {
        'name': 'type',
        'description': '效应类型',
        'type': 'string',
        'enum': ["main" , "treatment" , "omnibus"],
        'default': 'main',
        },
    ],
    'WebPower.wp.mrt3arm':[
        CommonParams['n'],
        {
        'name': 'f1',
        'description': '实验主效应的效应大小。 效应量必须为正。',
        'type': 'number',
        },
        {
        'name': 'f2',
        'description': '两种实验处理差异的效应大小。 效应量必须为正。',
        'type': 'number',
        },
        {
        'name': 'J',
        'description': '簇数/组数。 它告诉我们研究设计中考虑了多少个组。 至少需要两个组。',
        'type': 'number',
        },
        {
        'name': 'tau',
        'description': '组间效应的方差',
        'type': 'number',
        },

        {
        'name': 'sg2',
        'description': '第一层的残差方差。',
        'type': 'number',
        },

        CommonParams['power'],
        CommonParams['alpha'],
        CommonParams['alternative'],
        {
        'name': 'type',
        'description': '效应类型',
        'type': 'string',
        'enum': ["main" , "treatment" , "omnibus"],
        'default': 'main',
        },
    ],
}


class PyPower:
    datafile = HERE / 'functions.csv'
    TestNameCol = 'testname'
    PackageCol = 'Package'
    FunctionCol = 'Function'
    AdjCol = 'adj'
    
    
    @cached_property
    def rows(self)->List[dict]:
        df = pd.read_csv(self.datafile)
        return df.to_dict('records')
    
    @cached_property
    def name2package(self)->dict:
        map = {}
        for row in self.rows:
            map[row[self.TestNameCol]] = row[self.PackageCol]
        return map
            
    @cached_property
    def name2function(self)->dict:
        map = {}
        for row in self.rows:
            map[row[self.TestNameCol]] = row[self.FunctionCol]
        return map
    
    @cached_property
    def name2config(self)->dict:
        config = {}
        for row in self.rows:
            config[row[self.TestNameCol]] = row
        return config
    
    def description(self, name: str)->str:
        info = self.rows[name]
        return info['description']

    def parameters(self, name: str):
        pk = self.name2package[name]
        func = self.name2function[name]
        return Parameters[f'{pk}.{func}']
    
    def samplesize(self, name:str, params: dict):
        pk = self.name2package[name]
        funcName = self.name2function[name]
        paramMeta = self.parameters(name)
        config = self.name2config[name]
        ssName = config['sampleSizeName']
        pdata = {}
        package = importr(pk)
        for meta in paramMeta:
            pname = meta['name']
            if pname in params:
                if 'enum' in meta:
                    assert params[pname] in meta['enum'], ValueError(f'{pname} value must be one of {meta["enum"]}')
                if pname != ssName:
                    pdata[pname] = params[pname]
            else:
                assert 'default' in meta, ValueError(f'Lack of Parameter <{pname}>')
                pdata[pname] = meta['default']
        print('pdata:', pdata)
        func = getattr(package, funcName.replace('.', '_'))
        r = func(**pdata)
        ss = None
        for k, v in r.items():
            if k == ssName:
                ss = v
        if ss is None:
            raise ValueError(f'There is no key named [{ssName}] in the result')    
        return ss    
    
    def plotData(self, name, params: dict, xname: str=None, yname: str=None, xrange=None, xstep=0.01):
        pdata = copy.copy(params)
        maxLimit = xrange[1]
        xvalue = xrange[0]
        rows = []
        with conversion.localconverter(default_converter):
            while xvalue < maxLimit:
                pdata[xname] = xvalue
                xvalue += xstep
                res = self._point_estimate(name, pdata, xname, yname)
                rows.append(res)
        return rows
    
    @cached_property
    def packages(self)->dict:
        return {
            'pwr': importr('pwr'),
            'WebPower': importr('WebPower'),
        }
        
    def point_estimate(self, name: str, params: dict, xname:str, yname: str)->dict:
        with conversion.localconverter(default_converter):
            res = self._point_estimate(name, params, xname, yname)
        return res
    
    def _point_estimate(self, name: str, params: dict, xname: str, yname: str)->dict:
        pk = self.name2package[name]
        funcName = self.name2function[name]
        package = self.packages[pk]
        paramMeta = self.parameters(name)
        pdata = {}
        for meta in paramMeta:
            pname = meta['name']
            if pname in params:
                if 'enum' in meta:
                    assert params[pname] in meta['enum'], ValueError(f'{pname} value must be one of {meta["enum"]}')
                pdata[pname] = params[pname]
                if isinstance(pdata[pname], str) and meta['type'] == 'number':
                    pdata[pname] = float(pdata[pname])
            else:
                if pname not in (xname, yname):
                    assert 'default' in meta, ValueError(f'Lack of Parameter <{pname}>')
                    pdata[pname] = meta['default']
        res = {}
        func = getattr(package, funcName.replace('.', '_'))
        r = func(**pdata)
        for k, v in r.items():
            res[k] = v[0]
        print(res)
        return res
            
        

    def plot(self, name, params: dict, xname: str=None, yname: str=None, xrange=None, xstep=0.01)->go.Figure:
        plotData = self.plotData(name, params, xname, yname, xrange, xstep)
        x_data = [d[xname] for d in plotData]
        y_data = [d[yname] for d in plotData]
        fig = go.Figure(data=[go.Scatter(x=x_data, y=y_data, mode='lines', name='Smooth Line')])
        fig.update_layout(title=f'{name} Sample Size',
                    xaxis_title=xname,
                    yaxis_title=yname)
        return fig
    
if __name__ == '__main__':
    funcs = PyPower()
    fig = funcs.plot('Paired T-test',{}, 'd', 'n')
    fig.show()