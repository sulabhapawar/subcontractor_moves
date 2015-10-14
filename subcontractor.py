from openerp.osv import fields, osv

class subcontractor_moves(osv.osv):
    _name='subcontractor.moves'
    _columns={
              'partner_id':fields.many2one('res.partner',"Supplier"),
            'move_lines':fields.one2many('stock.move','subcontractor_picking',"Products")
              }
    
    def send_to_subcontractor(self,cr,uid,ids,context=None):
        sub_obj=self.pool.get('subcontractor.moves').browse(cr,uid,ids,context=context)
        sup_partner=sub_obj.partner_id.id
        list_moves=[]
        for m in sub_obj.move_lines:
            list_moves.append(m.id)
        
            out_vals={
                      'partner_id':sup_partner,
                      'picking_type_id':m.picking_type_id.id,
                      'location_id':m.location_id.id,
                      'location_dest_id':m.location_dest_id.id,
                      'group_id':m.group_id.id,
                      }
            pick_id=self.pool.get('stock.picking').create(cr,uid,out_vals,context=context)
                
            self.pool.get('stock.move').write(cr,uid,list_moves,{
                                                                 'picking_id':pick_id,
                                                                 },context=context)
        
        
#         for l in sub_obj.move_lines:
#             in_vals={
#                       'partner_id':sup_partner,
#                       'picking_type_id':1,
#                       'location_id':l.location_dest_id.id,
#                       'location_dest_id':l.location_id.id,
#                       }
#             pick_id1=self.pool.get('stock.picking').create(cr,uid,in_vals,context=context)
#                    
#             self.pool.get('stock.move').write(cr,uid,list_moves,{
#                                                                  'picking_id':pick_id1,
#                                                              },context=context)
        
        
        
class stoke_move(osv.osv):
    _inherit="stock.move"
    _columns={
            'subcontractor_picking':fields.many2one('subcontractor.moves','Subcontractor Picking')
              } 
    
class stock_picking(osv.osv):
    _inherit="stock.picking"
    
    def open_sub_wizard(self,cr,uid,ids,context=None):
        stock_obj=self.pool.get('stock.picking').browse(cr,uid,ids,context=context)
        
        move_obj=self.pool.get('stock.move').browse(cr,uid,ids,context=context)
        list_moves=[]
        for m in stock_obj.move_lines:
            list_moves.append(m.id)
            
        print "list---------------------------",list_moves
        vals={
              'partner_id':False,
              'move_lines':False
              }
        sub_id=self.pool.get('subcontractor.moves').create(cr,uid,vals,context=context)
        self.pool.get('stock.move').write(cr,uid,list_moves,{'subcontractor_picking':sub_id},context)

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