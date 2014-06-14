var baseurl = 'http://127.0.0.1:8080';
var userData;
var pricePattern = /^[0-9]{1}[0-9]{0,3}(\.[0-9]{0,2})?$/

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
					showServerMessage(jqXHR, "Inloggen niet gelukt vanwege een onbekende fout.", "Fout");
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
		async: false,
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + "/current_user/details",
		crossDomain: true,
		error: function(jqXHR, textStatus, errorThrown){
			console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
			showServerMessage(jqXHR, "Inloggen niet gelukt. Kan geen gebruikersgegevens ophalen.", "Fout");
			$state.go('login');
		}
	});

	request.done(function(data){
		userData = data;
		$scope.userName = userData.first_name + " " + userData.last_name;
		$scope.userId = userData.employee_number;
		$scope.userClass = userData.class_name;
	});

	$scope.selectedNavBtn;

	// Button listeners
	$scope.logoutBtnClick = function(){ 
		$state.go('login');
	}

	$scope.navBtnClick = function(targetState, params) {
		if(targetState == "template.declarationForm") {
			$state.go(targetState, {action: "new", declarationId: ""});
		} else {
			$state.go(targetState);
		}
	}

	$scope.navBtnSelect = function (navBtnId) {
		if($scope.selectedNavBtn) {$scope.selectedNavBtn.removeClass("selected");}
		if(navBtnId != null) {
			$("#"+navBtnId).addClass("selected");
			$scope.selectedNavBtn = $("#"+navBtnId);
		} else {
			$scope.selectedNavBtn = null;
		}
    }
});

ilmoitusApp.controller('declarationsController', function($scope, $state) {
	$scope.navBtnSelect("declarationsBtn");
	
	var request = $.ajax({
		type: "GET",
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + "/current_user/declarations",
		crossDomain: true
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
			
			//Format price
			$scope.declarationList[i].items_total_price = Number($scope.declarationList[i].items_total_price).formatMoney(2, ",", ".");
		}
		$scope.$apply();
	}).fail(function() {
    	$scope.declarationList = [];
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
		var request = $.ajax({
			type: "DELETE",
			headers: {"Authorization": sessionStorage.token},
			url: baseurl + "/declaration/"+$scope.currentdeclaration.id,
			crossDomain: true,
			error: function(jqXHR, textStatus, errorThrown){
				console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
				showServerMessage(jqXHR, "Kan de declaratie niet annuleren vanwege een onbekende fout.", "Fout");
			}
		});

		request.done(function(){
			for(var i = 0 ; i < $scope.declarationList.length ; i++){
				if($scope.declarationList[i].id == $scope.currentdeclaration.id) {
					$scope.declarationList.splice(i, 1);
					$scope.$apply();
					break;
				}
			}
		});
  	}
});

