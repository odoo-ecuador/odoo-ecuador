odoo.define('pos_restaurant.floors', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var Model = require('web.DataModel');

var QWeb = core.qweb;
var _t = core._t;

models.load_models({
    model:  'res.partner',
    fields: ['type_ced_ruc','ced_ruc','name','street','city','state_id','country_id','vat','phone','zip','mobile','email','barcode','write_date'],
    domain: [['customer','=',true]], 
    loaded: function(self,partners){
        self.partners = partners;
        self.db.add_partners(partners);
    },
});

var PosDB = core.Class.extend({
    _partner_search_string: function(partner){
        var str =  partner.name;
        if(partner.ced_ruc){
            str += '|' + partner.ced_ruc;
        }
        if(partner.barcode){
            str += '|' + partner.barcode;
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
    },
});

});
