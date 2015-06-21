function changeDate() {
    var selectMonth = document.getElementById('month');
    month = selectMonth.options[selectMonth.selectedIndex].value;
    var selectYear = document.getElementById('year');
    year = selectYear.options[selectYear.selectedIndex].value;
    window.location.href = '/comptes?mois=' + month + '&annee=' + year;
}

function removeExpense(urlsafe, month, year, category, amount ) {
    if (confirm('Êtes-vous sûr de vouloir supprimer la dépense\n' + category + ' - ' + amount + ' EUR\nde vos comptes ?')) {
        window.location.href = '/supprimer?urlsafe=' + urlsafe + '&mois=' + month + '&annee=' + year;
    }
}

function initMonthRange() {
  var months = ["Janvier", "F&eacute;vrier", "Mars", "Avril", "Mai", "Juin", "Juillet", "Ao&ucirc;t", "Septembre", "Octobre", "Novembre", "D&eacute;cembre"];
  for (var i=1; i<13; i++) {
    $('#month_' + i).html(months[i-1]);
  }
  var selectedMonthName = months[parseInt($('#month').html()) - 1];
  //var oldValue = $('.selected-month').html();
  //var newValue = oldValue.replace("#SELECTED_MONTH#", selectedMonthName)
  $('span.selected-month').html(selectedMonthName);
}

function initOnRemoveClick() {
    $('.remove').click(function(e) {
        var row = $(e.target).parent().parent();
        var key = row.find('.exp-key').html();
        var name = row.find('.exp-category').children().first().html();
        var amount = row.find('.exp-amount').html();
        var selectMonth = $('#month');
        var month = parseInt(selectMonth.html());
        var year = parseInt($('#year').html());
        //year = selectYear.options[selectYear.selectedIndex].value;
        removeExpense(key, month, year, name, amount);
    });
}

function initTagEditor() {
	$('#tageditor').bind('keyup', function(e) {
		if (e.keyCode == 32) {
			var tageditor = $('#tageditor');
			var inputwidth = tageditor.width();
			var tag = tageditor.val().trim();
			var tagisvalid = tag.length > 0;
			tageditor.siblings('.tag').each(function() {
				if ($(this).text() == tag) {
					tagisvalid = false;
				}
			});
			if (!tagisvalid) {
				tageditor.val('');
				return;
			}
			
			tageditor.before('<span class="tag">'+tag+'<span class="delete-tag" title="remove this tag" /></span>');
			inputwidth -= (tageditor.prev().width() + 25);
			tageditor.val('');
			if (inputwidth > 50) {
				tageditor.width(inputwidth);
			}
			else {
				tageditor.width('100%');
			}
			
			/* now set the real value that will be send to the backend */
			var tags = $('#tags');
			var tagValues = tags.val();
			if (tagValues != '')
				tagValues += ';';
			tagValues += tag;
			tags.val(tagValues);
			bindDeleteTag();
			bindClickToChart();
		}
	});
}


function bindDeleteTag() {
	$('.delete-tag').click(function(e) {
		var tagcell = $(e.target).parent().parent();
		$(e.target).parent().remove();
		var existingTags = new Array();
		tagcell.children('.tag').each(function() {
			existingTags.push($(this).text());
		});
		tagcell.find("#tags").val(existingTags.join(';'));
	});
}