ilmoitusApp.controller('declarationFormController', function($scope, $state, $stateParams) {
	
	//Declaration fields
	$scope.declaration = { comment: "", lines:[{}], attachments:[{}] };
	$scope.selectedattachment = null;
	$scope.declarationamount = 0;
	$scope.declarationAmountDisplay = "0,-";
	
	//Declaration type fields
	$scope.declaration_types = [];
	$scope.declaration_sub_types = [];
	
	// Get declaration information if we need to edit a declaration. 
	editMode = $stateParams.action == "edit";
	if(editMode) {
		$scope.declarationId = $stateParams.declarationId;
		//Get declaration details
		var declarationRequest = $.ajax({
			type: "GET",
			headers: {"Authorization": sessionStorage.token},
			url: baseurl + "/declaration/"+$scope.declarationId,
			crossDomain: true,
			error: function(jqXHR, textStatus, errorThrown){
				console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
				showServerMessage(jqXHR, "Kan de declaratie gegevens niet ophalen vanwege een onbekende fout.", "Fout");
				$state.go('template.declarations');
			}
		});

		declarationRequest.done(function(data){
			//Change all the received declaration data to the way the form needs them.
			$scope.declaration = data;
			$scope.declaration.supervisor = $scope.declaration.last_assigned_to.id;
			$scope.declaration.items_total_price = Number($scope.declaration.items_total_price).formatMoney(2, ",", ".")
		
		if($scope.declaration.attachments.length > 0){
			$scope.selectedattachment = $scope.declaration.attachments[0].id;
		}
		
		for(var i = 0 ; i < $scope.declaration.lines.length; i++){
			//Format price
			$scope.declaration.lines[i].cost = Number($scope.declaration.lines[i].cost).formatMoney(2, ",", ".");
		}
			
			if($scope.declaration.attachments.length > 0){
				$scope.selectedattachment = $scope.declaration.attachments[0];
			}
			for(var i = 0; i < $scope.declaration.lines.length; i++){ 
				$scope.declaration.lines[i].receipt_date = new Date($scope.declaration.lines[i].receipt_date).toISOString().substring(0, 10);
				$scope.declaration.lines[i].cost = Number($scope.declaration.lines[i].costs).formatMoney(2, ",", ".")+"";
				
				$scope.declaration.lines[i].declaration_type = $scope.declaration.lines[i].declaration_type.id;
				$scope.loadSubList(i);
				$scope.declaration.lines[i].declaration_sub_type = $scope.declaration.lines[i].declaration_sub_type.id;
				$scope.checkFields(i);
			}
			//Add extra empty line so new lines can be added.
			$scope.addRow();
			$scope.$apply();
		});
	} else {
		$scope.navBtnSelect("newDeclarationBtn");
	}

	//Preload supervisors
	var supervisorRequest = $.ajax({
		type: "GET",
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + "/current_user/supervisors",
		crossDomain: true,
		error: function(jqXHR, textStatus, errorThrown){
			console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
		}
	});
	supervisorRequest.done(function(data){
		$scope.supervisorList = data;
		if(data.length > 0){
			if(!editMode) {
				$scope.declaration.supervisor = data[0].id;
			}
		}
		$scope.$apply();
	});
	
	//Preload declaration types
	var declarationtypeRequest = $.ajax({
		type: "GET",
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + "/declarationtypes",
		crossDomain: true,
		error: function(jqXHR, textStatus, errorThrown){
			console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
		}
	});
	declarationtypeRequest.done(function(data){
		$scope.declaration_types = data;
		$scope.declaration_types.unshift({ id:0, name:"<selecteer>" });
		if(!editMode) {
			$scope.declaration.lines[0].declaration_type = $scope.declaration_types[0].id;
		}
		$scope.$apply();
	});
	
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
	
	$scope.postDeclaration = function() {
		var declaration = $scope.declaration;
		var errorReasons = [];

		// Check if everything is correctly filled in. If not, show messagebox and don't submit anything.
		if(declaration.lines.length == 1) {
			errorReasons.push("Geef minimaal 1 declaratie item op.<br/>");
		}

		if(declaration.attachments.length == 0 || declaration.attachments[0].name == undefined) {
			errorReasons.push("Voeg minimaal 1 bewijsstuk toe.<br/>");
		}

		for(var i = 0; i < declaration.lines.length - 1; i++){
			if(!declaration.lines[i].approvedate) {
				errorReasons.push("Niet alle declaratie items hebben een geldige datum. Een datum mag niet in de toekomst liggen<br/>");
			}

			if(!declaration.lines[i].approvesubtype || declaration.lines[i].approvesubtype <= 0){
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
		//replace all comma's with dots.
		for (var i = 0; i < declaration.lines.length; i++) {
			declaration.lines[i].cost = declaration.lines[i].cost.replace(",", ".");
		};
		
		if (editMode) {
			var type = "PUT";
			var url = "/declaration/"+declaration.id;
		} else {
			var type = "POST";
			var url = "/declaration";
		}

		var request = $.ajax({
			type: type,
			headers: {"Authorization": sessionStorage.token},
			url: baseurl + url,
			crossDomain: true,
			data: JSON.stringify({ 'declaration':declaration }),
			error: function(jqXHR, textStatus, errorThrown){
				console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
				showServerMessage(jqXHR, "Kan de declaratie niet verzenden vanwege een onbekende fout.", "Fout");
			}
		});
		request.done(function(data){
			if(editMode) {
				$state.go('template.declarationDetails', {declarationId: declaration.id});
			} else {
				$state.go('template.declarations');
			}
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
			url: baseurl + "/declarationtype/" + $scope.declaration.lines[row].declaration_type,
			crossDomain: true,
			error: function(jqXHR, textStatus, errorThrown){
				console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
			}
		});
		request.done(function(data){
			$scope.declaration_sub_types[row] = data;
			$scope.declaration_sub_types[row].unshift({ id:0, name:"<selecteer>" });
			if(!editMode) {
				$scope.declaration.lines[row].declaration_sub_type = $scope.declaration_sub_types[row][0].id;
			}
			$scope.$apply();
		});
	}

	$scope.checkFields = function(row){
		var today = new Date();

		if(!$scope.declaration.lines[row].receipt_date || new Date($scope.declaration.lines[row].receipt_date) > today) {
			$scope.declaration.lines[row].approvedate = false;
		} else {
			$scope.declaration.lines[row].approvedate = true;
		}

		if(!$scope.declaration.lines[row].declaration_type || $scope.declaration.lines[row].declaration_type <= 0){
			$scope.declaration.lines[row].approvetype = false;
			$scope.declaration.lines[row].approvesubtype = false;
		} else if(!$scope.declaration.lines[row].declaration_sub_type || $scope.declaration.lines[row].declaration_sub_type <= 0){
			$scope.declaration.lines[row].approvetype = true;
			$scope.declaration.lines[row].approvesubtype = false;
		} else {
			$scope.declaration.lines[row].approvetype = true;
			$scope.declaration.lines[row].approvesubtype = true;
		}

		$scope.checkPrice(row);
	}
	
	//Check if the price is valid
	$scope.checkPrice = function(row){
		if($scope.declaration.lines[row].cost == undefined || $scope.declaration.lines[row].cost == ""){
			$scope.declaration.lines[row].approvecosts = false;
		} else {
			var cost = $scope.declaration.lines[row].cost.replace(",", ".");
			var subtype = getSubtypeByID(row, $scope.declaration.lines[row].declaration_sub_type);
			var maxcost = subtype != null && subtype.max_cost ? subtype.max_cost : 0;
			$scope.declaration.lines[row].approvecosts = isFinite(Number(cost)) && Number(cost) > 0 && (maxcost <= 0 || Number(cost) <= maxcost) && pricePattern.test(cost);
		}

		$scope.calcTotal();
	}
	
	//Calculate total declaration amount each change
	$scope.calcTotal = function(){
		$scope.declarationamount = 0;
		
		for(var i = 0; i < $scope.declaration.lines.length; i++){
			if($scope.declaration.lines[i].approvecosts){
				var money = $scope.declaration.lines[i].cost.replace(",", ".");
				//if(money.indexOf(",") == money.length -1){ money = money.substr(0, money.length-1); }
				$scope.declarationamount += Number(money);
			}
		}
		
		$scope.declarationAmountDisplay = Number($scope.declarationamount).formatMoney(2, ",", ".");
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
			if($scope.declaration.attachments[0] && !$scope.declaration.attachments[0].name){
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


ilmoitusApp.controller('sentDeclarationsController', function($scope, $state) {
	$scope.navBtnSelect("sentDeclarationsBtn");

	if (userData.class_name == "human_resources") {
		var url = "/declarations/hr"
	} else {
		var url = "/current_user/declarations/assigned";
	}

	var request = $.ajax({
		type: "GET",
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + url,
		crossDomain: true
	});

	request.done(function(data){
		$scope.declarationList = data;
		for(var i = 0 ; i < $scope.declarationList.length ; i++){
			//turn created_at dates to actual javascript dates for comparison and string convertion.
			$scope.declarationList[i].created_at = new Date($scope.declarationList[i].created_at);
			
			//Format price
			$scope.declarationList[i].items_total_price = Number($scope.declarationList[i].items_total_price).formatMoney(2, ",", ".");
		}
		$scope.$apply();
	}).fail(function() {
    	$scope.declarationList = [];
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
    $scope.isAllowedToApprove = true;
    $scope.hasSupervisor = (userData.supervisor != null);

    //Get declaration details
    var request = $.ajax({
        type: "GET",
        headers: {"Authorization": sessionStorage.token},
        url: baseurl + "/declaration/" + $scope.declarationId,
        crossDomain: true,
        error: function (jqXHR, textStatus, errorThrown) {
            console.error("Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: " + errorThrown);
            showServerMessage(jqXHR, "Er is iets fout gegaan bij het ophalen van de gegevens van deze declaratie.", "Error!");
        }
    });

    request.done(function (data) {
        $scope.declaration = data;
        $scope.supervisorId = data.last_assigned_to.id;
        $scope.supervisor = data.last_assigned_to.first_name + " " + data.last_assigned_to.last_name;
        $scope.declaration.items_total_price = Number($scope.declaration.items_total_price).formatMoney(2, ",", ".");
		
		if($scope.declaration.attachments.length > 0){
			$scope.selectedattachment = $scope.declaration.attachments[0].id;
		}
		
		for(var i = 0 ; i < $scope.declaration.lines.length; i++){
			//Format price
			$scope.declaration.lines[i].cost = Number($scope.declaration.lines[i].cost).formatMoney(2, ",", ".");
		}
		
        lockIfNeeded();
        checkIfCanApprove();

        $scope.$apply();
    });

    function lockIfNeeded() {
        if ($scope.userClass == "supervisor" && $scope.declaration.class_name == "open_declaration") {
            //Lock the declaration since we are now reviewing it
            var request = $.ajax({
                type: "PUT",
                headers: {"Authorization": sessionStorage.token},
                url: baseurl + "/declaration/" + $scope.declarationId + "/lock",
                crossDomain: true,
                error: function (jqXHR, textStatus, errorThrown) {
                    console.error("Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: " + errorThrown);
                    showServerMessage(jqXHR, "Het vergrendelen van de declaratie is niet gelukt.", "Fout bij het vergrendelen!");
                }
            });
            //No done callback; we don't need to wait for the declaration to get locked
        }
    }

    if ($scope.userClass == "supervisor") {
        //Preload supervisors
        request = $.ajax({
            type: "GET",
            headers: {"Authorization": sessionStorage.token},
            url: baseurl + "/current_user/supervisors",
            crossDomain: true,
            error: function (jqXHR, textStatus, errorThrown) {
                console.error("Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: " + errorThrown);
                showServerMessage(jqXHR, "Er is iets fout gegaan bij het ophalen van uw leidinggevenden.", "Error!");
            }
        });

        request.done(function (data) {
            $scope.supervisorList = data;
            $scope.supervisorList.unshift(userData);

            $scope.$apply();
        });
    }

    $scope.openAttachment = function () {
		var request = $.ajax({
			type: "GET",
			headers: {"Authorization": sessionStorage.token},
			url: baseurl + "/attachment_token/"+$scope.selectedattachment,
			crossDomain: true,
			error: function(jqXHR, textStatus, errorThrown){
                console.error("Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: " + errorThrown);
				showServerMessage(jqXHR, "Kan de attachment niet ophalen vanwege een onbekende fout.", "Fout");
			}
		});

        request.done(function(data){
			var token = data["attachment_token"];
			window.open(baseurl + "/attachment/"+$scope.selectedattachment+"/"+token, '_blank');
		});
    };

    function checkIfCanApprove() {
        if($scope.userClass == "supervisor") {
            var userMaxPrice = parseInt(userData.max_declaration_price);
            $scope.isAllowedToApprove = (parseInt($scope.declaration.items_total_price) <= userMaxPrice);
            if (userMaxPrice) {
                $scope.max_declaration_price = userMaxPrice;
            }
            else {
                $scope.max_declaration_price = "0.0";
            }
        }
    }

    function approveDeclarationHR() {
        showMessageInputForDeclarationAction(
            "Declaratie goedkeuren",
            "Goedkeuren",
            "U heeft gekozen om de declaratie goed te keuren.<br /><br />Vul hieronder in welke maand de declaratie wordt uitbetaald en eventueel nog een opmerking in.",
            function (data) {
                var comment = (data["comment"] == "") ? null : data["comment"]; //Comment is optional.

                var request_data = {};
                if (comment != null) {
                    request_data["comment"] = comment;
                }
                //Date will always be picked, but just to be safe:
                var will_be_payed_out_on = (data["will_be_payed_out_on"] == "") ? null : data["will_be_payed_out_on"];
                if (will_be_payed_out_on) {
                    request_data["will_be_payed_out_on"] = will_be_payed_out_on;
                } else {
                    showMessage("Er is geen datum opgegeven waarin de declaratie wordt uitbetaald!", "Error!");
                    return;
                }
                handleSentDeclaration("/declaration/" + $scope.declaration.id + "/approve_by_hr", "PUT",
                    request_data, function () {
                        $state.go("template.sentDeclarations");
                    });
            },
            true
        );
    }

    function approveDeclarationSupervisor() {
        if (parseInt($scope.declaration.items_total_price) <= parseInt($scope.max_declaration_price)) {
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
                            $state.go("template.sentDeclarations");
                        });
                }
            );
        } else {
            showMessage("<p>U mag deze declaratie niet goedkeuren omdat het bedrag te hoog is!</p>" +
                    "<p>Uw maximaal goed te keuren bedrag is: &euro;" + $scope.declaration.last_assigned_to.max_declaration_price +
                    "</p><p>Terwijl deze declaratie een totaal bedrag heeft van: &euro;" +
                    $scope.declaration.items_total_price + "</p><p>U mag deze declaratie alleen doorsturen.</p>",
                "Error!");
        }
    }

    function forwardDeclarationSupervisor() {
        var new_supervisor_id = $scope.supervisorId; //This is the index value of the selection box
        var new_supervisor_name = "";
        if (new_supervisor_id != $scope.declaration.last_assigned_to.id) {
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
                        $state.go("template.sentDeclarations");
                    });
            }
        );
    }

    function declineDeclarationHR() {
        showMessageInputForDeclarationAction(
            "Declaratie afwijzen",
            "Afwijzen",
            "U heeft gekozen om de declaratie af te wijzen.<br /><br />Geef hieronder eventueel nog de reden van afwijzing op.",
            function (data) {
                var comment = (data["comment"] == "") ? null : data["comment"];

                var request_data = {};
                if (comment != null) {
                    request_data["comment"] = comment;
                } //Comment is optional for HR!

                handleSentDeclaration("/declaration/" + $scope.declaration.id + "/decline_by_hr", "PUT",
                    request_data, function () {
                        $state.go("template.sentDeclarations");
                    });
            }
        );
    }

    function declineDeclarationSupervisor() {
        showMessageInputForDeclarationAction(
            "Declaratie afwijzen",
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
                        $state.go("template.sentDeclarations");
                    });
            }
        );
    }

    //Approve declaration button
    $scope.approveDeclarationBtn = function () {
        if ($scope.userClass == "supervisor") {
            approveDeclarationSupervisor();
        } else {
            approveDeclarationHR();
        }
    };


    //Forward declaration button
    $scope.forwardDeclarationBtn = function () {
        if ($scope.userClass == "supervisor") {
            forwardDeclarationSupervisor();
        } //HR can't forward; no else
    };

    //Decline declaration button
    $scope.declineDeclarationBtn = function () {
        if ($scope.userClass == "supervisor") {
            declineDeclarationSupervisor();
        } else {
            declineDeclarationHR();
        }
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
                console.error("Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: " + errorThrown);
                closeMessage();
                setTimeout(function () {
                    showServerMessage(jqXHR, "Een onbekende fout is opgetereden bij deze actie", "Error!");
                }, 601); // 1 millisecond more than the close message timer

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
        var currentYear = new Date().getFullYear();
        var years = {};
        var numberOfYearsFromNow = currentYear + 10;
        //Add at least 10 years in the years dict
        for(var i = parseInt(currentYear); i < numberOfYearsFromNow; i++){
            years[i + ""] = i;
        }

        var keys = Object.keys(months).sort(); //To correctly order the months, otherwise Oktober (10) would be first
        for (i = 0; i < keys.length; i++) {
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
        var currentMonth = new Date().getMonth();  //Returns the month number
        $("#payedOnYear").val(currentYear);
        $("#payedOnMonth").val(keys[currentMonth]);
        $("#payedOnSelectors").show();
    }
});

