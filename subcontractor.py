from openerp.osv import fields, osv
from bsddb.dbtables import _columns

class subcontractor_moves(osv.osv):
    _name='subcontractor.moves'
    _columns={
              'partner_id':fields.many2one('res.partner',"Supplier"),
              'move_lines':fields.one2many('stock.move','picking_id',"Products")
              }
    
    def send_to_subcontractor(self,cr,uid,ids,context):
        print "***************"
        sub_obj=self.browse(cr,uid,ids)
        for m in sub_obj.move_lines:
            vals={
                  'partner_id':sub_obj.partner_id.id,
                  'location_id':m.location_id.id,
                  'location_dest_id':m.location_dest_id,
                  'procure_method':m.procure_method,
                  'product_id':m.product_id,
                  'product_uom_qty':m.product_uom_qty,
                  'picking_type_id':m.picking_type_id.id,
                  }
            delivery_id=self.pool.get('stock.move').create(cr,uid,vals,context=context)
#         print "created..............",delivery_id
 
# class stoke_move(osv.osv):
#     _inherit="stock.move"
#     _columns={
#               'pick_id':fields.many2one('subcontractor.moves','Picking')
#               }
    
class stock_picking(osv.osv):
    _inherit="stock.picking"
    
    def open_sub_wizard(self,cr,uid,ids,context=None):
        pur_obj=self.pool.get('stock.picking').browse(cr,uid,ids,context=context)
        move_obj=self.pool.get('stock.move').browse(cr,uid,ids,context=context)
        sub_obj=self.pool.get('subcontractor.moves')
         
        list_moves=list(pur_obj.move_lines)
        list_moves=[]
         
        print "pur_obj.partner_id---------------------",list(pur_obj.move_lines),ids,pur_obj.partner_id
         
        for m in pur_obj.move_lines:
            print "all fields ======================",m.id,m.product_id,m.product_uom_qty,m.procure_method,m.location_id,m.location_dest_id,m.name,m.product_uom.id,m.picking_id.id
            list_moves.append(pur_obj.move_lines)
            vals={
                  'partner_id':m.partner_id.id,
                    'move_lines':[(0,0, {
                                         'product_id':m.product_id.id,
                                         'name':m.name,
                                        'product_uom':m.product_uom.id,
                                        'picking_id':m.picking_id.id,
                                         'product_uom_qty':m.product_uom_qty,
                                         'procure_method':m.procure_method,
                                         'location_id':m.location_id.id,
                                         'location_dest_id':m.location_dest_id.id,
                                         })]
                  }
        sub_id=sub_obj.create(cr,uid,vals,context=context)
         
        print "----------------------------id",sub_id
#         sub_obj.write(cr,uid,sub_id,{
#                                          'partner_id':pur_obj.partner_id.id,
#                                             "move_lines":
#                                               }
#                                        ,context)
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
      