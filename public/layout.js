function OnFCUpdated() {

    observer.disconnect();

    let fcScrol = document.getElementsByClassName('fc-scroller').item(0);
    fcScrol.style.height = calHeight + 'px';

    let fcHead = document.getElementsByClassName('fc-header-toolbar').item(0);
    for (let i = 0; i < fcHead.childElementCount; i++) {
        for (let j = 0; j < fcHead.children.item(i).childElementCount; j++) {
            let elt = fcHead.children.item(i).children.item(j);
            if ((i !== 0 || j !== 0) && elt.classList.contains('btn-group')) {
                elt.classList.remove('btn-group');
                elt.classList.add('btn-group-vertical');
            }
        }
    }

    observer.observe(fcScrol, { attributes: true, attributeFilter: ['style'] });

    if (localStorage.getItem('showTooltips') === 'true') {

        let toDel = $('.ui-tooltip');

        for (let i = 0; i < toDel.length; i++) {
            toDel[i].remove();
        }


        $($('.fc-today-button')[0]).attr('title', 'Revenir au jour/ la semaine en cours.').tooltip();
        $($('.fc-prev-button')[0]).attr('title', 'Passer  la semaine prcdente / au jour prcdent.').tooltip();
        $($('.fc-next-button')[0]).attr('title', 'Passer  la semaine suivante / au jour suivant.').tooltip();
    }
}

let observer = new MutationObserver(function (mutations) {
    OnFCUpdated();
});
let calHeight = 800;

function ApplyColumnLayout() {

    let calElt = document.getElementById('calendar');
    calElt.style.display = 'flex';
    calElt.style.flexDirection = 'row-reverse';

    let fcScroller = document.getElementsByClassName('fc-scroller').item(0);
    let fcHeader = document.getElementsByClassName('fc-header-toolbar').item(0);
    calHeight = fcScroller.offsetHeight + fcHeader.offsetHeight;

    OnFCUpdated();

    for (let i = 0; i < document.styleSheets.length; i++) {
        let ss = document.styleSheets[i];
        if (ss.href != null && ss.href.toLowerCase().includes('fullcalendar') && ss.href.toLowerCase().includes('core')) {
            for (let j = 0; j < ss.cssRules.length; j++) {
                var rule = ss.cssRules[j];

                if (rule.selectorText != null && rule.selectorText.toLowerCase() === '.fc-toolbar.fc-header-toolbar') {
                    rule.style["flex-direction"] = 'column';
                    rule.style["align-items"] = 'space-around';
                    rule.style["justify-content"] = 'space-around';
                    rule.style["overflow-y"] = 'auto';
                    rule.style.height = '100vh';
                    rule.style.minWidth = '10%';
                }
            }
        }
    }

    let style = document.createElement('style');
    //style.innerHTML = '.fc-left, .fc-left button, .fc-center, .fc-center button, .fc-right, .fc-right button { display:flex; flex-direction:column;justify-content:center;align-content:space-between; }';

    style.innerHTML = '.fc-left               { display:flex; flex-direction:column; justify-content:space-evenly; align-content:space-between; align-items: center; min-height: 65%;} ';
    style.innerHTML += '.fc-center, .fc-right { display:flex; flex-direction:column; justify-content:space-evenly; align-content:space-between; align-items: center; min-height: 17%;}';

    document.body.appendChild(style);

}
