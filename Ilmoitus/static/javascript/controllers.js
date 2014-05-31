var baseurl = 'http://127.0.0.1:8080';
var userData;
var pricePattern = /^[0-9]{1}[0-9]{0,3}(\.[0-9]{2})?$/

ilmoitusApp.controller('loginController', function($scope, $state) {
	//Login button. Check for correct credentials.
	$scope.username = 'developers.42IN11EWa@gmail.com';
	$scope.password = '123456';
	
	$scope.loginBtnClick = function() {
		if($scope.username && $scope.password) {
			var jsonData = {"email": $scope.username, "password": $scope.password}

			var request = $.ajax({
				type: "POST",
				url: baseurl + "/auth/login",
				crossDomain: true,
				data: jsonData,
				error: function(jqXHR, textStatus, errorThrown){
					console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
				}
			});

			request.done(function(data){
				if(data.token){
					sessionStorage.token = data.token;
					$state.go('template.declarations');
				}
				else {
					showMessage("Naam en wachtwoord combinatie is incorrect.");
				}
			});
		} else {
			showMessage("Vul alstublieft uw gebruikersnaam en wachtwoord beiden in.");
		}
		
	}
});

ilmoitusApp.controller('templateController', function($scope, $state) {
	
	//Check if user is logged in. If not, redirect to login page. 
	if(!sessionStorage.token) {
		$state.go('login');
	}

	//Get current user details
	var request = $.ajax({
		type: "GET",
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + "/current_user/details",
		crossDomain: true,
		error: function(jqXHR, textStatus, errorThrown){
			console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
		}
	});

	request.done(function(data){
		userData = data;
		$scope.userName = userData.first_name + " " + userData.last_name;
		$scope.userId = userData.employee_number;
		$scope.userClass = userData.class_name;
		$scope.$apply();
	});

	$scope.selectedNavBtn;

	// Button listeners
	$scope.logoutBtnClick = function(){ 
		$state.go('login');
	}

	$scope.navBtnClick = function(targetState) {
		$state.go(targetState);
	}

	$scope.navBtnSelect = function (navBtnId) {
		if($scope.selectedNavBtn) {$scope.selectedNavBtn.removeClass("selected");}
		$("#"+navBtnId).addClass("selected");
		$scope.selectedNavBtn = $("#"+navBtnId);
    }
});

ilmoitusApp.controller('declarationsController', function($scope, $state) {
	$scope.navBtnSelect("declarationsBtn");
	
	var request = $.ajax({
		type: "GET",
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + "/current_user/declarations",
		crossDomain: true,
		error: function(jqXHR, textStatus, errorThrown){
			console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
		}
	});

	request.done(function(data){
		$scope.declarationList = data;
		for(var i = 0 ; i < $scope.declarationList.length ; i++){
			switch($scope.declarationList[i].class_name){
				case "supervisor_declined_declaration":
					$scope.declarationList[i].info = $scope.declarationList[i].supervisor_comment;
					break;
				case "human_resources_declined_declaration":
					$scope.declarationList[i].info = $scope.declarationList[i].human_resources_comment;
					break;
				case "human_resources_approved_declaration":
					$scope.declarationList[i].info = "Word uitbetaald op: "+$scope.declarationList[i].will_be_payed_out_on;
					break;
				default:
					$scope.declarationList[i].info = "";
			}
			//turn created_at dates to actual javascript dates for comparison and string convertion.
			$scope.declarationList[i].created_at = new Date($scope.declarationList[i].created_at);
		}
		$scope.$apply();
	});
		
	//Select declaration
	$scope.selectDeclaration = function(declaration){
		$scope.currentdeclaration = declaration;
	}
	
	//Doubleclick declaration
	$scope.openDeclarationDetails = function(declarationid){
 		$state.go('template.declarationDetails', {declarationId: declarationid});
  	}
	
	//Open declaration button
	$scope.openDeclarationDetailsBtn = function(declarationid){
 		$state.go('template.declarationDetails', {declarationId: $scope.currentdeclaration.id});
  	}
	
	//Delete declaration button
	$scope.deleteDeclarationDetailsBtn = function(declarationid){
 		//TODO: bind DELETE handler
		alert('Consider declaration "'+$scope.currentdeclaration.id+'" deleted.');
  	}
});

