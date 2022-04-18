from multiprocessing.dummy import active_children
from odoo import models, fields


class RequestWizardAssign(models.TransientModel):
    _name = 'request.wizard.assign'
    _inherit = ['mail.activity.mixin']

    _description = 'Request Wizard: Assign'

    def _default_user_id(self):
        return self.env.user

    request_ids = fields.Many2many(
        'request.request', string='Requests', required=True)
    user_id = fields.Many2one(
        'res.users', string="User", default=_default_user_id, required=True)
    partner_id = fields.Many2one(
        'res.partner', related="user_id.partner_id",
        readonly=True, store=False)
    comment = fields.Text()

    def _prepare_assign(self):
        """ Prepare assign data

            This method have to prepare dict with data to be written to request
        """
        self.ensure_one()
        return {
            'user_id': self.user_id.id,
        }

    def _do_assign(self):
        self.ensure_one()
        self.request_ids.with_context(
            assign_comment=self.comment
        ).write(self._prepare_assign())

    def do_assign(self):
        self.ensure_one()
        self.request_ids.ensure_can_assign()
        self._do_assign()
       
        if self.request_ids.project_id:
            request = self.request_ids

            values = {
                'name':request.name,
                'project_id':request.project_id.id,
                'date_deadline':self.request_ids.deadline_date,
                'user_ids':self.user_id,
                'request_text':self.request_ids.request_text[3:][:-4]
            }
            for rec in self.request_ids.project_id:
                print(rec.stage_id.name)
            for rec in self.request_ids:
                rec.action_notify(self.comment)
            self.env['project.task'].create(values)
            # self.env['project.task'].activity_schedule('project.mt_task_new',user_id = self.user_id.id, note = self.comment)
        # activity_type = self.env.ref('generic_request.printer_request_mail_activity_call')
        # self.activity_schedule('generic_request.mail_send_create_notification',user_id = self.user_id.id, note = self.comment)
        if self.comment:
            for request in self.request_ids:
                request.message_post(body=self.comment)
