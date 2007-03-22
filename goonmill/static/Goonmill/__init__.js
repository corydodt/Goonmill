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

        self.configForm = self.firstNodeByClass("configForm");
        DeanEdwards.addEvent(self.configForm, 'submit', 
            function onConfigSubmit(event) { return self.onConfigSubmit(event) 
        });
    }, // }}}

    function onSearchSubmit(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault();

        self.clearConfigure();

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
    }, // }}}

    function clearConfigure(self) { // {{{
        var f = self.configForm;
        f.monster_id.value = '';
        self.firstNodeByClass('monster_name').innerHTML = '';
        self.firstNodeByClass('organization').innerHTML = '';
        f.style['display'] = 'none';
    }, // {{{

    function onConfigSubmit(self, event) { // {{{
        event.stopPropagation();
        event.preventDefault();

        var f = self.configForm;

        var args = {'monster_count': f.monster_count.value,
                'monster_label': f.monster_label.value,
                'monster_id': f.monster_id.value
        };
        var d = self.callRemote("onConfigSubmit", args);
        return d
    }, // }}}

    /* call to set up and display the configure form */
    function setupConfigure(self, id, name, organization) { // {{{
        var f = self.configForm;
        f.monster_id.value = id;
        self.firstNodeByClass('monster_name').innerHTML = name;
        self.firstNodeByClass('organization').innerHTML = organization;
        f.style['display'] = 'block';
        return null;
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
                return null;
            });
            ll.push(d);
        }

        return Divmod.Defer.DeferredList(ll);
    } // }}}
); // }}}

// vi:foldmethod=marker
