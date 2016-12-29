# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Eval
from decimal import Decimal

__all__ = ['ShipmentWork', 'ProjectSummary', 'Work']


class ShipmentWork:
    __name__ = 'shipment.work'
    __metaclass__ = PoolMeta

    project = fields.Many2One('project.work', 'Project')

    @classmethod
    def pending(cls, shipments):
        for shipment in shipments:
            shipment.parent = shipment.origin

        cls.save(shipments)
        super(ShipmentWork, cls).pending(shipments)

    @classmethod
    def _get_cost(cls, shipments):
        vals = cls.get_cost(shipments, 'cost')
        return vals['cost']

    @classmethod
    def _get_revenue(cls, shipments):
        vals = cls.get_cost(shipments, 'revenue')
        return vals['revenue']

    @staticmethod
    def _get_summary_related_field():
        return 'project'


class Work:
    'Work Project'
    __name__ = 'project.work'
    __metaclass__ = PoolMeta

    @classmethod
    def _get_related_cost_and_revenue(cls):
        res = super(Work, cls)._get_related_cost_and_revenue()
        return res + [('shipment.work', 'project', '_get_revenue',
            '_get_cost')]


class ProjectSummary:

    __name__ = 'project.work.summary'
    __metaclass__ = PoolMeta


    @classmethod
    def union_models(cls):
        res = super(ProjectSummary, cls).union_models()
        return ['shipment.work'] + res
