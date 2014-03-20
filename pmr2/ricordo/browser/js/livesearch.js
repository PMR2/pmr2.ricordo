var lastQuery = '';
var selectedTerm = '';
var selectedRelation = '';

// These relations should be derived directly from the OWL store, but
// then the owlkb doesn't really use those URLs so...

var relations = [
    "topObjectProperty (ANY)",
    "part-of (RICORDO)",
    "has-part (RICORDO)",
    "contained-in (RICORDO)",
    "has_participant (RICORDO)",
    "inheres-in (RICORDO)",
    "participates-in (RICORDO)",
    "results_in (RICORDO)",
    "results_in_movement_of (RICORDO)",
    "results_in_transport_from (RICORDO)",
    "results_in_transport_to (RICORDO)",
    "inheres_in_part_of (RICORDO)",
    "occurs_in (RICORDO)",
    "composed_of (OPB)",
    "physicalPropertyOf (OPB)",
    "contained_in (RO)",
    "part_of (RO)",
    "attaches_to (FMA)",
    "bounds (FMA)",
    "branch_of (FMA)",
    "constitutional_part_of (FMA)",
    "regional_part_of (FMA)",
    "systemic_part_of (FMA)",
    "has_part (GO)",
    "negatively_regulates (GO)",
    "positively_regulates (GO)",
    "regulates (GO)",
    "OBO_REL_part_of (PATO)",
    "decreased_in_magnitude_relative_to (PATO)",
    "different_in_magnitude_relative_to (PATO)",
    "directly_associated_with (PATO)",
    "has_cross_section (PATO)",
    "has_dividend_entity (PATO)",
    "has_dividend_quality (PATO)",
    "has_divisor_entity (PATO)",
    "has_divisor_quality (PATO)",
    "has_part (PATO)",
    "has_ratio_quality (PATO)",
    "has_relative_magnitude (PATO)",
    "increased_in_magnitude_relative_to (PATO)",
    "inheres_in (PATO)",
    "inversely_associated_with (PATO)",
    "is_magnitude_of (PATO)",
    "is_measurement_of (PATO)",
    "is_unit_of (PATO)",
    "reciprocal_of (PATO)",
    "similar_in_magnitude_relative_to (PATO)",
    "singly_occurring_form_of (PATO)",
    "towards (PATO)",
    "part_of (PATO)"
];

$(document).ready(function () {

    $(".queryrelation").typeahead({
        source: relations,
        items: 16,
        updater: updateRelationSelection,
        minLength: 2
    });

    $(".queryterm").typeahead({
        source: suggestTerms,
        matcher: function(term) { return true; },
        updater: updateTermSelection,
        items: 32,
        minLength: 2
    });

    $('#btnBuildQuery').button().on('click', function() {
        var result = '';
        if (selectedRelation) {
            result = selectedRelation + 'some ';
        }
        result = result + selectedTerm;
        $('#form-widgets-query').val(result);
    });

});

function suggestTerms(query, process) {
    setTimeout(function() {
        if ((query == $(".queryterm").val()) && (query != lastQuery)) {
            lastQuery = query;
            getTerms(query, process);
        }
    }, 200);
}

function getTerms(query, process) {
    target = window.location.href.toString().replace(
        /pmr2_ricordo\/query.*/, 'pmr2_ricordo/owlterms/') + query;
    console.log(target);
    $.getJSON(target, function(data) {
        var items = [];
        $.each(data["results"], function(key, val) {
            items.push(
                val[0] + ' (' + val[1].replace(/[^#]*#/, '') + ')'
            );
        })
        process(items);
    })
}

function updateTermSelection(item) {
    selectedTerm = item.replace(/[^(]*\((.*)\)/, '$1');
    return item;
}


function updateRelationSelection(item) {
    selectedRelation = item.replace(/([^(]*).*/, '$1');
    return item;
}
