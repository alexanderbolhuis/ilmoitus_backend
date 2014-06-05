ilmoitusApp.config(function($stateProvider, $urlRouterProvider) {
	
	// For any unmatched url, redirect to /
	$urlRouterProvider.otherwise("/board/declarations");
	
	// Now set up the states
	$stateProvider
	.state('login', {
		url: "/login",
		templateUrl: "html/login.html",
		controller: "loginController"
	})
	.state('template', {
		url: "/board",
		templateUrl: "html/template.html",
		controller: "templateController"
	})
	.state('template.declarations', {
		url: "/declarations",
		templateUrl: "html/declarations.html",
		controller: "declarationsController"
	})
	.state('template.sentDeclarations', {
		url: "/declarationsSubmitted",
		templateUrl: "html/sentDeclarations.html",
		controller: "sentDeclarationsController"
	})
	.state('template.declarationForm', {
		url: "/declarationForm/:action/:declarationId",
		templateUrl: "html/declarationForm.html",
		controller: "declarationFormController"
	})
	.state('template.sentDeclarationDetails', {
		url: "/sentDeclarationDetails/:declarationId",
		templateUrl: "html/sentDeclarationDetails.html",
		controller: "sentDeclarationDetailsController"
	})
	.state('template.declarationsHistory', {
		url: "/declarationsHistory",
		templateUrl: "html/declarationsHistory.html",
		controller: "declarationsHistoryController"
	})
	.state('template.declarationDetails', {
		url: "/declarationDetails/:declarationId",
		templateUrl: "html/declarationDetails.html",
		controller: "declarationDetailsController"
	})
});
