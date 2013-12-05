function validate(){
	//$.validity.setup({ outputMode:"label" });
	$.validity.start();
	$("#username").require();
	$("#password").require();
	var result = $.validity.end()
	if(result.errors ==0){
		authenticate();
	}
}

function authenticate(){
	var params = {username:$("#username").val(), password:$("#password").val()};
	$.post( "/api/auth/login/", params, function( data ) {
	  $.localStorage.set("token", data.token);
	  window.location ="/index.html";
	}).fail(function(error) {
		//alert( $.parseJSON(error.responseText).errors[0] );
		$("#errorform").html(i18n.t("error.loginIncorrect")).show();
	});
}
$(document).ready(function(){
	var option = { resGetPath: '/static/locales/__lng__/__ns__.json' };
	i18n.init(option, function(t) {
		$("body").i18n();	
		loadConfigGeneral();
		$("#btnLogin").click(function(){validate()});	
		$("#loginform input").keydown(function(event){
			if(event.keyCode == 13 && jQuery.support.submitBubbles) {
				validate();
			};
		})
	});	
});