ilmoitusApp.controller('declarationsHistoryController', function($scope, $state) {
	$scope.navBtnSelect("declarationsHistoryBtn");

	if (userData.class_name == "human_resources") {
		var url = "/declarations/hr_history"
	} else {
		var url = "/current_user/declarations/assigned_history";
	}
	
	var request = $.ajax({
		type: "GET",
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + url,
		crossDomain: true
	});

	request.done(function(data){
		$scope.declarationList = data;
			for(var i = 0 ; i < $scope.declarationList.length ; i++){
				//turn created_at dates to actual javascript dates for comparison and string convertion.
				$scope.declarationList[i].created_at = new Date($scope.declarationList[i].created_at);
				
				//Format price
				$scope.declarationList[i].items_total_price = Number($scope.declarationList[i].items_total_price).formatMoney(2, ",", ".");
			}
			$scope.$apply();
		}).fail(function() {
			$scope.declarationList = [];
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

ilmoitusApp.controller('declarationDetailsController', function($scope, $state, $stateParams) {
	$scope.navBtnSelect(null);

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
			showServerMessage(jqXHR, "Kan de declaratie gegevens niet ophalen vanwege een onbekende fout.", "Fout");
			$state.go('template.declarations');
		}
	});

	request.done(function(data){
		$scope.declaration = data;
		$scope.comments = data.comment;
		$scope.supervisorId = data.last_assigned_to.employee_number
		$scope.supervisor = data.last_assigned_to.first_name + " " + data.last_assigned_to.last_name;
		$scope.declaration.items_total_price = Number($scope.declaration.items_total_price).formatMoney(2, ",", ".")
		
		if($scope.declaration.attachments.length > 0){
			$scope.selectedattachment = $scope.declaration.attachments[0].id;
		}
		
		for(var i = 0 ; i < $scope.declaration.lines.length; i++){
			//Format price
			$scope.declaration.lines[i].cost = Number($scope.declaration.lines[i].cost).formatMoney(2, ",", ".");
		}
			
		$scope.$apply();
	});

    $scope.openAttachment = function() {
		
		var request = $.ajax({
			type: "GET",
			headers: {"Authorization": sessionStorage.token},
			url: baseurl + "/attachment_token/"+$scope.selectedattachment,
			crossDomain: true,
			error: function(jqXHR, textStatus, errorThrown){
				showServerMessage(jqXHR, "Kan de attachment niet ophalen vanwege een onbekende fout.", "Fout");
			}
		});	
		
        request.done(function(data){
			var token = data["attachment_token"];
			window.open(baseurl + "/attachment/"+$scope.selectedattachment+"/"+token, '_blank');
		});
    }

    $scope.editDeclarationBtn = function() {
    	$state.go('template.declarationForm', {action: "edit", declarationId: $scope.declarationId});
    }
    
});