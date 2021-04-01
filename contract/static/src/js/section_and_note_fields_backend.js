/* Copyright 2020 Tecnativa - Ernesto Tejeda
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */
/*
    If in the sub-tree view where the sections and notes are to be used
there are fields that have defined in the XML attrs = {'invisible': ....}
and this condition is met, then an extra space appears in the rows
corresponding to the sections and lines.
    This js was written to deal with that problem, but a solution based on
this can be applied directly to Odoo*/
odoo.define("contract.section_and_note_backend", function (require) {
    "use strict";

    require("account.section_and_note_backend");
    var fieldRegistry = require("web.field_registry");
    var section_and_note_one2many = fieldRegistry.get("section_and_note_one2many");

    section_and_note_one2many.include({
        _getRenderer: function () {
            var result = this._super.apply(this, arguments);
            if (this.view.arch.tag === "tree") {
                result.include({
                    _renderBodyCell: function (record) {
                        var $cell = this._super.apply(this, arguments);

                        var isSection = record.data.display_type === "line_section";
                        var isNote = record.data.display_type === "line_note";

                        if (isSection || isNote) {
                            $cell.removeClass("o_invisible_modifier");
                        }
                        return $cell;
                    },
                });
            }
            return result;
        },
    });
});
