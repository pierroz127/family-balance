function changeDate() {
    var selectMonth = document.getElementById('month');
    month = selectMonth.options[selectMonth.selectedIndex].value;
    var selectYear = document.getElementById('year');
    year = selectYear.options[selectYear.selectedIndex].value;
    window.location.href = '/comptes?mois=' + month + '&annee=' + year;
}

function remove(urlsafe, month, year) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette dépenses de vos comptes ?')) {
		window.location.href = '/supprimer?urlsafe=' + urlsafe + '&mois=' + month + '&annee=' + year;
    }
}

function initOnRemoveClick() {
    $('.remove').click(function(e) {
        var key = $(e.target).parent().parent().parent().find('.exp-key').html();
        var selectMonth = document.getElementById('month');
        month = selectMonth.options[selectMonth.selectedIndex].value;
        var selectYear = document.getElementById('year');
        year = selectYear.options[selectYear.selectedIndex].value;
        remove(key, month, year);
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
			var newtype = '<select name="type"><option value="1" ';
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
			editbutton.html('<input type="submit" value="Modifier">');
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
        var element = parent.find(".tax-ratio");
        var oldRatio = parent.find(".tax-ratio-title .tax-ratio-value");
        var oldRatioValue = oldRatio.text();
        element.html('<input name="taxratio" type="text" id="taxratio" value="' + oldRatioValue + '"/>').show();
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
                           year: $("#year").val()
                       },
                       dataType: "json",
                       success: function(data) {
                           parent.find(".tax-ratio-error").hide();
                           element.hide();
                           editButton.show();

                           $('span.tax-ratio-value').each(function() {
                              if ($(this).parent().siblings('.edit-tax-ratio').length != 0) {
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
	
	ie6 = ($.browser.msie && ($.browser.version == "6.0")) ? true : false;

	// CSS
	$("body").css("position", "relative");
	

	function PPNopen(url) {
		
		if(settings.onStart != null) {
			settings.onStart();
		}
		
		if(ie6 == true) {
			$("#PPNCSS").remove();
			$("body").append(''
				+	'<style type="text/css" id="PPNCSS">'
				+	'.popin-voile {top:expression(documentElement.scrollTop + body.scrollTop + "px")}'
				+	'.popin {top:expression(documentElement.scrollTop + body.scrollTop + (documentElement.clientHeight/2) - ' + (settings.height/2) + ' + "px")}'
				+	'</style>'
				+	'');
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
		if(ie6 == true) {
			$(".popin-voile")		.css("position",					"absolute")
									;
		}
		else {
			$(".popin-voile")		.css("top",							0)
									.css("position",					"fixed")
									;
		}
		
		// Patch IE6
		if(ie6 == true) {
			
			PPNhtmlScroll 			= document.getElementsByTagName("html")[0].scrollTop;
			var PPNbodyMargin 		= new Object();
			PPNbodyMargin.top 		= parseInt($("body").css("margin-top"));
			PPNbodyMargin.right 	= parseInt($("body").css("margin-right"));
			PPNbodyMargin.bottom 	= parseInt($("body").css("margin-bottom"));
			PPNbodyMargin.left 		= parseInt($("body").css("margin-left"));
			
			$("html, body").css("height", "100%");
			$("html, body").css("overflow", "hidden");
			$("body").height($("body").height());
			PPNbodyHeight = parseInt($("body").height());
			$("html, body").css("overflow", "visible");
			$("html, body").css("overflow-x", "visible");
			
			PPNbodyTop = ((PPNbodyMargin.top + PPNbodyMargin.bottom) < PPNhtmlScroll) ? (PPNbodyMargin.top + PPNbodyMargin.bottom - PPNhtmlScroll) : 0;
			$("body").css("top", PPNbodyTop );		
			$(".popin-voile").css("top", -(PPNbodyMargin.top + PPNbodyMargin.bottom - PPNhtmlScroll) );
			$(".popin-voile").css("left", (- PPNbodyMargin.left) );
			$(".popin-voile").css("width", $("html").width());
			
		} else {
			$("html, body").css("overflow", "hidden");
		}
	
		// Affichage du voile
		$(".popin-voile").animate({opacity:settings.opacity, height:((ie6 == true) ? (PPNbodyHeight + PPNbodyMargin.top + PPNbodyMargin.bottom) : "100%")}, function() {
		
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
					if(ie6 == true) {
						$(".popin")		.css("position",					"absolute")
										.css("margin-top",					0)
										;
					}
					else {
						$(".popin")		.css("position",					"fixed")
										.css("top",							"50%")
										.css("margin-top",					-(settings.height/2))
										;
					}		
					
					// Chargement du contenu
					$(".popin-content").html(m);
	
				},
				complete: function(){
					
					// Loader
					$(".popin-voile").css("background-image", "");
					
					// Affichage
					if(ie6 == true) {
						$(".popin").css("top", parseInt($(".popin").css("top")) - PPNbodyTop );
					}
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
				if(ie6 == true) {
					$("html, body").css("height", "auto");
					$("html, body").css("overflow", "auto");
					$("html, body").css("overflow-x", "hidden");
					$("body").css("top", 0);
					window.scrollTo(0, (PPNhtmlScroll) );
				} else {
					$("html, body").css("overflow", "auto");
				}
				$(".popin, .popin-voile").remove();
				
				if(settings.onExit != null) {
					settings.onExit();
				}	
			});
		});		
	}
};