ilmoitusApp.controller('newDeclarationController', function($scope, $state) {
	$scope.navBtnSelect("newDeclarationBtn");
	$(".datepicker").datepicker();
	
	//Declaration fields
	$scope.declaration = { comment: "", lines:[{}], attachments:[{}] };
	$scope.selectedattachment = null;
	$scope.declarationamount = 0;
	$scope.declarationAmountDisplay = "0,-";
	
	//Declaration type fields
	$scope.declaration_types = [];
	$scope.declaration_sub_types = [];
	
	var getSubtypeByID = function(row, id){
		if($scope.declaration_sub_types[row]){
			for(var i = 0; i < $scope.declaration_sub_types[row].length; i++){
				if($scope.declaration_sub_types[row][i].id == id){
					return $scope.declaration_sub_types[row][i];
				}
			}
		}
		
		return null;
	}
	
	$scope.getSupervisorByID = function(id){
		if($scope.supervisorList){
			for(var i = 0; i < $scope.supervisorList.length; i++){
				if($scope.supervisorList[i].id == id){
					return $scope.supervisorList[i];
				}
			}
		}
		
		return null;
	}
	
	//Preload supervisors
	var request = $.ajax({
		type: "GET",
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + "/current_user/supervisors",
		crossDomain: true,
		error: function(jqXHR, textStatus, errorThrown){
			console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
		}
	});
	request.done(function(data){
		$scope.supervisorList = data;
		if(data.length > 0){
			$scope.declaration.assigned_to = data[0].id;
		}
		$scope.$apply();
	});
	
	//Preload declaration types
	var request = $.ajax({
		type: "GET",
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + "/declarationtypes",
		crossDomain: true,
		error: function(jqXHR, textStatus, errorThrown){
			console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
		}
	});
	request.done(function(data){
		$scope.declaration_types = data;
		$scope.declaration_types.unshift({ id:0, name:"<selecteer>" });
		$scope.declaration.lines[0].declaration_type = $scope.declaration_types[0].id;
		$scope.$apply();
	});
	
	
	$scope.postDeclaration = function() {
		var declaration = $scope.declaration;
		var today = new Date();
		var errorReasons = [];

		// Check if everything is correctly filled in. If not, show messagebox and don't submit anything.
		if(declaration.lines.length == 1) {
			errorReasons.push("Geef minimaal 1 declaratie item op.<br/>");
		}

		if(declaration.attachments.length == 0 || declaration.attachments[0].name == undefined) {
			errorReasons.push("Voeg minimaal 1 bewijsstuk toe.<br/>");
		}

		for(var i = 0; i < declaration.lines.length - 1; i++){
			if(!declaration.lines[i].receipt_date || new Date(declaration.lines[i].receipt_date) > today) {
				errorReasons.push("Niet alle declaratie items hebben een geldige datum. Een datum kan niet in de toekomst liggen<br/>");
			}

			if(!declaration.lines[i].declaration_sub_type || declaration.lines[i].declaration_sub_type <= 0){
				errorReasons.push("Niet alle declaratie items hebben een soort en subsoort.<br/>");
			}

			if(!declaration.lines[i].approvecosts){
				errorReasons.push("Niet alle bedragen zijn correct.<br/>");
			}
		}

		if(errorReasons.length > 0) {
			var errorMessage = "Kan de declaratie niet verzenden vanwege de volgende redenen:<br/><ul>"
			for (var i = 0; i < errorReasons.length; i++) {
				errorMessage += "<li>" + errorReasons[i] + "</li>";
			};
			errorMessage += "</ul>";
			showMessage(errorMessage, "Fout");
			return;
		}

		//Remove the last empty line and send the declaration data
		declaration.lines.splice(declaration.lines.length - 1, 1);
		
		var request = $.ajax({
			type: "POST",
			headers: {"Authorization": sessionStorage.token},
			url: baseurl + "/declaration",
			crossDomain: true,
			data: JSON.stringify({ 'declaration':declaration }),
			error: function(jqXHR, textStatus, errorThrown){
				console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
			}
		});
		request.done(function(data){
			//TODO: check succes
			$state.go('template.declarations');
		});
	}
	
	//Add new row
	$scope.addRow = function(){
		if($scope.declaration.lines[$scope.declaration.lines.length-1].receipt_date){ 
			$scope.declaration.lines.push({}); 
		}	
	}
	
	//Remove row
	$scope.removeRow = function(row){
		if($scope.declaration.lines[row].receipt_date && $scope.declaration.lines.length > 1){
			$scope.declaration.lines.splice(row, 1);
		}else{
			$scope.declaration.lines[row] = {};
		}
			
		$scope.calcTotal();
	}
	
	//Load sub list when declaration type has been selected
	$scope.loadSubList = function(row){
		if($scope.declaration.lines[row].declaration_type == 0){
			$scope.declaration_sub_types[row] = [{ id:0, name:"<selecteer>" }];
			$scope.declaration.lines[row].declaration_sub_type = $scope.declaration_sub_types[row][0].id;
			return;
		}
		
		var request = $.ajax({
			type: "GET",
			headers: {"Authorization": sessionStorage.token},
			url: baseurl + "/declarationsubtypes/" + $scope.declaration.lines[row].declaration_type,
			crossDomain: true,
			error: function(jqXHR, textStatus, errorThrown){
				console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
			}
		});
		request.done(function(data){
			$scope.declaration_sub_types[row] = data;
			$scope.declaration_sub_types[row].unshift({ id:0, name:"<selecteer>" });
			$scope.declaration.lines[row].declaration_sub_type = $scope.declaration_sub_types[row][0].id;
			$scope.$apply();
			
			$scope.checkPrice(row);
		});
	}
	
	//Check if the price is valid
	$scope.checkPrice = function(row){
		var cost = $scope.declaration.lines[row].cost.replace(",", ".");
		var subtype = getSubtypeByID(row, $scope.declaration.lines[row].declaration_sub_type);
		var maxcost = subtype != null && subtype.max_cost ? subtype.max_cost : 0;

		if($scope.declaration.lines[row].cost == ""){
			$scope.declaration.lines[row].approvecosts = false;
		} else {
			$scope.declaration.lines[row].approvecosts = isFinite(Number(cost)) && Number(cost) > 0 && (maxcost <= 0 || Number(cost) <= maxcost) && pricePattern.test(cost);
		}

		$scope.calcTotal();
	}
	
	//Calculate total declaration amount each change
	$scope.calcTotal = function(){
		$scope.declarationamount = 0;
		
		for(var i = 0; i < $scope.declaration.lines.length; i++){
			if($scope.declaration.lines[i].approvecosts){
				$scope.declarationamount += Number($scope.declaration.lines[i].cost.replace(",", "."));
			}
		}

		$scope.declarationAmountDisplay = $scope.declarationamount.toString().replace(".", ",");
		if($scope.declarationAmountDisplay.indexOf(",") == -1) {
			$scope.declarationAmountDisplay += ",-";
		} else {
			if ($scope.declarationAmountDisplay.split(",")[1].length < 2) {
				$scope.declarationAmountDisplay += "0";
			}
		}
	}
	
	//Remove attachment
	$scope.removeAttachment = function(){
		if($scope.selectedattachment){
			var index = $scope.declaration.attachments.indexOf($scope.selectedattachment);
			if(index >= 0){ $scope.declaration.attachments.splice(index, 1); }
			
			$scope.selectedattachment = $scope.declaration.attachments.length > 0 ? $scope.declaration.attachments[0] : null;
		}
	}
	
	//New attachment
	$scope.addAttachments = function(){
		//Trigger the hidden file input field.
		$('#fileInput').click();
	}

	attachmentsAdded = function(){
		var fileInput = document.getElementById('fileInput');
		var files = fileInput.files;
		var i = 0;
		var allFilesSuccess = true;
		var fileReader = new FileReader();

		//When file has finished reading, add it to the attachments
		fileReader.onload = function(fileLoadedEvent) 
		{
			//Remove the first empty element that keeps apearing the first time.
			if($scope.declaration.attachments[0] && !$scope.declaration.attachments[0].file){
				$scope.declaration.attachments.splice(0, 1);
			}
			$scope.declaration.attachments.push({name: files[i].name, file: fileLoadedEvent.target.result}); 
			$scope.selectedattachment = $scope.declaration.attachments[0];
			$scope.$apply();

			//Start reading the next file. Was unable to read multiple files simultaneously.
			i++;
			readFile(i);
		};

		//Read the file, if unsupported type, skip it. 
		readFile = function(index) {
			if(i <= files.length - 1) {
				if(files[i].type == "application/pdf" || files[i].type.split("/")[0] == "image"){
					fileReader.readAsDataURL(files[i]); //Results in base64 string
				} else {
					allFilesSuccess = false;
					i++;
					readFile(i);
				}
			} else {
				//No more files left to read.
				//Clear file input to allow adding files that have already just been added. (and possibly deleted)
				resetFileInput();
				if(!allFilesSuccess){
					showMessage("Niet alle geselecteerde bestanden konden toegevoegd worden.\nAlleen afbeeldingen en pdf's zijn toegestaan.", "Fout");
				}
			}
			
		}

		resetFileInput = function() {
			$("#fileInput").wrap('<form>').parent('form').trigger('reset');
    		$("#fileInput").unwrap();
		}

		//Start reading the first file.
		readFile(i);

	}
	
});


