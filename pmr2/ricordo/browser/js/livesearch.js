$(document).ready(function () {

    $(".queryterm").typeahead({
        source: suggestTerms,
        matcher: function(term) { return true; },
        items: 32,
        minLength: 2
    });

});

function suggestTerms(query, process) {
    return getTerms(query, process);
}


function getTerms(query, process) {
    target = window.location.href.toString().replace(
        /pmr2_ricordo\/query.*/, 'pmr2_ricordo/owlterms/') + query;
    console.log(target);
    $.getJSON(target, function(data) {
        var items = [];
        $.each(data["results"], function(key, val) {
            items.push(val[0] + ' - ' + val[1]);
        })
        process(items);
    })
}
