var baseurl = 'http://127.0.0.1:8080';
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
		$scope.userName = data.first_name + " " + data.last_name;
		$scope.userId = data.employee_number;
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

ilmoitusApp.controller('declarationsController', function($scope, $state, $http) {
	$scope.navBtnSelect("declarationsBtn");
	
	var request = $.ajax({
		type: "GET",
		headers: {"Authorization": sessionStorage.token},
		url: baseurl + "/declarations/employee",
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

		//sort the array on creation date
		$scope.declarationList.sort(function(a, b) {
		    a = a.created_at;
		    b = b.created_at;
		    return a>b ? -1 : a<b ? 1 : 0;
		});
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
	$scope.declaration = { lines:[{}] };
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
		url: baseurl + "/supervisors/",
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
		for(var i = 0; i < declaration.lines.length; i++){
			if(!declaration.lines[i].declaration_sub_type || declaration.lines[i].declaration_sub_type <= 0){
				declaration.lines.splice(i, 1);	
			}
		}
		
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
	$scope.addAttachment = function(){
		
	}
	
});


ilmoitusApp.controller('declarationsSubmittedController', function($scope) {
	$scope.navBtnSelect("sendedDeclarationsBtn");
});

ilmoitusApp.controller('sentDeclarationDetailsController', function($scope) {
	$scope.navBtnSelect("sentDeclarationDetailsBtn");
});

ilmoitusApp.controller('declarationsHistoryController', function($scope) {
	$scope.navBtnSelect("declarationsHistoryBtn");
	
	//TODO: use Angular like in declarations.html
	SetTableSelectable("declarationTable");
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
		if($scope.declaration.attachments.length > 0){
			$scope.selectedattachment = $scope.declaration.attachments[0].id;
		}
		$scope.$apply();
		
		//Get supervisor name and id
		var supervisorKey = data.assigned_to[data.assigned_to.length-1];
		var request2 = $.ajax({
			type: "GET",
			headers: {"Authorization": sessionStorage.token},
			url: baseurl + "/persons/"+supervisorKey,
			crossDomain: true,
			error: function(jqXHR, textStatus, errorThrown){
				console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
			}
		});

		request2.done(function(data){
			$scope.supervisorId = data.employee_number;
			$scope.supervisor = data.first_name + " " + data.last_name;
			$scope.$apply();
		});
	});

    $scope.openAttachment = function() {
        window.open("/attachment/"+$scope.selectedattachment, '_blank');
    }
    
});