// timekeeper.js

;(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
    typeof define === 'function' && define.amd ? define(factory) :
    global.TimeKeeper = factory()
}(this, (function () { 'use strict';

  var TimeKeeper = {};

  var pendingEvent = undefined;

  var elemDialog = $("#createNew");

  var configurationMenu = $("#mainMenu");

  var redmineObj = $("#idRedmine");

  var redmineComment = $('#idComment');

  var redmineText = $("#redmineText");

  var timeouts = {
    otrs: undefined,
    redmine: undefined,
    exchange: undefined,
    gitlab: undefined,
    assigned: undefined,
    assigne: undefined,
  };

  var eventInfo = null;

  var themeSelector = document.getElementById("themeName");

  var calendar = {};
  var calendarOptions = {};

  // theme list: https://www.bootstrapcdn.com/bootswatch/
  var allowedThemes = {
    default: {
      name: "Default (bootstrap)",
      url: "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css",
      integrity: 'sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh',
    },
    darky: {
      name: "Darkly",
      url: "https://stackpath.bootstrapcdn.com/bootswatch/4.4.1/darkly/bootstrap.min.css",
      integrity: 'sha384-rCA2D+D9QXuP2TomtQwd+uP50EHjpafN+wruul0sXZzX/Da7Txn4tB9aLMZV4DZm',
    },
  };

  var defaultConfiguration = {};
  
  var requestedConf = {};
  
  var configuration = {};

  var btnHideExchangeEvent = $("#hideEvent");

  //form = elemDialog.children('form')[0]; //submit = elemDialog.find('p input[type=button]')[0];

  var btnSubmit = $(elemDialog.find('#timeentryAdd')[0]);

  var btnCancel;

  var redmineUpdateButton = undefined;

  var btnConfigurationSave = $("#configurationSave");
  
  var plugins = {};

  function convertSessionStorageToLocalStorage()
  {
    localStorage.setItem("colorOtrs",            sessionStorage.getItem("colorOtrs"             ));
    localStorage.setItem("colorRedmine",         sessionStorage.getItem("colorRedmine"          ));
    localStorage.setItem("colorExchange",        sessionStorage.getItem("colorExchange"         ));
    localStorage.setItem("colorGitlab",          sessionStorage.getItem("colorGitlab"           ));
    localStorage.setItem("showWeekend",          sessionStorage.getItem("showWeekend"           ));
    localStorage.setItem("businessHourStart",    sessionStorage.getItem("businessHourStart"     ));
    localStorage.setItem("businessHourEnd",      sessionStorage.getItem("businessHourEnd"       ));
    localStorage.setItem("businessHourEndFri",   sessionStorage.getItem("businessHourEndFri"    ));
    localStorage.setItem("showOnlyBusinessHour", sessionStorage.getItem("showOnlyBusinessHour"  ));
    localStorage.setItem("showTooltips",         sessionStorage.getItem("showTooltips"          ));
    localStorage.setItem("showMaskedEvents",     sessionStorage.getItem("showMaskedEvents"      ));
    sessionStorage.clear();
  }

  function initialize(options, userPlugins)
  {
    plugins = userPlugins;
    
    if(sessionStorage.getItem('colorOtrs'))
    {
      //console.log('converting session storage to local storage');
      convertSessionStorageToLocalStorage();
    }
    
    if(localStorage.getItem("colorOtrs"))
    {
      //console.log('converting old color storage values to new');
      localStorage.setItem("color_otrs", localStorage.getItem("colorOtrs"));
      localStorage.setItem("color_redmine", localStorage.getItem("colorRedmine"));
      localStorage.setItem("color_exchange", localStorage.getItem("colorExchange"));
      localStorage.setItem("color_gitlab", localStorage.getItem("colorGitlab"));
      
      localStorage.removeItem("colorOtrs");
      localStorage.removeItem("colorRedmine");
      localStorage.removeItem("colorExchange");
      localStorage.removeItem("colorGitlab");
    }

    defaultConfiguration = {
      showWeekend: true,
      businessHourStart: "08:00",
      businessHourEnd: "17:00",
      businessHourEndFri: "16:00",
      showOnlyBusinessHour: false,
      refresh: 600, // seconds
      showTooltips: true,
      showMaskedEvents: false,
      theme: "default",
      //visibility_otrs: 'visible',
      //visibility_redmine: 'visible',
      //visibility_exchange: 'visible',
      //visibility_gitlab: 'visible',
    }

    requestedConf = {
      //colorOtrs:            localStorage.getItem("colorOtrs"),
      //colorRedmine:         localStorage.getItem("colorRedmine"),
      //colorExchange:        localStorage.getItem("colorExchange"),
      //colorGitlab:          localStorage.getItem("colorGitlab"),
      showWeekend:          localStorage.getItem("showWeekend") === "false" ? false : true,
      businessHourStart:    localStorage.getItem("businessHourStart"),
      businessHourEnd:      localStorage.getItem("businessHourEnd"),
      businessHourEndFri:   localStorage.getItem("businessHourEndFri"),
      showOnlyBusinessHour: localStorage.getItem("showOnlyBusinessHour") === "true" ? true : false,
      showTooltips:         localStorage.getItem('showTooltips') === 'false' ? false : true,
      showMaskedEvents:     localStorage.getItem('showMaskedEvents') === 'true' ? true : false,
      theme:                localStorage.getItem('theme'),
      //visibility_otrs:      localStorage.getItem('visibility_otrs'),
      //visibility_redmine:   localStorage.getItem('visibility_redmine'),
      //visibility_exchange:  localStorage.getItem('visibility_exchange'),
      //visibility_gitlab:    localStorage.getItem('visibility_gitlab'),
    };
    for(key in plugins)
    {
      defaultConfiguration['color_' + key] = plugins[key].color;
      defaultConfiguration['visibility_' + key] = plugins[key].color;
      requestedConf['color_' + key] = localStorage.getItem("color_" + key);
      requestedConf['visibility_' + key] = localStorage.getItem("visibility_" + key);
    }

    Object.keys(requestedConf).forEach((key) => (requestedConf[key] === null) && delete requestedConf[key]);

    configuration = {...defaultConfiguration, ...requestedConf};
    console.log(configuration);
    redmineObj.val("");
    redmineText.html("");
    redmineComment.val("");

    elemDialog.dialog({
      'autoOpen': false,
      zIndex: 100,
    });

    configurationMenu.dialog({
      autoOpen: false,
      zIndex: 101,
      minWidth: "40%",
      width: "40%",
    });

    //$("#idColorOtrs").val(configuration.colorOtrs);
    //$("#idColorRedmine").val(configuration.colorRedmine);
    //$("#idColorExchange").val(configuration.colorExchange);
    //$("#idColorGitlab").val(configuration.colorGitlab);
    var configurationColorParentDiv = $("#configuration-colors");
    var colorTemplateForm = $("#configuration-colors-color-template");
    for(key in plugins)
    {
      var colorForm = colorTemplateForm.clone();
      colorForm.find('label').text("Couleur " + plugins[key].name + " :");
      colorForm.find('input').attr('id', 'idColor_' + key).val(configuration['color_' + key]);
      //$("#idColor_" + key).val(configuration['color_' + key]);
      configurationColorParentDiv.append(colorForm);
    }
    colorTemplateForm.remove();
    $("#showWeekend").prop('checked', configuration.showWeekend);
    $("#businessHourStart").val(configuration.businessHourStart);
    $("#businessHourEnd").val(configuration.businessHourEnd);
    $("#businessHourEndFri").val(configuration.businessHourEndFri);
    $("#idShowOnlyBusinessHour").prop('checked', configuration.showOnlyBusinessHour);
    $('#refreshTimer').val(configuration.refresh);
    $('#showTooltips').prop('checked', configuration.showTooltips);
    $('#showMaskedEvents').prop('checked', configuration.showMaskedEvents);

    elemDialog.on('dialogclose', function(event, ui) {
      //console.log(event, ui);
      elemDialog.find("#datetime").text("");
      //redmineId = redmineObj.val();
      redmineObj.val("");
      redmineComment.val("");
      redmineText.html("");
      pendingEvent && pendingEvent.remove();
      timeouts.redmine && clearTimeout(timeouts.redmine);
      timeouts.redmine = setTimeout(updateRedmine, 1000 * configuration.refresh);
      redmineUpdateButton.removeClass('pulsating-button');
    });

    //elemDialog.
    btnSubmit.bind('click', function(event) {
      event.preventDefault();
      var redmineId = redmineObj.val();
      //console.log("adding time for redmine " + redmineId);
      var comment = redmineComment.val();

      var postData = {
        start: pendingEvent.start,
        end: pendingEvent.end,
        comment: comment,
        rid: redmineId,
        uid: pendingEvent.extendedProps.uid,
      }

      pendingEvent.setProp('title', redmineId);
      pendingEvent.setProp('color', '#EA7D73');
      $.post('/api/redmine/add', postData, function(data, status, xhr) {
        var newEntry = data;
        calendar.addEvent(newEntry);
      })
      .fail(function() {
        alert('Impossible de créer l\'entrées');
      })
      .always(function() {
        updateRedmine()
      })
      ;

      pendingEvent = undefined;
      redmineObjCleanup();
    });

    btnHideExchangeEvent.bind('click', function(event) {
      event.preventDefault();
      var postData = {
        start: pendingEvent.start,
        uid: pendingEvent.extendedProps.uid,
      };
      //console.log(postData);
      $.post('/api/exchange/event-hide', postData, function(data, status, xhr) {
        pendingEvent.extendedProps.original.remove();
        elemDialog.dialog('close');
      });
    });

    btnCancel = $(elemDialog.find("#timeentryCancel")[0]);
    btnCancel.bind('click', function(event) {
      event.preventDefault();
      redmineObjCleanup();
    });

    redmineObj.autocomplete({
      appendTo: "#createNew",
      source: '/api/redmine/autocomplete',
      minLength: 0,
      select: function(event, ui) {
        redmineObj.val("");
        //console.log('setting');
        redmineObj.val(ui.item.rid);
        redmineText.text(ui.item.label);
        //console.log('set', $("#idRedmine").val());

        //event = {
        //  start:
        //};
        //calendarEl.addEvent(event);

        // activer le bouton que si on a un ticket redmine
        $("#timeentryAdd").removeAttr('disabled');
        return false;
      },
      focus: function(event, ui) {
        if(!ui.item.rid)
        {
          return false;
        }
        redmineObj.val(ui.item.rid);
        redmineText.text(ui.item.label);
        //realRedmine.val(ui.item.rid);
      },
      close(event, ui) {
        if(redmineObj.val() != '')
        {
          return;
        }
        redmineText.html("");
      },
      open: function () {
          $('.ui-autocomplete.ui-front').css('z-index', elemDialog.css('z-index') + 1);
      },
      response: function(event, ui)
      {
        var nbOfElement = ui.content.length;
        if(0 == nbOfElement)
        {
          var notFoundElement = {
            rid: '',
            label: 'Aucun redmine ? Essayez le bouton "Mes redmines" pour forcer une mise à jour des redmines !',
            value: '',
          };
          ui.content.push(notFoundElement);
          redmineUpdateButton.addClass('pulsating-button');
        }
      }
    });

    var customButtonsUpdate = {};
    var customButtonsToggle = {};
    var updateButtons = [];
    var toggleButtons = [];
    var otherButtons = [];
    for(var key in plugins)
    {
      var plugin = plugins[key];
      var updateKey = 'update_' + key;
      var toggleKey = 'toggle_' + key;
      plugins[key].updateCallback = function(el) {
        if(!el)
        {
          console.log("update callback called without clicked element !");
          return;
        }
        console.log('got el', el.target.className);
        var k = el.target.className.match(/fc-update_([^ ]+)-button/);
        console.log('found k', k);
        if(2 != k.length)
        {
          return;
        }
        k = k[1];
        timeouts[k] && clearTimeout(timeouts[k]);
        displayDate(calendar, k, true);
      };
      plugins[key].toggleCallback = function(el) {
        var k = el.target.className.match(/fc-toggle_([^ ]+)-button/);
        if(2 != k.length)
        {
          return;
        }
        k = k[1];
        toggleElement(k, el.target);
      };

      customButtonsUpdate[updateKey] = {
        text: "↻ " + plugin.name,
        click: plugins[key].updateCallback,
      };
      customButtonsToggle[toggleKey] = {
        text: "Toggle " + plugin.name,
        click: plugins[key].toggleCallback,
      };
      
      updateButtons.push(updateKey);
      toggleButtons.push(toggleKey);
    };
    
    var header = {
      left: ['prev,next today'], // + updateButtons.join(',') + ' ' + toggleButtons.join(','), // myRedmines',
      center: 'title',
      right: ['timeGridWeek,timeGridDay'], // openBurgerMenu'], // gotoMetabase gotoGitlab'
    }

    header.left.push(updateButtons.join(','));
    header.left.push(toggleButtons.join(','));
    
    var actionsUserCustomButtons = {};
    for(var key in options.actionsCustomButtons)
    {
      console.log("adding custom action button ", key);
      actionsUserCustomButtons[key] = options.actionsCustomButtons[key];
      header.left.push(key);
    }
    
    var otherUserCustomButtons = {};
    for(var key in options.otherCustomButtons)
    {
      console.log("adding custom button ", key);
      otherUserCustomButtons[key] = options.otherCustomButtons[key];
      header.right.push(key);
    }
    
    var customButtonBurger = {
      openBurgerMenu: {
        text: "☰",
        click: openBurgerMenu,
      }
    }
    header.right.push("openBurgerMenu");
    header.right = header.right.join(' ');
    
    header.left = header.left.join(' ');
    
    console.log('header.right', header.right);
    
    var customButtons = { ...customButtonsUpdate, ...customButtonsToggle, ...actionsUserCustomButtons, ...otherUserCustomButtons, ...customButtonBurger};
    /*customButtons = {
      updateOtrs: {
        text: "↻ OTRS",
        click: updateOtrs,
      },
      updateRedmine: {
        text: "↻ Redmine",
        click: updateRedmine,
      },
      updateExchange: {
        text: "↻ Exchange",
        click: updateExchange,
      },
      updateGitlab: {
        text: "↻ Gitlab",
        click: updateGitlab,
      },
      toggleOtrs: {
        text: "Toggle OTRS",
        click: toggleOtrs,
      },
      toggleRedmine: {
        text: "Toggle Redmine",
        click: toggleRedmine,
      },
      toggleExchange: {
        text: "Toggle Exchange",
        click: toggleExchange,
      },
      toggleGitlab: {
        text: "Toggle Gitlab",
        click: toggleGitlab,
      },
      myRedmines: {
        text: "Mes redmines",
        click: updateMyRedmines,
      },
      gotoGitlab: {
        text: 'Gitlab',
        click: gotoGitlab,
      },
      gotoMetabase: {
        text: 'Metabase',
        click: gotoMetabase,
      },
      openBurgerMenu: {
        text: "☰",
        click: openBurgerMenu,
      },
    };*/
    //customButtons = customButtonsUpdate;
    console.log(customButtons);

    calendarOptions = {
      themeSystem: 'bootstrap',
      locale: 'fr',
      defaultView: 'timeGridWeek',
      // duree minimale d'une tache
      slotDuration: '00:15:00',

      // display business hours
      businessHours: [
        {
          daysOfWeek: [1, 2, 3, 4],
          startTime: configuration.businessHourStart,
          //endTime: '18:30',
          endTime: configuration.businessHourEnd,
        },
        {
          daysOfWeek: [5],
          startTime: configuration.businessHourStart,
          //endTime: '18:30',
          endTime: configuration.businessHourEndFri,
        }
      ],
      plugins: [
        'dayGrid',
        'timeGrid',
        'list',
        'interaction',
        //'resourceDayGrid',
        'bootstrap',
      ],
      height: 'parent',
      // commence le lundi
      firstDay: 1,
      //minTime: '07:00:00',
      //minTime: '00:00:00',
      //maxTime: '24:00:00',
      //maxTime: '19:00:00',
      // affichage des numeros de la semaine
      weekNumbers: true,
      //navLinks: true,
      selectable: true,
      select: createNewEvent,
      // barre rouge indiquant le jour/heure courant
      nowIndicator: true,
      weekends: configuration.showWeekend,
      //events: events,
      eventClick: function(info) {
        //console.log(info.event);
        if(info.event.extendedProps.type == 'exchange')
        {
          showPopupToConvertToRedmine(info.event);
        }
        info.jsEvent.preventDefault();
        if((info.event.extendedProps.type == 'redmine' || info.event.extendedProps.type == 'otrs') && info.event.url)
        {
          window.open(info.event.url);
        }
      },
      datesRender: displayDate,
      rerenderDelay: 100,
      customButtons: customButtons,
      header: header,
      eventRender: function(info) {
        var targetStatus = configuration['visibility_' + info.event.extendedProps.type];
        //console.log('status must be ', targetStatus, '#visility-' + info.event.extendedProps.type);
        return targetStatus == 'visible';
      },
      //eventDurationEditable: true,
      //eventResourceEditable: true,
      editable: true,
      eventResize: onEventResizeOrDrop,
      eventDrop: onEventResizeOrDrop,
    };

    var urlParams = new URL(window.location);
    var initialDate = urlParams.search.replace('?', '');
    if(initialDate)
    {
      //console.log('loading custom date', initialDate);
      calendarOptions.defaultDate = initialDate;
    }
    if(configuration.showOnlyBusinessHour)
    {
      calendarOptions.minTime = calendarOptions.businessHours[0].startTime;
      calendarOptions.maxTime = calendarOptions.businessHours[0].endTime;
    }

    var calendarEl = document.getElementById('calendar');
    calendar = new FullCalendar.Calendar(calendarEl, calendarOptions);
    //var calendar = $('#calendar').fullCalendar(calendarOptions);

    btnConfigurationSave.bind('click', function()
    {
      var oldTheme = configuration.theme;
      //localStorage.setItem("colorOtrs",             configuration.colorOtrs = $("#idColorOtrs").val());
      //localStorage.setItem("colorRedmine",          configuration.colorRedmine = $("#idColorRedmine").val());
      //localStorage.setItem("colorExchange",         configuration.colorExchange = $("#idColorExchange").val());
      //localStorage.setItem("colorGitlab",           configuration.colorGitlab = $("#idColorGitlab").val());
      localStorage.setItem("showWeekend",           configuration.showWeekend = $("#showWeekend").prop('checked'));
      localStorage.setItem("businessHourStart",     configuration.businessHourStart = $("#businessHourStart").val());
      localStorage.setItem("businessHourEnd",       configuration.businessHourEnd = $("#businessHourEnd").val());
      localStorage.setItem("businessHourEndFri",    configuration.businessHourEndFri = $("#businessHourEndFri").val());
      localStorage.setItem("showOnlyBusinessHour",  configuration.showOnlyBusinessHour = $("#idShowOnlyBusinessHour").prop('checked'));
      localStorage.setItem("showTooltips",          configuration.showTooltips = $("#showTooltips").prop('checked'));
      localStorage.setItem("showMaskedEvents",      configuration.showMaskedEvents = $("#showMaskedEvents").prop('checked'));
      localStorage.setItem("theme",                 configuration.theme = $("#themeName").children('option:selected').val());
      for(key in plugins)
      {
        localStorage.setItem("color_" + key, configuration['color_' + key] = $("#idColor_" + key).val());
      }

      calendar.setOption('businessHours', [
        {
          daysOfWeek: [1, 2, 3, 4],
          startTime: configuration.businessHourStart,
          endTime:   configuration.businessHourEnd,
        },
        {
          daysOfWeek: [5],
          startTime: configuration.businessHourStart,
          endTime:   configuration.businessHourEndFri,
        }
      ]);

      calendar.setOption('weekends', configuration.showWeekend);
      if(configuration.showOnlyBusinessHour)
      {
        calendar.setOption('minTime', calendarOptions.businessHours[0].startTime);
        calendar.setOption('maxTime', calendarOptions.businessHours[0].endTime);
      }
      else
      {
        calendar.setOption('minTime', "00:00");
        calendar.setOption('maxTime', "24:00");
      }

      if(configuration.theme != oldTheme)
      {
        setCustomTheme();
      }

      configurationMenu.dialog('close');
    });
    setThemeInConfiguration();
    setCustomTheme();

    $("#IE").remove();

  }

  function run()
  {
    calendar.render();
  }

  function finalize()
  {
    redmineUpdateButton = $($('.fc-myRedmines-button')[0]);
    redmineUpdateButton.data('default-text', redmineUpdateButton.text());

    updateAssignedRedmines();

    if(configuration.showTooltips)
    {
      redmineUpdateButton.attr('title', 'Mise à jour des tickets en « assigné » ou en « watcher ». Ces tickets sont proposé lors de la création d\'une imputation de temps').tooltip()

      /**
       * since it's not possible to specify other button texts, sets them here ...
       */
      $($('.fc-updateOtrs-button')[0]).attr('title', 'Mise à jour des tickets OTRS depuis metabase. Une mise à jour est faite automatiquement toutes les 10 minutes.').tooltip();
      $($('.fc-updateRedmine-button')[0]).attr('title', 'Mise à jour des tickets Redmine depuis l\'api redmine. Une mise à jour est faite automatiquement toutes les 10 minutes.').tooltip();
      $($('.fc-updateExchange-button')[0]).attr('title', 'Mise à jour du calendrier Exchange depuis l\'OWA. Une mise à jour est faite automatiquement toutes les 10 minutes.').tooltip();
      $($('.fc-updateGitlab-button')[0]).attr('title', 'Mise à jour des imputation de temps dans les issues Gitlab depuis metabase. Une mise à jour est faite automatiquement toutes les 10 minutes.').tooltip();

      $($('.fc-toggleOtrs-button')[0]).attr('title', 'Cacher/Afficher les événements OTRS').tooltip();
      $($('.fc-toggleRedmine-button')[0]).attr('title', 'Cacher/Afficher les événements Redmine').tooltip();
      $($('.fc-toggleExchange-button')[0]).attr('title', 'Cacher/Afficher les événements du calendrier Exchange (OWA)').tooltip();
      $($('.fc-toggleGitlab-button')[0]).attr('title', 'Cacher/Afficher les événements Gitlab').tooltip();
      $($('.fc-toggleOtrs-button')[0]).attr('title', 'Cacher/Afficher les événements OTRS').tooltip();

      $($('.fc-timeGridWeek-button')[0]).attr('title', 'Passer à la vue hebdomadaire.').tooltip();
      $($('.fc-timeGridDay-button')[0]).attr('title', 'Passer à la vue journalière.').tooltip();

      $($('.fc-gotoMetabase-button')[0]).attr('title', 'Aller au tableau métabase (dans un nouvel onglet).').tooltip();
      $($('.fc-gotoGitlab-button')[0]).attr('title', 'Aller sur le projet gitlab (dans un nouvel onglet).').tooltip();
      $($('.fc-openBurgerMenu-button')[0]).attr('title', 'Configuration de l\'application.').tooltip();
      $($('.fc-today-button')[0]).attr('title', 'Revenir au jour/à la semaine en cours.').tooltip();
      $($('.fc-prev-button')[0]).attr('title', 'Passer à la semaine précédente / au jour précédent.').tooltip();
      $($('.fc-next-button')[0]).attr('title', 'Passer à la semaine suivante / au jour suivant.').tooltip();
    }

    /**
     * on load, set button toggle to the user configuration state
     */
    $('button[class^=fc-toggle]').each(function(index) {
      //var className = this.className.split(' ')[0];
      var sourceType = this.className.match(/fc-toggle_([^ ]+)-button/)[1];
      updateButtonStatus(sourceType, this);
      //console.log(this);
    });
  } // end run

  function setThemeInConfiguration()
  {
    for(var key in allowedThemes)
    {
      var option = document.createElement('option');
      option.text = allowedThemes[key]['name'];
      option.value = key;
      if(key == configuration.theme)
      {
        option.selected = "selected";
      }
      themeSelector.add(option);
    }
  }

  function setCustomTheme()
  {
    var themeInfos = allowedThemes[configuration.theme];
    if(!themeInfos)
    {
      return;
    }
    $('link[data-theme="theme"]').attr('integrity', themeInfos.integrity).attr('href', themeInfos.url);
  }

  function formatNumber(integer)
  {
    return (integer > 9) ? integer : '0' + integer;
  }

  function createNewEvent(info)
  {
    var hourStart = formatNumber(info.start.getHours()) + ":" + formatNumber(info.start.getMinutes());
    var hourEnd   = formatNumber(info.end.getHours()) + ":" + formatNumber(info.end.getMinutes());

    var dt = elemDialog.find('#datetime').text("De " + hourStart + " -> " + hourEnd);
    elemDialog.dialog('open');

    pendingEvent = {
      start: info.start,
      end: info.end,
      color: '#ECC2BE',
      title: info.title,
      editable: false,
    }
    // when converting exchange to redmine, add exchange uid
    if(info.extendedProps && info.extendedProps.type == 'exchange' && info.extendedProps.uid)
    {
      pendingEvent.extendedProps = {
        uid: info.extendedProps.uid,
        original: info,
      };

      var matches = info.title.match(/#([0-9]{5})/);
      if(matches != null)
      {
        redmineObj.val(matches[1]).autocomplete('search', matches[1]);
      }
    }
    pendingEvent = calendar.addEvent(pendingEvent);
  }

  function redmineObjCleanup()
  {
    elemDialog.find("#datetime").text("");
    //redmineId = redmineObj.val();
    redmineObj.val("");
    elemDialog.dialog("close");
    redmineComment.val("");
    redmineText.html("");
  }

  function showPopupToConvertToRedmine(event)
  {
    //console.log('converting', event);
    timeouts.redmine && clearTimeout(timeouts.redmine);
    redmineComment.val(event.title);
    createNewEvent(event);
  }

  function cleanupOldEvents(info, source)
  {
    $.each(calendar.getEvents(), function(k, v) {
      if(v.extendedProps.type == source)
      {
        v.remove();
      }
    })
  }

  function displayDate(info, sourceToUpdate = 'all', force = false)
  {
    //console.log('callign displayDate for', sourceToUpdate);
    var activeDateIso = info.view.activeStart.toISOString();
    //console.log('checking date', activeDateIso, loadedDates[activeDateIso]);
    var currentState = {
      date: info.view.activeStart.toISOString(),
    }
    history.pushState(currentState, activeDateIso, '/?' + activeDateIso)
    //console.log('trying to force reload of times', sources, force, activeDateIso)
    var sources = [];
    if('all' == sourceToUpdate)
    {
      for(var key in plugins)
      {
        sources.push(key);
      }
    }
    else
    {
      sources = [sourceToUpdate]
    }
    for(var i in sources)
    {
      var source = sources[i];
      cleanupOldEvents(info, source);
      //console.log(info.view.activeStart, info.view.activeEnd);
      var dates = '&start=' + info.view.activeStart.toISOString() + '&end=' + info.view.activeEnd.toISOString();
      if(force)
      {
        dates += '&force=true';
      }
      //console.log('looking for ' + '.fc-update_' + source + '-button');
      var clickedButton = $($('.fc-update_' + source + '-button')[0]);
      clickedButton.attr('disabled', 'disabled');
      var url = '/api/update?type=' + source + dates;
      $.ajax({url: url, dataType: 'json', tksource: source, success: function(data) {
        //console.log('received infos for ' + this.tksource);
        var tksource = this.tksource;
        $.each(data, function(k, v) {
          v.durationEditable = v.resourceEditable = v.editable = (v.rid != '');
          v.color = configuration['color_' + tksource]; // fixme
          //console.log('setting color for ' + tksource + ' to ' + v.color);
          calendar.addEvent(v);
          //console.log('adding to calendar');
        });
        timeouts[tksource] = setTimeout(plugins[tksource].updateCallback, 1000 * configuration.refresh);
      }})
      .fail(function() {
        alert('Impossible de mettre à jour depuis ' + this.tksource);
      })
      .always(function() {
        $($('.fc-update_' + this.tksource + '-button')[0]).removeAttr('disabled');
      })
      ;
    }
    //console.log('test', sources == 'all' || sources == 'otrs')
    //if(sources == 'all' || sources == 'redmine')
    //{
    //  var btnUpdateRedmine = $($('.fc-updateRedmine-button')[0]);
    //  btnUpdateRedmine.attr('disabled', 'disabled');
    //
    //  var urlRedmine = '/api/update?type=redmine' + dates;
    //  $.getJSON(urlRedmine, function(data) {
    //    //console.log(data);
    //    $.each(data, function(k, v) {
    //      v.durationEditable = v.resourceEditable = v.editable = (v.rid != '');
    //      v.color = configuration.colorRedmine;
    //      calendar.addEvent(v);
    //      //console.log('adding to calendar');
    //    });
    //    timeouts.redmine = setTimeout(updateRedmine, 1000 * configuration.refresh);
    //  })
    //  .fail(function() {
    //    alert('Impossible de mettre à jour depuis redmine');
    //  })
    //  .always(function() {
    //    btnUpdateRedmine.removeAttr('disabled');
    //  })
    //  ;
    //}
    //if(sources == 'all' || sources == 'otrs')
    //{
    //  var btnUpdateOtrs = $($('.fc-updateOtrs-button')[0]);
    //  btnUpdateOtrs.attr('disabled', 'disabled');
    //
    //  var urlOtrs = '/api/update?type=otrs' + dates;
    //  $.getJSON(urlOtrs, function(data) {
    //    //console.log('calling otrs', data);
    //    $.each(data, function(k, v) {
    //      v.durationEditable = false;
    //      v.resourceEditable = false;
    //      v.editable = false;
    //      v.color = configuration.colorOtrs;
    //      calendar.addEvent(v);
    //    });
    //    timeouts.otrs = setTimeout(updateOtrs, 1000 * configuration.refresh);
    //  })
    //  .fail(function() {
    //    alert('Impossible de mettre à jour depuis otrs');
    //  })
    //  .always(function() {
    //    btnUpdateOtrs.removeAttr('disabled');
    //  })
    //  ;
    //}
    //if(sources == 'all' || sources == 'exchange')
    //{
    //  var btnUpdateExchange = $($('.fc-updateExchange-button')[0]);
    //  btnUpdateExchange.attr('disabled', 'disabled');
    //
    //  var urlExchange = '/api/update?type=exchange' + dates;
    //  if(configuration.showMaskedEvents)
    //  {
    //    urlExchange += "&showMasked=1";
    //  }
    //  $.getJSON(urlExchange, function(data) {
    //    //console.log(data);
    //    $.each(data, function(k, v) {
    //      v.durationEditable = false;
    //      v.resourceEditable = false;
    //      v.editable = false;
    //      v.color = configuration.colorExchange;
    //      calendar.addEvent(v);
    //    });
    //    timeouts.exchange = setTimeout(updateExchange, 1000 * configuration.refresh);
    //  })
    //  .fail(function() {
    //    alert('Impossible de mettre à jour depuis exchange');
    //  })
    //  .always(function() {
    //    btnUpdateExchange.removeAttr('disabled');
    //  })
    //  ;
    //}
    //if(sources == 'all' || sources == 'gitlab')
    //{
    //  var btnUpdateGitlab = $($('.fc-updateGitlab-button')[0]);
    //  btnUpdateGitlab.attr('disabled', 'disabled');
    //  var urlGitlab = '/api/update?type=gitlab' + dates;
    //  $.getJSON(urlGitlab, function(data) {
    //    //console.log(data);
    //    $.each(data, function(k, v) {
    //      v.durationEditable = false;
    //      v.resourceEditable = false;
    //      v.editable = false;
    //      v.color = configuration.colorGitlab;
    //      calendar.addEvent(v);
    //    });
    //    timeouts.gitlab = setTimeout(updateGitlab, 1000 * configuration.refresh);
    //  })
    //  .fail(function() {
    //    alert('Impossible de mettre à jour depuis gitlab');
    //  })
    //  .always(function() {
    //    btnUpdateGitlab.removeAttr('disabled');
    //  })
    //  ;
    //}
  }

  function toggleElement(sourceType, button)
  {
    var key = 'visibility_' + sourceType;
    var currentStatus = configuration[key];
    var newStatus = currentStatus == 'hidden' ? 'visible' : 'hidden';
    var newDecoration = newStatus == 'visible' ? 'none' : 'line-through';

    configuration[key] = newStatus;
    localStorage.setItem(key, newStatus);
    //console.log(calendar, calendarEl)
    updateButtonStatus(sourceType, button);
    calendar.rerenderEvents();
  }

  function updateButtonStatus(sourceType, button)
  {
    var key = 'visibility_' + sourceType;
    var newStatus = localStorage.getItem(key);
    if(null === newStatus)
    {
      newStatus = 'visible';
    }
    var newDecoration = newStatus == 'visible' ? 'none' : 'line-through';
    $(button).css("text-decoration", newDecoration);
  };

  function updateMyRedmines()
  {
    timeouts.assigne && clearTimeout(timeouts.assigne);
    $.getJSON('/api/redmine/assign', function(i) {
      redmineUpdateButton.text(redmineUpdateButton.data('default-text') + ' (' + i.count + ')');
    })
    .fail(function() {
      alert('Impossible de mettre a jour le nombre d\'issue redmine');
    })
    .always(function() {
      timeouts.assigne = setTimeout(updateMyRedmines, 1000 * configuration.refresh);
    })
    ;
  };

  function onEventResizeOrDrop(info)
  {
    if(plugins[info.event.extendedProps.type].resizable == false)
    {
      return false;
    }
    //console.log('updating time entry', info.event.extendedProps.teid);

    var postData = {
      start: info.event.start,
      end: info.event.end,
      rid: info.event.extendedProps.rid,
      teid: info.event.extendedProps.teid,
      comment: info.event.extendedProps.comment,
    };
    $.post('/api/' + info.event.extendedProps.type + '/timeentry-update', postData, function(data, status, xhr) {
      // todo
    })
    .fail(function() {
      alert('Impossible de mettre a jour l\'entrée');
    })
    ;
  };

  function openBurgerMenu()
  {
    configurationMenu.dialog('open');
  };

  //document.addEventListener('DOMContentLoaded', function() {

  function updateAssignedRedmines() {
    $.getJSON('/api/redmine/assigned', function(issues) {
      if(0 == issues.count)
      {
        updateMyRedmines();
        return;
      }
      redmineUpdateButton.text(redmineUpdateButton.data('default-text') + ' (' + issues.count + ')');
      //console && console.log('loaded ', issues.count, 'issues for this user');
    })
    .fail(function() {
      alert('Impossible de mettre à jour depuis redmine');
    })
    .always(function() {
      setTimeout(updateAssignedRedmines, 1000 * configuration.refresh);
    });
    ;
  };

  TimeKeeper = {
    initialize: initialize,
    run: run,
    finalize: finalize,
    formatNumber: formatNumber
  };

  return TimeKeeper;
})));
