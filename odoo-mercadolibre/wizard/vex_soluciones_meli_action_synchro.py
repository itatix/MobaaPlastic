import requests
import threading
import base64
from ..models.vex_soluciones_meli_config  import API_URL, INFO_URL, get_token
from ..models.vex_soluciones_product_template import Product
from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError
import pprint

import logging
_logger = logging.getLogger(__name__)

id_api       = 'id_app'
server_api   = 'server_meli'

class MeliActionSynchro(models.TransientModel):
    _name               = "meli.action.synchro"
    _description        = "Synchronized Server"
    server              = fields.Many2one('meli.synchro.instance',
                             "Instance", required=True)
    action              = fields.Many2many('meli.action.list')

    def check_synchronize(self,server):
        access_token = server.access_token
        res = requests.get(INFO_URL, params={'access_token': access_token})

        if res.status_code != 200:
            token = get_token(server.app_id, server.secret_key, server.redirect_uri, '', server.refresh_token)
            if token:
                update = {
                    'access_token' : token['access_token'],
                    'refresh_token' : token['refresh_token'],
                }
                exist = self.env['meli.synchro.instance'].search([('user_id', '=', str(server.user_id))])
                exist.write(update)


    @api.model
    def insert_variants(self, variants, pictures, product,server):
        product_product = self.env['product.product'].search([('product_tmpl_id', '=', int(product.id))])
        pictures_dict = dict()

        for picture in pictures:
            pictures_dict[picture['id']] = picture['url']

        for variant in variants:
            variant_id       = variant['id']
            variant_price    = variant['price']
            variant_image_id = variant['picture_ids'][0]
            variant_combinations = variant['attribute_combinations']
            variant_attr_ids = []
            for combination in variant_combinations:
                #buscar el atributo
                attribute = self.env['product.attribute'].search([('id_app', '=', str(combination['id'])),
                                                                  ('server_meli','=',server.id)])
                attr_value = combination['value_name']
                attr_line = self.env['product.attribute.value'].search([('name', '=', str(attr_value)), ('attribute_id', '=', attribute.id)])
                if not attr_line:
                    raise ValidationError(str(attribute.id)+'-'+str(combination['id'])+'/'+str(attr_value))

                variant_attr_ids.append(attr_line.id)
            #if str(variant_id) == '67216440550':
            #    raise ValidationError(variant_attr_ids)


            attr_value_ids = []
            for produc in product_product:
                for attr_value_id in produc.product_template_attribute_value_ids:
                    attr_value_ids.append(attr_value_id.product_attribute_value_id.id)

                bb = list(set(variant_attr_ids).intersection(attr_value_ids))


                if len(variant_attr_ids) == len(bb):
                    #if produc.id == 41:
                    #    raise ValidationError('sii')
                    #if set(variant_attr_ids) == set(attr_value_ids):
                    variant_image = requests.get(pictures_dict[variant_image_id])
                    produc.write({
                        'id_app_varition': str(variant_id),
                        'meli_regular_price': float(variant_price),
                        'image_1920' : base64.b64encode(variant_image.content),
                    })
                attr_value_ids = []

    @api.model
    def check_customer(self,dr,server):
        buyer_exist = self.env['res.partner'].search([(id_api, '=', str(dr['id'])), ('server_meli', '=', server.id)])
        if not buyer_exist:
            buyer_exist = self.env['res.partner'].create({
                        'name': str(dr['first_name']) + ' ' + str(dr['last_name']) ,
                        'id_app' : str(dr['id']),
                        'server_meli': server.id,
                        'email':str(dr['email']),
                        'phone':str(dr['phone']['area_code'])+str(dr['phone']['number'])
                    })
        return  buyer_exist

    #funcion donde se declaran los valores a importar
    @api.model
    def json_fields(self, dr, query,  server):
        # inicializando variables create y write
        create = {}
        write = {}

        if query == "products":
            body = dr['body']
            active = True if  body['status'] == 'active' else False

            thumbnail = body['thumbnail']
            myimage = requests.get(thumbnail)
            id_category = body['category_id']
            available_product = body['available_quantity']



            create = {
                            'server_meli'      : server.id,
                            'id_app'           : body['id'],
                            'name'             : body['title'],
                            'currency_id'      : body['currency_id'],
                            'list_price'       : body['price'],
                            'type'             : 'product',
                            'image_1920'       : base64.b64encode(myimage.content),
                            'is_published'     : active,
                            'product_condition': body['condition'],
                            'active_meli'           : active,
                            'permalink'        : body['permalink'],
                            'public_categ_ids' : [(6, 0, [self.check_categories(body['category_id'],server,None).id])]
                        }
            write = create
            if server.company:
                create['company_id']  = server.company.id
                write['company_id']   = server.company.id

        if query == "questions":
            create = {
                            'id_app' : dr['item_id'],
                            'server_meli': server.id,
                            'question_id' : dr['id'],
                            'date_created' : dr['date_created'],
                            'product_id' : dr['product_id'],
                            'seller_id' : dr['seller_id'],
                            'status' : dr['status'],
                            'text' : dr['status'],
                            'answer_text' : dr['answer']['text'] if dr['answer'] else '',
            }

            write = create

        if query == "categories":
            create = {
                'name':dr['name'],
                 'id_app' : dr['id'],
                 'server_meli': server.id,
                }

            write = create
        if query == "orders":
            create = {
                        'partner_id': self.check_customer(dr['buyer'],server).id,
                        'id_app' : dr['id'],
                        'server_meli': server.id,
                        'pricelist_id': server.pricelist.id,
                        #'meli_order_id' : meli_order_id,
                        #'meli_status' : meli_status,
                        #'meli_status_detail' : meli_status_detail,
                        #'meli_total_amount' : meli_total_amount,
                        'warehouse_id'            :   server.warehouse.id
                    }
            write = {
                'pricelist_id': server.pricelist.id,
                'warehouse_id'            :   server.warehouse.id
                }
            if server.company:
                create['company_id']  = server.company.id
                write['company_id']   = server.company.id


        result = {
            'create': create,
            'write': write,

        }
        return result

    @api.model
    def meli_api(self,server,query,filtro):
        if query == "products":
            products_url = '{}/users/{}/items/search?search_type=scan&access_token={}'.format(API_URL, str(server.user_id),str(server.access_token))
            res = requests.get(products_url)
            res = res.json()[filtro]
            array_products = []
            for r in res:
                item_url = '{}/items?ids={}&access_token={}'.format(API_URL,r,server.access_token)
                item = requests.get(item_url).json()
                array_products.append(item)

            #string_items = ','.join(res)
            #item_url = '{}/items?ids={}&access_token={}'.format(API_URL,string_items,server.access_token)
            #raise ValidationError(item_url)
            #items = requests.get(item_url).json()
            #raise ValidationError(products_url)
            return  array_products
        if query == 'categories':
            categories_url =  "https://api.mercadolibre.com/sites/{}/categories".format(server.meli_country)
            res = requests.get(categories_url).json()
            return  res
        if query == "orders":
            orders_url = '{}/orders/search?seller={}&access_token={}'.format(API_URL,str(server.user_id),str(server.access_token))
            #raise ValidationError(orders_url)
            res = requests.get(orders_url)
            res = res.json()[filtro]
            return res

    @api.model
    def check_picture(self,image,server,product):
        #verificar si la imagen existe
        img = product.product_template_image_ids.search([('id_app','=',image['id']),
                                                ('server_meli','=',server.id),('product_tmpl_id','=',product.id)], limit=1)
        #raise ValidationError(img)
        if not img:
            url = image['url']
            myfile = requests.get(url)
            img = self.env['product.image'].create({
            'id_app'     : image['id'],
            'server_meli': server.id,
            'image_1920': base64.b64encode(myfile.content),
            'product_tmpl_id': product.id,
            'name': image['id'],

            })
        return img

    @api.model
    def check_categories(self,id ,  server , parent):
        cat_id = None
        existe = self.env['product.public.category'].search([('id_app', '=', str(id)),('server_meli','=',int(server.id))])
        if existe:
            cat_id = existe
        else:
            #buscar la data en el woocommerce
            #cwoo = wcapi.get("products/categories/"+str(id)).json()
            cwoo = 0
            category_url = '{}/categories/{}'.format(API_URL, id)
            #raise ValidationError(category_url)
            cwoo = requests.get(category_url).json()
            #name_categor = res.json()['name']
            #crear la categoria

            json = self.json_fields(cwoo,'categories',server)
            #pro = self.env['product.public.category'].create(json['create'])
            if not parent:
                parent = 'NULL'
            self.env.cr.execute("INSERT INTO product_public_category(name,id_app,server_meli,parent_id)"
                                " VALUES ('{}','{}',{},{})".format(json['create']['name'],id,server.id,parent))
            pro = self.env['product.public.category'].search([('id_app', '=', str(id)),
                                                                 ('server_meli','=',int(server.id))])

            cat_id = pro
        return  cat_id


    @api.model
    def insert_questions(self,exist,server):
        questions_url = '{}/questions/search?item_id={}&access_token={}'.format(API_URL,str(exist.id_app),str(server.access_token))
        res = requests.get(questions_url)
        res = res.json()
        questions = res['questions']
        for question in questions:
            existq = self.env['meli.questions'].search([('question_id', '=', question['id']), ('server_meli', '=', int(server.id))])
            question['product_id'] = exist.id
            json = self.json_fields(question, 'questions', server)

            if not  existq:
                existq = self.env['meli.questions'].create(json['create'])
            else:
                existq.write(json['write'])

    @api.model
    def check_imagenes(self,imagenes,server,exist):
        #verificar las imagenes
        imagenes_array = {'ja'}

        for i in imagenes:
            imm = self.check_picture(i,server,exist)
            imagenes_array.add(imm.id)
            imagenes_odoo_array = {'ja'}
            for ii in exist.product_template_image_ids:
                imagenes_odoo_array.add(ii.id)
            resta = imagenes_odoo_array - imagenes_array
            for r in resta:
                self.env['product.image'].search([('id', '=', int(r))]).unlink()

    @api.model
    def inser_terminos(self,term,atributo,server):
        #import json
        #y = json.dumps(term)
        for t in term:
            et = self.env['product.attribute.value'].search([('name', '=', str(t['name'])),
                                                             (server_api,'=',server.id),('attribute_id','=',atributo.id)])
            if not et:
                atributo.value_ids += self.env['product.attribute.value'].create({
                    'name'        : t['name'],
                    id_api      : t['id'],
                    server_api : server.id,
                    'attribute_id': atributo.id
                })
    @api.model
    def check_attributes(self, at,server):
        at_id = None
        existe = self.env['product.attribute'].search([(id_api, '=', str(at['id'])),(server_api,'=',int(server.id))])
        if existe:
            at_id = existe
        else:
            #json = self.json_fields(attr, 'products/attributes', wcapi,server)
            #raise ValidationError(json['create']['server'])
            pro  = self.env['product.attribute'].create({
                'name': at['name'],
                id_api: at['id'],
                server_api : server.id
            })
            at_id = pro
        #insertar sus terminod
        self.inser_terminos(at['values'],at_id,server)
            #raise

        return at_id

    @api.model
    def check_terminos(self,t,server,atr):
        #sincronizar todos los terminos
        #buscar el id  del termino
        t_id = None
        existe = self.env['product.attribute.value'].search([('name', '=', str(t)),(server_api, '=', int(server.id)),('attribute_id', '=', int(atr.id))])
        if existe:
            t_id = existe
        return t_id


    @api.model
    def insert_variations(self,dr,server,creado):
        #recorrer las variantes y chekar todas los atrbutos
        #guardar el id por atributo y luego colocarlo en el respectivo
        variants = dr['variations']
        variantes_array   = {'ja'}
        #variants_array = {}
        values_array = {'ja'}
        if variants:
             c = 0
             #import json
             #raise ValidationError(json.dumps(variants))
             for v in variants:
                 for vi in v['attribute_combinations']:
                     at = self.check_attributes(vi,server)
                     #values_array[at.id] += {'ja'}
                     variantes_array.add(at.id)
                     json_at = []
                     if at:
                         #buscar si existe el atributo en atribute line
                         atl = self.env['product.template.attribute.line'].search(
                                    [('attribute_id', '=', int(at.id)), ('product_tmpl_id', '=', int(creado.id))])
                         if atl:
                             #verificar si existe ese valor  en ese atributo line
                             valores_actuales  = atl.value_ids
                             va_array = []
                             for va in valores_actuales:
                                 va_array.append(va.name)

                             for vx in vi['values']:
                                 #raise ValidationError(vx)
                                 if not vx['name'] in va_array:
                                     vv = self.check_terminos(vx['name'], server , at)
                                     #raise ValidationError('que')
                                     if vv:
                                         atl.value_ids += vv
                                 values_array.add(str(at.id)+'_'+vx['name'])
                                 if creado.id == 356 :
                                     _logger.info('Value %s', pprint.pformat(values_array))

                         else:
                             for vx in vi['values']:
                                 vv = self.check_terminos(vx['name'], server , at)
                                 json_at.append(vv.id)
                             creado.attribute_line_ids += self.env['product.template.attribute.line'].new({
                                        'attribute_id': int(at.id),
                                        'value_ids':[(6,0,json_at)]
                                    })
                 ppp = self.env['product.product'].search([('product_tmpl_id', '=', int(creado.id)),
                                                           ('id_app_varition','=',False)])
                 ppp.write({'id_app_varition' : v['id']})
                 '''
                 if c == 1:
                     raise ValidationError(ppp)
                 c += 1
                 '''
                 #verificar el producto product creado
             #self.insert_variants(variants,dr['pictures'],creado,server)


             #depurar las variantes eliminadas
             '''
             variantes_odoo_array = {'ja'}
             for ii in creado.attribute_line_ids:
                 variantes_odoo_array.add(ii.attribute_id.id)
             resta = variantes_odoo_array - variantes_array
             for r in resta:
                 self.env['product.template.attribute.line'].search([('attribute_id', '=', int(r)),('product_tmpl_id','=',creado.id)]).unlink()

             interseccion = variantes_odoo_array & variantes_array
             interseccion.remove('ja')
             for i in interseccion:
                 ii = self.env['product.template.attribute.line'].search([('attribute_id.id', '=', int(i))
                                                                             ,('product_tmpl_id','=',creado.id)])
                 #depurar los valores que no coinciden
                 if ii:
                     valores_odoo =  {'ja'}
                     for va in ii.value_ids:
                         valores_odoo.add(str(va.attribute_id.id)+'_'+va.name)
                     #if creado.id == 356 :
                     #    raise ValidationError(values_array)
                     resta = valores_odoo - values_array
                     if creado.id == 356 :
                             _logger.info('Valores Iniciales: %s', pprint.pformat(values_array))
                             _logger.info('Valores Finales: %s', pprint.pformat(valores_odoo))
                             #raise ValidationError(resta)
                     #resta.remove('ja')
                     for r in resta:
                         split = r.split('_')
                         split = split[1]

                         for x in ii.value_ids:
                             if x.name == split:
                                 ii.value_ids = [(3,x.id)]
                                 #if creado.id == 356 :
                                 #    raise ValidationError(x)
                         d = self.env['product.attribute.value'].search([('attribute_id', '=', int(ii.id)),('name','=',str(r))])

                         d.unlink()
             '''


        return 0

    @api.model
    def check_produc(self,id ,server):
        pro_id = None
        existe = self.env['product.template'].search([(id_api, '=', str(id)),(server_api,'=',int(server.id))])
        if existe:
            pro_id = existe
        else:
            #buscar la data en mercado libre
            pwoo = None
            item_url = '{}/items?ids={}&access_token={}'.format(API_URL,id,server.access_token)
            #raise ValidationError(item_url)
            item = requests.get(item_url).json()
            json = self.json_fields(item[0],'products',server)
            pro = self.env['product.template'].create(json['create'])
            #insertar los atributos y variantes
            self.check_imagenes(item[0]['body']['pictures'],server,pro)
            self.insert_variations(item[0]['body'],server,pro)
            self.insert_questions(pro,server)

            pro_id = pro
        return  pro_id

    @api.model
    def check_product_order(self,p  , server):
        #raise ValidationError('jaaa')
        pp = None
        atributo = p['variation_id']
        #condicion para verificar si es un atributo
        if  atributo:
            #raise ValidationError(atributo)
            #buscar en product product
            pp = self.env['product.product'].search([('id_app_varition','=',int(atributo)),('server_meli','=',int(server.id)),])
            #si no existe crearlo
            if not pp:
                self.check_produc(p['id'], server)
                pp = self.env['product.product'].search([('id_app_varition', '=', int(atributo)),('server_meli', '=', int(server.id))])
        else:
            pt = self.check_produc(p['id'],  server)
            #raise ValidationError('jooo')
            #raise ValidationError(pt.product_variant_ids)

            pp = self.env['product.product'].search([('product_tmpl_id', '=', int(pt.id))])
        return  pp

    @api.model
    def insert_lines(self,lines,server,creado):
        amount_untaxed = amount_tax = 0.0
        for p in lines:
            #raise ValidationError(p['quantity'])
            existe = self.check_product_order(p['item'] ,server)
            #raise ValidationError(existe)
            new_line = {
                                    'name':'line_'+str(existe.id),
                                    'product_id': existe.id,
                                    'product_uom_qty': int(p['quantity']),
                                    'price_unit': float(p['unit_price'])-float(p['sale_fee'])  ,
                                    'order_id': creado.id,
                                    #'price_subtotal': p['subtotal'],
                                    'price_tax': 0.0,
                                    #'price_total': p['subtotal'],
                                    'tax_id': None,
                                    #campos requeridos
                                    'customer_lead':1.0,
                                }
            creado.order_line += self.env['sale.order.line'].new(new_line)
            #raise ValidationError(creado.order_line)
            amount_untaxed += (float(p['unit_price'])-float(p['sale_fee']))*int(p['quantity'])


        creado.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax,
                            })

    @api.model
    def for_child(self,childrens,server,parent):
        if childrens:
            for child in childrens:
                c = self.check_categories(child['id'],server,parent.id)
                #category_url = '{}/categories/{}'.format(API_URL, str(c.id_app))
                #childchild = requests.get(category_url).json()
                #self.for_child(childchild['children_categories'],server,c)

    @api.model
    def insert_categorias_children(self,id,server,parent):
        categories_url =  "https://api.mercadolibre.com/categories/{}".format(str(id))
        res = requests.get(categories_url).json()
        if 'children_categories' in res:
            self.for_child(res['children_categories'],server,parent)


    @api.model
    def synchronize(self, api, action, server):
        query = str(action.argument)
        table = str(action.model)

        self.check_synchronize(server)

        data_request = self.meli_api(server , query , 'results')
        #import json
        #raise ValidationError(json.dumps(data_request))
        for dr in data_request:
            if query == "products":
                dr = dr[0]
            #import json
            #raise ValidationError(json.dumps(dr))
            if query == "products" and  server.import_products_paused == False:
                if  dr['body']['status'] != 'active':
                    continue
            #import json
            #raise ValidationError(json.dumps(dr[0]['body']['id']))
            #raise ValidationError(json.dumps(dr['body']['id']))
            id_appx = dr['body']['id'] if query == "products" else dr['id']
            exist = self.env[table].search([('id_app', '=', str(id_appx)), ('server_meli', '=', int(server.id))])
            json = self.json_fields(dr, query, server)
            if not  exist:
                #raise ValidationError(json)
                exist = self.env[table].create(json['create'])
                if query == "orders":
                    self.insert_lines(dr['order_items'],server,exist)

            else:
                #raise ValidationError('f')
                exist.write(json['write'])

            if query == "products":
                self.check_imagenes(dr['body']['pictures'],server,exist)
                self.insert_variations(dr['body'],server,exist)
                self.insert_questions(exist,server)
            if query == 'categories':
                self.insert_categorias_children(dr['id'],server,exist)


    def meli_import(self):
        server = self.server
        action = self.action
        api = None
        start_date = fields.Datetime.now()
        for i in action:
            self.synchronize(api, i, server)
            end_date = fields.Datetime.now()
            i.log += self.env['meli.logs'].new({
                'start_date': start_date,
                'end_date': end_date,
                'description': 'Syncro Manually' ,
                'state': 'done',
                'server': server.id
            })

    def meli_import_thread(self):
        threaded_synchronization = threading.Thread(target=self.meli_import())
        threaded_synchronization.run()

        view_rec = self.env.ref('odoo-mercadolibre.meli_ok',
                                raise_if_not_found=False)
        action = self.env.ref(
            'odoo-mercadolibre.action_view_meli_synchro', raise_if_not_found=False
        ).read([])[0]
        action['views'] = [(view_rec and view_rec.id or False, 'form')]

        return action

    @api.model
    def sync_start(self, server, action):
        print("serveeeer", server, action)
        if server:
            self.synchronize(None, action, server)

    def start_start(self, argument):
        accion = self.env['meli.action.list'].search([('argument', '=', argument)])
        print("acccciooon", accion)
        if accion:
            servers = self.env['meli.synchro.instance'].search([('active_automatic', '=', True)])
            print("serveeeeers", servers)
            for server in servers:
                start_date = fields.Datetime.now()
                threaded_synchronization = threading.Thread(target=self.sync_start(server, accion))
                threaded_synchronization.run()
                end_date = fields.Datetime.now()
                accion.log += self.env['meli.logs'].new({
                    'start_date': start_date,
                    'end_date': end_date,
                    'description': 'Syncro Automatic',
                    'state': 'done',
                    'server': server.id
                })

    # sincronizar un producto
    def start_sync_products(self):
        self.start_start('products')

    def start_sync_orders(self):
        self.start_start('orders')
