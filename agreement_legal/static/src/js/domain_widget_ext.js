odoo.define("agreement_legal.domain_widget_ext", function(require) {
    "use strict";

    const basic_fields = require("web.basic_fields");
    const DomainSelector = require("web.DomainSelector");
    const session = require("web.session");
    const core = require("web.core");
    const qweb = core.qweb;

    basic_fields.FieldDomain.include({
        /**
         * Init
         */
        init: function() {
            this._super.apply(this, arguments);
            // Add Additional options
            this.partialUse = this.nodeOptions.partial_use || false;
        },

        // ----------------------------------------------------------------------
        // Private
        // ----------------------------------------------------------------------

        /**
         * @private
         * @override _render from AbstractField
         * @returns {Deferred}
         */
        /* eslint-disable no-unused-vars */
        _render: function() {
            // If there is no model, only change the non-domain-selector content
            if (!this._domainModel) {
                this._replaceContent();
                return $.when();
            }

            // Convert char value to array value
            const value = this.value || "[]";

            // Create the domain selector or change the value of the current
            // one...
            var def = null;
            if (this.domainSelector) {
                def = this.domainSelector.setDomain(value);
            } else {
                this.domainSelector = new DomainSelector(
                    this,
                    this._domainModel,
                    value,
                    {
                        readonly: this.mode === "readonly" || this.inDialog,
                        filters: this.fsFilters,
                        debugMode: session.debug,
                        partialUse: this.partialUse || false,
                    }
                );
                def = this.domainSelector.prependTo(this.$el);
            }
            // ... then replace the other content (matched records, etc)
            return def.then(this._replaceContent.bind(this));
        },
        /**
         * Render the field DOM except for the domain selector part. The full
         * field DOM is composed of a DIV which contains the domain selector
         * widget, followed by other content. This other content is handled by
         * this method.
         *
         * @private
         */
        _replaceContent: function() {
            if (this._$content) {
                this._$content.remove();
            }
            this._$content = $(
                qweb.render("FieldDomain.content", {
                    hasModel: Boolean(this._domainModel),
                    isValid: Boolean(this._isValidForModel),
                    nbRecords: this.record.specialData[this.name].nbRecords || 0,
                    inDialogEdit: this.inDialog && this.mode === "edit",
                    partialUse: this.partialUse || false,
                })
            );
            this._$content.appendTo(this.$el);
        },
    });
});
