// import Nevow.Athena
// import Divmod.Defer

var Widget = Nevow.Athena.Widget;

Goonmill.DiceSandbox = Widget.subclass('Goonmill.DiceSandbox');
Goonmill.DiceSandbox.methods( // {{{
    function __init__(self, node) { // {{{
        Goonmill.DiceSandbox.upcall(self, '__init__', node);

        self.queryForm = self.node.select('.queryForm')[0];
        self.results = self.node.select('.results')[0]
        self.queryArea = self.queryForm.query;

        DeanEdwards.addEvent(self.queryArea, 'keyup', 
            function onQueryAreaKeyup(event) { 
                return self.onQueryAreaKeyup(event);
        });
        DeanEdwards.addEvent(self.queryForm, 'submit', 
            function onQuerySubmit(event) { return self.onQuerySubmit(event) 
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
); // }}}

Goonmill.SparqlSandbox = Widget.subclass('Goonmill.SparqlSandbox');
Goonmill.SparqlSandbox.methods( // {{{
    function __init__(self, node) { // {{{
        Goonmill.SparqlSandbox.upcall(self, '__init__', node);

        self.queryForm = self.node.select('.queryForm')[0];
        self.results = self.node.select('.results')[0];
        self.queryArea = self.queryForm.query;

        DeanEdwards.addEvent(self.queryArea, 'keyup', 
            function onQueryAreaKeyup(event) { 
                return self.onQueryAreaKeyup(event);
        });
        DeanEdwards.addEvent(self.queryForm, 'submit', 
            function onQuerySubmit(event) { return self.onQuerySubmit(event) 
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
); // }}}

/* a guise is a static-text region that can be clicked to become editable */
Goonmill.Guise = Widget.subclass('Goonmill.Guise');
Goonmill.Guise.methods( // {{{
    /* display inputNode.value inside staticNode, using the formatting I was
     * passed in self.template */
    function display(self) { // {{{
        var id = Goonmill.nextId();
        if (self.inputNode.value) { 
            var v = Goonmill.quoteSafeString(self.inputNode.value);
            var hash = {quote_safe_value: v, id: id};
        } else {
            var hash = {quote_safe_value: '&#xA0;', id: id};
        }
        var markup = self.template.evaluate(hash);
        self.staticNode.update(markup);
        self.staticNode.style['display'] = 'inline';
    }, // }}}

    function pushed(self, newValue) { // {{{
        if (newValue) {
            self.inputNode.value = newValue;
        }
        self.display();
    } // }}}
); // }}}

Goonmill.WarmText = Widget.subclass('Goonmill.WarmText')
Goonmill.WarmText.methods(
    function __init__(self, node, template) { // {{{
        Goonmill.WarmText.upcall(self, '__init__', node);

        // if (!template) template = '#{quote_safe_value}';

        // self.template = new Template(template);

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

        self.form.observe('submit', function (event) {
            self.onSubmit(event);
        });

        // self.display(); FIXME
    }, // }}}

    /* put guise into editing mode */
    function editWarmText(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault();
        self.anchor.hide();
        self.inputNode.show();
        self.inputNode.select();
        self.inputNode.focus();
    }, // }}}

    function onSubmit(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault();
        self.inputNode.hide();
        var v = self.inputNode.value;
        if (v) {
            // todo - validate
            // notify the server
            d = self.callRemote("editedValue", v);
        }
        // self.display(); fixme
    }, // }}}

);


Goonmill.quoteSafeString = function (s) { // {{{
    var s = s.gsub(/\\/, '\\\\');
    var s = s.gsub(/'/, "\\'");
    var s = s.gsub(/"/, '\\"');
    return s;
}; // }}}

Goonmill.idCounter = 0;

Goonmill.nextId = function () { // {{{
    Goonmill.idCounter += 1;
    return Goonmill.idCounter;
}; // }}}
// vi:foldmethod=marker
