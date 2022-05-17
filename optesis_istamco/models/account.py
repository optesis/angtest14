from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class Account(models.Model):
        _inherit= "account.move"
        
        port_depart = fields.Many2one('optesis.port', string='port de Chargement')
        port_arrivee = fields.Many2one('optesis.port', string='port d\'arrivée')
        bon_livraison = fields.Many2one('optesis.bon.livraison', string='B/L')
        voyage = fields.Many2one('optesis.voyage',string=' Code Voyage')
        vehicule = fields.Many2one('optesis.vehicule',string='Vehicule')
        site = fields.Many2one('optesis.site', string='Site')
        etat = fields.Integer(string='etat',default=0)
        date_arrivee_select=fields.Date(related="voyage.date_arrivee")
        code_select=fields.Char(related="voyage.code")
        
        
#         @api.model
#         def tax_line_move_line_get(self):
#             res = []
#             # keep track of taxes already processed
#             # loop the invoice.tax.line in reversal sequence
#             for tax_line in sorted(self.tax_line_ids, key=lambda x: -x.sequence):
#                 tax = tax_line.tax_id

#                 analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in tax_line.analytic_tag_ids]
#                 if tax_line.amount_total:
#                     tax_line_vals = {
#                         'invoice_tax_line_id': tax_line.id,
#                         'tax_line_id': tax_line.tax_id.id,
#                         'type': 'tax',
#                         'name': tax_line.name,
#                         'price_unit': tax_line.amount_total,
#                         'quantity': 1,
#                         'price': tax_line.amount_total,
#                         'account_id': tax_line.account_id.id,
#                         'account_analytic_id': tax_line.account_analytic_id.id,
#                         'analytic_tag_ids': analytic_tag_ids,
#                         'invoice_id': self.id,
#                         'op_voyag': tax_line.voyag.id,
#                         'op_arrivee': tax_line.arrivee.id
#                     }

#                     if tax.include_base_amount:
#                         affected_taxes = []
#                         for invoice_line in tax_line.invoice_id.invoice_line_ids:
#                             if tax in invoice_line.invoice_line_tax_ids:
#                                 following_taxes = invoice_line.invoice_line_tax_ids.filtered(lambda x: x.sequence > tax.sequence
#                                                                                                        or (x.sequence == tax.sequence and x.id > tax.id))
#                                 affected_taxes += following_taxes.ids
#                                 affected_taxes += following_taxes.mapped('children_tax_ids.id')

#                         tax_line_vals['tax_ids'] = [(6, 0, affected_taxes)]

#                     res.append(tax_line_vals)
#             return res
        
        @api.model
        def invoice_line_move_line_get(self):
            res = []
            for line in self.invoice_line_ids:
                if not line.account_id:
                    continue
                if line.quantity==0:
                    continue
                tax_ids = []
                for tax in line.invoice_line_tax_ids:
                    tax_ids.append((4, tax.id, None))
                    for child in tax.children_tax_ids:
                        if child.type_tax_use != 'none':
                            tax_ids.append((4, child.id, None))
                analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

                move_line_dict = {
                    'invl_id': line.id,
                    'type': 'src',
                    'name': line.name,
                    'price_unit': line.price_unit,
                    'quantity': line.quantity,
                    'price': line.price_subtotal,
                    'account_id': line.account_id.id,
                    'product_id': line.product_id.id,
                    'uom_id': line.uom_id.id,
                    'account_analytic_id': line.account_analytic_id.id,
                    'analytic_tag_ids': analytic_tag_ids,
                    'tax_ids': tax_ids,
                    'invoice_id': self.id,
                    'op_voyag': line.voyag.id,
                    'op_vehicul': line.vehicul.id,
                    'op_sit': line.sit.id
                }
                res.append(move_line_dict)
            return res
        
        @api.onchange('voyage')
        def set_date_voyage(self):
            """ Creates invoice related analytics and financial move lines """
            if self.etat==0:
                self.etat=1
        
        
        
        
        #@api.multi
        def action_move_create(self):
            """ Creates invoice related analytics and financial move lines """
            _logger.info('IN THE FUNCTION CREATE MOVE')
            account_move = self.env['account.move']

            for inv in self:
                if not inv.journal_id.sequence_id:
                    raise UserError(_('Please define sequence on the journal related to this invoice.'))
                if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
                    raise UserError(_('Please add at least one invoice line.'))
                if inv.move_id:
                    continue


                if not inv.date_invoice:
                    inv.write({'date_invoice': fields.Date.context_today(self)})
                if not inv.date_due:
                    inv.write({'date_due': inv.date_invoice})
                company_currency = inv.company_id.currency_id

                # create move lines (one per invoice line + eventual taxes and analytic lines)
                iml = inv.invoice_line_move_line_get()
                iml += inv.tax_line_move_line_get()

                diff_currency = inv.currency_id != company_currency
                # create one move line for the total and possibly adjust the other lines amount
                total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)

                _logger.info('IN THE FUCTION action_move_create 1' +str(iml))
                name = inv.name or ''
                if inv.payment_term_id:
                    totlines = inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                    res_amount_currency = total_currency
                    for i, t in enumerate(totlines):
                        _logger.info('LA VALEUR de T' + str(t))
                        if inv.currency_id != company_currency:
                            amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id, inv._get_currency_rate_date() or fields.Date.today())
                        else:
                            amount_currency = False

                        # last line: add the diff
                        res_amount_currency -= amount_currency or 0
                        if i + 1 == len(totlines):
                            amount_currency += res_amount_currency

                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': t[1],
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                else:
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
                line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
                _logger.info('IN THE FUCTION action_move_create 2 ' +str(line))
                line = inv.group_lines(iml, line)

                line = inv.finalize_invoice_move_lines(line)
                #_logger.info('LA VALEUR DE MOVE LINES ' + str(line))

                date = inv.date or inv.date_invoice
                move_vals = {
                    'ref': inv.reference,
                    'line_ids': line,
                    'journal_id': inv.journal_id.id,
                    'date': date,
                    'narration': inv.comment,
                }
                move = account_move.create(move_vals)
                # Pass invoice in method post: used if you want to get the same
                # account move reference when creating the same invoice after a cancelled one:
                move.post(invoice = inv)
                # make the invoice point to that move
                vals = {
                    'move_id': move.id,
                    'date': date,
                    'move_name': move.name,
                }
                inv.write(vals)
            return True
        

    
