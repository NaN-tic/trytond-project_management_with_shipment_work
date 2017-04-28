
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from trytond.transaction import Transaction

__all__ = ['ShipmentWork', 'ProjectSummary', 'Work']


class ShipmentWork:
    __name__ = 'shipment.work'
    __metaclass__ = PoolMeta

    project = fields.Many2One('project.work', 'Project')

    @classmethod
    def pending(cls, shipments):
        WorkProject = Pool().get('work.project')

        for shipment in shipments:
            if shipment.origin and isinstance(shipment.origin, WorkProject):
                shipment.work_project = shipment.origin

        cls.save(shipments)
        super(ShipmentWork, cls).pending(shipments)

    @classmethod
    def get_total(cls, shipments, names):
        Work = Pool().get('project.work')

        limit_date = Transaction().context.get('limit_date')
        res = {}
        for name in Work._get_summary_fields():
            res[name] = {}

        # Calc progress_shipments
        progress_shipments = []
        for shipment in shipments:
            if (limit_date != None and shipment.done_date != None and
                    shipment.done_date > limit_date):
                continue
            progress_shipments.append(shipment)

        res_p = cls.get_cost(progress_shipments, ['cost', 'revenue'])
        res['progress_revenue'] = res_p['revenue']
        res['progress_cost'] = res_p['cost']

        return res

    @staticmethod
    def _get_summary_related_field():
        return 'project'


class Work:
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
