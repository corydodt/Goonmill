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
                // closures in javascript, feh
                anc.observe('click', (function (anc, n, event) { 
                        self.clickedHit(event, anc, n)
                }).curry(anc, n));
                self.hitContainer.insert(anc);
                Effect.SlideDown(anc);
            }
        });
        return d;
    },

    function clickedHit(self, event, node, n) {
        event.stopPropagation();
        event.preventDefault();
        Goonmill.messageBox(node.innerHTML + ' ' + n);
    }
);


var LightboxConfig = Class.create({
opacity:0.7,
fade:true, 
fadeDuration: 0.4,
initialize: function() {},
beforeClose: function() { throw $break; }
});

// display any node or string as a message
Goonmill.messageBox = function (node) {
    if (node.innerHTML === undefined) {
        node = new Element('span').update(node);
    }

    // add a closing box always
    var hr = new Element('hr');
    var close = new Element('input', {type: 'button', value: 'close'});
    close.observe('click', function() { Control.Modal.current.close(true) } );

    var contents = $A([node, hr, close]);
    var m = Goonmill.Modal(contents);

    return m;
}

// copy the contents into a modal dialog (lightbox)
Goonmill.Modal = function (contents, extraOptions) {
    var config = new LightboxConfig();
    if (extraOptions !== undefined) {
        for (attr in extraOptions) {
            config[attr] = extraOptions[attr];
        }
    }
    config.contents = '<span>__ignored__</span>';

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
    modal.update(contents);

    return modal;
}


// display message.
// return a deferred that will fire with the number of the clicked button.
Goonmill.confirm = function (message, button1text, button2text) {
    // copy the content of node into a modal dialog (lightbox)
    var message = new Element('span').update(message);
    var button1 = new Element('input', {type:'button', value:button1text});
    var button2 = new Element('input', {type:'button', value:button2text});

    var d = new Divmod.Defer.Deferred(); 
    var f1 = (function(d) { Control.Modal.current.close(true); d.callback(1) }).curry(d);
    var f2 = (function(d) { Control.Modal.current.close(true); d.callback(2) }).curry(d);
    button1.observe('click', f1);
    button2.observe('click', f2);

    var contents = $A([message, new Element('hr'), button1, button2]);
            
    var m = Goonmill.Modal(contents);

    return d;
}


Goonmill.ConstituentList = Widget.subclass('Goonmill.ConstituentList');
Goonmill.ConstituentList.methods(
    function __init__(self, node) {
        Goonmill.ConstituentList.upcall(self, '__init__', node);
        // make all closing x's clickable
        node.select('.constituent').each(function (cnst) {
            cnst.select('.closingX')[0].observe('click', (function (c, event) {
                self.removeConstituent(c);
            }).curry(cnst));
        });
    }, 

    // throw the given constituent out of the workspace
    function removeConstituent(self, node) {
        var id = parseInt(node.readAttribute('rel'));
        var args = {name: node.select('.constituentName')[0].innerHTML};
        var d = Goonmill.confirm('Really delete #{name}?'.interpolate(args), 
                'delete', 'whoops no');
        d.addCallback(function (button) {
            if (button == 1) {
                d = self.callRemote('removeConstituent', id);
                d.addCallback(function (r) {
                    Effect.Fade(node, {afterFinish: (function(n) { n.remove() }).curry(node)});
                });
                return d;
            }
        });
    }
);


Goonmill.MainActions = Widget.subclass('Goonmill.MainActions');
Goonmill.MainActions.methods(
    function __init__(self, node) {
        Goonmill.MainActions.upcall(self, '__init__', node);
        node.select('[rev=npc]')[0].observe('click', function (event) {
            self.newNPCClicked()
        });
        node.select('[rev=monsterGroup]')[0].observe('click', function (event) {
            self.newMonsterGroupClicked()
        });
        node.select('[rev=stencil]')[0].observe('click', function (event) {
            self.newStencilClicked()
        });
        node.select('[rev=encounter]')[0].observe('click', function (event) {
            self.newEncounterClicked()
        });
    },

    function newNPCClicked(self, event) {
        Goonmill.messageBox('new npc');
    },

    function newMonsterGroupClicked(self, event) {
        Goonmill.messageBox('new monster group');
    },

    function newStencilClicked(self, event) {
        Goonmill.messageBox('new stencil');
    },

    function newEncounterClicked(self, event) {
        Goonmill.messageBox('new encounter');
    }
);


// use this to pump events out to listeners in a pub/sub model
Goonmill.EventBus = Widget.subclass('Goonmill.EventBus');
Goonmill.EventBus.methods(
    function __init__(self, node) {
        Goonmill.EventBus.upcall(self, '__init__', node);
        // for debugging
        document.observe('keypress', function (e) {
            if (e.keyCode == 68) { // 'd'
                Goonmill.debugView();
            }
        });
    }
);

// display all the widgets' top-level nodes, with hints
Goonmill.debugView = function () {
    var toPrint = Goonmill.findAllWidgetNodes();
    var printNodes = toPrint.map(function (n) {
        var dtText = n.readAttribute('class') + ' (' + n.identify() + ')';
        return [(new Element('dt')).update(dtText),
                (new Element('dd')).update(n.textContent)];
    }).flatten();
    var dl = new Element('dl');
    // FIXME - printNodes.each should work here, but i get
    // 'element.appendChild is not an attribute'
    for (n=0; n<printNodes.length; n++) dl.insert(printNodes[n]);
    Goonmill.messageBox(dl);
}

// the top-level node of every widget on the page
Goonmill.findAllWidgetNodes = function() {
    var ret = new Array();
    document.documentElement.select('[id]').each(function (el) {
        if (el.readAttribute('id').match(/^athena:/)) {
            ret.push(el)
        }
    });
    return ret;
}

// vim:set foldmethod=syntax:set smartindent:
