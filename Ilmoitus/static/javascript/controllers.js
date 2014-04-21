ilmoitusApp.controller('loginController', function($scope, $state) {
	//Login button. Check for correct credentials.
	$scope.loginBtnClick = function() {
		$state.go('template.declarations');
	}
});

ilmoitusApp.controller('templateController', function($scope, $state) {
	//PLACEHOLDERS login info. This info should be retrieved from models (factories).
	$scope.userName = "Piet Maas";
	$scope.userId = "9120103";

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
	$http.get('/declarations/employee').then(function(res){
		$scope.declarationList = res.data;
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

	}, function(err) { 
		console.error(err);
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

ilmoitusApp.controller('newDeclarationController', function($scope) {
	$scope.navBtnSelect("newDeclarationBtn");
	$(".datepicker").datepicker();
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
		url: "/declaration/"+$scope.declarationId,
		error: function(jqXHR, textStatus, errorThrown){
			console.error( "Request failed: \ntextStatus: " + textStatus + " \nerrorThrown: "+errorThrown );
		}
	});

	request.done(function(data){
		$scope.comments = data.comment;
		$scope.$apply();

		//Get supervisor name and id
		var supervisorKey = data.assigned_to[data.assigned_to.length-1];
		var request2 = $.ajax({
			type: "GET",
			url: "/persons/"+supervisorKey,
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

	$scope.totalPrice = "90,-"
	$scope.itemList =	[
							{"date": "asdf", "sort": "qwer", "subsort": "zcxv", "price": "20", "comment": "placeholder1"}, 
							{"date": "fdsa", "sort":  "poiu", "subsort":  "/,m", "price": "30", "comment": "placeholder2"}, 
							{"date": "123", "sort":  "456", "subsort": "789", "price": "40", "comment": "placeholder3"}
						];
});