class AccountMoveLine(models.Model):
       _inherit= "account.move.line"
    
       def _get_default_voyage(self):
            return self.invoive_id.voyage
       inv_id = fields.Many2one('account.move', ondelete="set null")
       arrivee = fields.Many2one('optesis.port',  string='port d\'arrivée')
       voyag = fields.Many2one('optesis.voyage',string='Voyage')
       vehicul = fields.Many2one('optesis.vehicule', string='Vehicule')
       sit = fields.Many2one('optesis.site', string='Site')
    
#class AccountTemplate(models.Model):
#        _inherit= "account.reconcile.model"
        
 #       voyag = fields.Many2one('optesis.voyage',string='Voyage')
        
        
#class AccountInvoiceTax(models.Model):
       #_inherit= "account.invoice.tax"
    
       #arrivee = fields.Many2one('optesis.port',  string='port d\'arrivée')
       #voyag = fields.Many2one('optesis.voyage', string='Voyage',readonly=False)
    

    
class AccountMoveLine(models.Model):
        _inherit= "account.move.line"
        
        op_arrivee = fields.Many2one('optesis.port', string='Port d\'arrivée')
        op_voyag = fields.Many2one('optesis.voyage', string='Voyage')
        op_vehicul = fields.Many2one('optesis.vehicule', string='Vehicule')
        op_sit = fields.Many2one('optesis.site', string='Site')
        op_line_id = fields.Many2one('account.move.line',ondelete="set null")
        
        
        
class ProductProductInherit(models.Model):
        _inherit = "product.product"

        @api.model
        def _convert_prepared_anglosaxon_line(self, line, partner):
            return {
                'date_maturity': line.get('date_maturity', False),
                'partner_id': partner,
                'name': line['name'],
                'debit': line['price'] > 0 and line['price'],
                'credit': line['price'] < 0 and -line['price'],
                'account_id': line['account_id'],
                'analytic_line_ids': line.get('analytic_line_ids', []),
                'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
                'currency_id': line.get('currency_id', False),
                'quantity': line.get('quantity', 1.00),
                'product_id': line.get('product_id', False),
                'product_uom_id': line.get('uom_id', False),
                'analytic_account_id': line.get('account_analytic_id', False),
                'invoice_id': line.get('invoice_id', False),
                'tax_ids': line.get('tax_ids', False),
                'tax_line_id': line.get('tax_line_id', False),
                'analytic_tag_ids': line.get('analytic_tag_ids', False),
                'op_voyag': line.get('op_voyag', False),
                'op_vehicul': line.get('op_vehicul', False),
                'op_sit': line.get('op_sit', False)
            }
                
    