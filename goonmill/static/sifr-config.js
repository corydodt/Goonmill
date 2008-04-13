var vinque = {
src: '/static/3p/vinque.swf'
/*
,filters: {
  DropShadow: {
    knockout: false
    ,distance: 1
    ,color: '#999'
    ,strength: 2
  }
}
*/
,transparent: true
,opaque: false
,wmode: 'transparent'
}

sIFR.activate(vinque);

sIFR.replace(vinque, {
          selector: 'h1'
          });

