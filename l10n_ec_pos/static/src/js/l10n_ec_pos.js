odoo.define('l10n_ec_pos.l10n_ec_pos', function(require) {
    "user strict";

    var models = require('point_of_sale.models');


    PosDB = PosDB.extend({

        _partner_search_string: function(partner){
            var str =  partner.name;
            if(partner.identifier){
	        str += '|' + partner.identifier;
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

    models.PosModel = models.PosModel.extend({

        models: [
            {
                label:  'version',
                loaded: function(self){
                    return session.rpc('/web/webclient/version_info',{}).done(function(version) {
                        self.version = version;
                    });
                },

            },{
                model:  'res.users',
                fields: ['name','company_id'],
                ids:    function(self){ return [session.uid]; },
                loaded: function(self,users){ self.user = users[0]; },
            },{
                model:  'res.company',
                fields: [ 'currency_id', 'email', 'website', 'company_registry', 'vat', 'name', 'phone', 'partner_id' , 'country_id', 'tax_calculation_rounding_method'],
                ids:    function(self){ return [self.user.company_id[0]]; },
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
                context: function(self){ return { active_test: false }; },
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
                model:  'res.partner',
                fields: ['identifier', 'name','street','city','state_id','country_id','vat','phone','zip','mobile','email','barcode','write_date','property_account_position_id'],
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
                fields: ['name','amount', 'price_include', 'include_base_amount', 'amount_type', 'children_tax_ids'],
                domain: null,
                loaded: function(self, taxes){
                    self.taxes = taxes;
                    self.taxes_by_id = {};
                    _.each(taxes, function(tax){
                        self.taxes_by_id[tax.id] = tax;
                    });
                    _.each(self.taxes_by_id, function(tax) {
                        tax.children_tax_ids = _.map(tax.children_tax_ids, function (child_tax_id) {
                            return self.taxes_by_id[child_tax_id];
                        });
                    });
                },
            },{
                model:  'pos.session',
                fields: ['id', 'journal_ids','name','user_id','config_id','start_at','stop_at','sequence_number','login_number'],
                domain: function(self){ return [['state','=','opened'],['user_id','=',session.uid]]; },
                loaded: function(self,pos_sessions){
                    self.pos_session = pos_sessions[0];
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

                    if (self.config.company_id[0] !== self.user.company_id[0]) {
                        throw new Error(_t("Error: The Point of Sale User must belong to the same company as the Point of Sale. You are probably trying to load the point of sale as an administrator in a multi-company setup, with the administrator account set to the wrong company."));
                    }

                    self.db.set_uuid(self.config.uuid);

                    var orders = self.db.get_orders();
                    for (var i = 0; i < orders.length; i++) {
                        self.pos_session.sequence_number = Math.max(self.pos_session.sequence_number, orders[i].data.sequence_number+1);
                    }
                },
            },{
                model:  'res.users',
                fields: ['name','pos_security_pin','groups_id','barcode'],
                domain: function(self){ return [['company_id','=',self.user.company_id[0]],'|', ['groups_id','=', self.config.group_pos_manager_id[0]],['groups_id','=', self.config.group_pos_user_id[0]]]; },
                loaded: function(self,users){
                    // we attribute a role to the user, 'cashier' or 'manager', depending
                    // on the group the user belongs.
                    var pos_users = [];
                    for (var i = 0; i < users.length; i++) {
                        var user = users[i];
                        for (var j = 0; j < user.groups_id.length; j++) {
                            var group_id = user.groups_id[j];
                            if (group_id === self.config.group_pos_manager_id[0]) {
                                user.role = 'manager';
                                break;
                            } else if (group_id === self.config.group_pos_user_id[0]) {
                                user.role = 'cashier';
                            }
                        }
                        if (user.role) {
                            pos_users.push(user);
                        }
                        // replace the current user with its updated version
                        if (user.id === self.user.id) {
                            self.user = user;
                        }
                    }
                    self.users = pos_users;
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
                fields: ['name','symbol','position','rounding'],
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
                model:  'pos.category',
                fields: ['id','name','parent_id','child_id','image'],
                domain: null,
                loaded: function(self, categories){
                    self.db.add_categories(categories);
                },
            },{
                model:  'product.product',
                fields: ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'barcode', 'default_code',
                         'to_weight', 'uom_id', 'description_sale', 'description',
                         'product_tmpl_id','tracking'],
                order:  ['sequence','default_code','name'],
                domain: [['sale_ok','=',true],['available_in_pos','=',true]],
                context: function(self){ return { pricelist: self.pricelist.id, display_default_code: false }; },
                loaded: function(self, products){
                    self.db.add_products(products);
                },
            },{
                model:  'account.bank.statement',
                fields: ['account_id','currency_id','journal_id','state','name','user_id','pos_session_id'],
                domain: function(self){ return [['state', '=', 'open'],['pos_session_id', '=', self.pos_session.id]]; },
                loaded: function(self, cashregisters, tmp){
                    self.cashregisters = cashregisters;

                    tmp.journals = [];
                    _.each(cashregisters,function(statement){
                        tmp.journals.push(statement.journal_id[0]);
                    });
                },
            },{
                model:  'account.journal',
                fields: ['type', 'sequence'],
                domain: function(self,tmp){ return [['id','in',tmp.journals]]; },
                loaded: function(self, journals){
                    var i;
                    self.journals = journals;

                    // associate the bank statements with their journals.
                    var cashregisters = self.cashregisters;
                    var ilen = cashregisters.length;
                    for(i = 0; i < ilen; i++){
                        for(var j = 0, jlen = journals.length; j < jlen; j++){
                            if(cashregisters[i].journal_id[0] === journals[j].id){
                                cashregisters[i].journal = journals[j];
                            }
                        }
                    }

                    self.cashregisters_by_id = {};
                    for (i = 0; i < self.cashregisters.length; i++) {
                        self.cashregisters_by_id[self.cashregisters[i].id] = self.cashregisters[i];
                    }

                    self.cashregisters = self.cashregisters.sort(function(a,b){
		        // prefer cashregisters to be first in the list
		        if (a.journal.type == "cash" && b.journal.type != "cash") {
		            return -1;
		        } else if (a.journal.type != "cash" && b.journal.type == "cash") {
		            return 1;
		        } else {
                            return a.journal.sequence - b.journal.sequence;
		        }
                    });

                },
            },  {
                model:  'account.fiscal.position',
                fields: [],
                domain: function(self){ return [['id','in',self.config.fiscal_position_ids]]; },
                loaded: function(self, fiscal_positions){
                    self.fiscal_positions = fiscal_positions;
                }
            }, {
                model:  'account.fiscal.position.tax',
                fields: [],
                domain: function(self){
                    var fiscal_position_tax_ids = [];

                    self.fiscal_positions.forEach(function (fiscal_position) {
                        fiscal_position.tax_ids.forEach(function (tax_id) {
                            fiscal_position_tax_ids.push(tax_id);
                        });
                    });

                    return [['id','in',fiscal_position_tax_ids]];
                },
                loaded: function(self, fiscal_position_taxes){
                    self.fiscal_position_taxes = fiscal_position_taxes;
                    self.fiscal_positions.forEach(function (fiscal_position) {
                        fiscal_position.fiscal_position_taxes_by_id = {};
                        fiscal_position.tax_ids.forEach(function (tax_id) {
                            var fiscal_position_tax = _.find(fiscal_position_taxes, function (fiscal_position_tax) {
                                return fiscal_position_tax.id === tax_id;
                            });

                            fiscal_position.fiscal_position_taxes_by_id[fiscal_position_tax.id] = fiscal_position_tax;
                        });
                    });
                }
            },  {
                label: 'fonts',
                loaded: function(){
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
                        c.height = height;
                        var ctx = c.getContext('2d');
                        ctx.drawImage(self.company_logo,0,0, width, height);

                        self.company_logo_base64 = c.toDataURL();
                        logo_loaded.resolve();
                    };
                    self.company_logo.onerror = function(){
                        logo_loaded.reject();
                    };
                    self.company_logo.crossOrigin = "anonymous";
                    self.company_logo.src = '/web/binary/company_logo' +'?dbname=' + session.db + '&_'+Math.random();

                    return logo_loaded;
                },
            }, {
                label: 'barcodes',
                loaded: function(self) {
                    var barcode_parser = new BarcodeParser({'nomenclature_id': self.config.barcode_nomenclature_id});
                    self.barcode_reader.set_barcode_parser(barcode_parser);
                    return barcode_parser.is_loaded();
                },
            }
        ],

    });
});
