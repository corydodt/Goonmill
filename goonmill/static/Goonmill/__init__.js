// import Nevow.Athena
// import Divmod.Defer

var Widget = Nevow.Athena.Widget;

Goonmill.DiceSandbox = Widget.subclass('Goonmill.DiceSandbox');
Goonmill.DiceSandbox.methods(
    function __init__(self, node) { // {{{
        Goonmill.DiceSandbox.upcall(self, '__init__', node);

        self.queryForm = self.node.select('.queryForm')[0];
        self.results = self.node.select('.results')[0]
        self.queryArea = self.queryForm.query;

        self.queryArea.observe('keyup', 
            function onQueryAreaKeyup(event) { 
                return self.onQueryAreaKeyup(event);
        });
        self.queryForm.observe('submit', 
            function onQuerySubmit(event) { 
                return self.onQuerySubmit(event) 
        });
        self.queryArea.select();
    }, // }}}

    function onQueryAreaKeyup(self, event) { // {{{
        // Ctrl+Enter submits.
        if (!(event.keyCode == 13 && event.ctrlKey))
            return true;

        self.onQuerySubmit(event);
    }, // }}}

    function onQuerySubmit(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault();

        var d = self.callRemote("onQuerySubmit", self.queryForm.query.value);
        d.addCallback(function gotResult(result) {
            self.results.innerHTML = result;
        });
     } // }}}
);

Goonmill.SparqlSandbox = Widget.subclass('Goonmill.SparqlSandbox');
Goonmill.SparqlSandbox.methods(
    function __init__(self, node) { // {{{
        Goonmill.SparqlSandbox.upcall(self, '__init__', node);

        self.queryForm = self.node.select('.queryForm')[0];
        self.results = self.node.select('.results')[0];
        self.queryArea = self.queryForm.query;

        self.queryArea.observe('keyup', 
            function onQueryAreaKeyup(event) { 
                return self.onQueryAreaKeyup(event);
        });
        self.queryForm.observe('submit', 
            function onQuerySubmit(event) { 
                return self.onQuerySubmit(event) 
        });
        self.queryArea.select();
    }, // }}}

    function onQueryAreaKeyup(self, event) { // {{{
        // Ctrl+Enter submits.
        if (!(event.keyCode == 13 && event.ctrlKey))
            return true;

        self.onQuerySubmit(event);
    }, // }}}

    function onQuerySubmit(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault();

        var d = self.callRemote("onQuerySubmit", self.queryForm.query.value);
        d.addCallback(function gotResult(result) {
            self.results.innerHTML = result;
        });
     } // }}}
);


Goonmill.WarmControl = Widget.subclass('Goonmill.WarmControl');
Goonmill.WarmControl.methods(
    function rollback(self, reason, oldValue, newValue) { // {{{
        alert('implement in a subclass')
    }, // }}}

    function setLocally(self, value) { // {{{
        alert('implement in a subclass')
    }, // }}}

    function validate(self, value) { // {{{
        return true;
    }, // }}}

    function serverUpdated(self, value) { // {{{
        if (! self.validate(value))
            throw "invalid value - client validation";

        var original = self.setLocally(value);

        return value;
    }, // }}}

    function clientUpdate(self, value) { // {{{
        if (! self.validate(value))
            throw "invalid value - client validation";

        var original = self.setLocally(value);

        var d = self.callRemote('clientUpdated', value);
        d.addErrback(function (f) { self.rollback(f, original, value) });

        return d
    } // }}}
);
        

Goonmill.WarmText = Goonmill.WarmControl.subclass('Goonmill.WarmText');
Goonmill.WarmText.methods(
    function __init__(self, node, template) { // {{{
        Goonmill.WarmText.upcall(self, '__init__', node);

        if (template === undefined || !template) template = '#{quote_safe_value}';

        self.template = new Template(template);

        // the anchor is the node that gets initialized.  It should probably
        // have the n:render attribute in the template.
        self.anchor = node.select('.warmText')[0];
        self.form = new Element('form');
        node.insert(self.form, {position: 'bottom'});

        self.inputNode = new Element('input');
        self.inputNode.hide();
        self.form.insert(self.inputNode, {position: 'top'});

        self.anchor.observe('click', function (event) {
            self.editWarmText(event);
        });

        var startValue = self.inputNode.value;
        self.form.observe('submit', function (event) {
            return self.onSubmit(event);
        });

        /* to make sure quoting and blanks are taken care of nicely, force a
         * call to setLocally now
         */
        self.setLocally(self.anchor.innerHTML);
    }, // }}}

    function rollback(self, reason, oldValue, newValue) { // {{{
        debugger;
        // TODO - slide out an error message here
        return self.setLocally(oldValue);
    }, // }}}

    function validate(self, value) { // {{{
        return (value.length < 2000);
    }, // }}}

    /* put warmtext into editing mode */
    function editWarmText(self, event) {
        event.stopPropagation();
        event.preventDefault();
        self.anchor.hide();
        self.inputNode.show();
        self.inputNode.select();
        self.inputNode.focus();
    },

    function onSubmit(self, event) {
        event.stopPropagation();
        event.preventDefault();
        self.inputNode.hide();
        var original = self.anchor.innerHTML;
        try {
            return self.clientUpdate(self.inputNode.value);
        } catch (err) {
            self.rollback(err, original, self.inputNode.value);
            return null;
        }
    },

    function setLocally(self, value) {
        if (value) { 
            var v = Goonmill.quoteSafeString(value);
            var hash = {quote_safe_value: v};
        } else {
            /* put a blank space in so the field will never be 0px wide */
            var hash = {quote_safe_value: '&#xA0'};
        }
        var original = self.anchor.innerHTML;
        self.inputNode.value = value;
        var markup = self.template.evaluate(hash);
        self.anchor.update(markup);
        Effect.Appear(self.anchor);
        return original;
    }
);


