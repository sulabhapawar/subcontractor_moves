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
        move_obj=self.pool.get('stock.move').browse(cr,uid,ids,context=context)
        list_moves=[]
        for m in sub_obj.move_lines:
            list_moves.append(m.id)
        
        out_vals={
                      'partner_id':sup_partner,
                      'picking_type_id':m.picking_type_id.id,
                      'origin':m.origin,
                      }
        pick_id=self.pool.get('stock.picking').create(cr,uid,out_vals,context=context)
        print "list_moves----------------",list_moves
        self.pool.get('stock.move').write(cr,uid,list_moves,{
                                                                 'picking_id':pick_id,
                                                                'location_id':m.location_id.id,
                                                                'location_dest_id':m.location_dest_id.id,
                                                                'group_id':m.group_id.id,
                                                                 },context=context)
        
        rece=self.pool.get('stock.picking').browse(cr,pick_id,context=context)
        move_list=[]
        for m in sub_obj.move_lines:
            move_list.append(m.id)
        print "move_list===================",move_list,rece.id,pick_id
        in_vals={
                      'partner_id':sup_partner,
                      'picking_type_id':1,
                      'origin':m.origin,
                      }
        pick_id1=self.pool.get('stock.picking').create(cr,uid,in_vals,context=context)
                            
        self.pool.get('stock.move').write(cr,uid,move_list,{
                                                                 'picking_id':pick_id1,
                                                                 'location_id':m.location_dest_id.id,
                                                                  'location_dest_id':m.location_id.id,
                                                                  'group_id':m.group_id.id,
                                                                       
                                                             },context=context)
        
        
        
class stoke_move(osv.osv):
    _inherit="stock.move"
    _columns={
            'subcontractor_picking':fields.many2one('subcontractor.moves','Subcontractor Picking'),
            'incoming_id':fields.many2one('incoming.delivery','Incoming Shipments'),
            'outgoing_id':fields.many2one('incoming.deliery','Delivery Orders')
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
        
# class incoming_refunds(osv.osv):
#     _inherit="product.product"
#     _columns={
# #             'state':fields.selection([('refund','Refunded'),('to_supplier','To supplier')]),
# #             'incoming_ship_ids':fields.one2many('stock.move','incoming_id','Incoming shipments'),
# #             'delivery_order_ids':fields.one2many('stock.move','outgoing_id','Delivery Orders'),
#             'count_refunds':fields.function('_count_refunds',string='# Incoming Refunds', type='integer'),
#             }
#     
#     def _count_refunds(self,cr,uid, ids, field_name, arg, context=None):
#         print "************"
#         res = dict.fromkeys(ids, 0)
#         for template in self.browse(cr, uid, ids, context=context):
#             res[template.id] = sum([p.count_moves for p in template.incoming_ship_ids])
#         return res
# 
#     def action_view_refunds(self,cr,uid,ids,context=None):
#         print "***********************"
#         products = self._get_products(cr, uid, ids, context=context)
#         result = self._get_act_window_dict(cr, uid, 'purchase.action_purchase_line_product_tree', context=context)
#         result['domain'] = "[('product_id','in',[" + ','.join(map(str, products)) + "])]"
#         return result
    
class sale_order(osv.osv):
    _inherit='sale.order'
    
    def show_incoming_ships(self,cr,uid,ids,context=None):
        print "**************"
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree_all')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]

        #compute the number of delivery orders to display
        pick_ids = []
        for so in self.browse(cr, uid, ids, context=context):
#             pick_ids += [picking.id for picking in so.picking_ids]

            for picking in so.picking_ids:
                if picking.picking_type_id.id==1 and picking.location_id.id==9 and picking.location_dest_id.id==12:
                    print "picking============",picking.picking_type_id.id
                    pick_ids.append(picking.id)
                
        #choose the view_mode accordingly
        
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
            print "map(str, pick_ids)--------------------",map(str, pick_ids),result['domain']
        else:
            res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result
    
    def show_customer_refunds(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree1')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        #compute the number of invoices to display
        inv_ids = []
        for so in self.browse(cr, uid, ids, context=context):
            for invoice in so.invoice_ids:
                if invoice.type=='out_refund' and invoice.state=='paid':
                    inv_ids.append(invoice.id)
        print "inv_ids--------------",inv_ids
        #choose the view_mode accordingly
        if len(inv_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
            print "result=========",result['domain']
        else:
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        return result
    
class account_invoice(osv.osv):
    _inherit="account.invoice"
    
    def send_invoice_to_supplier(self,cr,uid,ids,context=None):
        print "***********"
        obj=self.browse(cr,uid,ids,context=context)
        line_obj=self.pool.get('account.invoice.line').browse(cr,uid,ids,context=context)
        print "supplier==============",line_obj.partner_id
        
        
        
        
        
        
        
        
        