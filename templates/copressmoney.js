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
  $(thislink).find(".editlink").css("visibility","visible");
  $(thislink).addClass("lineid-editactive");
  $(thislink).one("click", function() {
      /*onclick, activate the whole line for editing*/
      Sheet.editLine($(thislink).parent(), thislink);
    });
}
Sheet.hideEditLink = function(thislink) {
  $(thislink).find(".editlink").css("visibility","hidden");
  $(thislink).removeClass("lineid-editactive");
  $(thislink).unbind("click");
}
Sheet.editLine = function(trline, thislink) {
  //trline.css("background-color","red");
  var id_s = trline.attr("id")
  var id = id_s.substr(id_s.indexOf('-')+1,id_s.length);
  //Sheet.inEdit = parseInt(id);
  $.get("/api/edit/line/"+id+"/", function(data) {
      $(data).insertBefore("#"+id_s);

      Sheet.bindCloseLink("editlineform-"+String(id), function() {
	  $("#line-"+String(id)).fadeIn();
        });

      $("#editSubmitButton-"+id).bind("click", function() {
	  Sheet.POSTLine("/api/edit/line/"+id+"/", id, function(data) {
	      trline.replaceWith(data);
	      Sheet.makeEditHoverable($("#line-"+id+" .lineid"));
	      /*
		modify trline in place, then
		replace this with a call to the close link's trigger
	       $(closelink).triggerHandler("click");
	      */
	      $(".editlineform-"+id).find(".closelink").triggerHandler("click");
	    });
	}); //end submitButton 'click' event handler
      
      trline.hide();
      
    });
  
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

$(document).ready(function() {
    /*
      Makes table sortable on each column header
      http://tablesorter.com/docs/
     */
    //$("#ledger").tablesorter({ headers: { 6: {sorter:'currency'}, 7: {sorter:'currency'}, 8: {sorter:'currency'}, 9: {sorter:'currency'}, 10: {sorter:'currency'}, 11: {sorter:'currency'}, 12: {sorter:'currency'}, 13: {sorter:'digit'} }, 'debug':true });

    /*
      Adds link to add new lines
    */
    $("#addlink").bind("click", Sheet.addLineClick);


    /*
      Adds links to each line to edit it.
      On mouse over each lineid table cell, the table cell is activated with an event binding so that when clicked, a GET request is made to the server for the form to edit that particular line of the ledger.
    */
    Sheet.makeEditHoverable($("tbody .lineid"));

  });

