onmessage = function(e) {
    console.log('Got message ' + e.data);
    postMessage('Foo!!!');
};