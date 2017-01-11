odoo.define('l10n_ec_pos', function(require) {
"use strict";

    var PosDB = require('point_of_sale.DB');
    var models = require('point_of_sale.models');


    PosDB.include({

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

    var pos_models = models.PosModel.prototype.models;
    var _super_order_model = models.Order.prototype;

    models.Order = models.Order.extend({

	initialize: function(attributes,options){
	    _super_order_model.initialize.call(this, attributes, options);
	    var customer = this.pos.db.get_partner_by_id(this.pos.config.default_partner_id[0]);
	    if (!customer){
		console.log('WARNING: no default partner in POS');
	    }else{
		this.set({ client: customer });
	    }
	}

    });

    for (var i=0; i<pos_models.length; i++){
        var model = pos_models[i];
        if (model.model === 'res.partner') {
            model.fields.push('identifier', 'type_identifier', 'tipo_persona');
        }

	if (model.model === 'res.company') {
	    model.fields.push('street');
	}
    }
});
