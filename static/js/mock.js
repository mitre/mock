function applyScenario() {
    function doNothing(){}
    let scenario = document.getElementById("scenarios").value;
    console.log('Changing scenario to: ' + scenario);
    restRequest('POST', {"scenario": scenario}, doNothing, '/plugin/mock/scenario')
    flashy('mock-confirm', 'Scenario applied!');
}