ilmoitusApp.controller('declarationsSubmittedController', function($scope, $state) {
	$scope.navBtnSelect("declarationsSubmittedBtn");

	var request = $.ajax({
		type: "GET",
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + "/current_user/declarations/assigned",
		crossDomain: true,
		error: function(jqXHR, textStatus, errorThrown){
			console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
		}
	});

	request.done(function(data){
		$scope.declarationList = data;
		for(var i = 0 ; i < $scope.declarationList.length ; i++){
			//turn created_at dates to actual javascript dates for comparison and string convertion.
			$scope.declarationList[i].created_at = new Date($scope.declarationList[i].created_at);
		}
		$scope.$apply();
	});
		
	//Select declaration
	$scope.selectDeclaration = function(declaration){
		$scope.currentdeclaration = declaration;
	}
	
	//Doubleclick declaration
	$scope.openDeclarationDetails = function(declarationid){
 		$state.go('template.sentDeclarationDetails', {declarationId: declarationid});
  	}
	
	//Open declaration button
	$scope.openDeclarationDetailsBtn = function(declarationid){
 		$state.go('template.sentDeclarationDetails', {declarationId: $scope.currentdeclaration.id});
  	}

});

ilmoitusApp.controller('sentDeclarationDetailsController', function ($scope, $stateParams, $state) {
    // Get declaration ID from url parameter.
    $scope.declarationId = $stateParams.declarationId;

    //Get declaration details
    var request = $.ajax({
        type: "GET",
        headers: {"Authorization": sessionStorage.token},
        url: baseurl + "/declaration/" + $scope.declarationId,
        crossDomain: true,
        error: function (jqXHR, textStatus, errorThrown) {
            showMessage(jqXHR.responseJSON.user_message, "Error!");
            console.error("Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: " + errorThrown);
        }
    });

    request.done(function (data) {
        $scope.declaration = data;
        $scope.supervisorId = data.last_assigned_to.id;
        $scope.supervisor = data.last_assigned_to.first_name + " " + data.last_assigned_to.last_name;
        if ($scope.declaration.attachments.length > 0) {
            $scope.selectedattachment = $scope.declaration.attachments[0].id;
        }
        $scope.$apply();
    });

    //Preload supervisors
    request = $.ajax({
        type: "GET",
        headers: {"Authorization": sessionStorage.token},
        url: baseurl + "/current_user/supervisors",
        crossDomain: true,
        error: function (jqXHR, textStatus, errorThrown) {
            showMessage(jqXHR.responseJSON.user_message, "Error!");
            console.error("Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: " + errorThrown);
        }
    });
    request.done(function (data) {
        $scope.supervisorList = data;
        $scope.$apply();
    });

    $scope.openAttachment = function () {
        window.open("/attachment/" + $scope.selectedattachment, '_blank');
    };

    //Approve declaration button
    $scope.approveDeclarationBtn = function () {
        showMessageInputForDeclarationAction(
            "Declaratie goedkeuren",
            "Goedkeuren",
            "U heeft gekozen om de declaratie goed te keuren.<br /><br />Vul eventueel hieronder nog een opmerking in.",
            function (data) {
                var comment = (data["comment"] == "") ? null : data["comment"]; //Comment is optional.

                var request_data = {};
                if (comment != null) {
                    request_data["comment"] = comment;
                }

                handleSentDeclaration("/declaration/" + $scope.declaration.id + "/approve_by_supervisor", "PUT",
                    request_data, function () {
                        $state.go("template.declarationsSubmitted");
                    });
            }
        );
    };

    //Forward declaration button
    $scope.forwardDeclarationBtn = function () {
        var new_supervisor_id = $scope.supervisorId;
        var new_supervisor_name = "";
        if (new_supervisor_id != $scope.declaration.assigned_to) {
            for (var i in $scope.supervisorList) {
                var supervisor = $scope.supervisorList[i];
                if (supervisor.id == new_supervisor_id) {
                    new_supervisor_name = supervisor.last_name + ', ' + supervisor.first_name;
                }
            }
        } else {
            showMessage("U heeft een leidinggevende geselecteerd die al bij deze declaratie hoorde!", "Error!");
            return;
        }
        showMessageInputForDeclarationAction(
            "Declaratie doorsturen",
            "Doorsturen",
                "U heeft gekozen om de declaratie door te sturen naar: <br />\"" + new_supervisor_name +
                "\".<br />Klopt dit? Selecteer anders een andere leidinggevende.<br /><br />Vul eventueel hieronder nog een opmerking in.",
            function (data) {
                var comment = (data["comment"] == "") ? null : data["comment"]; //Comment is optional.

                var request_data = {};
                if (comment != null) {
                    request_data["comment"] = comment;
                }
                request_data["assigned_to"] = new_supervisor_id;

                handleSentDeclaration("/declaration/" + $scope.declaration.id + "/forward_to_supervisor", "PUT",
                    request_data, function () {
                        $state.go("template.declarationsSubmitted");
                    });
            }
        );
    };

    //Decline declaration button
    $scope.declineDeclarationBtn = function () {
        showMessageInputForDeclarationAction(
            "Declaration afwijzen",
            "Afwijzen",
            "U heeft gekozen om de declaratie af te wijzen.<br /><br />Geef hieronder de reden van afwijzing op (verplicht).",
            function (data) {
                var comment = (data["comment"] == "") ? null : data["comment"];

                var request_data = {};
                if (comment != null) {
                    request_data["comment"] = comment;
                } else {
                    //Comment is mandatory; show error text in the open dialog
                    var errorArea = $("#sentDeclarationDialogErrorArea");
                    if (errorArea != null) {
                        errorArea.text("Er is geen opmerking ingevuld. Dit is verplicht bij het afwijzen van een declaratie!");
                        errorArea.show();
                        return;
                    }
                }

                handleSentDeclaration("/declaration/" + $scope.declaration.id + "/decline_by_supervisor", "PUT",
                    request_data, function () {
                        $state.go("template.declarationsSubmitted");
                    });
            }
        );
    };

    function handleSentDeclaration(target_url, request_type, request_data, callback_function, should_pass_data_into_callback) {
        //Clear the error area since we don't want to give the impression it's not working
        var errorArea = $("#sentDeclarationDialogErrorArea");
        errorArea.text("");
        errorArea.hide();

        //Perform the wanted action
        var request = $.ajax({
            type: request_type,
            headers: {"Authorization": sessionStorage.token},
            url: baseurl + target_url,
            data: JSON.stringify(request_data),
            crossDomain: true,
            error: function (jqXHR, textStatus, errorThrown) {
                closeMessage();
                setTimeout(function () {
                    //TODO: find out and fix --> request body (data field above) is being appended to error response's responseText
                    //Clean the message up because for some strange reason, we get the request data appended after the wanted response
                    //This will fail if any text within this object contains a '}' character (escaped)
                    var cleanMessage = jqXHR.responseText.substring(0, jqXHR.responseText.indexOf("}") + 1);
                    showMessage(JSON.parse(cleanMessage).user_message, "Error!");
                }, 601); // 1 millisecond more than the close message timer

                console.error("Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: " + errorThrown);
            }
        });

        request.done(function (data) {
            closeMessage();
            if (should_pass_data_into_callback) {
                callback_function(data);
            } else {
                callback_function();
            }
        });
    }

    function showMessageInputForDeclarationAction(title, button_value, message, callback_function, should_show_date_selector) {
        should_show_date_selector = (typeof should_show_date_selector === "undefined") ? false : should_show_date_selector;

        var message_box = "<div class='coverBg' onclick='closeMessage();' id='coverBg' ></div>" +
            "<div class='cover' id='messageCover'>" +
            "<div class='header'>" + title +
            "<div class='closeButton' onclick='closeMessage();'>X</div>" +
            "</div>" +
            "<div class='contentMessage'>" + message +
            "<div id='payedOnSelectors'>" + "<br/>Wordt uitbetaald in:<br />Maand: <select id='payedOnMonth'/>" +
            "Jaar: <select id='payedOnYear'/>" + "</div>" +
            "<br /><br />Opmerking: <br /><input id='dialogActionComment' class='ng-pristine ng-valid' " +
            "type='text'/> <input id='confirmButton' type='button' value='" + button_value + "'/>" +
            "<br /><div id='sentDeclarationDialogErrorArea' class='errorArea' > </div>" +
            "</div>" +
            "</div>";

        $("body").append(message_box);
        if (should_show_date_selector) {
            show_date_selector_in_dialog();
        } else {
            $("#payedOnSelectors").hide();
        }
        $("#sentDeclarationDialogErrorArea").hide();
        $("#confirmButton").click(function () {
            var data = {};
            data["comment"] = $("#dialogActionComment").val();
            if (should_show_date_selector) {
                var year = $("#payedOnYear").val();
                var month = $("#payedOnMonth").val();
                //No checks needed: there is always a selected value by default
                data["will_be_payed_out_on"] = month + "-" + year;
            }
            callback_function(data);

        });
        $("#messageCover").fadeIn();
        $(".coverBg").fadeIn();
    }

    function show_date_selector_in_dialog() {
        var months = {"01": "Januari", "02": "Februari", "03": "Maart", "04": "April", "05": "Mei", "06": "Juni", "07": "Juli", "08": "Augustus", "09": "September", "10": "Oktober", "11": "November",
            "12": "December"};
        var years = {"2013": 2013, "2014": 2014, "2015": 2015, "2016": 2016, "2017": 2017, "2018": 2018, "2019": 2019,
            "2020": 2020, "2021": 2021, "2022": 2022, "2023": 2023, "2024": 2024, "2025": 2025, "2026": 2026};
        var keys = Object.keys(months).sort(); //To correctly order the months, otherwise Oktober (10) would be first
        for (var i = 0; i < keys.length; i++) {
            var key = keys[i];
            var value = months[key];
            $('#payedOnMonth')
                .append($('<option>', { value: key })
                    .text(value));
        }

        $.each(years, function (key, value) {
            $('#payedOnYear')
                .append($('<option>', { value: key })
                    .text(value));
        });
        var currentYear = new Date().getFullYear();
        $("#payedOnYear").val(currentYear);
        $("#payedOnSelectors").show();
    }
});