function initEditLink() {
    $(".edit").click(function(e) {
	var editrow = $(e.target).parent().parent();

	/* only one row modified at the same time */
	var edittable = editrow.parent().find('td img.edit').remove();
	
	if (editrow) { 
	    var editdate = editrow.find('td.exp-date');
	    if (editdate) { 
			var dt = editdate.html();
			editdate.html('<input name="date" type="text" id="date" value="' + dt + '"/>');
	    }
	    /* edit the key */
	    var editkey = editrow.find('td.exp-key');
	    if (editkey) {
			editkey.html('<input name="urlsafe" type="text" id="urlsafe" value="' + editkey.html() + '" />');
	    }

	    /* edit the category */
	    var editcategory = editrow.find('td.exp-category');
	    if (editcategory) { 
			var cat = editcategory.text();
			editcategory.html('<input name="category" type="text" id="category" value="' + cat + '"/>');
	    }
	    /* edit the amount */
	    var editamount = editrow.find('td.exp-amount');
	    if (editamount) { 
			var amount = editamount.text();
			editamount.html('<input name="amount" type="text" id="amount" value="' + amount + '"/>');
	    }
	    /* edit the type */
	    var edittype = editrow.find('td.exp-type');
	    if (edittype) { 
			var type = edittype.text().trim();
			var newtype = '<select class="form-control" name="type"><option value="1" ';
			if (type == 'Commun')
			    newtype = newtype + 'selected';
			newtype = newtype + '>Commun</option><option value="2" ';
			if (type == 'Avance')
			    newtype = newtype + 'selected';
			newtype = newtype + '>Avance</option><option value="3" ';
			if (type == 'Personnel')
			    newtype = newtype + 'selected';
			newtype = newtype + '>Personnel</option><option value="4" ';
            if (type == 'Impôts')
                newtype = newtype + 'selected';
            newtype = newtype + '>Impôts</option></select>';
			edittype.html(newtype);
	    }
	    
	    edittag(editrow.find('td.exp-tag'));
	    
	    /* button add */
	    var editbutton = editrow.find('td.exp-modify');
	    if (editbutton) { 
			editbutton.html('<button class="btn btn-primary btn-sm" type="submit">Modifier</button>');
	    } 
	}
	var newexp = $('#newexpense');
	if (newexp) {
	    newexp.remove();
	}    
    });
}

function edittag(tagcell) {
	var existingtags = new Array();
	inputwidth = tagcell.width()-15;
	tagcell.children('.tag').each(function() {
		$(this).append('<span class="delete-tag" title="remove this tag" />');
	});
	
	tagcell.children('.tag').each(function() {
		existingtags.push($(this).text());
		inputwidth -= ($(this).width() + 12);
	});
	if (inputwidth<50)
		inputwidth = tagcell.width()-15;
	
	tagcell.append('<input id="tageditor" style="width:'+inputwidth+'px;"></input>');
	tagcell.append('<input name="tags" type="text" id="tags" style="display:none;"></input>');
	tagcell.children().last().val(existingtags.join(';'));
	initTagEditor();
	bindDeleteTag();
}

function initEditTaxRatio() {
    $('.edit-tax-ratio').click(function(e) {
        var editButton = $(e.target);
        var parent = editButton.parent();
        var element = parent.next();
        //var oldRatio = parent.find(".tax-ratio-title .tax-ratio-value");
        var oldRatio = editButton.prev();
        var oldRatioValue = oldRatio.text();
        element.html('<input name="taxratio" class="form-control" type="text" id="taxratio" value="' + oldRatioValue + '"/>').show();
        oldRatio.hide();
        editButton.hide();
        $('#taxratio').bind('keyup', function(keyEvent) {
           if (keyEvent.keyCode == 13) // key code for 'Enter'
           {
               newRatio = element.find("#taxratio").val();
               if (checkRatio(newRatio)) {
                   $.ajax({
                       url: "/impots",
                       type: "post",
                       data: {
                           taxratio: newRatio,
                           year: parseInt($("#year").text())
                       },
                       dataType: "json",
                       success: function(data) {
                           parent.find(".tax-ratio-error").hide();
                           element.hide();
                           editButton.show();

                           $('span.tax-ratio-value').each(function() {
                              if ($(this).siblings('.edit-tax-ratio').length != 0) {
                                  // this is the ratio that needs to be updated with the value received from the server
                                  $(this).html(data.taxratio).show();
                              } else {
                                  // complementary value
                                  var x = 1.0 - parseFloat(data.taxratio);
                                  $(this).html(x).val();
                              }
                           });
                           var currentMonth = $("#month").val();
                           for (var i=0; i<data.newbalances.length; i++) {
                               var status = data.newbalances[i];
                               if (status.month == currentMonth) {
                                   $('#status-maxuser').html(status.maxuser);
                                   $('#status-minuser').html(status.minuser);
                                   $('#status-debt').html(status.debt);
                               }
                           }

                       },
                       error: function(err) {
                           window.alert("oups, we've got an error: " + err);
                       }
                    });
               }
               else {
                   parent.find(".tax-ratio-error").show();
               }

           }
        });
    });
}

