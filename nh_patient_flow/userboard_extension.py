from openerp.osv import orm, fields, osv


class nh_clinical_admin_userboard_pflow(orm.Model):
    _name = "nh.clinical.admin.userboard"
    _inherit = "nh.clinical.admin.userboard"

    _groups = {'hca': ['NH Clinical HCA Group'],
               'nurse': ['NH Clinical Nurse Group'],
               'ward_manager': ['NH Clinical Ward Manager Group', 'Contact Creation'],
               'senior_manager': ['NH Clinical Senior Manager Group', 'Contact Creation'],
               'admin': ['NH Clinical Admin Group', 'Contact Creation'],
               'kiosk': ['NH Clinical Kiosk Group'],
               'receptionist': ['NH Clinical Receptionist Group'],
               'referral_team': ['NH Patient Flow GP Referral Team Group'],
               'junior_doctor': ['NH Clinical Junior Doctor Group'],
               'registrar': ['NH Clinical Registrar Group'],
               'consultant': ['NH Clinical Consultant Group']}

    _columns = {
        'receptionist': fields.boolean('Receptionist'),
        'referral_team': fields.boolean('Referral Team'),
        'junior_doctor': fields.boolean('Junior Doctor'),
        'registrar': fields.boolean('Registrar'),
        'consultant': fields.boolean('Consultant')
    }

    def init(self, cr):
        cr.execute("""
            drop view if exists %s;
            create or replace view %s as (
                with user_groups as (
                    select
                        users.id as id,
                        array_agg(rgroup.name) as groups
                    from res_users users
                    inner join res_groups_users_rel gur on gur.uid = users.id
                    inner join res_groups rgroup on rgroup.id = gur.gid
                    group by users.id
                )
                select
                    users.id as id,
                    users.id as user_id,
                    users.active as active,
                    partner.name as name,
                    users.login as login,
                    users.password as password,
                    case
                        when ug.groups @> '{"NH Clinical HCA Group"}' then true
                        else false
                    end as hca,
                    case
                        when ug.groups @> '{"NH Clinical Nurse Group"}' then true
                        else false
                    end as nurse,
                    case
                        when ug.groups @> '{"NH Clinical Ward Manager Group"}' then true
                        else false
                    end as ward_manager,
                    case
                        when ug.groups @> '{"NH Clinical Doctor Group"}' then true
                        else false
                    end as doctor,
                    case
                        when ug.groups @> '{"NH Clinical Kiosk Group"}' then true
                        else false
                    end as kiosk,
                    case
                        when ug.groups @> '{"NH Clinical Admin Group"}' then true
                        else false
                    end as admin,
                    case
                        when ug.groups @> '{"NH Clinical Receptionist Group"}' then true
                        else false
                    end as receptionist,
                    case
                        when ug.groups @> '{"NH Clinical Junior Doctor Group"}' then true
                        else false
                    end as junior_doctor,
                    case
                        when ug.groups @> '{"NH Clinical Registrar Group"}' then true
                        else false
                    end as registrar,
                    case
                        when ug.groups @> '{"NH Clinical Consultant Group"}' then true
                        else false
                    end as consultant,
                    case
                        when ug.groups @> '{"NH Patient Flow GP Referral Team Group"}' then true
                        else false
                    end as referral_team,
                    case
                        when ug.groups @> '{"NH Clinical Senior Manager Group"}' then true
                        else false
                    end as senior_manager
                from res_users users
                inner join res_partner partner on partner.id = users.partner_id
                inner join user_groups ug on ug.id = users.id
                where users.id != 1 and (ug.groups @> '{"NH Clinical HCA Group"}' or
                ug.groups @> '{"NH Clinical Senior Manager Group"}' or ug.groups @> '{"NH Clinical Nurse Group"}' or
                ug.groups @> '{"NH Clinical Ward Manager Group"}' or ug.groups @> '{"NH Clinical Doctor Group"}' or
                ug.groups @> '{"NH Clinical Kiosk Group"}' or ug.groups @> '{"NH Clinical Admin Group"}' or
                ug.groups @> '{"NH Patient Flow GP Referral Team Group"}' or
                ug.groups @> '{"NH Clinical Receptionist Group"}' or ug.groups @> '{"NH Clinical Junior Doctor Group"}'
                or ug.groups @> '{"NH Clinical Registrar Group"}' or ug.groups @> '{"NH Clinical Consultant Group"}')
            )
        """ % (self._table, self._table))