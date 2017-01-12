
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.pyson import Eval
from decimal import Decimal
from trytond.transaction import Transaction
__all__ = ['ShipmentWork', 'ProjectSummary', 'Work']


class ShipmentWork:
    __name__ = 'shipment.work'
    __metaclass__ = PoolMeta

    project = fields.Many2One('project.work', 'Project')

    @classmethod
    def pending(cls, shipments):
        for shipment in shipments:
            shipment.work_project = shipment.origin

        cls.save(shipments)
        super(ShipmentWork, cls).pending(shipments)

    @classmethod
    def get_total(cls, shipments, names):
        limit_date = Transaction().context.get('limit_date')
        res = {}
        for name in Work._get_summary_fields():
            res[name] = {}

        # Calc teorical cost and revenue
        # TODO: return values from generated sale.
        res.update(cls.get_cost(shipments, ['cost', 'revenue']))

        # Calc progress_shipments
        progress_shipments = []
        for shipment in shipments:
            if limit_date != None and shipment.done_date > limit_date:
                continue
            progress_shipments.append(shipment)

        res_p = cls.get_cost(shipments, ['cost', 'revenue'])
        res['progress_revenue'] = res_p['revenue']
        res['progress_cost'] = res_p['cost']

        return res

    @staticmethod
    def _get_summary_related_field():
        return 'project'


class Work:
    'Work Project'
    __name__ = 'project.work'
    __metaclass__ = PoolMeta

    @classmethod
    def _get_summary_models(cls):
        res = super(Work, cls)._get_summary_models()
        return res + [('shipment.work', 'project', 'get_total')]


class ProjectSummary:

    __name__ = 'project.work.summary'
    __metaclass__ = PoolMeta

    @classmethod
    def union_models(cls):
        res = super(ProjectSummary, cls).union_models()
        return ['shipment.work'] + res