checkRatio = function(ratio) {
    value = parseFloat(ratio);
    if (isNaN(value) || value > 1.0 || value < 0.0)
        return false;
    return true;
}


jQuery.fn.popin = function(o) { 	
	var settings = jQuery.extend({
		width : 250,
		height : 250,
		className: "",
		loaderImg: "",
		opacity: .5,
		onStart: null,
		onComplete: null,
		onExit: null
	}, o);
			
	// Action ouverture
	jQuery(this).each(function() {
		jQuery(this).click(function() {
			PPNopen($(this).attr("href"));
			return false;
		});
	});
	
	// Popin Ouverture
	var Loader = new Image();
	Loader.src = settings.loaderImg;
	
	// CSS
	$("body").css("position", "relative");
	

	function PPNopen(url) {
		
		if(settings.onStart != null) {
			settings.onStart();
		}
		
		// Insertion du voile & Verrouillage du scroll	
		$("body").prepend('<div class="popin-voile"></div>');
		
		// CSS du voile
		$(".popin-voile")	.css("opacity", 0)
							.css("left", 0)
							.css("z-index", "9000")
							.css("width", "100%")
							.css("height", 0)
							.css("background-color", "#000")
							.css("background-position", "center center")
							.css("background-repeat", "no-repeat")
							;
		
		$(".popin-voile").css("top", 0).css("position", "fixed");
		
		$("html, body").css("overflow", "hidden");
	
		// Affichage du voile
		$(".popin-voile").animate({opacity:settings.opacity, height: "100%"}, function() {
		
			// Loader
			$(".popin-voile").css("background-image", "url('"+settings.loaderImg+"')");
			
			// Insertion de la popin et animation
			$(".popin").css("height", $("body").height() );
							
			// Requête
			$.ajax({
				type: "GET",
				url: url,
				dataType: "html",
				success: function(m){
	
					// Création de la popin
					$("body").prepend('<div class="popin ' + settings.className + '"><div class="popin-content"></div></div>');
					
					// CSS du voile
					$(".popin")			.css("left",						"50%")
										.css("z-index",						"9500")
										.css("width",						settings.width)
										.css("height",						settings.height)
										.css("overflow",					"hidden")
										.css("margin-left",					-(settings.width/2))
										;
					$(".popin-content")	.css("overflow",					"auto")
										.css("height",							$(".popin").height()
																			- 	parseInt($(".popin").css("padding-top"))
																			- 	parseInt($(".popin").css("padding-bottom"))
																			)
										;
					$(".popin")		.css("position",					"fixed")
										.css("top",							"50%")
										.css("margin-top",					-(settings.height/2))
										;	
					
					// Chargement du contenu
					$(".popin-content").html(m);
	
				},
				complete: function(){
					
					// Loader
					$(".popin-voile").css("background-image", "");
					
					// Affichage
					$(".popin").fadeIn("slow", function() {
						if(settings.onComplete != null) {
							settings.onComplete();
						}
					});
					
					// Action fermeture
					$(".popin-close, .popin-voile").click(function() {
						PPNclose();
						return false;
					});
				}
			});	
		});
			
		$("html").keydown(function(e){
			if(e.keyCode == '27') {
				PPNclose();
			}
		});	
	}
	
	// Popin fermeture
	function PPNclose() {
	
		$("html").unbind("keydown");
		
		$(".popin").fadeOut("slow", function() {
		
			$(".popin-voile").animate({opacity:0, height:0}, function() {
			
				// Suppression du voile & Déverrouillage du scroll	
				$("html, body").css("overflow", "auto");
				$(".popin, .popin-voile").remove();
				
				if(settings.onExit != null) {
					settings.onExit();
				}	
			});
		});		
	}
};

