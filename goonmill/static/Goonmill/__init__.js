// import Nevow.Athena
// import Divmod.Defer


// BEGIN MONKEYPATCHING
var Widget = Nevow.Athena.Widget;
// monkey patch a bug with detach not cleaning up properly
// see: http://divmod.org/trac/ticket/2678
Widget.method('_athenaDetachClient', function (self) {
    var l = self.childWidgets.length;
    for (var i = l-1; i >= 0; --i) {
        self.childWidgets[i]._athenaDetachClient();
    }
    if (self.widgetParent !== null) {
        self.widgetParent.removeChildWidget(self);
    }
    delete Nevow.Athena.Widget._athenaWidgets[self.objectID];
    self.detached();
});
// END MONKEYPATCHING



body = document.body; // less typing yay


// attach certain automatic behavior to every widget, such as checking for
// behavior-oriented class names and applying those behaviors
Goonmill.GoonmillWidget = Widget.subclass('Goonmill.GoonmillWidget');
Goonmill.GoonmillWidget.methods(
    function __init__(self, node) {
        Goonmill.GoonmillWidget.upcall(self, '__init__', node);
        // apply behaviors based on class
        for (behavior in Goonmill.Behaviors) {
            if (Goonmill.Behaviors.hasOwnProperty(behavior)) {
                node.select('.' + behavior).each(Goonmill.Behaviors[behavior]);
            }
        }
    }
);

// methods of this will be used to look for the corresponding class names
// inside nodes.  any node that has one of these classes will get the
// corresponding behavior attached.
Goonmill.Behaviors = {
    truncate18: function (n) {
        // this class should never be used on a node that isn't a
        // container of only text.
        if (n.childElements().length > 0) {
            debugger;
        }
        n.update(n.innerHTML.truncate(15));
    },

    truncate25: function (n) {
        // this class should never be used on a node that isn't a
        // container of only text.
        if (n.childElements().length > 0) {
            debugger;
        }
        n.update(n.innerHTML.truncate(22));
    },

    checkboxCell: function (n) {
        n.observe('click', function (e) { 
            var checkboxes = e.element().select('input[type=checkbox]');
            if (checkboxes === undefined) { return true; }
            checkboxes[0].click();
        });
    }
};

Goonmill.DiceSandbox = Goonmill.GoonmillWidget.subclass('Goonmill.DiceSandbox');
Goonmill.DiceSandbox.methods(
    function __init__(self, node) { // {{{
        Goonmill.DiceSandbox.upcall(self, '__init__', node);

        self.queryForm = self.node.select('.queryForm')[0];
        self.results = self.node.select('.results')[0];
        self.queryArea = self.queryForm.query;

        self.queryArea.observe('keyup', 
            function onQueryAreaKeyup(event) { 
                return self.onQueryAreaKeyup(event);
        });
        self.queryForm.observe('submit', 
            function onQuerySubmit(event) { 
                return self.onQuerySubmit(event);
        });
        self.queryArea.select();
    }, // }}}

    function onQueryAreaKeyup(self, event) { // {{{
        // Ctrl+Enter submits.
        if (!(event.keyCode == 13 && event.ctrlKey)) {
            return true;
        }

        self.onQuerySubmit(event);
    }, // }}}

    function onQuerySubmit(self, event) { // {{{
        event.stop();
        event.preventDefault();

        var d = self.callRemote("onQuerySubmit", self.queryForm.query.value);
        d.addCallback(function gotResult(result) {
            self.results.innerHTML = result;
        });
     } // }}}
);

Goonmill.SparqlSandbox = Goonmill.GoonmillWidget.subclass('Goonmill.SparqlSandbox');
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
                return self.onQuerySubmit(event);
        });
        self.queryArea.select();
    }, // }}}

    function onQueryAreaKeyup(self, event) { // {{{
        // Ctrl+Enter submits.
        if (!(event.keyCode == 13 && event.ctrlKey)) {
            return true;
        }

        self.onQuerySubmit(event);
    }, // }}}

    function onQuerySubmit(self, event) { // {{{
        event.stop();
        event.preventDefault();

        var d = self.callRemote("onQuerySubmit", self.queryForm.query.value);
        d.addCallback(function gotResult(result) {
            self.results.innerHTML = result;
        });
     } // }}}
);


