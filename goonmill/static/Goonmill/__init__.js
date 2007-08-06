// import Nevow.Athena
// import DeanEdwards
// import Divmod.Defer

/* convenience func to find class'd nodes underneath a node, such as
 * widget.node
 */
var $CN = function (className, node) {
    return document.getElementsByClassName(className, node)[0];
}

Goonmill.SparqlSandbox = Nevow.Athena.Widget.subclass('Goonmill.SparqlSandbox');
Goonmill.SparqlSandbox.methods( // {{{
    function __init__(self, node) { // {{{
        Goonmill.SparqlSandbox.upcall(self, '__init__', node);

        self.queryForm = $CN("queryForm", self.node);
        self.results = $CN("results", self.node);
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

Goonmill.Result = Nevow.Athena.Widget.subclass('Goonmill.Result');
Goonmill.Result.methods( // {{{
    function __init__(self, node) { // {{{
        Goonmill.Result.upcall(self, '__init__', node);

        self.foldable = $CN("foldable", self.node);
        self.plus = $CN("plus", self.node);
        self.minus = $CN("minus", self.node);
        DeanEdwards.addEvent(self.plus, 'click', 
            function onPlusClick(event) { return self.onPlusClick(event)
        });
        DeanEdwards.addEvent(self.minus, 'click', 
            function onMinusClick(event) { return self.onMinusClick(event)
        });

    }, // }}}

    function onPlusClick(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault();
        self.expand();
    }, // }}}

    function expand(self) { // {{{
        if (!self.foldable.visible()) { 
            new Effect.SlideDown(self.foldable, {duration:0.3});
            self.plus.hide();
            self.minus.show();
        }
    }, // }}}

    function hi(self) { // {{{
        var title = $CN('monsterTitle', self.node);
        var bg = title.style['background-color'];
        new Effect.Highlight(title,
            {delay: 0.3, 
             beforeStart: function(){self.node.scrollIntoView()} ,
             endcolor: bg
             });
    }, // }}}

    function collapse(self) { // {{{
        if (self.foldable.visible()) { 
            new Effect.SlideUp(self.foldable, {duration:0.3});
            self.plus.show();
            self.minus.hide();
        };
    }, // }}}

    function onMinusClick(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault();
        self.collapse();
    } // }}}
); // }}}

Goonmill.Search = Nevow.Athena.Widget.subclass('Goonmill.Search');
Goonmill.Search.methods( // {{{
    function __init__(self, node) { // {{{
        Goonmill.Search.upcall(self, '__init__', node);

        self.searchForm = $CN("searchForm", self.node);
        DeanEdwards.addEvent(self.searchForm, 'submit', 
            function onSearchSubmit(event) { return self.onSearchSubmit(event) 
        });
        self.searchForm.search_terms.select();

    }, // }}}

    function onSearchSubmit(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault();

        var args = {'search_terms': self.searchForm.search_terms.value};
        var d = self.callRemote("onSearchSubmit", args);
        d.addCallback(function gotHits(hits) {
            hitsNode = $CN("hits", self.node);

            self.clearHits();

            for (var i=0; i<hits.length; i++) {
                var id = hits[i][0];
                var name = hits[i][1];
                var anchor = document.createElement('a');
                DeanEdwards.addEvent(anchor, 'click', function (id) {
                      return function chosen(event) {
                        event.stopPropagation();
                        event.preventDefault()
                        return self.chose(id);
                      }}(id)
                );
                anchor.setAttribute('href', id); // ignored
                anchor.innerHTML = name;
                hitsNode.appendChild(anchor);
                hitsNode.appendChild(document.createTextNode(', '));
            }
            return hits;
        });
        return d;
    }, // }}}

    /* user clicked on a hit in the list */
    function chose(self, hit) { // {{{
        self.clearHits();
        return self.callRemote("chose", hit);
    }, // }}}

    function clearHits(self) { // {{{
        $CN("hits", self.node).innerHTML = '';
    } // }}}
); // }}}

Goonmill.HistoryView = Nevow.Athena.Widget.subclass('Goonmill.HistoryView');
Goonmill.HistoryView.methods( // {{{
    function postResult(self, result) { // {{{
        var ll = [];
        for (var i=0; i<result.length; i++) {
            $A(self.childWidgets).each(function (w) {
                w.collapse();
            });

            var d = self.addChildWidgetFromWidgetInfo(result[i]);
            d.addCallback(function addedWidget(w) {
                var par = $CN('boxRight', self.node);
                w.foldable.hide();
                par.appendChild(w.node);
                w.expand();
                w.hi();
                return null;
            });
            ll.push(d);
        }

        return Divmod.Defer.DeferredList(ll);
    } // }}}
); // }}}

/* a guise is a static-text region that can be clicked to become editable */
Goonmill.Guise = Nevow.Athena.Widget.subclass('Goonmill.Guise');
Goonmill.Guise.methods( // {{{
    function __init__(self, node, template) { // {{{
        Goonmill.Guise.upcall(self, '__init__', node);

        if (!template) template = '#{quote_safe_value}';

        self.template = new Template(template);

        self.staticNode = node.getElementsByTagName('span')[0];
        self.inputNode = node.getElementsByTagName('input')[0];

        DeanEdwards.addEvent(self.staticNode, 'click', function (event) {
            self.editGuise(event);
        });
        DeanEdwards.addEvent(node, 'submit', function (event) {
            self.onSubmit(event);
        });

        self.display();
    }, // }}}

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

    /* put guise into editing mode */
    function editGuise(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault();
        self.staticNode.style['display'] = 'none';
        self.inputNode.style['display'] = 'inline';
        self.inputNode.select();
        self.inputNode.focus();
    }, // }}}

    function onSubmit(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault();
        self.inputNode.style['display'] = 'none';
        var v = self.inputNode.value;
        if (v) {
            // notify the server
            d = self.callRemote("editedValue", v);
        }
        self.display();
    }, // }}}

    function pushed(self, newValue) { // {{{
        if (newValue) {
            self.inputNode.value = newValue;
        }
        self.display();
    } // }}}
); // }}}

Goonmill.ReadOnlyGuise = Goonmill.Guise.subclass('Goonmill.ReadOnlyGuise');
Goonmill.ReadOnlyGuise.methods( // {{{
    function editGuise(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault()
        return null;
    } // }}}
); // }}}

Goonmill.idCounter = 0;

Goonmill.quoteSafeString = function (s) { // {{{
    var s = s.gsub(/\\/, '\\\\');
    var s = s.gsub(/'/, "\\'");
    var s = s.gsub(/"/, '\\"');
    return s;
}; // }}}

Goonmill.nextId = function () { // {{{
    Goonmill.idCounter += 1;
    return Goonmill.idCounter;
}; // }}}
// vi:foldmethod=marker
