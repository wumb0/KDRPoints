$.getScript('/static/kon/konami.js', function()
{
    var script = new Konami();
    script.code = function () {
        var i = Math.random() * -360;
        document.body.style.MozTransform = 'rotate(' + i + 'deg)';
        document.body.style['-webkit-transform'] = 'rotate(' + i + 'deg)';
        var mydiv = document.getElementById("footerdiv");
        mydiv.innerHTML += "<audio autoplay loop><source src='/static/pianoman.mp3' type='audio/mpeg'></audio>";
        alert("Nerd.");
    }
    script.load()
});

$(window).on('resize load', function() {
    $('body').css({"padding-top": $(".navbar").height()+15 + "px"});
});