ilmoitusApp.controller('declarationsHistoryController', function($scope, $state) {
	$scope.navBtnSelect("declarationsHistoryBtn");
	
	var request = $.ajax({
		type: "GET",
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + "/current_user/declarations/assigned_history",
		crossDomain: true,
		error: function(jqXHR, textStatus, errorThrown){
			console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
		}
	});

	request.done(function(data){
		$scope.declarationList = data;
		for(var i = 0 ; i < $scope.declarationList.length ; i++){
			//turn created_at dates to actual javascript dates for comparison and string convertion.
			$scope.declarationList[i].created_at = new Date($scope.declarationList[i].created_at);
		}
		$scope.$apply();
	});
		
	//Select declaration
	$scope.selectDeclaration = function(declaration){
		$scope.currentdeclaration = declaration;
	}
	
	//Doubleclick declaration
	$scope.openDeclarationDetails = function(declarationid){
 		$state.go('template.declarationDetails', {declarationId: declarationid});
  	}
	
	//Open declaration button
	$scope.openDeclarationDetailsBtn = function(declarationid){
 		$state.go('template.declarationDetails', {declarationId: $scope.currentdeclaration.id});
  	}

  	//Filter function for the result table.
  	$scope.searchFilter = function(declaration)
	{
		var fromDate = new Date($scope.searchFromDate);
		var toDate = new Date($scope.searchToDate);

		if(fromDate != "Invalid Date" && declaration.created_at < fromDate){
			return false;
		}

		if(toDate != "Invalid Date" && declaration.created_at > toDate) {
			return false;
		}

	    if($scope.searchTerm &&
	    	declaration.state.toLowerCase().indexOf($scope.searchTerm.toLowerCase()) == -1 && 
	    	(declaration.created_by.first_name + " " +declaration.created_by.last_name).toLowerCase().indexOf($scope.searchTerm.toLowerCase()) == -1 &&
    		declaration.created_by.department.name.toLowerCase().indexOf($scope.searchTerm.toLowerCase()) == -1 &&
			declaration.items_count.toLowerCase().indexOf($scope.searchTerm.toLowerCase()) == -1 &&
			declaration.items_total_price.toLowerCase().indexOf($scope.searchTerm.toLowerCase()) == -1) {
	        return false;
	    }

	    return true; // It will be shown in the results
	};
});

ilmoitusApp.controller('declarationDetailsController', function($scope, $stateParams) {
	// Get declaration ID from url parameter.
	$scope.declarationId = $stateParams.declarationId;

	//Get declaration details
	var request = $.ajax({
		type: "GET",
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + "/declaration/"+$scope.declarationId,
		crossDomain: true,
		error: function(jqXHR, textStatus, errorThrown){
			console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
		}
	});

	request.done(function(data){
		$scope.declaration = data;
		$scope.comments = data.comment;
		$scope.supervisorId = data.last_assigned_to.employee_number
		$scope.supervisor = data.last_assigned_to.first_name + " " + data.last_assigned_to.last_name;
		if($scope.declaration.attachments.length > 0){
			$scope.selectedattachment = $scope.declaration.attachments[0].id;
		}
		$scope.$apply();
	});

    $scope.openAttachment = function() {
        window.open("/attachment/"+$scope.selectedattachment, '_blank');
    }
    
});