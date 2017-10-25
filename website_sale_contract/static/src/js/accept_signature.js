/* Copyright 2017 LasLabs Inc.
 * License LGPL-3 or later (http://www.gnu.org/licenses/lgpl.html) */

odoo.define('website_sale_contract.website_contract_sign', function (require) {
    'use strict';

    var Ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var Config = require('web.config');
    var Website = require('website.website');

    // Accept Modal, with jSignature
    var AcceptModal = Widget.extend({
        events: {
            'shown.bs.modal': 'initSignature',
            'click #contractSignClean': 'clearSignature',
            'submit #contractAccept': 'submitForm',
        },
        initSignature: function(ev) {
            this.$("#drawContractSign").empty().jSignature({'decor-color' : '#D1D0CE', 'color': '#000', 'background-color': '#fff'});
            this.emptySign = this.$("#drawContractSign").jSignature("getData",'image');
        },
        clearSignature: function(ev) {
            this.$("#drawContractSign").jSignature('reset');
        },
        submitForm: function(ev) {
            // extract data
            var $confirm_btn = this.$el.find('button[type="submit"]');
            var contract_id = this.$el.find('form').data("contract-id");
            var token = this.$el.find('form').data("token");

            ev.preventDefault();
            // process : display errors, or submit
            var signerName = this.$("#signatoryName").val();
            var signature = this.$("#drawContractSign").jSignature("getData",'image');
            var isEmpty = this.emptySign[1] === signature[1];

            this.$('#signer').toggleClass('has-error', !signerName);
            this.$('#contractSignature').toggleClass('panel-danger', isEmpty).toggleClass('panel-default', !isEmpty);

            if (isEmpty || ! signerName){
                setTimeout(function () {
                    this.$('button[type="submit"], a.a-submit').removeAttr('data-loading-text').button('reset');
                });
                return false;
            }
            $confirm_btn.prepend('<i class="fa fa-spinner fa-spin"></i> ');
            $confirm_btn.attr('disabled', true);
            Ajax.jsonRpc("/shop/checkout/contract/accept", 'call', {
                'contract_id': contract_id,
                'token': token,
                'signatory_name': signerName,
                'signature_image': JSON.stringify(signature[1]),
            }).then($.proxy(
                function (data) {
                    this.$el.modal('hide');
                    window.location.href = '/shop/checkout/contract/'+contract_id.toString()+'/'+token+'?message_id='+data.message_id;
                }, this)
            );
            return false;
        },
    });

    var acceptModal = new AcceptModal();
    acceptModal.setElement($('#modalContractAccept'));
    acceptModal.start();

});
