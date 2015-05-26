$.getScript('/static/kon/konami.js', function()
{
    var script = new Konami();
    script.code = function () {
        document.body.style.MozTransform = 'rotate(180deg)';
        document.body.style['-webkit-transform'] = 'rotate(180deg)';
        alert("Nerd.");
    }
    script.load()
});
