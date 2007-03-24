// import Nevow.Athena
// import DeanEdwards
// import Divmod.Defer

Goonmill.Search = Nevow.Athena.Widget.subclass('Goonmill.Search');
Goonmill.Search.methods( // {{{
    function __init__(self, node) { // {{{
        Goonmill.Search.upcall(self, '__init__', node);

        self.searchForm = self.firstNodeByClass("searchForm");
        DeanEdwards.addEvent(self.searchForm, 'submit', 
            function onSearchSubmit(event) { return self.onSearchSubmit(event) 
        });

    }, // }}}

    function onSearchSubmit(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault();

        var args = {'search_terms': self.searchForm.search_terms.value};
        var d = self.callRemote("onSearchSubmit", args);
        d.addCallback(function gotHits(hits) {
            hitsNode = self.firstNodeByClass('hits');

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
        self.firstNodeByClass('hits').innerHTML = '';
    } // }}}
); // }}}

Goonmill.HistoryView = Nevow.Athena.Widget.subclass('Goonmill.HistoryView');
Goonmill.HistoryView.methods( // {{{
    function postResult(self, result) { // {{{
        var ll = [];
        for (var i=0; i<result.length; i++) {
            var d = self.addChildWidgetFromWidgetInfo(result[i]);
            d.addCallback(function addedWidget(w) {
                self.node.appendChild(w.node);

                /* hook up Guise machinery to all the guise nodes in this
                 * widget */
                var guises = w.nodesByAttribute('class', 'guise');
                for (var g=0; g<guises.length; g++) {
                    var _ignored = new Goonmill.Guise(guises[g], w);
                }

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
    function __init__(self, node) { // {{{
        Goonmill.Guise.upcall(self, '__init__', node);
        self.staticNode = node.getElementsByTagName('span')[0];
        self.inputNode = node.getElementsByTagName('input')[0];
        DeanEdwards.addEvent(self.staticNode, 'click', function (event) {
            self.editGuise(event);
        });
        DeanEdwards.addEvent(node, 'submit', function (event) {
            self.onSubmit(event);
        });

        if (self.inputNode.value) { 
            self.staticNode.innerHTML = self.inputNode.value;
        } else {
            self.staticNode.innerHTML = '&#xA0;';
        }
    }, // }}}

    /* put guise into editing mode */
    function editGuise(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault()
        self.staticNode.style['display'] = 'none';
        self.inputNode.style['display'] = 'inline';
        self.inputNode.select();
        self.inputNode.focus();
    }, // }}}

    function onSubmit(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault()
        self.inputNode.style['display'] = 'none';
        if (self.inputNode.value) {
            var v = self.inputNode.value;
            self.staticNode.innerHTML = v;
            // notify the server
            d = self.callRemote("editedValue", v);
        } else {
            self.staticNode.innerHTML = '&#xA0;';
        }
        self.staticNode.style['display'] = 'inline';
    } // }}}
    
); // }}}
// vi:foldmethod=marker
