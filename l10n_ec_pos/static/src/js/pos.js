function l10n_ec_pos(instance, module) {

  var PosDB = module.PosDB;
  module.PosDB = module.PosDB.extend({

    _partner_search_string: function(partner){
      var str =  partner.name;
      if(partner.ced_ruc){
        str += '|' + partner.ced_ruc;
      }
      if(partner.ean13){
        str += '|' + partner.ean13;
      }
      if(partner.address){
        str += '|' + partner.address;
      }
      if(partner.phone){
        str += '|' + partner.phone.split(' ').join('');
      }
      if(partner.mobile){
        str += '|' + partner.mobile.split(' ').join('');
      }
      if(partner.email){
        str += '|' + partner.email;
      }
      str = '' + partner.id + ':' + str.replace(':','') + '\n';
      return str;
    }
    
  });
  
  var PosModelSuper = module.PosModel;
  module.PosModel = module.PosModel.extend({

        models: [
        {
            model:  'res.users',
            fields: ['name','company_id'],
            ids:    function(self){ return [self.session.uid]; },
            loaded: function(self,users){ self.user = users[0]; },
        },{ 
            model:  'res.company',
            fields: [ 'currency_id', 'email', 'website', 'company_registry', 'vat', 'name', 'phone', 'partner_id' , 'country_id'],
            ids:    function(self){ return [self.user.company_id[0]] },
            loaded: function(self,companies){ self.company = companies[0]; },
        },{
            model:  'decimal.precision',
            fields: ['name','digits'],
            loaded: function(self,dps){
                self.dp  = {};
                for (var i = 0; i < dps.length; i++) {
                    self.dp[dps[i].name] = dps[i].digits;
                }
            },
        },{ 
            model:  'product.uom',
            fields: [],
            domain: null,
            loaded: function(self,units){
                self.units = units;
                var units_by_id = {};
                for(var i = 0, len = units.length; i < len; i++){
                    units_by_id[units[i].id] = units[i];
                    units[i].groupable = ( units[i].category_id[0] === 1 );
                    units[i].is_unit   = ( units[i].id === 1 );
                }
                self.units_by_id = units_by_id;
            }
        },{
            model:  'res.users',
            fields: ['name','ean13'],
            domain: null,
            loaded: function(self,users){ self.users = users; },
        },{
            model:  'res.partner',
            fields: ['type_ced_ruc','ced_ruc','name','street','city','state_id','country_id','vat','phone','zip','mobile','email','ean13','write_date'],
            domain: [['customer','=',true]],
            loaded: function(self,partners){
                self.partners = partners;
                self.db.add_partners(partners);
            },
        },{
            model:  'res.country',
            fields: ['name'],
            loaded: function(self,countries){
                self.countries = countries;
                self.company.country = null;
                for (var i = 0; i < countries.length; i++) {
                    if (countries[i].id === self.company.country_id[0]){
                        self.company.country = countries[i];
                    }
                }
            },
        },{
            model:  'account.tax',
            fields: ['name','amount', 'price_include', 'include_base_amount', 'type'],
            domain: null,
            loaded: function(self,taxes){ 
                self.taxes = taxes; 
                self.taxes_by_id = {};
                for (var i = 0; i < taxes.length; i++) {
                    self.taxes_by_id[taxes[i].id] = taxes[i];
                }
            },
        },{
            model:  'pos.session',
            fields: ['id', 'journal_ids','name','user_id','config_id','start_at','stop_at','sequence_number','login_number'],
            domain: function(self){ return [['state','=','opened'],['user_id','=',self.session.uid]]; },
            loaded: function(self,pos_sessions){
                self.pos_session = pos_sessions[0]; 

                var orders = self.db.get_orders();
                for (var i = 0; i < orders.length; i++) {
                    self.pos_session.sequence_number = Math.max(self.pos_session.sequence_number, orders[i].data.sequence_number+1);
                }
            },
        },{
            model: 'pos.config',
            fields: [],
            domain: function(self){ return [['id','=', self.pos_session.config_id[0]]]; },
            loaded: function(self,configs){
                self.config = configs[0];
                self.config.use_proxy = self.config.iface_payment_terminal || 
                                        self.config.iface_electronic_scale ||
                                        self.config.iface_print_via_proxy  ||
                                        self.config.iface_scan_via_proxy   ||
                                        self.config.iface_cashdrawer;
                
                self.barcode_reader.add_barcode_patterns({
                    'product':  self.config.barcode_product,
                    'cashier':  self.config.barcode_cashier,
                    'client':   self.config.barcode_customer,
                    'weight':   self.config.barcode_weight,
                    'discount': self.config.barcode_discount,
                    'price':    self.config.barcode_price,
                });

                if (self.config.company_id[0] !== self.user.company_id[0]) {
                    throw new Error(_t("Error: The Point of Sale User must belong to the same company as the Point of Sale. You are probably trying to load the point of sale as an administrator in a multi-company setup, with the administrator account set to the wrong company."));
                }
            },
        },{
            model: 'stock.location',
            fields: [],
            ids:    function(self){ return [self.config.stock_location_id[0]]; },
            loaded: function(self, locations){ self.shop = locations[0]; },
        },{
            model:  'product.pricelist',
            fields: ['currency_id'],
            ids:    function(self){ return [self.config.pricelist_id[0]]; },
            loaded: function(self, pricelists){ self.pricelist = pricelists[0]; },
        },{
            model: 'res.currency',
            fields: ['symbol','position','rounding','accuracy'],
            ids:    function(self){ return [self.pricelist.currency_id[0]]; },
            loaded: function(self, currencies){
                self.currency = currencies[0];
                if (self.currency.rounding > 0) {
                    self.currency.decimals = Math.ceil(Math.log(1.0 / self.currency.rounding) / Math.log(10));
                } else {
                    self.currency.decimals = 0;
                }

            },
        },{
            model: 'product.packaging',
            fields: ['ean','product_tmpl_id'],
            domain: null,
            loaded: function(self, packagings){ 
                self.db.add_packagings(packagings);
            },
        },{
            model:  'pos.category',
            fields: ['id','name','parent_id','child_id','image'],
            domain: null,
            loaded: function(self, categories){
                self.db.add_categories(categories);
            },
        },{
            model:  'product.product',
            fields: ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'ean13', 'default_code', 
                     'to_weight', 'uom_id', 'uos_id', 'uos_coeff', 'mes_type', 'description_sale', 'description',
                     'product_tmpl_id'],
            domain: [['sale_ok','=',true],['available_in_pos','=',true]],
            context: function(self){ return { pricelist: self.pricelist.id, display_default_code: false }; },
            loaded: function(self, products){
                self.db.add_products(products);
            },
        },{
            model:  'account.bank.statement',
            fields: ['account_id','currency','journal_id','state','name','user_id','pos_session_id'],
            domain: function(self){ return [['state', '=', 'open'],['pos_session_id', '=', self.pos_session.id]]; },
            loaded: function(self, bankstatements, tmp){
                self.bankstatements = bankstatements;

                tmp.journals = [];
                _.each(bankstatements,function(statement){
                    tmp.journals.push(statement.journal_id[0]);
                });
            },
        },{
            model:  'account.journal',
            fields: [],
            domain: function(self,tmp){ return [['id','in',tmp.journals]]; },
            loaded: function(self, journals){
                self.journals = journals;

                // associate the bank statements with their journals. 
                var bankstatements = self.bankstatements;
                for(var i = 0, ilen = bankstatements.length; i < ilen; i++){
                    for(var j = 0, jlen = journals.length; j < jlen; j++){
                        if(bankstatements[i].journal_id[0] === journals[j].id){
                            bankstatements[i].journal = journals[j];
                        }
                    }
                }
                self.cashregisters = bankstatements;
            },
        },{
            label: 'fonts',
            loaded: function(self){
                var fonts_loaded = new $.Deferred();

                // Waiting for fonts to be loaded to prevent receipt printing
                // from printing empty receipt while loading Inconsolata
                // ( The font used for the receipt ) 
                waitForWebfonts(['Lato','Inconsolata'], function(){
                    fonts_loaded.resolve();
                });

                // The JS used to detect font loading is not 100% robust, so
                // do not wait more than 5sec
                setTimeout(function(){
                    fonts_loaded.resolve();
                },5000);

                return fonts_loaded;
            },
        },{
            label: 'pictures',
            loaded: function(self){
                self.company_logo = new Image();
                var  logo_loaded = new $.Deferred();
                self.company_logo.onload = function(){
                    var img = self.company_logo;
                    var ratio = 1;
                    var targetwidth = 300;
                    var maxheight = 150;
                    if( img.width !== targetwidth ){
                        ratio = targetwidth / img.width;
                    }
                    if( img.height * ratio > maxheight ){
                        ratio = maxheight / img.height;
                    }
                    var width  = Math.floor(img.width * ratio);
                    var height = Math.floor(img.height * ratio);
                    var c = document.createElement('canvas');
                        c.width  = width;
                        c.height = height
                    var ctx = c.getContext('2d');
                        ctx.drawImage(self.company_logo,0,0, width, height);

                    self.company_logo_base64 = c.toDataURL();
                    logo_loaded.resolve();
                };
                self.company_logo.onerror = function(){
                    logo_loaded.reject();
                };
                    self.company_logo.crossOrigin = "anonymous";
                self.company_logo.src = '/web/binary/company_logo' +'?_'+Math.random();

                return logo_loaded;
            },
        },
        ],    
    
  });
}


(function(){
    var _super = window.openerp.point_of_sale;
    window.openerp.point_of_sale = function(instance){
        _super(instance);
        var module = instance.point_of_sale;

        l10n_ec_pos(instance, module);

    }
})()
