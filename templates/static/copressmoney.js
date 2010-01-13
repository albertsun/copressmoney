/*
The Sheet object holds all functions and variables needed by the Ledger table
*/
Sheet = new Object();

/*
  POST a line to the server from a specified form. Server should return a ledger line in <tr> tags.
  url: address to POST to
  suffix: form fields are named id_(field)_(suffix). This makes sure values from the right form get sent when multiple are open for editing
  callback: function(data) { } determining what to do with the returned data and doing cleanup
*/
Sheet.POSTLine = function(url, suffix, callback) {
  
  var relatedvalues = new Array();
  if ($("#id_related_"+suffix).val() != '') {
    relatedvalues = $("#id_related_"+suffix).val().split(',');
  }
  console.log(relatedvalues);

  //construct a post query and submit it to /api/add/line/
  $.post(url, { date: $("#id_date_"+suffix).val(),
	title: $("#id_title_"+suffix).val(),
	client: $("#id_client_"+suffix).val(),
	description: $("#id_description_"+suffix).val(),
	documentation: $("#id_documentation_"+suffix).val(),
	category: $("#id_category_"+suffix).val(),
	revenue: $("#id_revenue_"+suffix).val(),
	expenses: $("#id_expenses_"+suffix).val(),
	cash: $("#id_cash_"+suffix).val(),
	unearned: $("#id_unearned_"+suffix).val(),
	prepaid: $("#id_prepaid_"+suffix).val(),
	acctsreceivable: $("#id_acctsreceivable_"+suffix).val(),
	acctspayable: $("#id_acctspayable_"+suffix).val(),
	related: relatedvalues,
	},
    callback,
    "html");
}

Sheet.bindCloseLink = function(formclass, callback) {
  $("."+formclass).find(".closelink").bind("click", function() {
      //closes the addline or editline form
      $("#cancellink").trigger('click');
      $("."+formclass).remove();
      if (callback) { callback(); }
    });
}

/*
  Handles when the 'add line' button is clicked. Creates a form for submitting new ledger lines
 */
Sheet.addLineClick = function() {
  $.get("/api/add/line/", function(data) {
      $("#addlink").unbind("click").removeClass("navlink");
      $(data).prependTo("#ledger");
      Sheet.bindCloseLink("addlineform", function() { $("#addlink").bind("click",Sheet.addLineClick).addClass("navlink"); });

      $("#addlineSubmitButton").bind("click", function() {
	  $("#donelink").trigger('click');

	  Sheet.POSTLine("/api/add/line/", "add", function(data) {
	      /*callback upon completion of POST adds new line to ledger and removes submission form*/
	      $(data).prependTo("#ledger tbody");

	      /*replace this with a call to the close link's trigger
	       $(closelink).triggerHandler("click");
	      */
	      $(".addlineform").remove();
	      $("#addlink").bind("click",Sheet.addLineClick).addClass("navlink");
	      Sheet.summarize();
	    });
	    }); //end submitButton 'click' event handler.
      
      //activate the select lines button
      $("#selectrelatedbutton-add .selectrelatedlink").bind('click', function() {
	  Sheet.startSelectLines();
	});
    }); //end $.get, adding line
} //end addLineClick

Sheet.editLine = function(trline) {
  /*Queries server for form data to make a line of the ledger editable.

    trline is the jQuery object of the whole <tr>
  */
  var id_s = trline.attr("id")
  var id = id_s.substr(id_s.indexOf('-')+1,id_s.length);
  
  $.get("/api/edit/line/"+id+"/", function(data) {
      $(data).insertAfter("#"+id_s);
      
      Sheet.bindCloseLink("editlineform-"+String(id), function() {
	  $("#line-"+String(id)).fadeIn();
        });
      
      $("#editSubmitButton-"+id).bind("click", function() {
	  $("#donelink").trigger('click');

	  Sheet.POSTLine("/api/edit/line/"+id+"/", id, function(data) {
	      /*On completion of the POST, replaces the previous <tr> with a new <tr> returned from the server.
		Then binds an event handler onto the edit link for that new <tr>
		Then activates the event handler on the 'close' button to close the edit form
	      */
	      trline.replaceWith(data);
	      Sheet.makeEditHoverable($("#line-"+id+" .lineid"));
	      $(".editlineform-"+id).find(".closelink").triggerHandler("click");
	      Sheet.summarize();
	    });
	}); //end submitButton 'click' event handler
      
      trline.hide();
      /*Add a delete button to the editingline*/
      var deleteLinkTd = $(".formheading.editlineform-"+id+" td:first").append($("<span><small><em>delete row</em></small></span>").addClass("navlink deletelink"));
      //console.log(deleteLinkTd);
      $(deleteLinkTd).find(".deletelink").one("click", function() {
	  $.get("/api/delete/line/"+id+"/", function(data) { 
	      //TODO. delete line from DOM. untested.
	      $("#line-"+id).remove();
	      $(".formheading.editlineform-"+id+" .closelink").trigger('click');
	    },
	    "json");
	});

      //activate the select lines button
      $("#selectrelatedbutton-"+id+" .selectrelatedlink").bind('click', function() {
	  Sheet.startSelectLines(id);
	});

    }); //end $.get of edit form line
} //end Sheet.editLine
/*
  handles edit links in each lineid box
 */