Goonmill.WarmControl = Goonmill.GoonmillWidget.subclass('Goonmill.WarmControl');
Goonmill.WarmControl.methods(
    function rollback(self, reason, oldValue, newValue) { // {{{
        alert('implement in a subclass');
    }, // }}}

    function setLocally(self, value) { // {{{
        alert('implement in a subclass');
    }, // }}}

    function validate(self, value) { // {{{
        return true;
    }, // }}}

    function serverUpdated(self, value) { // {{{
        if (! self.validate(value)) {
            throw "invalid value - client validation";
        }

        var original = self.setLocally(value);

        return value;
    }, // }}}

    function clientUpdate(self, value) { // {{{
        if (! self.validate(value)) {
            throw "invalid value - client validation";
        }

        var original = self.setLocally(value);

        var d = self.callRemote('clientUpdated', value);
        d.addErrback(function (f) { self.rollback(f, original, value); });

        return d;
    } // }}}
);
        

Goonmill.WarmText = Goonmill.WarmControl.subclass('Goonmill.WarmText');
Goonmill.WarmText.methods(
    function __init__(self, node, defaultText, template) { // {{{
        Goonmill.WarmText.upcall(self, '__init__', node);
        self.defaultText = (defaultText ? defaultText : 'Click to edit');

        if (template === undefined || !template) { template = '#{quote_safe_value}'; }
 
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

        self.inputNode.observe('blur', function (event) {
            return self.onSubmit(event);
        });

        /* to make sure quoting and blanks are taken care of nicely, force a
         * call to setLocally now
         */
        self.setLocally(self.anchor.innerHTML);
    }, // }}}

    function rollback(self, reason, oldValue, newValue) { // {{{
        var message = Goonmill.message("I can't do that because " + reason + 
                ". " + "(changing " + oldValue + " to " + newValue + ")");
        return self.setLocally(oldValue);
    }, // }}}

    function validate(self, value) { // {{{
        return (value.length < 2000);
    }, // }}}

    /* put warmtext into editing mode */
    function editWarmText(self, event) {
        event.stop();
        event.preventDefault();
        self.anchor.hide();
        self.inputNode.show();
        self.inputNode.select();
        self.inputNode.focus();
    },

    function onSubmit(self, event) {
        event.stop();
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
        var v, hash;
        if (value) { 
            v = Goonmill.quoteSafeString(value);
            hash = {quote_safe_value: v};
            self.anchor.removeClassName('defaultText');
        } else {
            /* put something in so the field will never be 0px wide */
            hash = {quote_safe_value: self.defaultText};
            self.anchor.addClassName('defaultText');
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
    s = s.gsub(/\\/, '\\\\');
    s = s.gsub(/'/, "\\'");
    s = s.gsub(/"/, '\\"');
    return s;
};


Goonmill.BasicSearch = Goonmill.GoonmillWidget.subclass('Goonmill.BasicSearch');
Goonmill.BasicSearch.methods(
    function __init__(self, node) { // {{{
        Goonmill.BasicSearch.upcall(self, '__init__', node);
        self.searchForm = node.select('.searchForm')[0];

        self.searchTerms = self.searchForm.searchTerms;

        self.searchTerms.observe('click', function (event) {
            self.searchTerms.value = '';
            self.searchTerms.removeClassName('defaultText');
        });

        var searchTermsValid = new LiveValidation(self.searchTerms,
            {validMessage: '' }
        );
        searchTermsValid.add(Validate.Presence, {failureMessage: ''});
        searchTermsValid.add(Validate.Exclusion,
            {within: ['Search for a monster'], failureMessage: ''}
        );

        self.searchForm.observe('submit', function (event) {
            if (LiveValidation.massValidate([searchTermsValid])) {
                return self.onSubmitSearch(event);
            }
        });

        self.searchTerms.observe('blur', function (event) {
            if (self.searchTerms.value === '') {
                self.searchTerms.value = 'Search for a monster';
                self.searchTerms.addClassName('defaultText');
            }
        });
        self.hitContainer = node.select('div[rev=hits]')[0];
    }, // }}}

    // clear the search form and reset it
    function resetSearchInput(self) {
        self.searchForm.searchTerms.clear();
        self.searchForm.searchTerms.nextSiblings()[0].focus();
    },

    // tell the server we want a new list of search results
    function onSubmitSearch(self, event) {
        event.stop();
        event.preventDefault();
        // $A(self.hitContainer.childNodes).each(function (e) { e.remove(); } ); FIXME - dont need to clear each time now that we use transclude
        var d = self.callRemote('searched', self.searchForm.searchTerms.value);

        d.addCallback(function (hits) {
            var ctx, hitHits, monsterId, setupHit;
            self.resetSearchInput();

            hitHits = $A(hits).map(function (hit) {
                return { 
                    monsterName: hit[0],
                    monsterId: hit[1], 
                    teaser: hit[2],
                    setupHit: function(anc, ctx) {
                        // TODO - add teaser
                        anc.observe('click', function (event) {
                            self.onClickedHit(event, anc, ctx.monsterId);
                        });
                        anc.removeAttribute('title');
                        var _ignored = new Goonmill.GoonTip(anc, ctx.teaser);
                    }
                };
            });
            ctx = new JsEvalContext({'hits':hitHits});
            jstProcess(ctx, self.hitContainer);
            self.hitContainer = ctx.getVariable("newContainer");

            Effect.BlindDown(self.hitContainer);
        });

        return d;
    },

    // tell the server that this search hit is our search hit
    function onClickedHit(self, event, node, monsterId) {
        event.stop();
        event.preventDefault();
        var name = node.innerHTML;
        var d = Goonmill.whichNewThing(name);

        d.addCallback(function (which) {
            var count, dd;
            if (which[0] == 'npc') {
                dd = self.callRemote('newNPC', monsterId);
                dd.addCallback(function (wi) {
                    document.fire('Goonmill:newNPC', {
                        npc:wi
                    });
                    return null;
                });
            } else if (which[0] == 'monsterGroup') {
                count = parseInt(which[1], 10);
                dd = self.callRemote('newMonsterGroup', monsterId, count);
                dd.addCallback(function (wi) {
                    document.fire('Goonmill:newMonsterGroup', {
                        monsterGroup:wi
                    });
                    return null;
                });
            }
            return dd;
        });

        return d;
    }
);


Goonmill.ConstituentList = Goonmill.GoonmillWidget.subclass('Goonmill.ConstituentList');
Goonmill.ConstituentList.methods(
    function __init__(self, node) {
        Goonmill.ConstituentList.upcall(self, '__init__', node);
        node.select('.constituent').each(function (cnst) {
            self._setEvents(cnst);
        });

        // using custom events
        document.observe('Goonmill:constituentDetailUpdate', function (e) {
            self.updateConstituentDetail(e.memo.id, e.memo.detail);
        });
    }, 

    // make all closing x's clickable, and the buttons themselves clickable
    function _setEvents(self, constituent) {
        // closing x
        constituent.select('.closingX')[0].observe('click', function (event) {
            self.removeConstituentClicked(event, constituent);
        });

        // the button itself
        constituent.observe('click', function (event) {
            self.constituentClicked(constituent);
        });
    },

    // put a constituent on the stage
    function constituentClicked(self, node) {
        var id = parseInt(node.readAttribute('rel'), 10);
        d = self.callRemote('displayConstituent', id);
        var spinner = Goonmill.spin(body.select('.x2x')[0]);

        d.addCallback(function (wi) {
            if (node.hasClassName('kind-monsterGroup')) {
                document.fire('Goonmill:newMonsterGroup', {monsterGroup:wi});
            } else if (node.hasClassName('kind-npc')) {
                document.fire('Goonmill:newNPC', {npc:wi});
            } else {
                throw 'Not implemented - clicked constituent';
            }
        });

        d.addBoth(function () { Goonmill.unspin(spinner); });
        return d;
    },

    // throw the given constituent out of the workspace
    function removeConstituentClicked(self, event, node) {
        event.stop();
        var args = {name: node.select('.constituentName')[0].innerHTML,
            detail: node.select('.constituentDetail')[0].innerHTML
        };
        var message, button1;

        if (node.hasClassName('kind-monsterGroup')) { 
            message = 'Delete the monster group #{name}, with #{detail} creatures?';
            button1 = 'delete';
        } else if (node.hasClassName('kind-encounter')) {
            message = 'Delete the encounter #{name}, with #{detail} creatures?';
            button1 = 'delete';
        } else if (node.hasClassName('kind-stencil')) {
            message = 'Remove stencil for #{name} from this workspace? (#{name} will remain in your user library.)';
            button1 = 'remove';
        } else if (node.hasClassName('kind-npc')) {
            message = 'Remove NPC named #{name} from this workspace? (#{name} will remain in your user library.)';
            button1 = 'remove';
        } else {
            message = 'ONO XX';
            button1 = 'ONO';
        }
        message = message.interpolate(args);


        var d = Goonmill.confirm(message, button1, 'whoops no');
        d.addCallback(function (button) { 
            if (button == 1) {
                var id = parseInt(node.readAttribute('rel'), 10);
                var d = self.callRemote('removeConstituent', id);
                d.addCallback(function (r) {
                    Effect.Fade(node, {afterFinish: function() { node.remove(); }});
                    document.fire('Goonmill:removedConstituent', {id:id});
                    // FIXME - this isn't working if the constituent is one i
                    // just added
                });
                return d;
            }
        });
    },

    // put a new constituent into the list
    function addConstituent(self, kind, id, name, detail) {
        var source = self.node.select('.template')[0];
        var listItem = source.jstClone({'title':'FIXME', 
            'name':name, 'rel':id, 'detail':detail, 'kind':kind
        });
        self.node.insert(listItem);
        self._setEvents(listItem);
        Effect.Appear(listItem);
        return null;
    },

    // set the visible detail of a constituent item in the list
    function updateConstituentDetail(self, id, detail) {
        var match = '.constituent[rel=' + id + '] .constituentDetail';
        detail = detail.toString().truncate(15);
        var n = self.node.select(match)[0];
        n.hide();
        n.update(detail);
        Effect.Appear(n);
    }

);


Goonmill.MainActions = Goonmill.GoonmillWidget.subclass('Goonmill.MainActions');
Goonmill.MainActions.methods(
    function __init__(self, node) {
        Goonmill.MainActions.upcall(self, '__init__', node);
        node.select('[rev=npc]')[0].observe('click', function (event) {
            self.newNPCClicked();
        });
        node.select('[rev=monsterGroup]')[0].observe('click', function (event) {
            self.newMonsterGroupClicked();
        });
        node.select('[rev=stencil]')[0].observe('click', function (event) {
            self.newStencilClicked();
        });
        node.select('[rev=encounter]')[0].observe('click', function (event) {
            self.newEncounterClicked();
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
Goonmill.EventBus = Goonmill.GoonmillWidget.subclass('Goonmill.EventBus');
Goonmill.EventBus.methods(
    function __init__(self, node) {
        Goonmill.EventBus.upcall(self, '__init__', node);

        // watch for incoming widgets, and field them.
        document.observe('Goonmill:newNPC', function (e) {
            self.showConstituent(e.memo.npc);
        });

        document.observe('Goonmill:newMonsterGroup', function (e) {
            if (e.memo.monsterGroup === undefined) {
                throw ('must fire this event with {monsterGroup:someWidget}');
            }
            self.showConstituent(e.memo.monsterGroup);
        });

        document.observe('Goonmill:removedConstituent', function (e) {
            var d = self.hideConstituent(e.memo.id);
            return d;
        });
    },

    // display a constituent on the stage
    function showConstituent(self, wi) {
        self.hideConstituent();
        var d = self.addChildWidgetFromWidgetInfo(wi);
        return null;
    },

    // clean up the stage when a constituent is there that was just removed
    function hideConstituent(self, id) {
        if (self.childWidgets.length > 1) {
            debugger;
        }
        // get the widget currently on the stage
        var w = self.childWidgets[0];

        // nothing on the stage -> nothing to do
        if (w === undefined) { return; }
 
        // id undefined -> don't check id. if we must check id, do nothing
        // IF the id on the stage is not the id we're trying to hide
        if ((id !== undefined) && (id == w.constituentId)) { return; }

        w.detach();

        var blank = body.select('.offstage .itemView')[0].cloneNode(true);
        w.node.replace(blank);
    }
);


// base class of everything that replaces the main pane
Goonmill.ItemView = Goonmill.GoonmillWidget.subclass('Goonmill.ItemView');
Goonmill.ItemView.methods(
    function __init__(self, node) {
        Goonmill.ItemView.upcall(self, '__init__', node);
        node.hide();
        var oldView = document.documentElement.select('.itemView')[0];
        oldView.replace(node);
        node.show();
    }
);


// view of a monster group in the main pane
Goonmill.MonsterGroup = Goonmill.ItemView.subclass('Goonmill.MonsterGroup');
Goonmill.MonsterGroup.methods(
    function __init__(self, node, constituentId) {
        Goonmill.MonsterGroup.upcall(self, '__init__', node);
        self.constituentId = constituentId;

        var printButton = $$('.printButton')[0];
        printButton.observe('click', function (e) {
            e.stop();
            e.preventDefault();
            return self.printWindow();
        });

        node.select('.deleteChecked').each(function (n) {
            n.observe('click', function (nn, e) {
                self.deleteClicked(nn, e);
            }.curry(n) );
        });

        var toggleAll = node.select('[name=toggleAll]')[0];
        toggleAll.observe('click', function (e) {
                self.toggleAllClicked(toggleAll, e);
        });

        var randomize = node.select('.randomize')[0];
        randomize.observe('click', function (e) {
            self.randomizeClicked(e);
        });

        // the "increase by" form must have a limit to prevent overloading the
        // browser.  Server code will check to make sure the total is in sane
        // limits (and raise if not)
        var increaseBy = node.select('[name=increaseBy]')[0];

        var imageBox = node.select('.imageBox')[0];
        imageBox.observe('click', function (e) {
            self.imageBoxClicked(imageBox, e);
        });

        node.select('.tabHandle').each(function (n) {
            n.observe('click', function (nn, e) {
                self.tabHandleClicked(nn, e);
            }.curry(n));
        });

        if (window.LiveValidation) {
            var increaseValid = new LiveValidation(increaseBy.increaseByAmount, {
                validMessage:''
            });
            increaseValid.add(Validate.Presence);
            increaseValid.add(Validate.Numericality, {
                onlyInteger: true, minimum: 1, maximum: 123
            });

            increaseBy.observe('submit', function (e) { 
                // we have to manually validate the form to block submittal, since
                // we are overriding the default submit behavior.  LiveValidation
                // only attempts to block the default submit behavior.
                if (LiveValidation.massValidate([increaseValid])) {
                    return self.onIncreaseBySubmit(e);
                }
            });
        }

        // whenever this displays, fix the constituent list to match it
        document.fire('Goonmill:constituentDetailUpdate', {
            id: self.constituentId,
            detail: node.select('.groupieRow').length
        });

        self.fixDeleteButtons();
    },

    function printWindow(self) {
        var url, w2;
        url = 'printMonsterGroup/' + self.constituentId;
        w2 = window.open(url,'Print View','width=700,height=600,directories=no,location=no,menubar=no,toolbar=no,scrollbars=yes');
        return false;
    },

    // ask the server to increase groupies.
    function onIncreaseBySubmit(self, event) {
        event.stop();
        event.preventDefault();
        var amount = parseInt(event.element().increaseByAmount.value, 10);
        var d = self.callRemote('increaseGroupies', amount);
            
        var spinner = Goonmill.spin(body.select('.x2x')[0]);

        d.addCallback(function (wi) {
            Goonmill.unspin(spinner);
            document.fire('Goonmill:newMonsterGroup', {monsterGroup:wi});
        });
        return d;
    },

    // which gropuies are checked?  returns a 2-tuple of rows and ids
    function checked(self) {
        var rows = self.node.select('.groupieRow');
        var checkedRows = [];

        var ids = rows.map(function (r) {
            var checkbox = r.select('[name=selectGroupie]')[0];
            if (checkbox.checked) {
                checkedRows.push(r);
                return parseInt(r.readAttribute('rel'), 10);
            }
        }).filter(Prototype.K);

        return [ids, checkedRows];
    },

    // hide other tabs
    function tabHandleClicked(self, tabHandle, event) {
        event.stop();
        event.preventDefault();
        var which = tabHandle.getAttribute('rel');
        var n = self.node;
        n.select('.tab').each(function (tab) {
            tab.removeClassName('tabSelected');
        });
        n.select('.' + which)[0].addClassName('tabSelected');
    },

    // tell the server to remove the groupies that were checked
    function deleteClicked(self, node, event) {
        var checked = self.checked();
        var ids = checked[0];
        var checkedRows = checked[1];

        if (ids.length === 0) { return null; }

        var d = self.callRemote('deleteChecked', ids);

        var spinner = Goonmill.spin(body.select('.x2x')[0]);

        d.addCallback(function (count) {
            Goonmill.unspin(spinner);

            if (count != checkedRows.length) { 
                throw 'count != checkedRows.length'; 
            }
            checkedRows.invoke('remove');
            self.fixDeleteButtons();
            
            document.fire('Goonmill:constituentDetailUpdate', {
                id:self.constituentId, 
                detail:self.node.select('.groupieRow').length
            });

            return null;
        });

        return d;
    },

    // hide delete buttons if there's no groupies left
    function fixDeleteButtons(self) {
        var remaining = self.node.select('.groupieRow');
        if (remaining.length === 0) {
            self.node.select('.deleteChecked').invoke('hide');
        } else {
            self.node.select('.deleteChecked').invoke('show');
        }
    },

    // when the 'toggle all' is clicked, all the other checkboxes toggle
    // to match it
    function toggleAllClicked(self, node, event) {
        self.node.select('[name=selectGroupie]').each( function (n) {
                n.checked = node.checked;
        });
    },

    // popup a big version of the image
    function imageBoxClicked(self, node, event) {
        var url = node.getAttribute('rel');
        Goonmill.imageBox(url);
    },

    function randomizeClicked(self, node, event) {
        var checked = self.checked();
        var ids = checked[0];

        var rows = checked[1];

        if (ids.length === 0) { return null; }

        var d = self.callRemote('randomizeChecked', ids);

        rows.map(function (n) {
            return Effect.Pulsate(n, {pulses: 2, duration: 2.0});
        });

        d.addCallback(function (wi) {
            document.fire('Goonmill:newMonsterGroup', {
                monsterGroup:wi
            });
            return null;
        });

        return d;

    }
);


// view of an npc in the main pane
Goonmill.NPC = Goonmill.ItemView.subclass('Goonmill.NPC');
Goonmill.NPC.methods(
);


// with hax, subclass prototip Tip and customize it
Goonmill.GoonTip = Divmod.Class.subclass('Goonmill.GoonTip');
Goonmill.GoonTip.methods(
    function __init__(self, node, content) {
        self.content = self.containerize(content);
        var TIPCONFIG = {
            fixed: true,
            closeButton: false,
            hook: { target: 'bottomRight', tip: 'bottomLeft' },
            className: 'tipTip',
            offset: { x:10, y:3 },
            effect: 'appear',
            duration: 0.2
            // hideOn: { element: 'closeButton' }
        };
        self.node = node;

        // kludgy but apparently works
        self.__proto__ = new Tip(self.node, self.content, TIPCONFIG);
    },

    // wrap 
    function containerize(self, content) {
        return body.select('.offstage .prototipTip')[0].jstClone(content);
    }
);


Element.addMethods({
    // clone the element and jstProcess it
    jstClone: function (element, context) {
        var cloned = element.cloneNode(true);
        cloned.context = new JsEvalContext(context);
        jstProcess(cloned.context, cloned);
        return cloned;
    },

    // try getVariable
    jstGet: function (element, name) {
        return element.context.getVariable(name);
    }
});


/* functions begin here **************************************************/
/* functions begin here **************************************************/
/* functions begin here **************************************************/
/* functions begin here **************************************************/
/* functions begin here **************************************************/
/* functions begin here **************************************************/
/* functions begin here **************************************************/
/* functions begin here **************************************************/
/* functions begin here **************************************************/
/* functions begin here **************************************************/
/* functions begin here **************************************************/
/* functions begin here **************************************************/
/* functions begin here **************************************************/




// display the dialog that disambiguates monster groups and npcs
Goonmill.whichNewThing = function(name) {
    var d = new Divmod.Defer.Deferred(); 
    var f1 = function() { Control.Modal.current.close(true); d.callback(1); };
    var f2 = function() { Control.Modal.current.close(true); d.callback(2); };
    var closer = function (e) { Control.Modal.current.close(true); };

    var clone = body.select('.offstage .whichNewThing')[0].jstClone({'name': name});

    /* if using new monster group, only integers between 1-123 allowed */
    var count = clone.jstGet('$count');
    var countValid = new LiveValidation(count, {validMessage:''} );
    countValid.add(Validate.Presence);
    countValid.add(Validate.Numericality, 
            { onlyInteger: true, minimum: 1, maximum: 123 }
    );

    clone.jstGet('$newMonsterGroup').observe('click', f1);
    clone.jstGet('$newNPC').observe('click', f2);
    clone.jstGet('$cancel').observe('click', closer);

    d.addCallback(function (button) {
        if (button == 1) { return ['monsterGroup', count.value]; }
        else if (button == 2) { return ['npc' ]; }
    });

    clone.show();
    var m = Goonmill.Modal(clone);

    return d;
};

// this is the standard default way lightboxes will display in goonmill
// (function is for folding purposes only)
var LightboxConfig = {
    overlayOpacity:0.7,
    fade: false,  // too slow joe
    className: 'modal_container'
};


// display an image
Goonmill.imageBox = function (url) {
    var clone = body.select('.offstage .imageBoxMeat')[0].jstClone({'url':url});
    var close = clone.jstGet('$close');
    var m = Goonmill.Modal(clone, {closeOnClick: close});

    return m;
};


// display any node or string as a message
Goonmill.messageBox = function (node) {
    var meat = body.select('.offstage .messageBoxMeat')[0].jstClone({});

    meat.jstGet('$container').update(node);

    var close = meat.jstGet('$close');
    var m = Goonmill.Modal(meat, {closeOnClick: close});

    return m;
};

// copy the contents into a modal dialog (lightbox)
Goonmill.Modal = function (contents, extraOptions) {
    var config = $H(LightboxConfig).merge(extraOptions).toObject();

    // esc to close
    var escHotkey = new HotKey('esc', function (event) { 
            Control.Modal.current.close(true); 
    }, {ctrlKey:false});

    // restore embedded stuff when closing the modal
    config.afterClose = function () { 
        Control.Modal.current.destroy();
        escHotkey.destroy();
    };

    var modal = new Control.Modal(null, config);
    modal.container.insert(contents);
    modal.open();

    return modal;
};


// ask a question, then return a deferred that will fire with the number of
// the clicked button.
Goonmill.confirm = function (message, button1text, button2text) {
    // copy the content of node into a modal dialog (lightbox)
    var d = new Divmod.Defer.Deferred(); 
    var clone = body.select('.offstage .confirm')[0].jstClone({'message':message, 
            'button1text': button1text, 'button2text': button2text
    });
    var f1 = function() { Control.Modal.current.close(true); d.callback(1); };
    var f2 = function() { Control.Modal.current.close(true); d.callback(2); };
    clone.jstGet('$button1').observe('click', f1);
    clone.jstGet('$button2').observe('click', f2);

    var m = Goonmill.Modal(clone);

    return d;
};


// display all the widgets' top-level nodes, with hints
Goonmill.debugView = function () {
    var toPrint = Goonmill.findAllWidgets();

    var printNodes = toPrint.map(function (w) {
        var n = w.node;
        var dtText = n.readAttribute('class') + ' (' + n.identify() + ')';
        return [new Element('dt').update(dtText),
                new Element('dd').update(n.textContent.truncate(60))];
    }).flatten();

    var dl = new Element('dl');
    // FIXME - printNodes.each should work here, but i get
    // 'element.appendChild is not an attribute'
    for (n=0; n<printNodes.length; n++) { dl.insert(printNodes[n]); }
    Goonmill.messageBox(dl);
};

// collect all the widgets (using Athena internals) and return them
Goonmill.findAllWidgets = function() {
    var widgets = [];
    var widgetMap = Nevow.Athena.Widget._athenaWidgets;
    $H(widgetMap).values().each(function (wid) { widgets.push(wid); });
    return widgets;
};


// display a spinner while busy loading
Goonmill.spin = function(el) {
    var spinner = new Element('img', {src: '/static/loading.gif'});
    el.insert(spinner);
    return spinner;
};

// destroy a spinner
Goonmill.unspin = function(spinner) {
    spinner.remove();
};


Goonmill.message = function(text, severity) {
    var span = new Element('span').update(text);
    span.hide();
    // TODO - severity
    var messageArea = document.documentElement.select('.messageArea')[0];
    $A(messageArea.childNodes).each(function (e) { e.remove(); } );
    messageArea.insert(span);
    messageArea.addClassName('contents');
    span.show();
    Effect.Pulsate(messageArea, {pulses: 2, duration: 0.5});
    return span;
};

if (window.HotKey) {
    // for debugging, shift+esc = debug
    var _ignored = new HotKey('esc', function (event) {
            Goonmill.debugView();
            }, {ctrlKey:false, shiftKey:true});
}

// vim:set foldmethod=syntax:set smartindent:
