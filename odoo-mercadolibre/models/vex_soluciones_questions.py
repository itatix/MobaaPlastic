from odoo import api, fields, models

class Questions(models.Model):
	_name 				= "meli.questions"
	_description 		= "Preguntas de Mercado Libre"

	server_meli 		= fields.Many2one('meli.synchro.instance', "Instance Meli")
	id_app				= fields.Char(string="App ID" ,default =  None)
	product_id 			= fields.Many2one('product.template', "Product ID")
	question_id 		= fields.Char('Question ID')
	date_created 		= fields.Date('Creation date')
	seller_id 			= fields.Char(string="Seller ID")
	text 				= fields.Text('Question')
	status 				= fields.Selection([("UNANSWERED", "Question is not answered yet."),
							   ("ANSWERED", "Question was answered."),
							   ("CLOSED_UNANSWERED",
								"The item is closed and the question was never answered."),
							   ("UNDER_REVIEW",
								"The item is under review and the question too."),
							   ("BANNED", "The item was banned")],
							  string='Question Status')
	answer_date_created = fields.Date('Answer creation date')
	answer_status 		= fields.Selection(
		[("ACTIVE", "Active"), ("DISABLED", "Disabled"), ("BANNED", "Banned")], string='Answer Status')
	answer_text 		= fields.Text("Answer Text")
