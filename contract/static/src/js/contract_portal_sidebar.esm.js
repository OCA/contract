import PortalSidebar from "@portal/js/portal_sidebar";
import publicWidget from "@web/legacy/js/public/public_widget";
import {scrollTo} from "@web/core/utils/scrolling";

publicWidget.registry.AccountPortalSidebar = PortalSidebar.extend({
    selector: ".o_portal_contract_sidebar",
    events: {
        "click .o_portal_contract_print": "_onPrintInvoice",
    },

    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);

        var $contractHtml = this.$el.find("iframe#contract_html");
        var updateIframeSize = this._updateIframeSize.bind(this, $contractHtml);

        $(globalThis.window).on("resize", updateIframeSize);

        var iframeDoc =
            $contractHtml[0].contentDocument || $contractHtml[0].contentWindow.document;
        if (iframeDoc.readyState === "complete") {
            updateIframeSize();
        } else {
            $contractHtml.on("load", updateIframeSize);
        }

        return def;
    },

    // --------------------------------------------------------------------------
    // Handlers
    // --------------------------------------------------------------------------

    /**
     * Called when the iframe is loaded or the window is resized on customer portal.
     * The goal is to expand the iframe height to display the full report without scrollbar.
     *
     * @private
     * @param {Object} $el: the iframe
     */
    _updateIframeSize: function ($el) {
        var $wrapwrap = $el.contents().find("div#wrapwrap");
        // Set it to 0 first to handle the case where scrollHeight is too big for its content.
        $el.height(0);
        $el.height($wrapwrap[0].scrollHeight);

        // Scroll to the right place after iframe resize
        const isAnchor = /^#[\w-]+$/.test(globalThis.window.location.hash);
        if (!isAnchor) {
            return;
        }
        var $target = $(globalThis.window.location.hash);
        if (!$target.length) {
            return;
        }
        scrollTo($target[0], {behavior: "instant"});
    },
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onPrintInvoice: function (ev) {
        ev.preventDefault();
        var href = $(ev.currentTarget).attr("href");
        this._printIframeContent(href);
    },
});
