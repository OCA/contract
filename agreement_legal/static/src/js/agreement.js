odoo.define("agreement_legal.agreement", function(require) {
    "use strict";

    var KanbanController = require("web.KanbanController");
    var ListController = require("web.ListController");
    var FormController = require("web.FormController");

    var includeDict = {
        renderButtons: function() {
            this._super.apply(this, arguments);
            if (this.modelName === "agreement" && this.$buttons) {
                var self = this;
                var data = this.model.get(this.handle);
                if (data.context.default_is_template === true) {
                    // Hide create from template
                    this.$buttons.find(".create_agreement_from_template").hide();
                } else {
                    // Hide create button
                    this.$buttons.find(".o-kanban-button-new").hide();
                    this.$buttons.find(".o_list_button_add").hide();
                    this.$buttons.find(".o_form_button_create").hide();
                }
                this.$buttons
                    .find(".create_agreement_from_template")
                    .on("click", function() {
                        self.do_action(
                            "agreement_legal.create_agreement_from_template_action",
                            {
                                additional_context: {},
                            }
                        );
                    });
            }
        },
    };

    KanbanController.include(includeDict);
    ListController.include(includeDict);
    FormController.include(includeDict);
});
