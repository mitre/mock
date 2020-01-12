function applyScenario() {
    function doNothing(){}
    let scenario = document.getElementById("scenarios").value;
    console.log('Changing scenario to: ' + scenario);
    restRequest('POST', {"scenario": scenario}, doNothing, '/plugin/mock/scenario')
    flashy('mock-confirm', 'Scenario applied!');
}

function handleStart() {
    function handleStartAction(data){
        $("#togBtnOp").prop("checked", false).change();
        let op_elem = $("#batch-list");
        if(!op_elem.find('option[value="'+data.name+'"]').length > 0){
            op_elem.append('<option id="' + data.name + '"' + 'value="' + data.name +'" >' + data.name + ' - ' + data.start + '</option>');
        }
        op_elem.prop('selectedIndex', op_elem.find('option').length-1).change();
        refresh();
    }
    let batch = buildOperationObject();
    restRequest('POST', batch, handleStartAction, '/plugin/mock/batch');
}

function buildOperationObject() {
    let name = document.getElementById("queueName").value;
    if(!name){ alert('Please enter a batch name'); return; }
    return {
        "name":name,
        "number":document.getElementById("queueNumber").value,
        "group":document.getElementById("queueGroup").value,
        "adversary_id":document.getElementById("queueFlow").value,
        "planner":document.getElementById("queuePlanner").value,
        "phases_enabled":document.getElementById("queuePhasesEnabled").value,
        "source":document.getElementById("queueSource").value
    };
}

function toggleBatchView(){
    $('#viewBatch').toggle();
    $('#addBatch').toggle();
    if ($('#togBtnOp').is(':checked')) {
        showHide('.queueOption', '#batch-list');
    } else {
        showHide('#batch-list', '.queueOption');
    }
}

let refreshInterval = null;
function refresh() {
    function batchCallback(data){
        $("#batch-results").find("tr:gt(0)").remove();
        let batch = data[0];
        let finished = 0;
        $.each(batch.operations, function(index, op) {
            if(op.finish) { finished += 1; }
            $('#batch-results tr:last').after('<tr><td>'+op.start+'</td><td>'+op.finish+'</td><td>'+findOpDuration(op)+'</td><td>'+op.chain.length+'</td></tr>');
        });
        $('#batch-name').html(batch.name);

        if(finished === batch.operations.length) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        } else {
            if(!refreshInterval) {
                refreshInterval = setInterval(refresh, 10000);
            }
        }
    }
    let selected = $('#batch-list option:selected').attr('value');
    let postData = selected ? {'index':'batches','name': selected} : null;
    restRequest('POST', postData, batchCallback, '/plugin/chain/full');
}