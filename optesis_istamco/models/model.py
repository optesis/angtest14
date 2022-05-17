from odoo import api, fields, models, _

class Port(models.Model):
    _name = "optesis.port"
    _description = "Port"


    code =  fields.Char('Code')
    name =  fields.Char('Nom')
    _sql_constraints = [('constraints_id', 'unique(code)', 'Unique')]
    
    #@api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id,"%s - %s" % (rec.code, rec.name)))
        return res
    

class Vehicule(models.Model):
     _name = "optesis.vehicule"
     _description = "Vehicule"


     name =  fields.Char('Code')
     code =  fields.Char('Nom')
     _sql_constraints = [('constraints_id', 'Check(1=1)', 'Unique')]
                        
class Voyage(models.Model):
      _name = "optesis.voyage"
      _description = "Voyage"
  
      name =  fields.Char('Code')
      code =  fields.Char('Nom')
      date_arrivee =  fields.Date('date_arrivee')
      _sql_constraints = [('constraints_id', 'unique(name)', 'Unique')]
                        
class Site(models.Model):
     _name = "optesis.site"
     _description = "Site"


     code =  fields.Char('Code')
     name =  fields.Char('Nom')
     _sql_constraints = [('constraints_id', 'unique(code)', 'Unique')]

class BonLivraison(models.Model):
     _name = "optesis.bon.livraison"
     _description = "Bon Livraison"


     name =  fields.Char('Num B/L')
     num_bl =  fields.Char('Poids')
     volume =  fields.Char('Volume')
     nature = fields.Char('Nature')
     mode = fields.Selection([('import', 'Import'),('export', 'Export'),('intransit', 'In Transit')], string='Mode')  
     _sql_constraints = [('constraints_id', 'Unique(name)', 'Unique')]