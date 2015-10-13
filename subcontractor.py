from openerp.osv import fields, osv

class subcontractor_moves(osv.osv):
    _name='subcontractor.moves'
    _columns={
              'partner_id':fields.many2one('res.partner',"Supplier"),
              'move_lines':fields.one2many('stock.move','picking_id',"Products")
              }

class stoke_move(osv.osv):
    _inherit="stock.move"
    _columns={
              'picking_id':fields.many2one('subcontractor.moves','Picking')
              } 
    
class stock_picking(osv.osv):
    _inherit="stock.picking"
    
    def open_sub_wizard(self,cr,uid,ids,context=None):
        stock_obj=self.pool.get('stock.picking').browse(cr,uid,ids,context=context)
        
        move_obj=self.pool.get('stock.move').browse(cr,uid,ids,context=context)
        list_moves=[]
        for m in stock_obj.move_lines:
            list_moves.append(m)
            
        print "list---------------------------",list_moves
        vals={
              'partner_id':False,
              'move_lines':False
              }
        sub_id=self.pool.get('subcontractor.moves').create(cr,uid,vals,context=context)
        
        self.pool.get('subcontractor.moves').write(cr,uid,sub_id,{
                                                                  "partner_id":stock_obj.partner_id.id,
                                                                "move_lines":[(0,0,{
                                                                                  'picking_id':list_moves[0],
                                                                                  })],
#                                                                 'picking_id':10,
                                                                                    
                                                                    }
                                                                  ,context)
        return{
               'name':'subcontractor',
               'view_type':'form',
               'view_mode':'form',
               'res_model':'subcontractor.moves',
               'view_id':False,
               'target':'new',
               'res_id':sub_id,
               'type':'ir.actions.act_window'
               }