Goonmill.quoteSafeString = function (s) {
    var s = s.gsub(/\\/, '\\\\');
    var s = s.gsub(/'/, "\\'");
    var s = s.gsub(/"/, '\\"');
    return s;
};


Goonmill.BasicSearch = Widget.subclass('Goonmill.BasicSearch');
Goonmill.BasicSearch.methods(
    function __init__(self, node) { // {{{
        Goonmill.BasicSearch.upcall(self, '__init__', node);
        self.searchForm = node.select('.searchForm')[0];

        self.searchForm.observe('submit', function (event) {
            return self.onSubmitSearch(event);
        });

        self.searchTerms = self.searchForm.searchTerms;

        self.searchTerms.observe('click', function (event) {
            self.searchTerms.value = '';
            self.searchTerms.removeClassName('defaultText');
        });

        self.searchTerms.observe('blur', function (event) {
            if (self.searchTerms.value == '') {
                self.searchTerms.value = 'Search for a monster';
                self.searchTerms.addClassName('defaultText');
            }
        });
        self.hitContainer = node.select('div[rev=hits]')[0];
    }, // }}}

    /* clear the search form and reset it */
    function resetSearchInput(self) {
        self.searchForm.searchTerms.clear();
        self.searchForm.searchTerms.nextSiblings()[0].focus();
    },

    function onSubmitSearch(self, event) {
        event.stopPropagation();
        event.preventDefault();
        $A(self.hitContainer.childNodes).each(function (e) { e.remove() } );
        var d = self.callRemote('searched', self.searchForm.searchTerms.value);
        d.addCallback(function (hits) {
            self.resetSearchInput();
            for (var n=0; n<hits.length; n++) {
                var hit = hits[n];
                var anc = new Element('a', {href:'#' + n});
                anc.addClassName('hit');
                anc.update(hit[0] + ' ');
                var sub = new Element('sub');
                sub.update(hit[1] + '%');
                anc.insert(sub, {position: 'bottom'});
                anc.hide()
                // sigh, closures in javascript suck.
                var f = (function (anc, n) { 
                    return function (event) { self.clickedHit(event, anc, n) } 
                })(anc, n);
                anc.observe('click', f);
                self.hitContainer.insert(anc);
                Effect.SlideDown(anc);
            }
        });
        return d;
    },

    function clickedHit(self, event, node, n) {
        event.stopPropagation();
        event.preventDefault();
        Goonmill.Modal(node.innerHTML + ' ' + n);
    }
);


var LightboxConfig = Class.create({
opacity:0.7,
fade:true, 
fadeDuration: 0.7,
initialize: function() {},
beforeClose: function() { throw $break; }
});

Goonmill.Modal = function (node) {
    // copy the content of node into a modal dialog (lightbox)
    var config = new LightboxConfig();
    if (node.innerHTML !== undefined) {
        config.contents = node.innerHTML;
    } else {
        config.contents = '<span>' + node + '</span>';
    }
    var closer = '<div><a href="javascript:void(0)" onclick="Control.Modal.current.close(true)">Close</a></div>';
    config.contents = config.contents + closer;

    // kludge .. hide all embedded stuff when showing the modal
    var embeds = document.documentElement.select('embed');
    $A(embeds).each(function (e) { 
        e.setAttribute('_oldVisibility', e.style['visibility']);
        e.style['visibility'] = 'hidden'; 
    });
    
    // restore embedded stuff when closing the modal
    config.afterClose = function () { $A(embeds).each(function(e) {
        e.style['visibility'] = e.readAttribute('_oldVisibility');
        e.removeAttribute('_oldVisibility');
        }
    )};

    var modal = new Control.Modal(null, config);
    modal.open();
    return modal;
}

// vi:foldmethod=syntax
