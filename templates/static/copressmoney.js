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
	},
    callback,
    "html");
}


/*
  Handles the 'add' button 
 */
Sheet.addLineClick = function() {
  $("#addlink").unbind("click").removeClass("navlink");
  
  $.get("/api/add/line/", function(data) {
      
      $(data).prependTo("#ledger");
      Sheet.bindCloseLink("addlineform", function() { $("#addlink").bind("click",Sheet.addLineClick).addClass("navlink"); });

      $("#addlineSubmitButton").bind("click", function() {
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
	    }); //end submitButton 'click' event handler
    });
} //end addLineClick

Sheet.bindCloseLink = function(formclass, callback) {
  $("."+formclass).find(".closelink").bind("click", function() {
      //closes the add form
      $("."+formclass).remove();

      if (callback) { callback(); }
    });
}

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
      /*Add a delete button to trline*/
      var deleteLinkTd = $(".formheading.editlineform-"+id+" td:first").append($("<span><small><em>delete row</em></small></span>").addClass("navlink deletelink"));
      console.log(deleteLinkTd);
      $(deleteLinkTd).find(".deletelink").one("click", function() {
	  $.get("/api/delete/line/"+id+"/", function(data) { 
	      
	    },
	    "json");
	});
    }); //end $.get of edit form line
  
  //trline.find(".date");
}
Sheet.makeEditHoverable = function(jqobject) {
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
    console.log("no provided summaryrow");
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

  console.log(summaryrow);
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

$(document).ready(function() {
    /*
      Makes table sortable on each column header
      http://tablesorter.com/docs/
     */
    $("#ledger").tablesorter({ headers: { 3: {sorter:'text'}, 6: {sorter:'currency'}, 7: {sorter:'currency'}, 8: {sorter:'currency'}, 9: {sorter:'currency'}, 10: {sorter:'currency'}, 11: {sorter:'currency'}, 12: {sorter:'currency'}, 13: {sorter:'digit'} }, 'cancelSelection':false, 'debug':true });
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