Sheet.showEditLink = function(thislink) {
  //smacks head. these can be done in CSS
  //$(thislink).find(".editlink").css("visibility","visible");
  //$(thislink).addClass("lineid-editactive");
  $(thislink).one("click", function() {
      /*onclick, activate the whole line for editing*/
      Sheet.editLine($(thislink).parent());
    });
}
Sheet.hideEditLink = function(thislink) {
  //$(thislink).find(".editlink").css("visibility","hidden");
  //$(thislink).removeClass("lineid-editactive");
  $(thislink).unbind("click");
}
Sheet.makeEditHoverable = function(jqobject) {
  jqobject.unbind();
  jqobject.hover(function() {
      Sheet.showEditLink(this);
    },
    function() {
      Sheet.hideEditLink(this);
    });
}


/*
  Summarizes the currently displayed ledger's values and writes them into a header row.
  Takes the <tr> row in which to write the values as an argument.
*/
Sheet.summarize = function(summaryrow) {
  if (!summaryrow) {
    //console.log("no provided summaryrow");
    var summaryrow = $("#live-summary");
  }
  var sumcol = function(class) {
    /*Takes a String that's a class name of a table column and sums its values*/
    var tot = new Number(0.0);
    $("tbody td.dollars."+class).each(function(i,node) {
      tot += new Number(Sheet.parseAccounting($(node).text()));
    });
    return tot;
  }
  /*do above for each of the accounts*/
  summaryrow.find(".revenue").text(Sheet.toAccounting(sumcol("revenue")));
  summaryrow.find(".expenses").text(Sheet.toAccounting(sumcol("expenses")));
  summaryrow.find(".cash").text(Sheet.toAccounting(sumcol("cash")));
  summaryrow.find(".unearned").text(Sheet.toAccounting(sumcol("unearned")));
  summaryrow.find(".prepaid").text(Sheet.toAccounting(sumcol("prepaid")));
  summaryrow.find(".acctsreceivable").text(Sheet.toAccounting(sumcol("acctsreceivable")));
  summaryrow.find(".acctspayable").text(Sheet.toAccounting(sumcol("acctspayable")));
  
  //$("tr#prior-summary").after(summaryrow);
  //OR
  //.replaceWith(summaryrow);

  //console.log(summaryrow);
}

/*Formats a Number as a string in accounting notation*/
Sheet.toAccounting = function(n) {
  if (n<0) {
    return "$"+n.toFixed(2).toString().replace(/-/g,'(')+")";
  } else {
    return "$"+n.toFixed(2).toString();
  }
}
/*Parses a String in accounting notation and returns a Number*/
Sheet.parseAccounting = function(s) {
  return new Number(s.replace(/\$|\)/g,'').replace(/\(/,'-'));
}


