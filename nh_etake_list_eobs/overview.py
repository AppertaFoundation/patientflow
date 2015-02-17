from openerp.osv import orm, fields, osv
import logging
from openerp import SUPERUSER_ID
from datetime import datetime as dt
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

_logger = logging.getLogger(__name__)


class nh_etake_list_overview(orm.Model):
    _name = "nh.etake_list.overview"
    _inherit = "nh.etake_list.overview"

    _trend_strings = [('up', 'up'), ('down', 'down'), ('same', 'same'), ('none', 'none'), ('one', 'one')]
    _clinical_risk_selection = [['NoScore', 'No Score Yet'],
                                ['High', 'High Risk'],
                                ['Medium', 'Medium Risk'],
                                ['Low', 'Low Risk'],
                                ['None', 'No Risk']]

    _columns = {
        'ews_score_string': fields.text("Latest Score"),
        'ews_score': fields.integer("Latest Score"),
        'ews_trend_string': fields.selection(_trend_strings, "Score Trend String"),
        'ews_trend': fields.integer("Score Trend"),
        'clinical_risk': fields.selection(_clinical_risk_selection, "Clinical Risk")
    }

    def init(self, cr):

        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                with
                    ews as(
                            select
                                activity.patient_id,
                                activity.spell_id,
                                activity.state,
                                activity.date_scheduled,
                                ews.id,
                                ews.score,
                                ews.frequency,
                                ews.clinical_risk,
                                activity.rank
                            from wb_activity_ranked activity
                            inner join nh_clinical_patient_observation_ews ews on activity.data_id = ews.id
                                and activity.data_model = 'nh.clinical.patient.observation.ews'
                    ),
                    dt as (
                        select
                            activity.id as id,
                            activity.state as state,
                            activity.parent_id as parent_id,
                            data.blocking as blocking
                        from nh_activity activity
                        inner join nh_clinical_doctor_task data on data.activity_id = activity.id and activity.data_model = 'nh.clinical.doctor.task'
                        where state != 'completed' and state != 'cancelled'
                    )
                    select
                        patient.id as id,
                        patient.gender as gender,
                        extract(year from age(now(), patient.dob)) as age,
                        tci_activity.pos_id as pos_id,
                        (select count(*) from dt where dt.parent_id = spell_activity.id) as doctor_tasks,
                        (select count(*) from dt where dt.parent_id = spell_activity.id and dt.blocking) as blocking_tasks,
                        case
                            when referral_activity.state is null and tci_activity.state is null then 'Done'
                            when spell_activity.state = 'cancelled' then 'Done'
                            when ptwr_activity.state is not null and ptwr_activity.state = 'completed' then 'admitted'
                            when discharge_activity.state is not null and discharge_activity.state = 'completed' then 'Discharged'
                            when discharge_activity.state is not null and discharge_activity.state != 'completed' then 'To be Discharged'
                            when referral_activity.state is not null and referral_activity.state != 'completed' and referral_activity.state != 'cancelled' then 'Referral'
                            when tci_activity.state is not null and tci_activity.state = 'cancelled' then 'dna'
                            when tci_activity.state is not null and tci_activity.state = 'scheduled' and (extract(epoch from now() at time zone 'UTC' - tci_activity.date_scheduled) / 3600) >= 96 then 'to_dna'
                            when tci_activity.state is not null and tci_activity.state = 'scheduled' then 'TCI'
                            when clerking_activity.state = 'scheduled' then 'To be Clerked'
                            when clerking_activity.state = 'started' then 'Clerking in Process'
                            when ptwr_activity.state is not null and ptwr_activity.state != 'completed' and ptwr_activity.state != 'cancelled' then 'Consultant Review'
                            when review_activity.state = 'scheduled' then 'Senior Review'
                            else 'Other'
                        end as state,
                        case
                            when tci_activity.state is null then FALSE
                            when tci_activity.state is not null and tci_activity.state != 'scheduled' then FALSE
                            when now() at time zone 'UTC' >= ((extract(YEAR FROM tci_activity.date_scheduled) || '-' ||  extract(MONTH FROM tci_activity.date_scheduled) || '-' || extract(DAY FROM tci_activity.date_scheduled) || ' 08:00:00')::timestamp + '1 day') then TRUE
                            else FALSE
                        end as dna_able,
                        patient.id as patient_id,
                        case
                            when tci_activity.state = 'scheduled' then tci_activity.location_id
                            else location.id
                        end as location_id,
                        case
                            when tci_activity.state = 'scheduled' then 'ward'
                            else location.usage
                        end as location_type,
                        case
                            when referral_activity.state is not null and referral_activity.state != 'completed' and referral_activity.state != 'cancelled' then referral_activity.id
                            when tci_activity.state is not null and tci_activity.state = 'scheduled' then tci_activity.id
                            when clerking_activity.state = 'scheduled' or clerking_activity.state = 'started' then clerking_activity.id
                            when review_activity.state = 'scheduled' then review_activity.id
                            when ptwr_activity.state = 'new' or ptwr_activity.state = 'scheduled' or ptwr_activity.state = 'completed' then ptwr_activity.id
                            when discharge_activity.state = 'new' or discharge_activity.state = 'scheduled' or discharge_activity.state = 'completed' then discharge_activity.id
                            else spell_activity.id
                        end as activity_id,
                        spell_activity.id as spell_activity_id,
                        patient.other_identifier as hospital_number,
                        case
                            when char_length(patient.patient_identifier) > 6 then substring(patient.patient_identifier from 1 for 3) || ' ' || substring(patient.patient_identifier from 4 for 3) || ' ' || substring(patient.patient_identifier from 7)
                            else patient.patient_identifier
                        end as nhs_number,
                        referral.form_id as form_id,
                        form.specialty_id as specialty_id,
                        clerking_activity.date_started as clerking_started,
                        clerking_activity.date_terminated as clerking_terminated,
                        clerking_activity.user_id as clerking_user_id,
                        review_activity.date_terminated as review_terminated,
                        review_activity.terminate_uid as review_user_id,
                        ptwr_activity.date_terminated as ptwr_terminated,
                        ptwr_activity.user_id as ptwr_user_id,
                        case
                            when ptwr_activity.date_terminated is null then 0
                            else extract(epoch from now() at time zone 'UTC' - ptwr_activity.date_terminated) / 3600
                        end as hours_from_ptwr,
                        spell.diagnosis as diagnosis,
                        spell.doctor_plan as plan,
                        discharge_activity.date_terminated as discharge_terminated,
                        case
                            when discharge_activity.date_terminated is null then 0
                            else extract(epoch from now() at time zone 'UTC' - discharge_activity.date_terminated) / 3600
                        end as hours_from_discharge,
                        discharge_activity.terminate_uid as discharge_user_id,
                        case
                            when tci_activity.date_terminated is null then ''
                            when (tci_activity.date_terminated + interval '14 hours') >= now() at time zone 'UTC' then ''
                            else '-'
                        end as review_deadline_polarity,
                        case
                            when tci_activity.date_terminated is null then '14H 00M'
                            when @ extract(days from (tci_activity.date_terminated + interval '14 hours') - now() at time zone 'UTC') > 0 then @ extract(days from (tci_activity.date_terminated + interval '14 hours') - now() at time zone 'UTC') || 'D ' || extract(hours from (tci_activity.date_terminated + interval '14 hours') - now() at time zone 'UTC') || 'H ' || @ extract(minutes from (tci_activity.date_terminated + interval '14 hours') - now() at time zone 'UTC') || 'M'
                            else @ extract(hours from (tci_activity.date_terminated + interval '14 hours') - now() at time zone 'UTC') || 'H ' || @ extract(minutes from (tci_activity.date_terminated + interval '14 hours') - now() at time zone 'UTC') || 'M'
                        end as review_deadline,
                        case when ews1.id is null then 'none' else ews1.score::text end as ews_score_string,
                        ews1.score as ews_score,
                        case
                            when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) = 0 then 'same'
                            when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) > 0 then 'up'
                            when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) < 0 then 'down'
                            when ews1.id is null and ews2.id is null then 'none'
                            when ews1.id is not null and ews2.id is null then 'first'
                            when ews1.id is null and ews2.id is not null then 'no latest' -- shouldn't happen.
                        end as ews_trend_string,
                        case when ews1.id is null then 'NoScore' else ews1.clinical_risk end as clinical_risk,
                        ews1.score - ews2.score as ews_trend

                    from nh_clinical_patient patient
                    left join nh_clinical_spell spell on spell.patient_id = patient.id
                    left join nh_activity spell_activity on spell_activity.id = spell.activity_id
                    left join nh_activity referral_activity on referral_activity.patient_id = patient.id and referral_activity.data_model = 'nh.clinical.patient.referral'
                    left join nh_clinical_patient_referral referral on referral.activity_id = referral_activity.id
                    left join nh_clinical_patient_referral_form form on referral.form_id = form.id
                    left join nh_activity tci_activity on tci_activity.parent_id = spell_activity.id and tci_activity.data_model = 'nh.clinical.patient.tci'
                    left join nh_activity discharge_activity on discharge_activity.parent_id = spell_activity.id and discharge_activity.data_model = 'nh.clinical.adt.patient.discharge'
                    left join nh_activity clerking_activity on clerking_activity.parent_id = spell_activity.id and clerking_activity.data_model = 'nh.clinical.patient.clerking'
                    left join nh_activity review_activity on review_activity.parent_id = spell_activity.id and review_activity.data_model = 'nh.clinical.patient.review'
                    left join nh_activity ptwr_activity on ptwr_activity.parent_id = spell_activity.id and ptwr_activity.data_model = 'nh.clinical.ptwr'
                    left join nh_clinical_location location on location.id = spell_activity.location_id
                    left join ews ews1 on spell.id = ews1.spell_id and ews1.rank = 1 and ews1.state = 'completed'
                    left join ews ews2 on spell.id = ews2.spell_id and ews2.rank = 2 and ews2.state = 'completed'
                    where referral_activity.id is not null or tci_activity.id is not null
                )
        """ % (self._table, self._table))