from odoo import models, fields, api


class ProjectTaskInherit(models.Model):
    _inherit = "project.task"
    
    request_text = fields.Text(string='Request Text', readonly=True)
    request_id = fields.Many2one('request.request')
   