/* 
   Called when the user clicks on the buttons to 'select related lines' either while adding a new line or editing an existing line.
   Lets the user click on other lines in the ledger to set them as related.
*/
Sheet.startSelectLines = function(id) {

  var mouseOverLine = function() {
    //Adds a hover effect that highlights lines
    //it may be possible to do this with CSS instead of javascript
    $(this).css('background-color','#FF8952');
  }
  var mouseOutLine = function() {
    $(this).css('background-color','#FFFFFF');
  }

  //deactivate edit links
  $("tbody .lineid").unbind();

  var suffix = "";

  if (!id) {
    //no id passed, so we're working with .addlineform .selectrelatedbutton
    console.log("no id provided. selecting lines for adding a new line");    
    $(".closelink:not(.addlineform .closelink)").trigger('click');
    suffix = "add";
  } else {
    //console.log(id);
    //Collapse other editing dialogs
    console.log(".closelink:not(.editlineform-"+id+" .closelink)")
    $(".closelink:not(.editlineform-"+id+" .closelink)").trigger('click');
    suffix = id.toString();
  }

  $("#selectrelatedbutton-"+suffix).css('background-color','#CCEFFF');
  $("#selectrelatedbutton-"+suffix+" div").css('display','block');
  $("#selectrelatedbutton-"+suffix+" .selectrelatedlink").css('display','none'); //inline is default

  var clickSelect = function() {
    var id_s = $(this).attr("id");
    var id = id_s.substr(id_s.indexOf('-')+1,id_s.length);

    console.log("select "+id_s);
    
    //first time a line is clicked. selects it.
    $(this).css('background-color','#FF8952');
    $(this).unbind('mouseover').unbind('mouseout');
	  
    //Adds a hidden checkbox to the line to denote that it's selected	  
    $('<input type="checkbox" name="lineselected" value="'+id+'" checked="checked" />').css('display','none').appendTo($(this).find(".lineid"));
    $("#selected-count").text($(".ledgerline input:checkbox:checked").length.toString()+" selected");
  }
  var clickDeselect = function() {
    console.log('deselect '+$(this).attr("id"))
    //second time a line is clicked. deselects it.
    $(this).hover(mouseOverLine, mouseOutLine);
    $(this).css('background-color','#FFFFFF');
    
    //remove line from selected. deselect it
    $(this).find("input:checkbox").remove();
    $("#selected-count").text($(".ledgerline input:checkbox:checked").length.toString()+" selected");
  }
  
    /*Setup the lines of the ledger to be selected.
      When one is selected it gains a hidden checked checkbox <input> with its ID as the value.
    */
  $(".ledgerline").css({'cursor':'pointer','-webkit-user-select':'none','-moz-user-select':'none'}).hover(mouseOverLine, mouseOutLine).toggle(clickSelect, clickDeselect);

  /*Activate the cancel link*/
  $("#cancellink").bind('click', function() {
      //restores prior content
      console.log('canceling selection');
      $(".ledgerline input:checkbox:checked").parent().parent().trigger('click');
	
      $("#selectrelatedbutton-"+suffix).css('background-color','#FFFFFF');
      $("#selectrelatedbutton-"+suffix+" .selectrelatedlink").css('display','inline');
      $("#selectrelatedbutton-"+suffix+" div").css('display','none');
	
      Sheet.makeEditHoverable($("tbody .lineid"));
      $(".ledgerline").css({'cursor':'auto','-webkit-user-select':'text','-moz-user-select':'text','background-color':'#FFFFFF'}).unbind();
    });
  /*Activate the done link*/
  $("#donelink").bind('click', function() {
      //write the values of the checked boxes to the hidden input, and then trigger #cancellink click
      if ($(this).parent().parent().css('display') == 'block') {   
	var idvalues = $.map($(".ledgerline input:checkbox:checked"), function(el, i) {
	    return $(el).val().toString();
	  }).join(',');
	$("#id_related_"+suffix).val(idvalues);
	console.log('storing selected value '+idvalues);
	$("#cancellink").triggerHandler('click');
      }
    });

    /*Read the value of #id_related_(suffix) and sets those lines to start out selected*/
  if ($("#id_related_"+suffix).val() != '') {
    $.map($("#id_related_"+suffix).val().split(','), function(idstring, i) {
	if ($("#line-"+idstring).is(".ledgerline")) {
	  console.log("#line-"+idstring+" eists");
	  //the line exists in the ledger already, mark it as selected
	  $("#line-"+idstring).trigger('click');
	} else {
	  //get the line from the server, add it, and handlers to it, and select (click) it
	  console.log("asking server for #line-"+idstring);
	  $.get("/api/get/line/"+idstring+"/", function(data) {
	      var newLine = $(data);
	      newLine.appendTo("#ledger tbody").hover(mouseOverLine, mouseOutLine).toggle(clickSelect, clickDeselect);
	      newLine.trigger('click');
	    });
	}
	
      });
  }

} //end Sheet.startSelectLines();


$(document).ready(function() {
    /*
      Makes table sortable on each column header
      http://tablesorter.com/docs/
     */
    $("#ledger").tablesorter({ headers: { 3: {sorter:'text'}, 6: {sorter:'currency'}, 7: {sorter:'currency'}, 8: {sorter:'currency'}, 9: {sorter:'currency'}, 10: {sorter:'currency'}, 11: {sorter:'currency'}, 12: {sorter:'currency'}, 13: {sorter:'digit'} }, 'cancelSelection':false, 'debug':false });
    $("#ledger #summary th").unbind("click");

    /*
      Adds link to add new lines
    */
    $("#addlink").bind("click", Sheet.addLineClick);

    /*
      Adds links to each line to edit it.
      On mouse over each lineid table cell, the table cell is activated with an event binding so that when clicked, a GET request is made to the server for the form to edit that particular line of the ledger.
    */
    Sheet.makeEditHoverable($("tbody .lineid"));
    
    /*Create a new row, changes IDs and puts a javscript sum of each column in it*/
    
    Sheet.summarize($("tr#prior-summary").clone().attr('id','live-summary').find("th:first").attr('id','live-summary-head').text("Summary of Changes").parent().insertAfter("tr#prior-summary"));

  });

