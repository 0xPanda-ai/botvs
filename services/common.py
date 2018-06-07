# -*- coding: utf-8 -*-

import datetime
import importlib
import re

from sqlalchemy import or_

from constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from app.extensions import db


class CommonService(object):
    _model = None
    _error = None

    def __init__(self):
        super(CommonService, self).__init__()
        if not self._model:
            model_name = re.sub('Service$', '', self.__class__.__name__)
            models = importlib.import_module('app.models')
            self._model = getattr(models, model_name)
            self.columns = [t.name for t in self._model.__table__.columns]

    def get(self, _id):
        """根据id获取相应数据"""

        data = self.get_data(_id)

        if isinstance(_id, int):
            return data.first()
        elif isinstance(_id, list):
            if hasattr(self._model, 'active'):
                data = data.filter(self._model.active)
            return data.all()

    def get_data(self, where=None):
        """获取数据"""

        if where is None:
            where = {}

        data = self._model.query

        if isinstance(where, int) or isinstance(where, list):
            where = {'id': where}

        where["delete_time"] = None
        for key, value in where.items():
            if isinstance(value, list):
                data = data.filter(getattr(self._model, key).in_(value))
            elif isinstance(value, dict):
                for vk, vv in value.items():
                    operators = ['lt', 'gt', 'eq', 'le', 'ge', 'ne']
                    operator = '__{}__'.format(vk) if vk in operators else vk
                    operate = getattr(getattr(self._model, key), operator)
                    if isinstance(vv, list):
                        expression = operate(*vv)
                    else:
                        expression = operate(vv)
                    data = data.filter(expression)
            else:
                data = data.filter(getattr(self._model, key) == value)

        return data

    def get_order_data(self, where=None, order=None):
        """排序"""

        data = self.get_data(where)

        if order:
            order_list = []
            for key, value in order.items():
                order_list.append(getattr(getattr(self._model, key), value)())
            data = data.order_by(*order_list)
        else:
            data = data.order_by(self._model.id.desc())

        return data

    def get_first(self, where=None, order=None):
        """获取第一条数据"""

        data = self.get_order_data(where, order)

        return data.first()

    def get_list(self, where=None, order=None,
                 page=DEFAULT_PAGE, page_size=DEFAULT_PAGE_SIZE):
        """获取分页数据列表"""

        data = self.get_order_data(where, order)

        return data.paginate(page, page_size)

    def get_all(self, where=None, order=None):
        """获取所有数据"""

        data = self.get_order_data(where, order)

        return data.all()

    def get_count(self, where=None):
        """获取条数"""

        return self.get_data(where).count()

    def delete(self, where, real=False):
        """删除数据"""

        if not real:
            return self.update(where, {'delete_time': datetime.datetime.now()})

        return self.get_data(where).delete()

    def save(self, **kwargs):
        """保存数据"""

        if kwargs.get('id'):
            data = self.get(kwargs.pop('id'))
        else:
            data = self._model()

        for key, value in kwargs.items():
            if key in self.columns:
                setattr(data, key, value)

        db.session.add(data)
        db.session.flush()
        return data.id

    def search(self, fields, content):
        """查询数据"""

        if not content:
            data = self.get_list()
            return data.items

        data = self.get_data()
        if isinstance(fields, list):
            where = or_(*[getattr(self._model, field).like(u'%{str}%'.format(str=content)) for field in fields])
        else:
            where = getattr(self._model, fields).like(u'%{str}%'.format(str=content))

        data = data.filter(where).order_by(self._model.id.desc())
        return data.paginate(DEFAULT_PAGE, DEFAULT_PAGE_SIZE).items

    def update(self, where=None, data=None):
        """更新数据"""

        result = self.get_data(where)
        result.update(data, synchronize_session=False)

        return True

    def get_error(self):
        """获取错误信息"""

        return self._error

    def __getattr__(self, item):
        """动态方法"""

        if item.startswith('get_by_'):
            # 通过某一字段的值获取整列数据
            field_name = re.sub('^get_by_', '', item)
            if field_name in self.columns:
                def get_by_field(value):
                    data = self.get_data({field_name: value})
                    if isinstance(value, list):
                        return data.all()
                    return data.first()

                return get_by_field

        if item.startswith('has_'):
            # 判断某个字段的值是不是已经存在了,传入id表示除了这个id外
            field_name = re.sub('^has_', '', item)
            if field_name in self.columns:
                def has_field_value(value, _id=None):
                    where = {field_name: value}
                    if _id:
                        where["id"] = {'ne': _id}
                    return self.get_count(where) > 0

                return has_field_value
